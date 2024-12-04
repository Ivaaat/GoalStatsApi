from pydantic import BaseModel
from typing import Optional


class Season(BaseModel):
    season_id: int
    season_name: str