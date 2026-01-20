Feature: IoT Elevator Complete Test Suite

  Background:
    Given the elevator simulator and API are online

  # REQUIREMENTS 1 and 3: Movement and Boundaries
  Scenario Outline: Move the elevator to valid floors
    When I send the "MOVE" command to floor "<floor>"
    Then the elevator should report it is on floor "<floor>"

    Examples:
      | floor |
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

  Scenario: Attempt to move to an invalid floor
    When I send the "MOVE" command to floor "15"
    Then the system should register an invalid command error

  # REQUIREMENT 2: Maintenance
  Scenario: Activate and Deactivate maintenance mode
    When I send the "MAINTENANCE_ON" command
    Then the elevator should enter maintenance mode
    When I send the "MAINTENANCE_OFF" command
    Then the elevator should exit maintenance mode

  # REQUIREMENT 4: Continuous Monitoring
  Scenario: Verify continuous data reception
    Then the cloud should periodically receive "position", "weight", and "door_status" data

  # REQUIREMENT 5: API Validation (Negative Testing)
  Scenario: Send invalid payload to the API
    When I send a data packet without the "position" field to the API
    Then the API should return a 400 error

  # REQUIREMENT 6: Resilience (Bonus)
  Scenario: Store and Forward (Connection Resilience)
    Given that the API connection is lost
    When the elevator generates data for a few seconds
    And the API connection is restored
    Then the API should have received the stored data
