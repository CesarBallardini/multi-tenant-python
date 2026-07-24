@bdd
Feature: Guardianship applies only to minors
  Guardianship is stored but applies only while the ward is a minor; it is computed
  on read against the global age of majority.

  Background:
    Given the age of majority is 18
    And today is "2026-01-01"

  Scenario: guardianship applies to a minor ward
    Given a ward born on "2010-01-01"
    Then the guardianship applies

  Scenario: guardianship does not apply to an adult ward
    Given a ward born on "2000-01-01"
    Then the guardianship does not apply

  Scenario: a person cannot be their own guardian
    When a guardianship links a person to themselves
    Then it is rejected as self-guardianship
