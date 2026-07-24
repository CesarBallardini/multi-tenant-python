@bdd
Feature: Permissions on academic history
  A student's academic history (the full transcript) may be read by the student
  themselves, their guardian, and administrators. Teachers are scoped to the
  sections they teach and cannot read the whole history, and no relationship
  grants write access through the access policy.

  Scenario Outline: the relationship decides access to academic history
    Given an actor related to the record owner as "<relation>"
    When the actor requests to "<action>" the academic history
    Then access is "<outcome>"

    Examples:
      | relation           | action | outcome |
      | self               | read   | allowed |
      | self               | write  | denied  |
      | teacher_of_section | read   | denied  |
      | teacher_of_section | write  | denied  |
      | guardian_of        | read   | allowed |
      | guardian_of        | write  | denied  |
      | administrator      | read   | allowed |
      | administrator      | write  | denied  |

  Scenario: an unrelated actor cannot read academic history
    Given an actor with no relationship to the record owner
    When the actor requests to "read" the academic history
    Then access is "denied"
