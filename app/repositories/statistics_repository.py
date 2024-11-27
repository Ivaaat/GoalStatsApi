import asyncpg
from repositories import ClubRepository, ChampionshipRepository, SeasonRepository, PlayerRepository
from typing import Union

class StatisticsRepository:
    def __init__(self, db: asyncpg.Connection):
        self.db = db

    async def create(self, data: dict):
        # Логика создания статистики
        pass

    async def get_club(self, club_id):
        data = await self.db.fetch("""select s.name as season_name, JSONB_OBJECT_AGG(c.id, c.name)  as champ_name,  JSONB_OBJECT_AGG(t.id, t.name) as team_name  from seas_champ_teams sct 
                                    join seasons s on s.id = sct.id_season 
                                    join champs_info  c on c.id = sct.id_champ 
                                    join teams_info  t  on t.id = sct.id_teams
                                    where t.id = $1
                                    group by s.name
                                    order by s.name desc""", club_id)
        return data

    async def update(self, player_id: int, data: dict):
        # Логика обновления статистики игрока
        pass

    async def delete(self, player_id: int):
        # Логика удаления статистики игрока
        pass