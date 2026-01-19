import time
import json
import paho.mqtt.client as mqtt
import random

BROKER = "localhost"
PORT = 1883
TOPIC_DATA = "elevator/sensor_data"
TOPIC_COMMAND = "elevator/command"

elevator_state = {"position": 1, "door_status": "closed", "weight": 0, "maintenance_mode": False}

def on_message(client, userdata, message):
    command = message.payload.decode()
    if command == "MAINTENANCE_ON":
        elevator_state["maintenance_mode"] = True
    elif command == "MAINTENANCE_OFF":
        elevator_state["maintenance_mode"] = False
    elif command.startswith("MOVE_TO_"):
        try:
            floor = int(command.split("_")[-1])
            if 1 <= floor <= 10:
                elevator_state["position"] = floor
        except ValueError:
            pass

client = mqtt.Client()
client.on_message = on_message
client.connect(BROKER, PORT)
client.subscribe(TOPIC_COMMAND)
client.loop_start()

while True:
    client.publish(TOPIC_DATA, json.dumps(elevator_state))
    time.sleep(1) # Intervalo mais curto para o teste rodar rápido