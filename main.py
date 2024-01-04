#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from http.client import HTTPException
from typing import Union

from google.cloud.firestore_v1 import FieldFilter
from typing_extensions import Annotated


import requests
import uuid

from cryptography.fernet import Fernet
from fastapi import FastAPI, Form, Response, status
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore



from models.CredentialsModel import CredentialsModel
from models.WatchlistModel import WatchlistModel

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
def delete_watchlist(watchlist_id: str, response: Response):
    # Get the document reference for the specified watchlist_id
    doc_ref = db.collection("watchlists").document(watchlist_id)

    # Check if the document exists
    if not doc_ref.get().exists:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Watchlist does not exist"}

    # Delete the entire watchlist document
    doc_ref.delete()

    return {"message": "Watchlist deleted successfully"}


@app.get("/watchlist/{watchlist_id}")
def view_watchlist(watchlist_id: str, response : Response):
    # Get the document reference for the specified watchlist_id
    doc_ref = db.collection("watchlists").document(watchlist_id)
    default = "https://www.udacity.com/blog/wp-content/uploads/2021/02/img8.png"

    # Check if the document exists
    watchlist_data = doc_ref.get()
    if not watchlist_data.exists:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Watchlist does not exist"}

    # Get the data from the watchlist document
    watchlist_details = watchlist_data.to_dict()

    # Include the watchlist ID in the returned data
    watchlist_details["watchlist_id"] = watchlist_id

    watchlist_icons = []
    for i in range(4):
        if len(watchlist_details["movieIds"]) < i + 1:
            watchlist_icons.append(default)
            continue
        watchlist_icons.append(get_movie(watchlist_details["movieIds"][i])["poster_url"])
    watchlist_details["icons"] = watchlist_icons

    return watchlist_details
@app.post("/watchlist")
def create_watchlist(creation_request : WatchlistModel):

    watchlist_id = str(uuid.uuid4())

    doc_ref = db.collection("watchlists").document(watchlist_id)
    doc_ref.set({
        "name": creation_request.name,
        "userid": "123",
        "movieIds": []
    })

    return {"hello"}

@app.post("/watchlist/{watchlist_id}/movies")
def add_movie(watchlist_id: str, movie_id: Annotated[str, Form()], response: Response):
    # Get the document reference for the specified watchlist_id
    doc_ref = db.collection("watchlists").document(watchlist_id)

    # Check if the document exists
    if not doc_ref.get().exists:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Watchlist does not exist"}

    # Update the document to add the movie_id to the "movieIDS" array
    doc_ref.update({
        "movieIds": firestore.ArrayUnion([movie_id])
    })

    return {"message": "Movie added successfully"}

@app.delete("/watchlist/{watchlist_id}/movies/{movie_id}")
def delete_movie(watchlist_id: str, movie_id: str, response : Response):
    # Get the document reference for the specified watchlist_id
    doc_ref = db.collection("watchlists").document(watchlist_id)

    # Check if the document exists
    if not doc_ref.get().exists:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Watchlist does not exist"}

    # Update the document to remove the movie_id from the "movieIDS" array
    doc_ref.update({
        "movieIds": firestore.ArrayRemove([movie_id])
    })

    return {"message": "Movie deleted successfully"}

@app.get("/watchlist")
def read_db(response : Response):
    lists_ref = db.collection("watchlists")
    docs = lists_ref.stream()
    watchlists = []
    default = "https://www.udacity.com/blog/wp-content/uploads/2021/02/img8.png"
    for doc in docs:
        doc_id = str(doc.id)
        fields = doc.to_dict()
        if "movieIds" not in fields:
            continue

        watchlist_icons = []
        for i in range(4):
            if len(fields["movieIds"]) < i+1:
                watchlist_icons.append(default)
                continue
            watchlist_icons.append(get_movie(fields["movieIds"][i])["poster_url"])

        watchlists.append({
            "name" : fields["name"],
            "watchlist_id" : doc_id,
            "userid" : fields["userid"],
            "movieIds" : fields["movieIds"],
            "icons" : watchlist_icons
        })
    return watchlists




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
    #print(url)
    #response = requests.get(url, headers=headers).json()
    response = requests.get(url, headers=headers)

    if response.status_code == 200:

        response_data = response.json()

    simpleResult = [{
        "id": res["id"],
        "poster_url": MEDIA_URL + res["poster_path"],
        "backdrop_url": BACKDROP_URL + res["backdrop_path"] if res["backdrop_path"] is not None else default,
        "title": res["title"],
        "description": res["overview"],
        "rating": res["vote_average"],
        "release_date": res["release_date"]
    } for res in response_data.get("results", [])]

    return simpleResult

@app.get("/movies/new")
def new_movies ():
    route = "movie/now_playing"
    url = API_URL + route
    default = "https://www.udacity.com/blog/wp-content/uploads/2021/02/img8.png"
    #print(url)
    #response = requests.get(url, headers=headers).json()
    response = requests.get(url, headers=headers)

    if response.status_code == 200:

        response_data = response.json()

    simpleResult = [{
        "id": res["id"],
        "poster_url": MEDIA_URL + res["poster_path"],
        "backdrop_url": BACKDROP_URL + res["backdrop_path"] if res["backdrop_path"] is not None else default,
        "title": res["title"],
        "description": res["overview"],
        "rating": res["vote_average"],
        "release_date": res["release_date"]
    } for res in response_data.get("results", [])]

    return simpleResult

@app.get("/movies/search")
def search_movies(query : str = ""):
    params = "?query=" + query
    route = "search/movie"
    url = API_URL + route + params
    default = "https://www.udacity.com/blog/wp-content/uploads/2021/02/img8.png"
    print(url)
    response = requests.get(url, headers=headers).json()
    print(response)
    simpleResult = [{
        "id" : res["id"],
        "poster_url" : MEDIA_URL + res["poster_path"] if res["poster_path"] is not None else default,
        "backdrop_url": BACKDROP_URL + res["backdrop_path"] if res["backdrop_path"] is not None else default,        "title": res["title"],
        "description" : res["overview"],
        "rating" : res["vote_average"],
        "release_date" : res["release_date"]
    } for res in response["results"]

    ]

    return simpleResult


@app.post("/user/signup")
def user_signup(username: Annotated[str, Form()], email: Annotated[str, Form()], password: Annotated[str, Form()], response: Response):
    userid = str(uuid.uuid4())

    doc_ref = db.collection("users").document(userid)

    query = db.collection("users").where(filter=FieldFilter("email", "==", email)).stream()

    doc_id = ""
    fields = {}
    for doc in query:
        doc_id = str(doc.id)
        fields = doc.to_dict()
        response.status_code = status.HTTP_306_RESERVED
        return {"message": "User already exist"}

    doc_ref.set({
        "username": username,
        "email": email
    })
    return {
        "profile": {
            "id": userid,
            "name": username,
            "email": email
        }
    }


@app.post("/user/login")
def user_login(email: Annotated[str, Form()], password: Annotated[str, Form()], response: Response):

    users_ref = db.collection("users")

    query = users_ref.where(filter=FieldFilter("email", "==", email)).stream()

    doc_id = ""
    fields = {}
    for doc in query:
        doc_id = str(doc.id)
        fields = doc.to_dict()
        break
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "User not found"}

    return {
        "profile" : {
            "id" : doc_id,
            "name" : fields["username"],
            "email": fields["email"]
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


