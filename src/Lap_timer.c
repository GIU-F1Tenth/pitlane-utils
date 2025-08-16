#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <inttypes.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/event_groups.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_log.h"
#include "nvs_flash.h"
#include "esp_netif.h"
#include "esp_timer.h"
#include "driver/uart.h"
#include "driver/gpio.h"
#include "mqtt_client.h"

#define WIFI_SSID        "Tedata3421"
#define WIFI_PASS        "342911311rbhas"
#define BROKER_URI       "mqtt://192.168.1.8"   
#define WIFI_CONNECTED_BIT BIT0
#define UART_PORT        UART_NUM_2
#define UART_BAUD        500000
#define UART_RX_PIN      16
#define UART_TX_PIN      17
#define MQTT_TOPIC_DATA  "lap_timer/data"    // publishes
#define MQTT_TOPIC_CTRL  "lap_timer/control" // subscribes
//variables
#define THRESHOLD_MM     250     // crossing if distance < 250 mm
#define DEBOUNCE_MS      150     // reject bounces within 150 ms
#define COOLDOWN_MS      800     // prevent retrigger for this long
#define MEDIAN_WINDOW    5       //Size of the median filter window for smoothing noisy distances.


//globals 
static const char *TAG = "LAP";
static EventGroupHandle_t s_wifi_event_group;
static esp_mqtt_client_handle_t s_mqtt = NULL;
static int lap_count = 0;
static int64_t last_trigger_us = 0;
static int64_t last_lap_start_us = 0;
static int distances[MEDIAN_WINDOW] = {0};
static int d_idx = 0;
static int d_filled = 0;

// Wi-Fi 
static void wifi_event_handler(void* arg, esp_event_base_t event_base,
                               int32_t event_id, void* event_data) {
    if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_START) {
        esp_wifi_connect();
    } else if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_DISCONNECTED) {
        esp_wifi_connect();
        ESP_LOGW(TAG, "Wi-Fi disconnected, retrying...");
    } else if (event_base == IP_EVENT && event_id == IP_EVENT_STA_GOT_IP) {
        xEventGroupSetBits(s_wifi_event_group, WIFI_CONNECTED_BIT);
        ESP_LOGI(TAG, "Got IP.");
    }
}

static void wifi_init_sta(void) {
    s_wifi_event_group = xEventGroupCreate();
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    esp_netif_create_default_wifi_sta();

    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK( esp_wifi_init(&cfg) );

    esp_event_handler_instance_t any_id, got_ip;
    ESP_ERROR_CHECK(esp_event_handler_instance_register(WIFI_EVENT,ESP_EVENT_ANY_ID, &wifi_event_handler, NULL, &any_id));
    ESP_ERROR_CHECK(esp_event_handler_instance_register(IP_EVENT,IP_EVENT_STA_GOT_IP, &wifi_event_handler, NULL, &got_ip));

    wifi_config_t wifi_config = {
        .sta = {
            .ssid = WIFI_SSID,
            .password = WIFI_PASS,
            .threshold.authmode = WIFI_AUTH_WPA2_PSK,
        },
    };
    ESP_ERROR_CHECK( esp_wifi_set_mode(WIFI_MODE_STA) );
    ESP_ERROR_CHECK( esp_wifi_set_config(WIFI_IF_STA, &wifi_config) );
    ESP_ERROR_CHECK( esp_wifi_start() );

    ESP_LOGI(TAG, "Wi-Fi init STA done");
    xEventGroupWaitBits(s_wifi_event_group, WIFI_CONNECTED_BIT, false, true, portMAX_DELAY);
}

//mqtt
static esp_err_t mqtt_event_handler_cb(esp_mqtt_event_handle_t event) {
    switch (event->event_id) {
        case MQTT_EVENT_CONNECTED:
            ESP_LOGI(TAG, "MQTT connected");
            esp_mqtt_client_subscribe(s_mqtt, MQTT_TOPIC_CTRL, 0);
            break;
        case MQTT_EVENT_DATA: {
            // Optional: receive control commands from GUI ("start","reset","restart")
            char *topic = strndup(event->topic, event->topic_len);
            char *data = strndup(event->data, event->data_len);
            ESP_LOGI(TAG, "MQTT msg [%s]: %s", topic, data);

            if (strcmp(topic, MQTT_TOPIC_CTRL) == 0) {
                if (strcmp(data, "start") == 0) {
                    lap_count = 0;
                    last_lap_start_us = esp_timer_get_time();
                    ESP_LOGI(TAG, "Control: start");
                } else if (strcmp(data, "reset") == 0) {
                    lap_count = 0;
                    last_lap_start_us = 0;
                    ESP_LOGI(TAG, "Control: reset");
                } else if (strcmp(data, "restart") == 0) {
                    last_lap_start_us = esp_timer_get_time();
                    ESP_LOGI(TAG, "Control: restart");
                }
            }
            free(topic); free(data);
            break;
        }
        default: break;
    }
    return ESP_OK;
}

