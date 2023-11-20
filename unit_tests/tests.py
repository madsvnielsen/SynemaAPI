import unittest
import subprocess
import os
import time
import signal
from testAPI import API


class TestMovieMethods(unittest.TestCase):

    DEBUG_HEADERS = {
        "accept": "application/json"
    }
    movie_expected_keys = {"id", "poster_url", "backdrop_url", "title", "description", "rating", "release_date"}

    def setUp(self):
        self.api = API(self.DEBUG_HEADERS)

    def test_discover_movies(self):
        response = self.api.discover_movies()
        self.assertGreater(len(response), 0, "Discover movies response empty!")
        map(lambda i: self.assertTrue(self.movie_expected_keys.issubset(i), "Missing key in response!"), response)

    def test_discover_movies_genres(self):
        genres = "27"
        response = self.api.discover_movies(genres)
        self.assertGreater(len(response), 0, "Discover movies with genres response empty!")
        map(lambda i: self.assertTrue(self.movie_expected_keys.issubset(i), "Missing key in response!"), response)

    def test_discover_movies_multiple_genres(self):
        genres = "27,28,12"
        response = self.api.discover_movies(genres)
        self.assertGreater(len(response), 0, "Discover movies with multiple genres response empty!")
        map(lambda i: self.assertTrue(self.movie_expected_keys.issubset(i), "Missing key in response!"), response)

    def test_get_movie(self):
        movie_id = "615656"
        response = self.api.get_movie(movie_id)
        self.assertIsNotNone(response, "Get movie response empty!")
        self.assertTrue(self.movie_expected_keys.issubset(response), "Missing key in response!")


class TestUserMethods(unittest.TestCase):

    DEBUG_HEADERS = {
        "accept": "application/json"
    }

    DEBUG_USER_CREDS = {
        "email" : "unit@tests.py",
        "password" : "unitests"
    }

    DEBUG_SIGNUP_CREDS = {
        "email": "unit@tests.py",
        "password": "unitests",
        "name": "Unit test",
    }

    DEBUG_UPDATE_REQUEST = {
        "id": "0",
        "email": "unit@tests.py",
        "password": "unitests",
        "name": "unitests",
        "bio": "Bio Unit test",
    }

    def setUp(self):
        self.api = API(self.DEBUG_HEADERS)

    def test_user_login(self):
        response = self.api.user_login(self.DEBUG_USER_CREDS["email"], self.DEBUG_USER_CREDS["password"])
        self.assertIsNotNone(response, "User login response empty!")
        self.assertEquals(response["profile"]["email"],  self.DEBUG_USER_CREDS["email"], "Incorrect email in response")

    @unittest.expectedFailure
    def test_user_signup(self):

        response = self.api.user_signup(
            self.DEBUG_SIGNUP_CREDS["email"],
            self.DEBUG_SIGNUP_CREDS["password"],
            self.DEBUG_SIGNUP_CREDS["name"]
        )

        self.assertIsNotNone(response, "User signup response empty!")
        self.assertEquals(response["profile"]["email"],  self.DEBUG_USER_CREDS["email"], "Incorrect email in response")
        self.assertEquals(response["profile"]["name"], self.DEBUG_USER_CREDS["name"], "Incorrect name in response")
        self.assertIsNotNone(response["profile"]["id"], "No ID in response")
        self.userID = response["profile"]["id"]

    @unittest.expectedFailure
    def test_user_update_info(self):
        response = self.api.user_update(
            self.userID,
            self.DEBUG_UPDATE_REQUEST["email"],
            self.DEBUG_UPDATE_REQUEST["password"],
            self.DEBUG_UPDATE_REQUEST["name"],
            self.DEBUG_UPDATE_REQUEST["bio"]
        )

        self.assertIsNotNone(response, "User update info response empty!")
        self.assertEquals(response["profile"]["email"], self.DEBUG_USER_CREDS["email"], "Incorrect email in response")
        self.assertEquals(response["profile"]["name"], self.DEBUG_USER_CREDS["name"], "Incorrect name in response")
        self.assertEquals(response["profile"]["bio"], self.DEBUG_USER_CREDS["bio"], "Incorrect bio in response")
        self.assertIsNotNone(response["profile"]["id"], "No ID in response")

    @unittest.expectedFailure
    def test_user_get_info(self):

        response = self.api.get_user(self.userID)
        self.assertIsNotNone(response, "User get info response empty!")
        self.assertEquals(response["profile"]["email"], self.DEBUG_USER_CREDS["email"], "Incorrect email in response")
        self.assertEquals(response["profile"]["name"], self.DEBUG_USER_CREDS["name"], "Incorrect name in response")
        self.assertIsNotNone(response["profile"]["id"], "No ID in response")

    @unittest.expectedFailure
    def test_user_delete(self):
        response = self.api.delete_user(self.userID)
        self.assertIsNotNone(response, "User delete response empty!")
        self.assertEquals(response, "user deleted successfully")


class TestWatchlistMethods(unittest.TestCase):

    DEBUG_HEADERS = {
        "accept": "application/json"
    }

    DEBUG_ADD_MOVIE = {
        "movie_id" : "55512"
    }

    def setUp(self):
        self.api = API(self.DEBUG_HEADERS)

    @unittest.expectedFailure
    def test_watchlist_create(self):
        response = self.api.create_watchlist("testName")
        self.assertIsNotNone(response, "Create watchlist response empty!")
        self.assertIsNotNone(response["id"], "No id in create watchlist")
        self.assertEquals(response["name"], "testName")
        self.watchlistID = response["id"]

    @unittest.expectedFailure
    def test_watchlist_add_movie(self):
        response = self.api.add_movie_to_watchlist(self.watchlistID, self.DEBUG_ADD_MOVIE["movie_id"])
        self.assertIsNotNone(response, "Add movies to watchlist response empty!")

    @unittest.expectedFailure
    def test_get_watchlist(self):
        response = self.api.get_watchlist(self.watchlistID)
        self.assertIsNotNone(response, "Get watchlist response empty!")
        self.assertEquals(response["name"], "testName")
        self.assertEquals(response["movie_ids"][0], "55512")

    @unittest.expectedFailure
    def test_watchlist_delete_movie(self):
        response = self.api.delete_movie_from_watchlist(self.watchlistID, self.DEBUG_ADD_MOVIE["movie_id"])
        self.assertIsNotNone(response, "Delete movie from watchlist response empty!")

    @unittest.expectedFailure
    def test_watchlist_delete(self):
        response = self.api.delete_watchlist(self.watchlistID)
        self.assertIsNotNone(response, "Delete watchlist response empty!")


if __name__ == '__main__':
    proc = subprocess.Popen(["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"],
                            preexec_fn=os.setsid)
    time.sleep(5)
    unittest.main(exit=False)
    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
