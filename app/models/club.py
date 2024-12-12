from pydantic import BaseModel
from typing import Optional



class Club(BaseModel):
    id: Optional[int] = None
    name: str
    icon: Optional[str] = None
    old_id: Optional[int] = None
    