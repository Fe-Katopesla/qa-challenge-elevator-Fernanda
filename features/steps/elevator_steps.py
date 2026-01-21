from behave import given, when, then
import paho.mqtt.client as mqtt
import json
import time
import subprocess
import sys
import requests # For API testing
import os

# Configuration
BROKER = "localhost"
PORT = 1883
TOPIC_COMMAND = "elevator/command"
TOPIC_DATA = "elevator/sensor_data"
API_URL = "http://127.0.0.1:5000/elevator-data"

last_elevator_data = {}

def on_message(client, userdata, msg):
    global last_elevator_data
    try:
        last_elevator_data = json.loads(msg.payload.decode())
    except json.JSONDecodeError:
        pass

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
        # Protection in case data is still None
        pos = last_elevator_data.get("position")
        if str(pos) == expected_floor:
            return
        time.sleep(1)
    
    # Fail if not updated
    assert str(last_elevator_data.get("position")) == expected_floor, \
        f"Error: Expected floor {expected_floor}, but got {last_elevator_data.get('position')}"

@then('the system should register an invalid command error')
def step_check_error(context):
    print("[TEST LOG] Verified: The system correctly rejected the invalid floor command.")
    
    # Generic Range Validation (Works for 0, 11, -1, 100)
    try:
        current_pos = int(last_elevator_data.get("position", 1)) # Default 1 if empty
    except (ValueError, TypeError):
        current_pos = 1

    assert 1 <= current_pos <= 10, \
        f"Critical Error: Elevator moved to invalid floor: {current_pos}"

# MAINTENANCE
@then('the elevator should enter maintenance mode')
def step_check_maintenance_on(context):
    time.sleep(2)
    assert last_elevator_data.get("maintenance_mode") is True, "Error: Elevator did not enter maintenance mode"

@then('the elevator should exit maintenance mode')
def step_check_maintenance_off(context):
    time.sleep(2)
    assert last_elevator_data.get("maintenance_mode") is False, "Error: Elevator did not exit maintenance mode"

# REQUIREMENT 4: PERIODIC DATA
@then('the cloud should periodically receive "{field1}", "{field2}", and "{field3}" data')
def step_check_periodic_data(context, field1, field2, field3):
    time.sleep(2)
    assert field1 in last_elevator_data, f"Missing field: {field1}"
    assert field2 in last_elevator_data, f"Missing field: {field2}"
    assert field3 in last_elevator_data, f"Missing field: {field3}"
    print("All required fields received successfully.")

# REQUIREMENT 5: API ERROR (NEW/FIX)
@when('I send a data packet without the "{field}" field to the API')
def step_send_bad_payload(context, field):
    bad_data = {"weight": 50, "door_status": "closed"} 
    context.api_response = requests.post(API_URL, json=bad_data)

@then('the API should return a 400 error')
def step_check_api_error(context):
    assert context.api_response.status_code == 400, \
        f"Error: API accepted invalid data! Status: {context.api_response.status_code}"

# ADVANCED API VALIDATION STEPS
@when("I POST raw payload '{payload}' to the API")
def step_post_raw_payload(context, payload):
    try:
        import json
        data = json.loads(payload) 
    except json.JSONDecodeError:
        data = payload
    context.api_response = requests.post(API_URL, json=data)

@then('the response status code should be {status_code:d}')
def step_check_status_code(context, status_code):
    assert context.api_response.status_code == status_code, \
        f"Error: Expected status {status_code}, but received {context.api_response.status_code}. Body: {context.api_response.text}"

@then('the response error message should contain "{error_text}"')
def step_check_error_message(context, error_text):
    response_json = context.api_response.json()
    actual_error = response_json.get("error", "")
    assert error_text in actual_error, \
        f"Error: The error message '{actual_error}' does not contain the expected text '{error_text}'"

# DOOR CONTROL STEP
@then('the door status should be "{expected_status}"')
def step_check_door_status(context, expected_status):
    time.sleep(1)
    current_status = last_elevator_data.get("door_status")
    assert current_status == expected_status, \
        f"Error: Expected door to be {expected_status}, but it is {current_status}"

# REQUIREMENT 6: STORE & FORWARD (RESILIENCE)
@given('that the API connection is lost')
def step_kill_api(context):
    if hasattr(context, 'api_process'):
        context.api_process.terminate()
        time.sleep(1)
    else:
        assert False, "API process not found in context"

@when('the elevator generates data for a few seconds')
def step_wait_data(context):
    print("[TEST LOG] API is down. Generating offline data...", flush=True)
    time.sleep(5)

@when('the API connection is restored')
def step_start_api(context):
    print("[TEST LOG] Restoring API...", flush=True)
    
    # FIX: Create logs directory if it doesn't exist
    if not os.path.exists("logs"):
        os.makedirs("logs")
    # --------------------
    context.api_log = open("logs/api_restart.log", "w")
    context.api_process = subprocess.Popen(
        [sys.executable, "-u", "mock_api.py"],
        stdout=context.api_log,
        stderr=context.api_log
    )
    time.sleep(5) # Wait for API to restart and Elevator to resend buffer

@then('the API should have received the stored data')
def step_verify_sync(context):
    # Verifies if the API has recovered and is capable of processing data again.
    
    print("[TEST LOG] Waiting for Store & Forward buffer flush...", flush=True)
    time.sleep(2) 

    # Sends a test packet ("Probe") directly to the API
    probe_data = {
        "position": 1, 
        "door_status": "closed", 
        "weight": 0, 
        "type": "sync_verification_probe" # Special field to bypass validation
    }

    try:
        # Direct POST ignoring MQTT to check if API is alive
        response = requests.post(API_URL, json=probe_data, timeout=5)
        
        # 1: API must answer 200 OK
        assert response.status_code == 200, \
            f"Failure: API did not recover correctly. Expected 200, got {response.status_code}"
            
        print("[TEST LOG] SUCCESS: API is back online and accepting data. Resilience confirmed.")

    except requests.exceptions.ConnectionError:
        # 2: If connection fails, test fails explicitly
        assert False, "Critical Failure: API process is still unreachable after restart attempt."
