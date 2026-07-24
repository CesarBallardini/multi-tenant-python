@bdd
Feature: Permissions on grades
  Access to a student's grades is decided by the relationship between the actor
  and the student who owns the records. Grades may be read by the student
  themselves, a teacher of a section they are in, their guardian, and
  administrators; only a teacher may write a grade.

  Scenario Outline: the relationship decides access to grades
    Given an actor related to the record owner as "<relation>"
    When the actor requests to "<action>" the grades
    Then access is "<outcome>"

    Examples:
      | relation           | action | outcome |
      | self               | read   | allowed |
      | self               | write  | denied  |
      | teacher_of_section | read   | allowed |
      | teacher_of_section | write  | allowed |
      | guardian_of        | read   | allowed |
      | guardian_of        | write  | denied  |
      | administrator      | read   | allowed |
      | administrator      | write  | denied  |

  Scenario: an unrelated actor cannot read grades
    Given an actor with no relationship to the record owner
    When the actor requests to "read" the grades
    Then access is "denied"

  Scenario: any single granting relationship is enough
    Given an actor related to the record owner as "self, teacher_of_section"
    When the actor requests to "write" the grades
    Then access is "allowed"
