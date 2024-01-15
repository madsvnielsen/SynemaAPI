#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from http.client import HTTPException
from typing import Union

from google.cloud.firestore_v1 import FieldFilter
from google.cloud.firestore_v1.field_path import FieldPath

from typing_extensions import Annotated
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

import requests
import uuid

from cryptography.fernet import Fernet
from fastapi import FastAPI, Form, Response, status, Depends, Request
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from models.ReviewModel import ReviewModel
from models.CredentialsModel import CredentialsModel
from models.UserModel import User
from models.WatchlistModel import WatchlistModel
import datetime


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


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


def decode_token(token):
    user_token = db.collection("tokens").document(token).get()
    if not user_token.exists:
        return None
    user_id = user_token.to_dict()["userId"]
    user = db.collection("users").document(user_id).get()
    if not user.exists:
        return None

    user_data = user.to_dict()
    return User(
        name=user_data["username"], email= user_data["email"], id=user_id
    )


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    print("Token: %s " % token)
    user = decode_token(token)
    return user


def create_token(userid: str):
    token = str(uuid.uuid4())
    token_ref = db.collection("tokens").document(token)
    current_time = datetime.datetime.now()
    token_ref.set({"userId": userid, "date" : current_time})
    return token

def get_or_create_token(userid : str):
    tokens = list(db.collection("tokens").where(filter=FieldFilter("userId", "==", userid)).stream())
    print(len(tokens))
    if len(tokens) > 0:
        to_return = tokens[0].id
        old_tokens = (db.collection("tokens").where(filter=FieldFilter("userId", "==", userid)).stream())
        for doc in old_tokens:
            if doc.id == to_return:
                continue
            db.collection("tokens").document(doc.id).delete()

        return to_return
    return create_token(userid)




@app.delete("/watchlist/{watchlist_id}")
def delete_watchlist(watchlist_id: str,  response: Response, current_user: Annotated[User, Depends(get_current_user)] = None):
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
def view_watchlist(watchlist_id: str, response : Response, current_user: Annotated[User, Depends(get_current_user)] = None):
    # Get the document reference for the specified watchlist_id
    doc_ref = db.collection("watchlists").document(watchlist_id)
    default = "https://i0.wp.com/godstedlund.dk/wp-content/uploads/2023/04/placeholder-5.png?w=1200&ssl=1"

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
def create_watchlist(response : Response, creation_request: WatchlistModel, current_user: Annotated[User, Depends(get_current_user)] = None):
    if current_user is None:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message": "Unauthorized"}
    watchlist_id = str(uuid.uuid4())

    doc_ref = db.collection("watchlists").document(watchlist_id)
    doc_ref.set({
        "name": creation_request.name,
        "userid": current_user.id,
        "movieIds": []
    })

    return {"hello"}


@app.post("/watchlist/{watchlist_id}/movies")
def add_movie(watchlist_id: str, movie_id: Annotated[str, Form()], response: Response, current_user: Annotated[User, Depends(get_current_user)] = None):
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
def delete_movie(watchlist_id: str, movie_id: str, response: Response, current_user: Annotated[User, Depends(get_current_user)] = None):
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
def read_db(request: Request, response : Response, current_user: Annotated[User, Depends(get_current_user)] = None, ):
    lists_ref = db.collection("watchlists").where(filter=FieldFilter("userid", "==", current_user.id))
    docs = lists_ref.stream()
    watchlists = []
    default = "https://i0.wp.com/godstedlund.dk/wp-content/uploads/2023/04/placeholder-5.png?w=1200&ssl=1"
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

@app.get("/watchlist")
def read_other_user_db(request: Request, response : Response, user_id : str ):
    lists_ref = db.collection("watchlists").where(filter=FieldFilter("userid", "==", user_id))
    docs = lists_ref.stream()
    watchlists = []
    default = "https://i0.wp.com/godstedlund.dk/wp-content/uploads/2023/04/placeholder-5.png?w=1200&ssl=1"
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
def read_root(current_user: Annotated[User, Depends(get_current_user)] = None):
    if current_user is None:
        return {"detail" : "You are not authorized"}

    return {"detail" : "Authorized as %s" % current_user.name}




@app.get("/movies/discover")
def discover_movies(genres : str = ""):
    params = "?with_genres="+genres if genres != "" else ""
    route = "discover/movie"
    url = API_URL + route + params
    default = "https://i0.wp.com/godstedlund.dk/wp-content/uploads/2023/04/placeholder-5.png?w=1200&ssl=1"
    #print(url)
    #response = requests.get(url, headers=headers).json()
    response = requests.get(url, headers=headers)

    if response.status_code == 200:

        response_data = response.json()

    simpleResult = [{
        "id": res["id"],
        "poster_url":  MEDIA_URL + res["poster_path"] if res["poster_path"] is not None else default,
        "backdrop_url": BACKDROP_URL + res["backdrop_path"] if res["backdrop_path"] is not None else default,
        "title": res["title"],
        "description": res["overview"],
        "rating": res["vote_average"],
        "release_date": res["release_date"],
        "tagline": res["tagline"] if "tagline" in res else ""

    } for res in response_data.get("results", [])]

    return simpleResult


