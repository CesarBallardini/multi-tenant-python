@skip @bdd
Feature: Plan grandfathering over the API
  Needs the API, so it is @skip until that exists.

  Scenario: an existing cohort keeps its plan when a new plan is activated
    Given a student enrolled under plan "A"
    When an administrator activates a new plan "B" via the API
    Then the student still completes plan "A"
    And new students enroll under plan "B"
