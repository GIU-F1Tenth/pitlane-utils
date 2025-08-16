#include <stdio.h>
#include "freertos/FreeRTOS.h"  
#include "freertos/task.h"  
#include "driver/gpio.h"       // ← ADD THIS LINE (critical for GPIO functions)
#define LED_PIN 2  // ESP32 built-in LED (GPIO2)

void app_main() {
gpio_reset_pin(LED_PIN);
gpio_set_direction(LED_PIN, GPIO_MODE_OUTPUT);

    while (1) {
        gpio_set_level(LED_PIN, 1);  // LED ON
        vTaskDelay(1000 / portTICK_PERIOD_MS);
        gpio_set_level(LED_PIN, 0);  // LED OFF
        vTaskDelay(1000 / portTICK_PERIOD_MS);
    }
}