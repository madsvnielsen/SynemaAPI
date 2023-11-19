import unittest
import subprocess
import os
import time
import signal
import requests


class TestMovieMethods(unittest.TestCase):
    DEBUG_URL = "http://localhost:8000/"
    BASE_ROUTE = "movies"
    DEBUG_HEADERS = {
        "accept": "application/json"
    }
    movie_expected_keys = {"id", "poster_url", "backdrop_url", "title", "description", "rating", "release_date"}

    def test_discover_movies(self):
        route = "/discover"
        url = self.DEBUG_URL + self.BASE_ROUTE + route
        response = requests.get(url, headers=self.DEBUG_HEADERS).json()
        self.assertGreater(len(response), 0, "Discover movies response empty!")
        map(lambda i: self.assertTrue(self.movie_expected_keys.issubset(i), "Missing key in response!"), response)

    def test_discover_movies_genres(self):
        genres = "27"
        params = "?genres=%s" % genres
        route = "/discover"
        url = self.DEBUG_URL + self.BASE_ROUTE + route + params
        response = requests.get(url, headers=self.DEBUG_HEADERS).json()
        self.assertGreater(len(response), 0, "Discover movies with genres response empty!")
        map(lambda i: self.assertTrue(self.movie_expected_keys.issubset(i), "Missing key in response!"), response)

    def test_discover_movies_multiple_genres(self):
        genres = "27,28,12"
        params = "?genres=%s" % genres
        route = "/discover"
        url = self.DEBUG_URL + self.BASE_ROUTE + route + params
        response = requests.get(url, headers=self.DEBUG_HEADERS).json()
        self.assertGreater(len(response), 0, "Discover movies with multiple genres response empty!")
        map(lambda i: self.assertTrue(self.movie_expected_keys.issubset(i), "Missing key in response!"), response)

    def test_get_movie(self):
        route = "/615656"
        url = self.DEBUG_URL + self.BASE_ROUTE + route
        response = requests.get(url, headers=self.DEBUG_HEADERS).json()
        self.assertIsNotNone(response, "Get movie response empty!")
        self.assertTrue(self.movie_expected_keys.issubset(response), "Missing key in response!")


class TestUserMethods(unittest.TestCase):
    DEBUG_URL = "http://localhost:8000/"
    BASE_ROUTE = "user"
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
        "bio": "Bio Unit test",
    }

    def test_user_login(self):
        route = "/login"
        url = self.DEBUG_URL + self.BASE_ROUTE + route
        response = requests.post(url, headers=self.DEBUG_HEADERS, json=self.DEBUG_USER_CREDS).json()
        self.assertIsNotNone(response, "User login response empty!")
        self.assertEquals(response["profile"]["email"],  self.DEBUG_USER_CREDS["email"], "Incorrect email in response")

    @unittest.expectedFailure
    def test_user_signup(self):
        route = "/signup"
        url = self.DEBUG_URL + self.BASE_ROUTE + route
        response = requests.post(url, headers=self.DEBUG_HEADERS, json=self.DEBUG_SIGNUP_CREDS).json()
        self.assertIsNotNone(response, "User signup response empty!")
        self.assertEquals(response["profile"]["email"],  self.DEBUG_USER_CREDS["email"], "Incorrect email in response")
        self.assertEquals(response["profile"]["name"], self.DEBUG_USER_CREDS["name"], "Incorrect name in response")
        self.assertIsNotNone(response["profile"]["id"], "No ID in response")
        self.userID = response["profile"]["id"]

    @unittest.expectedFailure
    def test_user_update_info(self):
        route = "/%s" % self.userID
        url = self.DEBUG_URL + self.BASE_ROUTE + route
        data = self.DEBUG_UPDATE_REQUEST
        data["id"] = self.userID
        response = requests.post(url, headers=self.DEBUG_HEADERS, data=data).json()
        self.assertIsNotNone(response, "User update info response empty!")
        self.assertEquals(response["profile"]["email"], self.DEBUG_USER_CREDS["email"], "Incorrect email in response")
        self.assertEquals(response["profile"]["name"], self.DEBUG_USER_CREDS["name"], "Incorrect name in response")
        self.assertEquals(response["profile"]["bio"], self.DEBUG_USER_CREDS["bio"], "Incorrect bio in response")
        self.assertIsNotNone(response["profile"]["id"], "No ID in response")

    @unittest.expectedFailure
    def test_user_get_info(self):
        route = "/%s" % self.userID
        url = self.DEBUG_URL + self.BASE_ROUTE + route
        response = requests.get(url, headers=self.DEBUG_HEADERS).json()
        self.assertIsNotNone(response, "User get info response empty!")
        self.assertEquals(response["profile"]["email"], self.DEBUG_USER_CREDS["email"], "Incorrect email in response")
        self.assertEquals(response["profile"]["name"], self.DEBUG_USER_CREDS["name"], "Incorrect name in response")
        self.assertIsNotNone(response["profile"]["id"], "No ID in response")

    @unittest.expectedFailure
    def test_user_delete(self):
        route = "/%s" % self.userID
        url = self.DEBUG_URL + self.BASE_ROUTE + route
        response = requests.delete(url, headers=self.DEBUG_HEADERS).json()
        self.assertIsNotNone(response, "User delete response empty!")
        self.assertEquals(response, "user deleted successfully")


