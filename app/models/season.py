from pydantic import BaseModel
from typing import Optional


class Season(BaseModel):
    name: str