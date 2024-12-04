import asyncpg
from repositories import ClubRepository, ChampionshipRepository, SeasonRepository, PlayerRepository
from typing import Union

class StatisticsRepository:
    def __init__(self, db: asyncpg.Connection):
        self.db = db

    async def create(self, data: dict):
        # Логика создания статистики
        pass

    async def get_club(self, club_name):
        data = await self.db.fetch("""
                                    select
                                    s.name as season_name,
                                    JSONB_OBJECT_AGG(ci.name,
                                    ti.id) as champ_name_id_team
                                from
                                    stats.seas_champ_teams sct
                                join stats.seasons s on
                                    s.id = sct.id_season
                                join stats.champs_info ci on
                                    ci.id = sct.id_champ
                                join stats.teams_info ti on
                                    ti.id = sct.id_teams
                                join stats.teams t2 on
                                    t2.id = ti.team_id
                                where
                                    t2.name = $1
                                group by
                                    s.name
                                order by
                                    s.name desc""", club_name)
        return data

    async def update(self, player_id: int, data: dict):
        # Логика обновления статистики игрока
        pass

    async def delete(self, player_id: int):
        # Логика удаления статистики игрока
        pass