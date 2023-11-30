import requests


class API:
    BASE_URL = "http://localhost:8000/"
    headers = {
        "accept": "application/json"
    }

    def __init__(self, headers):
        self.headers = headers

    def discover_movies(self, genres=""):
        route = "movies/discover"
        params = "?genres="+genres if genres != "" else ""
        url = self.BASE_URL + route + params
        return requests.get(url, headers=self.headers).json()

    def get_movie(self, movie_id=""):
        route = "movies/%s" % movie_id
        url = self.BASE_URL + route
        return requests.get(url, headers=self.headers).json()

    def user_login(self, email, password):
        route = "user/login"
        url = self.BASE_URL + route
        return requests.post(url, headers=self.headers, json={
            "email": email,
            "password": password
        }).json()

    def user_signup(self, email, password, name):
        route = "user/signup"
        url = self.BASE_URL + route
        return requests.post(url, headers=self.headers, json={
            "email": email,
            "password": password,
            "name": name
        }).json()

    def user_update(self, user_id, email, password, name, bio):
        route = "user/%s" % user_id
        url = self.BASE_URL + route
        return requests.post(url, headers=self.headers, data={
            "id": "%s" % id,
            "email": "%s" % email,
            "name": "%s" % name,
            "password": "%s" % password,
            "bio": "%s" % bio
        }).json()

    def get_user(self, user_id):
        route = "user/%s" % user_id
        url = self.BASE_URL + route
        return requests.get(url, headers=self.headers).json()

    def delete_user(self, user_id):
        route = "user/%s" % user_id
        url = self.BASE_URL + route
        return requests.delete(url, headers=self.headers).json()

    def create_watchlist(self, watchlist_name):
        route = "watchlist"
        url = self.BASE_URL + route
        return requests.post(url, headers=self.headers, json={"name": "%s" % watchlist_name}).json()

    def add_movie_to_watchlist(self, watch_id, movie_id):
        route = "watchlist/%s/movies" % watch_id
        url = self.BASE_URL + route
        return requests.post(url, headers=self.headers, json={"movie_id": "%s" % movie_id}).json()

    def get_watchlist(self, watch_id):
        route = "watchlist/%s" % watch_id
        url = self.BASE_URL + route
        return requests.get(url, headers=self.headers).json()

    def delete_movie_from_watchlist(self, watch_id, movie_id):
        route = "watchlist/%s/movies/%s" % (watch_id, movie_id)
        url = self.BASE_URL + route
        return requests.delete(url, headers=self.headers).json()

    def delete_watchlist(self, watch_id):
        route = "watchlist/%s" % watch_id
        url = self.BASE_URL + route
        return requests.delete(url, headers=self.DEBUG_HEADERS).json()



