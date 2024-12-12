import asyncpg

class SeasonRepository:

    def __init__(self, db: asyncpg.Connection):
        self.db = db


    async def create(self, name: str):
        id = await self.db.fetchval("""INSERT INTO stats.seasons (name) VALUES ($1) ON CONFLICT (name) DO NOTHING RETURNING id;""", name)
        return id


    async def get_all(self):
        seasons = await self.db.fetch("""SELECT name, id FROM stats.seasons x
                                    where name like '%/%'
                                    ORDER BY x.name DESC""")
        return [dict(season) for season in seasons]


    async def get(self, season_id: int):
        data = await self.db.fetch("""SELECT c.id, c.name FROM stats.seasons_champs s
                                join stats.champs_info c on c.id = s.league_id 
                                where s.season_id = $1 and c.is_top 
                                ORDER BY c.name asc""", season_id)
        return data


    async def update(self, championship_id: int, data: dict):
        # Логика обновления чемпионата
        pass


    async def delete(self, championship_id: int):
        # Логика удаления чемпионата
        pass