@bdd
Feature: Teacher qualification for a course section
  A teacher may only be assigned to a section for a subject they are credentialed
  to teach. Qualification is hard-enforced when the section is created.

  Scenario: a credentialed teacher is assigned
    Given a teacher credentialed to teach "Maths"
    When a "Maths" section is created for the teacher
    Then the section is created

  Scenario: a teacher not credentialed for the subject is rejected
    Given a teacher credentialed to teach "History"
    When a "Maths" section is created for the teacher
    Then the assignment is rejected because the teacher is not qualified

  Scenario: a person without the teacher role is rejected
    Given a person who is not a teacher
    When a "Maths" section is created for that person
    Then the assignment is rejected because they are not a teacher
