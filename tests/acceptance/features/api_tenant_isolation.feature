@skip @bdd
Feature: Tenant isolation over the API
  Each person is a tenant; no one may read another person's records except through
  an allowed relationship. Needs the API, so it is @skip until that exists.

  Scenario: a user cannot read another user's grades
    Given two unrelated users
    When one requests the other's grades via the API
    Then the request is forbidden

  Scenario: a list endpoint returns only the caller's permitted records
    Given a user whose own grades and other people's grades exist
    When the user lists grades via the API
    Then only their own grades are returned
