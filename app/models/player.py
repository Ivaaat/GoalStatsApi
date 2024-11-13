from pydantic import BaseModel
from typing import Optional


class Player(BaseModel):
    def __init__(self, id: int, name: str, age: int, club_id: int):
        self.id = id
        self.name = name
        self.age = age
        self.club_id = club_id