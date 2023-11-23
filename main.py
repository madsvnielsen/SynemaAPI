#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from http.client import HTTPException
from typing import Union
import requests
import uuid

from cryptography.fernet import Fernet
from fastapi import FastAPI
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from models.WatchlistCreationModel import WatchlistCreationModel
from models.CredentialsModel import CredentialsModel


key = os.environ["DecryptKey"]
# using the key
fernet = Fernet(key)

# opening the encrypted file
with open('synema.key', 'rb') as enc_file:
    encrypted = enc_file.read()

# decrypting the file
decrypted = fernet.decrypt(encrypted)

# opening the file in write mode and
# writing the decrypted data
with open('Zert', 'wb') as dec_file:
    dec_file.write(decrypted)

'''
fireapp = firebase_admin.initialize_app()
db = firestore.client()
'''

# Use a service account.
cred = credentials.Certificate(("Zert"))

fireapp = firebase_admin.initialize_app(cred)

db = firestore.client()


app = FastAPI()

print(os.environ)

API_URL = os.environ["APIURL"]
MEDIA_URL = "https://www.themoviedb.org/t/p/w300_and_h450_bestv2"
BACKDROP_URL ="https://image.tmdb.org/t/p/w1920_and_h1080_bestv2"

headers = {
    "Authorization": os.environ["APIKEY"],
    "accept": "application/json"

}
@app.delete("/watchlist/{watchlist_id}")
def delete_watchlist(watchlist_id: str):
    # Get the document reference for the specified watchlist_id
    doc_ref = db.collection("watchlists").document(watchlist_id)

    # Check if the document exists
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="Watchlist not found")

    # Delete the entire watchlist document
    doc_ref.delete()

    return {"message": "Watchlist deleted successfully"}


@app.get("/watchlist/{watchlist_id}")
def view_watchlist(watchlist_id: str):
    # Get the document reference for the specified watchlist_id
    doc_ref = db.collection("watchlists").document(watchlist_id)

    # Check if the document exists
    watchlist_data = doc_ref.get()
    if not watchlist_data.exists:
        raise HTTPException(status_code=404, detail="Watchlist not found")

    # Get the data from the watchlist document
    watchlist_details = watchlist_data.to_dict()

    # Include the watchlist ID in the returned data
    watchlist_details["watchlist_id"] = watchlist_id

    return watchlist_details
@app.post("/watchlist")
def create_watchlist(creation_request : WatchlistCreationModel):

    watchlist_id = str(uuid.uuid4())

    doc_ref = db.collection("watchlists").document(watchlist_id)

    doc_ref.set({
        "name": creation_request.name,
        "userid": "123",
        "movieIDS": []
    })
    return {"hello"}

@app.post("/watchlist/{watchlist_id}/movies")
def add_movie(watchlist_id: str, movie_id: str):
    # Get the document reference for the specified watchlist_id
    doc_ref = db.collection("watchlists").document(watchlist_id)

    # Check if the document exists
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="Watchlist not found")

    # Update the document to add the movie_id to the "movieIDS" array
    doc_ref.update({
        "movieIDS": firestore.ArrayUnion([movie_id])
    })

    return {"message": "Movie added successfully"}

@app.delete("/watchlist/{watchlist_id}/movies/{movie_id}")
def delete_movie(watchlist_id: str, movie_id: str):
    # Get the document reference for the specified watchlist_id
    doc_ref = db.collection("watchlists").document(watchlist_id)

    # Check if the document exists
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="Watchlist not found")

    # Update the document to remove the movie_id from the "movieIDS" array
    doc_ref.update({
        "movieIDS": firestore.ArrayRemove([movie_id])
    })

    return {"message": "Movie deleted successfully"}

@app.get("/watchlist")
def read_db():
    users_ref = db.collection("watchlists")
    docs = users_ref.stream()

    return [{doc.id: doc.to_dict()} for doc in docs]


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
    default = "https://www.udacity.com/blog/wp-content/uploads/2021/02/img8.png"
    print(url)
    response = requests.get(url, headers=headers).json()

    simpleResult = [{
        "id" : res["id"],
        "poster_url" : MEDIA_URL + res["poster_path"],
        "backdrop_url": BACKDROP_URL + res["backdrop_path"] if res["backdrop_path"] is not None else default,        "title": res["title"],
        "description" : res["overview"],
        "rating" : res["vote_average"],
        "release_date" : res["release_date"]
    } for res in response["results"]

    ]

    return simpleResult

@app.post("/user/login")
def user_login(login_request: CredentialsModel):

    return {
        "profile" : {
            "id" : "test",
            "name" : "Api Works",
            "email": login_request.email
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
    default = "https://www.udacity.com/blog/wp-content/uploads/2021/02/img8.png"
    print(url)
    res = requests.get(url, headers=headers).json()

    simpleResult = {
        "id" : res["id"],
        "poster_url" : MEDIA_URL + res["poster_path"],
        "backdrop_url": BACKDROP_URL + res["backdrop_path"] if res["backdrop_path"] is not None else default,        "title": res["title"],
        "description" : res["overview"],
        "rating" : res["vote_average"],
        "release_date" : res["release_date"]
    }


    return simpleResult


