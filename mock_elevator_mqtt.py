import time
import json
import paho.mqtt.client as mqtt
import random

# MQTT Broker Configuration
BROKER = "localhost"
PORT = 1883
TOPIC_DATA = "elevator/sensor_data"
TOPIC_COMMAND = "elevator/command"

# Initial state of the elevator simulation
elevator_state = {
    "position": 1,
    "door_status": "closed",
    "weight": 0,
    "maintenance_mode": False
}

# Callback function to handle incoming messages from the broker
def on_message(client, userdata, message):
    # Decode the message payload from bytes to string
    command = message.payload.decode()
    
    # Check for maintenance commands
    if command == "MAINTENANCE_ON":
        elevator_state["maintenance_mode"] = True
    elif command == "MAINTENANCE_OFF":
        elevator_state["maintenance_mode"] = False
        
    # Check for movement commands (Format: MOVE_TO_X)
    elif command.startswith("MOVE_TO_"):
        try:
            # Extract the floor number from the string
            floor = int(command.split("_")[-1])
            
            # Validation: The elevator only exists between floors 1 and 10
            if 1 <= floor <= 10:
                elevator_state["position"] = floor
        except ValueError:
            # Ignore invalid commands to prevent the simulator from crashing
            pass

# Initialize the MQTT Client
client = mqtt.Client()
client.on_message = on_message

# Connect to the local broker
client.connect(BROKER, PORT)

# Subscribe to the command topic to receive instructions
client.subscribe(TOPIC_COMMAND)

# Start the network loop in a background thread
client.loop_start()

# Main loop to publish telemetry data continuously
while True:
    # Convert the dictionary to a JSON string and publish
    client.publish(TOPIC_DATA, json.dumps(elevator_state))
    
    # Short interval to ensure automated tests run quickly
    time.sleep(1)
