@bdd
Feature: Conferring graduation
  A student graduates only after passing every subject in their plan. Graduation
  is a dated, revocable event that issues a credential.

  Background:
    Given a plan with subjects "Maths, Physics"
    And a student

  Scenario: a student who passed every subject can graduate
    Given the student has passed "Maths, Physics"
    When graduation is conferred
    Then the graduation is active
    And it issues the program's credential

  Scenario: a student missing a subject is not eligible
    Given the student has passed "Maths"
    When graduation is conferred
    Then conferral is rejected because the student is not eligible

  Scenario: a conferred graduation can be revoked and reissued
    Given the student has passed "Maths, Physics"
    And graduation has been conferred
    When the graduation is revoked
    Then the graduation is not active
    When the graduation is reissued on "2026-09-01"
    Then the graduation is active
