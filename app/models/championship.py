from pydantic import BaseModel
from typing import Optional

class Championship(BaseModel):
    id: Optional[int] = None 
    name: str
    country: Optional[str] = None
    priority: Optional[int] = None
    img: Optional[str] = None
    old_id: Optional[int] = None
    link: Optional[str] = None
    is_active: Optional[bool] = None
    is_top: Optional[bool] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_cup: Optional[bool] = None
    alias: Optional[str] = None