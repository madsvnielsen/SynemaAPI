Feature: Watchlist
  Scenario: Adding and viewing watchlist
    Given A movie is added to the watchlist "id"
    When a user requests the watchlist "id"
    Then the added movie can is on the watchlist
