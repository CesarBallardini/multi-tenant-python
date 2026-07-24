@bdd
Feature: Best attempt counts in the academic history
  Every attempt is kept, and the best (highest) grade decides pass or fail.

  Scenario: a retake that improves the grade passes the subject
    Given an empty academic history
    When a grade of 4 is recorded for "Maths"
    And a grade of 7 is recorded for "Maths"
    Then the best grade for "Maths" is 7
    And "Maths" is passed

  Scenario: failing every attempt does not pass the subject
    Given an empty academic history
    When a grade of 3 is recorded for "Maths"
    And a grade of 5 is recorded for "Maths"
    Then "Maths" is not passed
