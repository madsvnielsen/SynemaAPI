from pydantic import BaseModel
from typing import Union


class User(BaseModel):
    id: str
    name: str
    email: Union[str, None] = None
    bio: Union[str, None] = None
    profilePicture:str=None

