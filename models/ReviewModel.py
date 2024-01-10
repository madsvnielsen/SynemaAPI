from pydantic import BaseModel


class ReviewModel(BaseModel):
    reviewText: str
    movieid: str
    userid: str
    rating: int
    username: str




