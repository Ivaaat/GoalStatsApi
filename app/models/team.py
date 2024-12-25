from pydantic import BaseModel
from typing import Optional



class Team(BaseModel):
    id: Optional[int] = None
    name: str
    icon: Optional[str] = None
    old_id: Optional[int] = None
    