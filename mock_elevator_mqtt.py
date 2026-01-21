import time
import json
import paho.mqtt.client as mqtt
import random
import requests

# Configurações
BROKER = "localhost"
PORT = 1883
TOPIC_DATA = "elevator/sensor_data"
TOPIC_COMMAND = "elevator/command"
TOPIC_EVENTS = "elevator/events"
API_URL = "http://127.0.0.1:5000/elevator-data"

# Estado Inicial
elevator_state = {
    "position": 1,
    "door_status": "closed",
    "weight": 0,
    "maintenance_mode": False
}

def publish_state(client):
    """Função auxiliar para publicar o estado imediatamente"""
    # Garante peso atualizado
    if elevator_state["weight"] == 0:
        elevator_state["weight"] = random.randint(0, 999)
        
    payload = json.dumps(elevator_state)
    client.publish(TOPIC_DATA, payload)
    return payload

def publish_error(client, command, error_message):
    payload = json.dumps({
        "type": "error",
        "error": error_message,
        "command": command,
        "ts": time.time()
    })
    client.publish(TOPIC_EVENTS, payload)
    print(f"[ELEVATOR ERROR] {error_message}", flush=True)

def on_message(client, userdata, message):
    command = message.payload.decode()
    state_changed = False # Flag para saber se precisamos publicar agora

    # MANUTENÇÃO
    if command == "MAINTENANCE_ON":
        elevator_state["maintenance_mode"] = True
        print("[ELEVATOR] Maintenance Mode ACTIVATED", flush=True)
        state_changed = True
    elif command == "MAINTENANCE_OFF":
        elevator_state["maintenance_mode"] = False
        print("[ELEVATOR] Maintenance Mode DEACTIVATED", flush=True)
        state_changed = True
        
    # PORTAS
    elif command == "OPEN_DOOR":
        elevator_state["door_status"] = "open"
        print("[ELEVATOR] Door OPENING...", flush=True)
        state_changed = True
    elif command == "CLOSE_DOOR":
        elevator_state["door_status"] = "closed"
        print("[ELEVATOR] Door CLOSING...", flush=True)
        state_changed = True
        
    # MOVIMENTO
    elif command.startswith("MOVE_TO_"):
        if elevator_state.get("maintenance_mode"):
            err = "Elevator is in maintenance mode; MOVE_TO commands are not allowed."
            publish_error(client, command, err)
            return

        try:
            floor = int(command.split("_")[-1])
            if floor < 1 or floor > 10:
                err = f"Floor {floor} is out of range (1-10)."
                publish_error(client, command, err)
            else:
                print(f"[ELEVATOR] Moving to floor {floor}", flush=True)
                elevator_state["position"] = floor
                state_changed = True
        except ValueError:
            err = "Invalid floor value in command."
            publish_error(client, command, err)
    
    else:
        err = f"Unknown command received: {command}"
        publish_error(client, command, err)

    # SE O ESTADO MUDOU, PUBLICA IMEDIATAMENTE (Não espera o loop de 5s)
    if state_changed:
        publish_state(client)

client = mqtt.Client()
client.on_message = on_message
client.connect(BROKER, PORT)
client.subscribe(TOPIC_COMMAND)
client.loop_start()

# --- LOOP PRINCIPAL ---
offline_buffer = []
print("[ELEVATOR] Simulator Started (Reactive Mode).", flush=True)

while True:
    # 1. Gera peso aleatório
    elevator_state["weight"] = random.randint(0, 999)
    
    # 2. Publica e pega o payload
    payload_str = publish_state(client)
    current_data = json.loads(payload_str)

    # 3. Store & Forward
    try:
        response = requests.post(API_URL, json=current_data, timeout=2)
        if response.status_code == 200 and offline_buffer:
            print(f"[RECOVERY] Reenviando {len(offline_buffer)} itens do buffer...", flush=True)
            for old_data in offline_buffer:
                requests.post(API_URL, json=old_data)
            offline_buffer = []
            print("[RECOVERY] Buffer esvaziado!", flush=True)

    except requests.exceptions.ConnectionError:
        offline_buffer.append(current_data)

    time.sleep(5)
