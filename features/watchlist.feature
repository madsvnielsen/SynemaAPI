Feature: Watchlist
  Scenario: Adding and viewing watchlist
    Given A movie "507043" is added to the watchlist "53288ff9-b4cc-46ac-af6e-e8e80eb514b0"
    When a user requests the watchlist "53288ff9-b4cc-46ac-af6e-e8e80eb514b0"
    Then the added movie is on the watchlist
