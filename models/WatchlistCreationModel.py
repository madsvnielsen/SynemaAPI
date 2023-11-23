from pydantic import BaseModel


class WatcglistCreationModel(BaseModel):
    watchlistName: str
