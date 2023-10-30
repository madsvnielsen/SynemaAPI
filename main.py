#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from typing import Union
import requests
from fastapi import FastAPI

app = FastAPI()


API_URL = os.environ["APIURL"]

headers = {
    "Authorization": os.environ["APIKEY"],
    "accept": "application/json"

}


@app.get("/")
def read_root():
    url = API_URL + "find/tt0816692?external_source=imdb_id"
    response = requests.get(url, headers=headers)
    return response.json()


@app.get("/test")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"test": "noob", "q": q}

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
