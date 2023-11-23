Feature: Movie details
  Scenario: User requests movie details
   Given we have a user
    When a user requests the movie with id "1234"
    Then movie details will be returned

  Scenario: Reviewing a movie
    Given A movie with id "1234" is reviewed
    When a user requests the movie with id "1234"
    Then the review will be returned