from pydantic import BaseModel


class WatchlistModel(BaseModel):
    name: str
    watchlist_id: str
    userid: str
    movieIds: list


