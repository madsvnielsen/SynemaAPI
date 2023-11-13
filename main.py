#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from typing import Union
import requests
from fastapi import FastAPI

app = FastAPI()

print(os.environ)

API_URL = os.environ["APIURL"]
MEDIA_URL = "https://www.themoviedb.org/t/p/w300_and_h450_bestv2"
BACKDROP_URL ="https://image.tmdb.org/t/p/w1920_and_h1080_bestv2"

headers = {
    "Authorization": os.environ["APIKEY"],
    "accept": "application/json"

}


@app.get("/")
def read_root():
    params = "?external_source=imdb_id"
    route = "find/tt3113782"
    url = API_URL + route + params
    response = requests.get(url, headers=headers)
    imageurl =  MEDIA_URL +  response.json()["movie_results"][0]["poster_path"]


    return response.json()


@app.get("/movies/discover")
def discover_movies(genres : str = ""):
    params = "?with_genres="+genres if genres != "" else ""
    route = "discover/movie"
    url = API_URL + route + params
    default = "https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.udacity.com%2Fblog%2F2021%2F03%2Fcreating-an-html-404-error-web-page.html&psig=AOvVaw1yQVUPOuNPULWSg2o094CB&ust=1699953772395000&source=images&cd=vfe&opi=89978449&ved=0CBEQjRxqFwoTCPjCjrjTwIIDFQAAAAAdAAAAABAJ"
    print(url)
    response = requests.get(url, headers=headers).json()

    simpleResult = [{
        "id" : res["id"],
        "poster_url" : MEDIA_URL + res["poster_path"],
        "backdrop_url" : BACKDROP_URL + res["backdrop_path"] if res["backdrop_path"] is not None else default,
        "title": res["title"],
        "description" : res["overview"],
        "rating" : res["vote_average"],
        "release_date" : res["release_date"]
    } for res in response["results"]

    ]

    return simpleResult

@app.post("/user/login")
def user_login():
    print("Requested!!")
    return {
        "profile" : {
            "id" : "apitest",
            "name" : "Api works",
            "email": "api@net.dk"
        }
    }



@app.get("/genres")
def read_root():
    params = ""
    route = "genre/movie/list"
    url = API_URL + route + params
    response = requests.get(url, headers=headers)

    return response.json()



@app.get("/movies/{id}")
def get_movie(id : str = ""):
    params = ""
    route = "movie/"+id
    url = API_URL + route + params
    print(url)
    res = requests.get(url, headers=headers).json()

    simpleResult = {
        "id" : res["id"],
        "poster_url" : MEDIA_URL + res["poster_path"],
        "backdrop_url": BACKDROP_URL + res["backdrop_path"],
        "title": res["title"],
        "description" : res["overview"],
        "rating" : res["vote_average"],
        "release_date" : res["release_date"]
    }


    return simpleResult