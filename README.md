# Venko Networks - QA Challenge

*Name:* Fernanda Lais de Souza Meira

This project is a complete automated test suite developed in Python using the Behave framework. It simulates an IoT ecosystem (Smart Elevator and Cloud API) to validate functional requirements, edge cases, and system resilience.
-----------------------------

## 1. How to install
The project uses Python and standard libraries managed by pip. To set up the environment, just run this command in the project folder:
```bash
# Install dependencies (Behave, Paho-MQTT, Flask, Requests)
pip install -r requirements.txt
```

## 2. How to run
Since this is an automated test suite, you do not need to manually start the simulators in separate terminals. I implemented hooks in `environment.py` that handle the full lifecycle (setup and teardown) of the simulators automatically.

**Step 1: Execute the Test Suite**
To run all test scenarios (including the bonus resilience tests), simply run:

```bash
python -m behave
```
Step 2: Check the Results The terminal will display the execution steps in real-time.
* [ ]Green: Scenario passed.

* [ ]Red: Scenario failed.

* You can also check the full log file generated after execution: log_execucao_final.txt

## 3. Automation Architecture
For this solution, I chose Python with Behave (BDD). I decided to use this stack because Gherkin syntax allows for clear, human-readable documentation of test cases, while Python provides the robust libraries needed to interact with both MQTT and HTTP interfaces seamlessly.

### Resilience Logic (Store & Forward)

One of the key technical features I implemented is the Store & Forward mechanism in the simulator (mock_elevator_mqtt.py) to handle network instability. Here is exactly how the data flow works during a connection failure:

* First, the Elevator Simulator generates telemetry data (random weight, position, door status).
* It attempts to send this data to the Cloud API via a POST request.
* If the connection fails (simulated by terminating the API process), the simulator catches the ConnectionError exception.
* Instead of discarding the data, it appends the payload to a local internal buffer (Queue).
* In the next cycle, it checks if the connection is restored.
* Once the API is back online, the simulator iterates through the buffer and resends all stored messages before sending new data.
* The Test Suite then validates that the API received the "missing" data, ensuring zero data loss.

A few implementation details:

I used subprocess in the environment.py file to spin up the API and Elevator scripts in the background before tests start.
I also implemented Negative Testing for the API, deliberately sending incomplete JSON payloads to ensure the server responds with HTTP 400.
I included a README.md and detailed logs to make the handover process smoother.

## 4. Project Roadmap

| ID | Task | Status | Type | Level |
|:---|:---|:---:|:---:|:---:|
| **01** | Planning & Scenarios | Done | Planning | Small |
| **02** | Core Automation (BDD) | Done | Backend | Medium |
| **03** | API Integration Tests | Done | Feature | Medium |
| **04** | Store & Forward Logic | Done | Logic | Large |
| **05** | Negative Testing | Done | Quality | Medium |
| **06** | Formatting & Linting | Done | Quality | Small |
| **07** | Documentation | Done | Docs | Small |

## 5. In case of troubleshooting
* [ ] 1. Connection Refused (Errno 111):

This means the MQTT Broker is not running.

Fix: Run 
```bash
sudo service mosquitto start.
```

* [ ] 2. Port 5000 is in use:

This happens if a previous test didn't close the API correctly.

Fix: Run 
```bash
pkill -f mock_api.py to free the port.
```


## 5. Future improvements
If this were to become a continuous integration pipeline, here is what I would improve:

* [ ] Create a Dockerfile to containerize the environment, ensuring the tests run identically on any machine or CI server.

* [ ] Integrate Allure Reports to generate visual, web-based test reports instead of simple text logs.

* [ ] Add a Github Actions workflow to trigger the tests automatically on every push to the main branch.

* [ ] Expand the MQTT coverage to test distinct QoS (Quality of Service) levels, verifying how the broker behaves under stress.

* I also included the execution log to validate the features. You can find it here: log_execucao_final.txt.

Thank you!

