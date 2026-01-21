# Step-by-Step Instructions

For the terminal:

```bash
wsl
pkill -f mock_api.py
pkill -f mock_elevator_mqtt.py
sudo fuser -k 5000/tcp
sudo fuser -k 1883/tcp
cd ~
mkdir teste_final
cd teste_final
git clone [https://github.com/Fe-Katopesla/qa-challenge-elevator-Fernanda.git](https://github.com/Fe-Katopesla/qa-challenge-elevator-Fernanda.git)
cd qa-challenge-elevator-Fernanda
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
sudo service mosquitto start
python -m behave
```

# 1. PREPARATION AND CLEANUP
```bash
wsl
```
Enters the Linux system

```bash
pkill -f mock_api.py
```
Terminates the API simulator if it is stuck at any point.

```bash
pkill -f mock_elevator_mqtt.py
```
Terminates the elevator simulator to avoid conflicts with the new one.

```bash
sudo fuser -k 5000/tcp
```
Brute force: opens port 5000 (API port) if pkill fails.

```bash
sudo fuser -k 1883/tcp
```
Brute force: opens port 1883 (MQTT port) to ensure a clean connection.

# 2. SIMULATING A NEW TEST
```bash
cd ~
```
Returns to the user's root folder to avoid clutter.

```bash
mkdir final_test
```
Creates a new folder to download the project from scratch.

```bash
cd final_test
```
Enters this new folder.

# 3. DOWNLOADING THE CODE
```bash
git clone https://github.com/Fe-Katopesla/qa-challenge-elevator-Fernanda.git
```
Downloads the code from GitHub

```bash
cd qa-challenge-elevator-Fernanda
```
Enters the downloaded project folder

# 4. SETTING UP THE ENVIRONMENT
```bash
python3 -m venv venv
```
Creates a virtual environment (a bubble) to install the components without overloading the PC.

```bash
source venv/bin/activate
```
Activates this bubble (the command venv should appear in the terminal).

```bash
pip install -r requirements.txt
```
Installs the necessary tools (Behave, Flask, Paho-MQTT, etc.).

# 5. EXECUTION
```bash
sudo service mosquitto start
```
Ensures the message broker (MQTT broker) is connected.

```bash
python -m behavior
```
Runs the complete set of tests to see everything working correctly on the screen! If you want to ensure an MQTT test, open a listener in the terminal:

```bash
sudo apt-get install mosquitto-clients
mosquitto_sub -h localhost -t "elevator/sensor_data"
```
