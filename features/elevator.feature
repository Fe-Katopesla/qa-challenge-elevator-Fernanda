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

  # NEW: Safety Lock (Verifies if elevator blocks movement during maintenance)
  Scenario: Safety Lock - Attempt to move during maintenance
    When I send the "MOVE" command to floor "1"
    Then the elevator should report it is on floor "1"
    # ----------
    When I send the "MAINTENANCE_ON" command
    Then the elevator should enter maintenance mode
    # Attempt to move, but it should stay in place
    When I send the "MOVE" command to floor "5"
    Then the elevator should report it is on floor "1"
    # Clean up state for next tests
    When I send the "MAINTENANCE_OFF" command

  # NEW: Door Status (Validates door actuator logic)
  Scenario: Open and close the door
    When I send the "OPEN_DOOR" command
    Then the door status should be "open"
    When I send the "CLOSE_DOOR" command
    Then the door status should be "closed"

  # REQUIREMENT 4: Continuous Monitoring
  Scenario: Verify continuous data reception
    Then the cloud should periodically receive "position", "weight", and "door_status" data

  # REQUIREMENT 5: API Validation (Advanced Negative Testing)
  Scenario Outline: API - Validate missing required fields
    When I POST raw payload '<payload>' to the API
    Then the response status code should be 400
    And the response error message should contain "Missing fields"

    Examples:
      | payload                                 |
      | {"door_status":"closed","weight":0}     |
      | {"position":1,"weight":0}               |
      | {"position":1,"door_status":"closed"}   |
      | {}                                      |

  Scenario Outline: API - Validate invalid position boundaries
    When I POST raw payload '<payload>' to the API
    Then the response status code should be 400
    And the response error message should contain "Invalid position"

    Examples:
      | payload                                                  |
      | {"position": 0, "door_status": "closed", "weight": 10}   |
      | {"position": 11, "door_status": "closed", "weight": 10}  |

  Scenario: API - Validate invalid door status enum
    When I POST raw payload '{"position": 1, "door_status": "broken", "weight": 10}' to the API
    Then the response status code should be 400
    And the response error message should contain "Invalid door_status"

  Scenario Outline: API - Validate weight limits
    When I POST raw payload '<payload>' to the API
    Then the response status code should be 400
    And the response error message should contain "Invalid weight"

    Examples:
      | payload                                                  |
      | {"position": 1, "door_status": "closed", "weight": -1}   |
      | {"position": 1, "door_status": "closed", "weight": 2001} |

  # REQUIREMENT 6: Resilience (Bonus)
  Scenario: Store and Forward (Connection Resilience)
    Given that the API connection is lost
    When the elevator generates data for a few seconds
    And the API connection is restored
    Then the API should have received the stored data
