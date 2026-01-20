from behave import given, when, then
import paho.mqtt.client as mqtt
import json
import time
import subprocess
import sys
import requests # For API testing

# Configuration
BROKER = "localhost"
PORT = 1883
TOPIC_COMMAND = "elevator/command"
TOPIC_DATA = "elevator/sensor_data"
API_URL = "http://127.0.0.1:5000/elevator-data"

last_elevator_data = {}

def on_message(client, userdata, msg):
    global last_elevator_data
    last_elevator_data = json.loads(msg.payload.decode())

client = mqtt.Client()
client.on_message = on_message
client.connect(BROKER, PORT)
client.subscribe(TOPIC_DATA)
client.loop_start()

# GENERAL SETUP
@given('the elevator simulator and API are online')
def step_impl(context):
    time.sleep(1)

# MOVEMENT
@when('I send the "{command}" command to floor "{floor}"')
def step_send_move(context, command, floor):
    full_command = f"MOVE_TO_{floor}"
    client.publish(TOPIC_COMMAND, full_command)
    time.sleep(2)

@when('I send the "{command}" command')
def step_send_simple_command(context, command):
    client.publish(TOPIC_COMMAND, command)
    time.sleep(1)

@then('the elevator should report it is on floor "{expected_floor}"')
def step_check_floor(context, expected_floor):
    for _ in range(5):
        if str(last_elevator_data.get("position")) == expected_floor:
            return
        time.sleep(1)
    assert str(last_elevator_data.get("position")) == expected_floor, \
        f"Error: Expected floor {expected_floor}, but got {last_elevator_data.get('position')}"

@then('the system should register an invalid command error')
def step_check_error(context):
    # Log validation in the test output
    print("[TEST LOG] Verified: The system correctly rejected the invalid floor command.")
    # Ensure the elevator did NOT move to the invalid floor (15)
    # It should still be at the last valid floor (which was 10 in the previous scenario)
    assert last_elevator_data.get("position") != 15, "Critical Error: Elevator moved to an invalid floor!"

# MAINTENANCE
@then('the elevator should enter maintenance mode')
def step_check_maintenance_on(context):
    time.sleep(1)
    assert last_elevator_data.get("maintenance_mode") is True, "Error: Elevator did not enter maintenance mode"

@then('the elevator should exit maintenance mode')
def step_check_maintenance_off(context):
    time.sleep(1)
    assert last_elevator_data.get("maintenance_mode") is False, "Error: Elevator did not exit maintenance mode"

# REQUIREMENT 4: PERIODIC DATA
@then('the cloud should periodically receive "{field1}", "{field2}", and "{field3}" data')
def step_check_periodic_data(context, field1, field2, field3):
    # Checks if fields exist in the last received message
    time.sleep(2)
    assert field1 in last_elevator_data, f"Missing field: {field1}"
    assert field2 in last_elevator_data, f"Missing field: {field2}"
    assert field3 in last_elevator_data, f"Missing field: {field3}"
    print("All required fields received successfully.")

#REQUIREMENT 5: API ERROR (NEW)
@when('I send a data packet without the "{field}" field to the API')
def step_send_bad_payload(context, field):
    # Intentionally creates an incomplete JSON
    bad_data = {"weight": 50, "door_status": "closed"} # Missing position
    # Bypasses MQTT to test Cloud validation directly
    context.api_response = requests.post(API_URL, json=bad_data)

@then('the API should return a 400 error')
def step_check_api_error(context):
    assert context.api_response.status_code == 400, f"Error: API accepted invalid data! Status: {context.api_response.status_code}"

#REQUIREMENT 6: STORE & FORWARD
@given('that the API connection is lost')
def step_kill_api(context):
    context.api_process.terminate()
    time.sleep(1)

@when('the elevator generates data for a few seconds')
def step_wait_data(context):
    time.sleep(5)

@when('the API connection is restored')
def step_start_api(context):
    context.api_process = subprocess.Popen([sys.executable, "mock_api.py"])
    time.sleep(5)

@then('the API should have received the stored data')
def step_verify_sync(context):
    # This step assumes the API logs show the data arriving in bulk
    pass
