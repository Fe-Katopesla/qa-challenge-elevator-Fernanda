#Solução do desafio técnico QA - IoT Elevador
#Fernanda Lais de Souza Meira

Este projeto contém a automação de testes para o sistema de elevador IoT, utilizando Python, linguagem Gherkin e Behave.

## Cobertura de Testes
1.Movimentação: Validação de todos os andares (1-10) e limites.
2.Segurança: Validação de comandos inválidos e inexistentes.
3.Manutenção: Fluxos de ativação e desativação.
4.Monitoramento: Verificação de payload de dados periódicos.
5.Integração API: Testes negativos enviando payloads incorretos.
6.Resiliência (Bônus): Implementação de Store & Forward. O simulador armazena dados em memória durante falhas de conexão e reenvia automaticamente ao restabelecer a rede.
//

##Diferenciais Implementados
Conforme sugerido na seção de bônus do desafio, implementei as seguintes melhorias:

### 1. Novas funcionalidades no simulador
Desenvolvi uma lógica de Store & Forward no script `mock_elevator_mqtt.py`.
* Comportamento: O elevador agora possui um buffer de memória local.
* Cenário: Em caso de falha de conexão com a API (Cloud), os dados são armazenados localmente. Assim que a conexão é restabelecida, o simulador reenvia automaticamente os dados pendentes, garantindo integridade.

### 2. Ampliação da Cobertura de Testes
Além dos requisitos obrigatórios, adicionei cenários extras em `elevator.feature`:
* Validação de API:Testes negativos enviando payloads incorretos para validar o tratamento de erros (HTTP 400).
* Limites: Validação dos andares limite (1 à 10).
* Schema Check: Validação da presença de todos os campos obrigatórios no payload JSON.

##Estrutura dos Arquivos
* `features/`: Arquivos .feature (Gherkin) e steps definition (Python).
* `mock_elevator_mqtt.py`: Simulador do elevador.
* `mock_api.py`: Simulador da Cloud/API.
* `log_execucao_final.txt`: Evidência de execução com 100% de sucesso (0 falhas).
//

##Como executar:
1. Instale as dependências: `pip install -r requirements.txt`
2. Execute os testes: `python -m behave`