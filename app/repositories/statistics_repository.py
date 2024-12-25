import asyncpg
from typing import Union

class StatisticsRepository:
    def __init__(self, db: asyncpg.Connection):
        self.db = db

    async def create(self, data: dict):
        # Логика создания статистики
        pass

    async def get_team(self, club_name):
        data = await self.db.fetch("""
                                    select
                                        season_name,
                                        JSONB_OBJECT_AGG(champ_name,
                                        team_id) as champ_name_id_team
                                    from
                                        stats.v_seas_champs_teams x
                                    where
                                        team_name = $1
                                    group by
                                        season_name
                                    order by
                                        season_name desc""", club_name)
        return data

    async def update(self, player_id: int, data: dict):
        # Логика обновления статистики игрока
        pass

    async def delete(self, player_id: int):
        # Логика удаления статистики игрока
        pass