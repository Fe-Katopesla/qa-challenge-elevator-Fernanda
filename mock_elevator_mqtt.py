import time
import json
import paho.mqtt.client as mqtt
import random

# MQTT Broker Configuration
BROKER = "localhost"
PORT = 1883
TOPIC_DATA = "elevator/sensor_data"
TOPIC_COMMAND = "elevator/command"

# Initial state
elevator_state = {
    "position": 1,
    "door_status": "closed",
    "weight": 0,
    "maintenance_mode": False
}

def on_message(client, userdata, message):
    command = message.payload.decode()
    
    # Check for maintenance commands
    if command == "MAINTENANCE_ON":
        elevator_state["maintenance_mode"] = True
        print("[ELEVATOR] Maintenance Mode ACTIVATED", flush=True)
    elif command == "MAINTENANCE_OFF":
        elevator_state["maintenance_mode"] = False
        print("[ELEVATOR] Maintenance Mode DEACTIVATED", flush=True)
        
    # Check for movement commands
    elif command.startswith("MOVE_TO_"):
        try:
            floor = int(command.split("_")[-1])
            
            # Validation: Only allow floors 1 to 10
            if 1 <= floor <= 10:
                elevator_state["position"] = floor
                print(f"[ELEVATOR] Moving to floor {floor}", flush=True)
            else:
                # NEW: Error message
                print(f"[ELEVATOR ERROR] Invalid command received: Floor {floor} is out of range (1-10)", flush=True)
                
        except ValueError:
            print(f"[ELEVATOR ERROR] Malformed command received: {command}", flush=True)

client = mqtt.Client()
client.on_message = on_message
client.connect(BROKER, PORT)
client.subscribe(TOPIC_COMMAND)
client.loop_start()

while True:
    client.publish(TOPIC_DATA, json.dumps(elevator_state))
    time.sleep(5)
