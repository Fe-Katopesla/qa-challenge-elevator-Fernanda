import subprocess
import time
import sys

#liga os simuladores antes do teste e desliga depois

def before_all(context):
    print("Iniciando Simuladores (API e Elevador)")
    #inicia a API (mock_api.py) em segundo plano
    context.api_process = subprocess.Popen([sys.executable, "mock_api.py"])
    
    #inicia o Elevador (mock_elevator_mqtt.py) em segundo plano
    context.elevator_process = subprocess.Popen([sys.executable, "mock_elevator_mqtt.py"])
    
    #espera 3 segundos para garantir que tudo ligou
    time.sleep(3)

def after_all(context):
    print("Desligando Simuladores")
    context.api_process.terminate()
    context.elevator_process.terminate()