@app.get("/movies/{movie_id}/similar")
def similar_movies(movie_id : str = ""):
    route = "movie/%s/similar" % movie_id
    url = API_URL + route
    default = "https://i0.wp.com/godstedlund.dk/wp-content/uploads/2023/04/placeholder-5.png?w=1200&ssl=1"

    response = requests.get(url, headers=headers)


    if response.status_code != 200:
        return {"details" : "error"}
    response_data = response.json()

    return [{
        "id": res["id"],
        "poster_url":  MEDIA_URL + res["poster_path"] if res["poster_path"] is not None else default,
        "backdrop_url": BACKDROP_URL + res["backdrop_path"] if res["backdrop_path"] is not None else default,
        "title": res["title"],
        "description": res["overview"],
        "rating": res["vote_average"],
        "release_date": res["release_date"],
        "tagline": res["tagline"] if "tagline" in res else ""
    } for res in response_data["results"]]



@app.get("/movies/new")
def new_movies ():
    route = "movie/now_playing"
    url = API_URL + route
    default = "https://i0.wp.com/godstedlund.dk/wp-content/uploads/2023/04/placeholder-5.png?w=1200&ssl=1"
    #print(url)
    #response = requests.get(url, headers=headers).json()
    response = requests.get(url, headers=headers)

    if response.status_code == 200:

        response_data = response.json()

    simpleResult = [{
        "id": res["id"],
        "poster_url":  MEDIA_URL + res["poster_path"] if res["poster_path"] is not None else default,
        "backdrop_url": BACKDROP_URL + res["backdrop_path"] if res["backdrop_path"] is not None else default,
        "title": res["title"],
        "description": res["overview"],
        "rating": res["vote_average"],
        "release_date": res["release_date"],
        "tagline": res["tagline"] if "tagline" in res else ""
    } for res in response_data.get("results", [])]

    return simpleResult

@app.get("/movies/search")
def search_movies(query : str = ""):

    params = "?query=" + query
    route = "search/movie"
    url = API_URL + route + params
    default = "https://i0.wp.com/godstedlund.dk/wp-content/uploads/2023/04/placeholder-5.png?w=1200&ssl=1"

    response = requests.get(url, headers=headers).json()

    simpleResult = [{
        "id" : res["id"],
        "poster_url" : MEDIA_URL + res["poster_path"] if res["poster_path"] is not None else default,
        "backdrop_url": BACKDROP_URL + res["backdrop_path"] if res["backdrop_path"] is not None else default,
        "title": res["title"],
        "description" : res["overview"],
        "rating" : res["vote_average"],
        "release_date" : res["release_date"],
        "tagline": res["tagline"] if "tagline" in res else ""
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
        "email": email,
        "bio": "",
        "profilePicture": "https://i.postimg.cc/3wJzmXPm/Avatar-Maker.png",

    })


    return {
        "profile": {
            "id": userid,
            "name": username,
            "email": email,
            "token": "Bearer " + create_token(doc_id),
            "bio":"",
            "profilePicture": "https://i.postimg.cc/3wJzmXPm/Avatar-Maker.png"
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

    token = get_or_create_token(doc_id)

    return {
        "profile" : {
            "id" : doc_id,
            "name" : fields["username"],
            "email": fields["email"],
            "token" : "Bearer " + token,
            "bio": fields["bio"],
            "profilePicture":fields["profilePicture"],

        }
    }


@app.post("/token/verify")
def verify_token(token: Annotated[str, Form()]):
    user = decode_token(token.split("Bearer ")[1])
    if user is None :
        return False
    return True

@app.post("/token/clear")
def clear_token(current_user: Annotated[User, Depends(get_current_user)] = None):
    if current_user is None :
        return {"detail" : "Unauthorized"}
    tokens = (db.collection("tokens").where(filter=FieldFilter("userId", "==", current_user.id)).stream())
    for doc in tokens:
        db.collection("tokens").document(doc.id).delete()
    return True


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
        "poster_url" : MEDIA_URL + res["poster_path"] if res["poster_path"] is not None else default ,
        "backdrop_url": BACKDROP_URL + res["backdrop_path"] if res["backdrop_path"] is not None else default,
        "title": res["title"],
        "description" : res["overview"],
        "rating" : res["vote_average"],
        "release_date" : res["release_date"],
        "tagline": res["tagline"] if "tagline" in res else ""
    }
    return simpleResult

@app.get("/movie/{id}/credits")
def get_movie_credits(id : str = ""):
    params = ""
    route = "movie/" + id +"/credits"
    url = API_URL + route + params
    res = requests.get(url, headers=headers).json()
    default = "https://www.google.com/url?sa=i&url=https%3A%2F%2Fuxwing.com%2Fno-profile-picture-icon%2F&psig=AOvVaw3iMZCY67eG17B8pGdaqRm4&ust=1705145407673000&source=images&cd=vfe&opi=89978449&ved=0CBIQjRxqFwoTCJD4geff14MDFQAAAAAdAAAAABAD"

    credit_data = []


    for actor in res["cast"]:
        credit_data.append({
            "character": actor["character"],
            "name": actor["name"],
            "picture_path" : MEDIA_URL + actor["profile_path"] if actor["profile_path"] is not None else default,
            "id" : str(actor["id"])
        })

    return credit_data


@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], response : Response):
    req = user_login(form_data.username, form_data.password, response)
    if "profile" not in req:
        response.status_code = status.HTTP_401_UNAUTHORIZED;
        return {"detail": "Incorrect username or password"}

    return {"access_token": req["profile"]["token"].split("Bearer ")[1], "token_type": "bearer"}

