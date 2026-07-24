@skip @bdd
Feature: Role capabilities over the API
  Acceptance criteria for the HTTP API. These need the application and adapter
  layers (use cases, persistence, FastAPI), so they are @skip until those exist.

  Scenario: an administrator manages teachers
    Given an administrator
    When they create a teacher via the API
    Then the teacher exists

  Scenario: a teacher records a grade for their student
    Given a teacher of a section with an enrolled student
    When the teacher records a grade via the API
    Then the grade appears in the student's academic history

  Scenario: a student reads only their own grades
    Given a student with grades
    When the student reads their grades via the API
    Then only their own grades are returned

  Scenario: a guardian reads their minor ward's grades
    Given a guardian of a minor ward with grades
    When the guardian reads the ward's grades via the API
    Then the ward's grades are returned
