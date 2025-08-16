import tkinter as tk
import csv
import paho.mqtt.client as mqtt

# BROKER = "localhost"
# TOPIC = "lap_timer/data"
BROKER = "192.168.1.8"  # same as BROKER_URI in ESP32 code (hostname -I)
TOPIC = "lap_timer/data" # must match exactly
CONTROL_TOPIC = "lap_timer/control"

lap_times = []  # stores lap times as floats
running = False

def on_message(client, userdata, msg):
    global lap_times
    try:
        data = msg.payload.decode()
        lap_num, lap_time = data.split(",")
        lap_time = float(lap_time)
        lap_times.append(lap_time)
        update_display()
    except Exception as e:
        print(f"Error processing message: {e}")

client = mqtt.Client()
client.on_message = on_message
client.connect(BROKER, 1883, 60)
client.subscribe(TOPIC)
client.loop_start()

def start_lap():
    global running
    running = True
    status_label.config(text="Status: Running")
    client.publish(CONTROL_TOPIC, "start")

def reset_laps():
    global lap_times, running
    lap_times = []
    running = False
    update_display()
    status_label.config(text="Status: Reset")
    client.publish(CONTROL_TOPIC, "reset")

def restart_lap():
    status_label.config(text="Status: Lap Restarted")
    client.publish(CONTROL_TOPIC, "restart")

def save_data():
    with open("lap_times.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Lap Number", "Lap Time (s)"])
        for i, t in enumerate(lap_times, 1):
            writer.writerow([i, t])
    status_label.config(text="Status: Data Saved")

def update_display():
    num_laps = len(lap_times)
    avg_time = sum(lap_times) / num_laps if num_laps > 0 else 0
    current_lap_label.config(text=f"Current Lap: {lap_times[-1] if lap_times else 0:.3f}s")
    avg_lap_label.config(text=f"Average Lap: {avg_time:.3f}s")
    laps_count_label.config(text=f"Laps: {num_laps}")

root = tk.Tk()
root.title("Lap Timer GUI")

current_lap_label = tk.Label(root, text="Current Lap: 0.000s", font=("Arial", 16))
current_lap_label.pack()

avg_lap_label = tk.Label(root, text="Average Lap: 0.000s", font=("Arial", 16))
avg_lap_label.pack()

laps_count_label = tk.Label(root, text="Laps: 0", font=("Arial", 16))
laps_count_label.pack()

status_label = tk.Label(root, text="Status: Idle", font=("Arial", 12))
status_label.pack(pady=5)

btn_frame = tk.Frame(root)
btn_frame.pack()

tk.Button(btn_frame, text="Start", command=start_lap).grid(row=0, column=0, padx=5, pady=5)
tk.Button(btn_frame, text="Reset", command=reset_laps).grid(row=0, column=1, padx=5, pady=5)
tk.Button(btn_frame, text="Restart Lap", command=restart_lap).grid(row=0, column=2, padx=5, pady=5)
tk.Button(btn_frame, text="Save Data", command=save_data).grid(row=0, column=3, padx=5, pady=5)

root.mainloop()
