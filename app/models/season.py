from pydantic import BaseModel
from typing import Optional


class Season(BaseModel):
    id: Optional[int] = None
    name: str