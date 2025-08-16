#!/usr/bin/env python3
# import json
# import time
# import paho.mqtt.client as mqtt

# BROKER = "localhost"  
# PORT = 1883
# TOPIC = "f1tenth/sensor/distance"

# def on_connect(client, userdata, flags, rc):
#     print("Connected, rc =", rc)
#     client.subscribe(TOPIC)
#     print("Subscribed to", TOPIC)

# def on_message(client, userdata, msg):
#     payload = msg.payload.decode('utf-8', errors='ignore')
#     try:
#         data = json.loads(payload)
#         ts = data.get("ts")
#         sensor = data.get("sensor_id")
#         distance = data.get("distance")
#         print(f"[{ts}] sensor={sensor} distance={distance}")
#     except Exception as e:
#         print("Received raw:", payload, " — parse error:", e)

# client = mqtt.Client()
# client.on_connect = on_connect
# client.on_message = on_message

# client.connect(BROKER, PORT, 60)
# client.loop_forever()

import paho.mqtt.client as mqtt

BROKER = "localhost"
TOPIC = "lap_timer/data"

def on_message(client, userdata, msg):
    data = msg.payload.decode()
    lap_num, lap_time = data.split(",")
    print(f"Lap {lap_num} completed in {lap_time} seconds")

client = mqtt.Client()
client.connect(BROKER, 1883, 60)

client.subscribe(TOPIC)
client.on_message = on_message

print(f"Subscribed to {TOPIC} on {BROKER}")
client.loop_forever()

