Feature: Watchlist
  Scenario: Adding and viewing watchlist
    Given A movie "1234" is added to the watchlist "1234"
    When a user requests the watchlist "1234"
    Then the added movie is on the watchlist