@app.post("/movie/{id}/reviews")
def create_review(id : str, creation_request : ReviewModel,current_user: Annotated[User, Depends(get_current_user)] = None):
    if current_user is None:
        return {"detail" : "You are not authorized"}

    existing_reviews = list((db.collection("reviews")
                             .document(id)
                             .collection("entities")
                             .where(filter=FieldFilter("userid", "==", current_user.id))
                             .stream()))

    if len(existing_reviews) == 0:
        review_id = str(uuid.uuid4())
        doc_ref = db.collection("reviews").document(id).collection("entities").document(review_id)
        doc_ref.set({
        "reviewText": creation_request.reviewText,
        "userid": current_user.id,
        "rating": creation_request.rating,
        "movieid": id,
        "username": current_user.name,
    })

    if len(existing_reviews) > 0:
        #User already has review
        existing_reviews[0].reference.update({
            "reviewText": creation_request.reviewText,
            "rating": creation_request.rating,
        })


    return {"hello"}

@app.delete("/movie/{movie_id}/reviews")
def delete_review(movie_id: str, current_user: Annotated[User, Depends(get_current_user)] = None):
    existing_reviews = list((db.collection("reviews")
                             .document(movie_id)
                             .collection("entities")
                             .where(filter=FieldFilter("userid", "==", current_user.id))
                             .stream()))


    # Get the document reference for the specified review
    if len(existing_reviews) > 0:
        for review in existing_reviews:
            review.reference.delete()

    return {"message": "Review deleted successfully"}


@app.get("/movie/{movie_id}/reviews")
def get_reviews_for_movie(movie_id: str):
    reviews = []

    reviews_collection = db.collection("reviews").document(movie_id).collection("entities").stream()

    for review in reviews_collection:
        review_data = review.to_dict()
        reviews.append(review_data)


    return reviews


@app.get("/user/reviews/")
def get_own_reviews(current_user: User = Depends(get_current_user)):
    reviews = []
    all_reviews_q = db.collection_group('entities')
    all_reviews_ref = all_reviews_q.stream()
    for doc in all_reviews_ref:
        print(f'Document: {doc.to_dict()}')
        review_data = doc.to_dict()

        if review_data["userid"] == current_user.id:
            reviews.append(review_data)

    return reviews

@app.get("/user/{user_id}/reviews/")
def get_reviews_for_user(user_id : str):
    reviews = []
    all_reviews_q = db.collection_group('entities')
    all_reviews_ref = all_reviews_q.stream()
    for doc in all_reviews_ref:
        print(f'Document: {doc.to_dict()}')
        review_data = doc.to_dict()

        if review_data["userid"] == user_id:
            reviews.append(review_data)

    return reviews


@app.get("/user/{username}")
def user_by_username(username: str, response : Response, current_user: Annotated[User, Depends(get_current_user)] = None):
    userlist=[]
    # Get the document reference for the specified username
    users_q = db.collection('users').where(filter=FieldFilter('username','>=', username)).where(filter=FieldFilter('username','<=', username + '\uf8ff'))
    users_ref = users_q.stream()
    for doc in users_ref:
        print(f'Document: {doc.to_dict()}')
        userdata = doc.to_dict()

        userlist.append( {
            "name" : userdata["username"],
            "email": userdata["email"],
            "bio": userdata["bio"],
            "profilePicture":userdata["profilePicture"],
            "id": doc.id
        })
    return userlist


@app.get("/user/profile/{userid}")
def user_by_id(userid: str, response : Response, current_user: Annotated[User, Depends(get_current_user)] = None):

    # Get the document reference for the specified username
    users_q = db.collection('users').document(userid)
    users_ref = users_q.get()
    if not users_ref.exists:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"details": "no user"}

    print(f'Document: {users_ref.to_dict()}')
    userdata = users_ref.to_dict()

    return {
        "name" : userdata["username"],
        "email": userdata["email"],
        "bio": userdata["bio"],
        "profilePicture":userdata["profilePicture"],
        "id": users_ref.id
    }

@app.post("/user/editbio/{userid}")
def edit_user_bio(userid: str, creation_request: User, response: Response,  current_user: Annotated[User, Depends(get_current_user)] = None):
    user=db.collection('users').document(userid)

    user.update({
        "bio":creation_request.bio
    })


@app.post("/user/editProfilePicture/{userid}")
def edit_user_bio(userid: str, creation_request: User, response: Response,
                  current_user: Annotated[User, Depends(get_current_user)] = None):
    user = db.collection('users').document(userid)

    user.update({
        "profilePicture": creation_request.profilePicture
    })

