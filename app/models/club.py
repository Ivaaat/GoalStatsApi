from pydantic import BaseModel
from typing import Optional



class Club(BaseModel):
    club_id: int
    name: str 
    icon: str
    old_id: int
    