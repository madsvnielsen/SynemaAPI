from pydantic import BaseModel


class WatchlistCreationModel(BaseModel):
    watchlistName: str

