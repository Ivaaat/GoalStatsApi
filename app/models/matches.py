from pydantic import BaseModel
from typing import Optional, Dict

class Match(BaseModel):
    old_id: int
    section: Optional[str] = None
    link: Optional[str] = None
    time: Optional[str] = None
    groups: Optional[Dict] = None
    flags: Optional[Dict] = None
    result: Optional[Dict] = None
    status: Optional[Dict] = None
    pub_date: Optional[int] = None
    score: Optional[Dict] = None
    total_home: Optional[int] = None
    total_away: Optional[int] = None
    roundforltandmc: Optional[str] = None
    tour: Optional[int] = None
    periods: Optional[Dict] = None
    time_str: Optional[str] = None
    link_title: Optional[str] = None
    date_id: int
    champ_id: int
    home_team_id: int
    away_team_id: int