static void mqtt_start(void) {
    esp_mqtt_client_config_t cfg = {
        .broker = {
            .address.uri = BROKER_URI,   // MQTT broker address
        },
        .session = {
            .keepalive = 60,             // Keepalive in seconds
        },
    };
    s_mqtt = esp_mqtt_client_init(&cfg);
    esp_mqtt_client_register_event(s_mqtt, ESP_EVENT_ANY_ID, mqtt_event_handler_cb, NULL);
    esp_mqtt_client_start(s_mqtt);
}


//uart
static void uart_init(void) {
    uart_config_t ucfg = {
        .baud_rate = UART_BAUD,
        .data_bits = UART_DATA_8_BITS,
        .parity    = UART_PARITY_DISABLE,
        .stop_bits = UART_STOP_BITS_1,
        .flow_ctrl = UART_HW_FLOWCTRL_DISABLE,
        .source_clk = UART_SCLK_DEFAULT,
    };
    ESP_ERROR_CHECK(uart_driver_install(UART_PORT, 2048, 0, 0, NULL, 0));
    ESP_ERROR_CHECK(uart_param_config(UART_PORT, &ucfg));
    ESP_ERROR_CHECK(uart_set_pin(UART_PORT, UART_TX_PIN, UART_RX_PIN, UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE));
}

// Parse a line like "1234\n" -> returns mm or -1 if not valid
static int parse_distance_line(const char *line) { // trim
    char *endp;
    long val = strtol(line, &endp, 10);
    if (endp == line) return -1;
    if (val < 0 || val > 50000) return -1; // sanity (up to 50 m)
    return (int)val;
}

static int median5(int *arr, int n) {
    // simple copy + sort small array
    int tmp[MEDIAN_WINDOW];
    int m = n;
    for (int i=0; i<m; ++i) tmp[i]=arr[i];

    // insertion sort
    for (int i=1; i<m; ++i){
        int key = tmp[i], j=i-1;
        while (j>=0 && tmp[j]>key){ tmp[j+1]=tmp[j]; j--; }
        tmp[j+1]=key;
    }
    return tmp[m/2];
}

//Lap logic
static void maybe_trigger_lap(int distance_mm) {
    int64_t now_us = esp_timer_get_time();

    // Debounce and cooldown
    if (last_trigger_us != 0) {
        int64_t since_ms = (now_us - last_trigger_us)/1000;
        if (since_ms < DEBOUNCE_MS) return; // debounce window
        if (since_ms < COOLDOWN_MS) return; // cooldown window
    }

    if (distance_mm < THRESHOLD_MM) {
        // First trigger primes the start and subsequent triggers end laps
        if (last_lap_start_us == 0) {
            last_lap_start_us = now_us;
            ESP_LOGI(TAG, "Primed first lap start.");
        } else {
            lap_count++;
            double lap_s = (now_us - last_lap_start_us) / 1000000.0;
            last_lap_start_us = now_us;
            last_trigger_us = now_us;
            char payload[64];
            snprintf(payload, sizeof(payload), "%d,%.3f", lap_count, lap_s);
            ESP_LOGI(TAG, "Lap %d: %.3fs → publish %s", lap_count, lap_s, payload);
            if (s_mqtt) {
                esp_mqtt_client_publish(s_mqtt, MQTT_TOPIC_DATA, payload, 0, 0, 0);
            }
        }
        last_trigger_us = now_us;
    }
}

// UART task
static void uart_reader_task(void *pv) {
    uint8_t buf[256];
    char line[128];
    int line_len = 0;

    while (1) {
        int n = uart_read_bytes(UART_PORT, buf, sizeof(buf), pdMS_TO_TICKS(20));
        for (int i=0; i<n; ++i) {
            char c = (char)buf[i];
            if (c == '\n' || c == '\r') {
                if (line_len > 0) {
                    line[line_len] = 0;
                    int mm = parse_distance_line(line);
                    line_len = 0;

                    if (mm >= 0) {
                        // median smoothing
                        distances[d_idx] = mm;
                        if (d_filled < MEDIAN_WINDOW) d_filled++;
                        d_idx = (d_idx + 1) % MEDIAN_WINDOW;

                        int smoothed = (d_filled >= 3) ? median5(distances, d_filled) : mm;
                        maybe_trigger_lap(smoothed);
                    }
                }
            } else {
                if (line_len < (int)sizeof(line)-1) {
                    line[line_len++] = c;
                }
            }
        }
        vTaskDelay(pdMS_TO_TICKS(5));
    }
}


void app_main(void) {
    ESP_ERROR_CHECK(nvs_flash_init());
    wifi_init_sta();
    mqtt_start();
    uart_init();
    xTaskCreate(uart_reader_task, "uart_reader_task", 4096, NULL, 10, NULL);
    ESP_LOGI(TAG, "Setup complete. Waiting for sensor data...");
}
