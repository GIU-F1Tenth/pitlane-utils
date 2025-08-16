#!/usr/bin/env python3
# import json
# import time
# import random
# import paho.mqtt.client as mqtt

# BROKER = "localhost"
# PORT = 1883
# TOPIC = "f1tenth/sensor/distance"
# SENSOR_ID = "tof_sim_01"

# client = mqtt.Client()
# client.connect(BROKER, PORT, 60)

# try:
#     while True:
#         # simulate distance in mm (tweak range as needed)
#         distance = random.uniform(30.0, 1500.0)
#         payload = {"ts": time.time(), "sensor_id": SENSOR_ID, "distance": distance}
#         client.publish(TOPIC, json.dumps(payload))
#         print("Published:", payload)
#         time.sleep(0.05)   # 20 Hz sample rate (adjust as needed)
# except KeyboardInterrupt:
#     client.disconnect()
#     print("Stopped publisher")

import time
import random
import paho.mqtt.client as mqtt

BROKER = "localhost"  
TOPIC = "lap_timer/data"

client = mqtt.Client()
client.connect(BROKER, 1883, 60)

lap_number = 1

while True:
    lap_time = round(random.uniform(10.0, 20.0), 3)  # Fake lap time in seconds
    payload = f"{lap_number},{lap_time}"
    client.publish(TOPIC, payload)
    print(f"Published: Lap {lap_number}, Time: {lap_time} sec")
    lap_number += 1
    time.sleep(5)  # Publish every 5 seconds

