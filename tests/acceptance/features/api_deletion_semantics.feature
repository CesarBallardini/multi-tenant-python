@skip @bdd
Feature: Deletion semantics over the API
  Needs the API, so it is @skip until that exists.

  Scenario: deleting a course section moves its grades to academic history
    Given a section with recorded grades
    When an administrator deletes the section via the API
    Then the grades remain in each student's academic history

  Scenario: deleting an entity with dependents is blocked
    Given a teacher who has recorded grades
    When an administrator deletes the teacher via the API
    Then the deletion is rejected because dependents exist
