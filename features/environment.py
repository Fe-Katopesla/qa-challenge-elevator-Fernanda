import subprocess
import time
import sys

# Hooks to manage the test lifecycle (Start/Stop simulators)

def before_all(context):
    print("Starting Simulators (API and Elevator)...")
    # Starts API (mock_api.py) in the background
    context.api_process = subprocess.Popen([sys.executable, "mock_api.py"])
    
    # Starts Elevator (mock_elevator_mqtt.py) in the background
    context.elevator_process = subprocess.Popen([sys.executable, "mock_elevator_mqtt.py"])
    
    # Waits 3 seconds to ensure services are fully up
    time.sleep(3)

def after_all(context):
    print("Stopping Simulators...")
    context.api_process.terminate()
    context.elevator_process.terminate()
