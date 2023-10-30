#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Union

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/test")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"test": noob, "q": q}
