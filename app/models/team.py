from pydantic import BaseModel
from typing import Optional



class Team(BaseModel):
    id: Optional[int] = 0
    name: str
    icon: Optional[str] = ""
    old_id: Optional[int] = 0
    