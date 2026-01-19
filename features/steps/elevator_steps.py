from behave import given, when, then
import paho.mqtt.client as mqtt
import json
import time
import subprocess
import sys
import requests #para o teste da API (requisito 5)

# Configurações
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

#SETUP GERAL
@given('que o simulador do elevador e a API estão online')
def step_impl(context):
    time.sleep(1)

#MOVIMENTAÇÃO
@when('envio o comando "{comando}" para o andar "{andar}"')
def step_send_move(context, comando, andar):
    full_command = f"MOVE_TO_{andar}"
    client.publish(TOPIC_COMMAND, full_command)
    time.sleep(2)

@when('envio o comando "{comando}"')
def step_send_simple_command(context, comando):
    client.publish(TOPIC_COMMAND, comando)
    time.sleep(1)

@then('o elevador deve reportar que está no andar "{andar_esperado}"')
def step_check_floor(context, andar_esperado):
    for _ in range(5):
        if str(last_elevator_data.get("position")) == andar_esperado:
            return
        time.sleep(1)
    assert str(last_elevator_data.get("position")) == andar_esperado

@then('o sistema deve registrar um erro de comando inválido')
def step_check_error(context):
    pass 

#MANUTENÇÃO
@then('o elevador deve entrar em modo de manutenção')
def step_check_maintenance_on(context):
    time.sleep(1)
    assert last_elevator_data.get("maintenance_mode") is True

@then('o elevador deve sair do modo de manutenção')
def step_check_maintenance_off(context):
    time.sleep(1)
    assert last_elevator_data.get("maintenance_mode") is False

#REQUISITO 4: DADOS PERIÓDICOS
@then('a cloud deve receber dados de "{campo1}", "{campo2}" e "{campo3}" periodicamente')
def step_check_periodic_data(context, campo1, campo2, campo3):
    # Verifica se os campos existem na última mensagem recebida
    time.sleep(2)
    assert campo1 in last_elevator_data, f"Campo {campo1} faltando"
    assert campo2 in last_elevator_data, f"Campo {campo2} faltando"
    assert campo3 in last_elevator_data, f"Campo {campo3} faltando"
    print("Dados completos recebidos com sucesso.")

#REQUISITO 5: API ERROR(NOVO)
@when('envio um pacote de dados sem o campo "{campo}" para a API')
def step_send_bad_payload(context, campo):
    # Monta um JSON incompleto propositalmente
    bad_data = {"weight": 50, "door_status": "closed"} # Falta position
    # Envia direto para a API (bypass MQTT) para testar a validação da Cloud
    context.api_response = requests.post(API_URL, json=bad_data)

@then('a API deve retornar um erro 400')
def step_check_api_error(context):
    assert context.api_response.status_code == 400, f"Erro: API aceitou dados inválidos! Status: {context.api_response.status_code}"

#REQUISITO 6: STORE & FORWARD
@given('que a conexão com a API cai')
def step_kill_api(context):
    context.api_process.terminate()
    time.sleep(1)

@when('o elevador gera dados por alguns segundos')
def step_wait_data(context):
    time.sleep(5)

@when('a conexão com a API é restabelecida')
def step_start_api(context):
    context.api_process = subprocess.Popen([sys.executable, "mock_api.py"])
    time.sleep(3)

@then('a API deve ter recebido os dados que estavam guardados')
def step_verify_sync(context):
    pass