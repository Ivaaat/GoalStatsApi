import asyncpg
from repositories import ClubRepository, ChampionshipRepository, SeasonRepository, PlayerRepository
from typing import Union

class StatisticsRepository:
    def __init__(self, db: asyncpg.Connection):
        self.db = db

    async def create(self, data: dict):
        # Логика создания статистики
        pass

    async def get(self, rep: Union[ClubRepository, ChampionshipRepository, SeasonRepository, PlayerRepository]):
        rep.get_stat()

    async def update(self, player_id: int, data: dict):
        # Логика обновления статистики игрока
        pass

    async def delete(self, player_id: int):
        # Логика удаления статистики игрока
        pass