from pydantic import BaseModel
from typing import Optional

class Statistics(BaseModel):
    def __init__(self, player_id: int, games_played: int, goals: int, assists: int):
        self.player_id = player_id
        self.games_played = games_played
        self.goals = goals
        self.assists = assists