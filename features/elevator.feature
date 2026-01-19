Feature: Suite Completa de Testes do Elevador IoT

  Background:
    Given que o simulador do elevador e a API estão online

  #REQUISITOS 1 e 3: Movimentação e Limites
  Scenario Outline: Mover o elevador para andares válidos
    When envio o comando "MOVE" para o andar "<andar>"
    Then o elevador deve reportar que está no andar "<andar>"

    Examples:
      | andar |
      | 1     |
      | 2     |
      | 3     |
      | 4     |
      | 5     |
      | 6     |
      | 7     |
      | 8     |
      | 9     |
      | 10    |

  Scenario: Tentar mover para um andar inválido
    When envio o comando "MOVE" para o andar "15"
    Then o sistema deve registrar um erro de comando inválido

  #REQUISITO 2: manutenção
  Scenario: Ativar e desativar modo de manutenção
    When envio o comando "MAINTENANCE_ON"
    Then o elevador deve entrar em modo de manutenção
    When envio o comando "MAINTENANCE_OFF"
    Then o elevador deve sair do modo de manutenção

  #REQUISITO 4: monitoramento continuo
  Scenario: Verificar recebimento contínuo de dados
    Then a cloud deve receber dados de "position", "weight" e "door_status" periodicamente

  #REQUISITO 5: validação da API (Dados incorretos)
  Scenario: Enviar payload inválido para a API
    When envio um pacote de dados sem o campo "position" para a API
    Then a API deve retornar um erro 400

  #REQUISITO 6: Resiliência
  Scenario: Store and Forward (Resiliência de conexão)
    Given que a conexão com a API cai
    When o elevador gera dados por alguns segundos
    And a conexão com a API é restabelecida
    Then a API deve ter recebido os dados que estavam guardados