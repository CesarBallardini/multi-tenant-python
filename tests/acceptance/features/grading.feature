@bdd
Feature: Recording a grade
  A teacher records a grade only for a student enrolled in a section the teacher
  teaches; the grade lands in that student's academic history.

  Background:
    Given a "Maths" section taught by teacher "T" in "2026-T1"
    And a student enrolled in the section

  Scenario: the teacher grades an enrolled student
    When teacher "T" records a grade of 8 for the student
    Then the grade is recorded in the student's history
    And the best grade for "Maths" is 8

  Scenario: a teacher who does not teach the section is rejected
    When teacher "OTHER" records a grade of 8 for the student
    Then grading is rejected because they do not teach the section

  Scenario: grading a student who is not enrolled is rejected
    Given another student who is not enrolled
    When teacher "T" records a grade of 8 for the other student
    Then grading is rejected because the student is not enrolled
