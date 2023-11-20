Feature: Movie list

  Scenario: Discover
     Given we have a user
      When a user requests discover
      Then a list of movies will be returned

  Scenario: New releases
    Given we have a user
    When a user requests discover
    Then the movies in the releases section are released recently

  Scenario: Popular movies
    Given we have a user
    When a user requests discover
    Then the movies in the popular section are released recently






