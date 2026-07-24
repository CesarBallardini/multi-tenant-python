@bdd
Feature: Enrolling a student in a course section
  A student may enroll in a section only when the subject is in their plan, the
  section runs in the current term, and they are not already enrolled in a
  section of that subject.

  Background:
    Given the current term is "2026-T1"
    And a plan that contains "Maths"

  Scenario: a valid enrollment succeeds
    Given a student
    And a "Maths" section in "2026-T1"
    When the student enrolls
    Then the student is enrolled

  Scenario: the subject is not in the student's plan
    Given a student
    And a "Physics" section in "2026-T1"
    When the student enrolls
    Then enrollment is rejected because the subject is not in the plan

  Scenario: the section runs in a different term
    Given a student
    And a "Maths" section in "2026-T2"
    When the student enrolls
    Then enrollment is rejected because the term is wrong

  Scenario: the student already has a section for that subject
    Given a student already enrolled in "Maths"
    And a "Maths" section in "2026-T1"
    When the student enrolls
    Then enrollment is rejected because they already have that subject

  Scenario: a non-student cannot enroll
    Given a person who is not a student
    And a "Maths" section in "2026-T1"
    When the student enrolls
    Then enrollment is rejected because they are not a student