class TestWatchlistMethods(unittest.TestCase):
    DEBUG_URL = "http://localhost:8000/"
    BASE_ROUTE = "watchlists"
    DEBUG_HEADERS = {
        "accept": "application/json"
    }

    DEBUG_ADD_MOVIE = {
        "movie_id" : "55512"
    }

    @unittest.expectedFailure
    def test_watchlist_create(self):
        route = "/create"
        url = self.DEBUG_URL + self.BASE_ROUTE + route
        response = requests.post(url, headers=self.DEBUG_HEADERS, json={"name": "testName"}).json()
        self.assertIsNotNone(response, "Create watchlist response empty!")
        self.assertIsNotNone(response["id"], "No id in create watchlist")
        self.assertEquals(response["name"], "testName")
        self.watchlistID = response["id"]

    @unittest.expectedFailure
    def test_watchlist_add_movie(self):
        route = "/%s/movies" % self.watchlistID
        url = self.DEBUG_URL + self.BASE_ROUTE + route
        response = requests.post(url, headers=self.DEBUG_HEADERS, json=self.DEBUG_ADD_MOVIE).json()
        self.assertIsNotNone(response, "Add movies to watchlist response empty!")

    @unittest.expectedFailure
    def test_get_watchlist(self):
        route = "/%s" % self.watchlistID
        url = self.DEBUG_URL + self.BASE_ROUTE + route
        response = requests.get(url, headers=self.DEBUG_HEADERS).json()
        self.assertIsNotNone(response, "Get watchlist response empty!")
        self.assertEquals(response["name"], "testName")
        self.assertEquals(response["movie_ids"][0], "55512")

    @unittest.expectedFailure
    def test_watchlist_delete_movie(self):
        route = "/%s/movies" % self.watchlistID
        url = self.DEBUG_URL + self.BASE_ROUTE + route
        response = requests.delete(url, headers=self.DEBUG_HEADERS, json=self.DEBUG_ADD_MOVIE).json()
        self.assertIsNotNone(response, "Delete movie from watchlist response empty!")

    @unittest.expectedFailure
    def test_watchlist_delete(self):
        route = "/%s" % self.watchlistID
        url = self.DEBUG_URL + self.BASE_ROUTE + route
        response = requests.delete(url, headers=self.DEBUG_HEADERS).json()
        self.assertIsNotNone(response, "Delete watchlist response empty!")


if __name__ == '__main__':
    proc = subprocess.Popen(["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"],
                            preexec_fn=os.setsid)
    time.sleep(5)
    unittest.main(exit=False)
    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
