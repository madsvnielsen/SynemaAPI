from pydantic import BaseModel


class CredentialsModel(BaseModel):
    email: str
    password: str