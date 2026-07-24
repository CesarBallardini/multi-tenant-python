@bdd
Feature: One active plan per degree program
  A degree program has at most one active plan; activating one deactivates the rest.

  Scenario: activating a plan deactivates the previously active one
    Given a program with plans "A" and "B"
    When plan "A" is activated
    And plan "B" is activated
    Then plan "B" is the active plan
    And plan "A" is not active

  Scenario: adding an already-active plan deactivates the others
    Given a program with an active plan "A"
    When an active plan "B" is added
    Then plan "B" is the active plan
    And plan "A" is not active
