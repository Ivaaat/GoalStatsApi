import asyncpg
from models import Season
class SeasonRepository:

    def __init__(self, db: asyncpg.Connection):
        self.db = db


    async def create(self, name: str):
        return await self.db.fetchval("""INSERT INTO stats.seasons (name) VALUES ($1) ON CONFLICT (name) DO NOTHING RETURNING id""", name)


    async def get_all(self):
        seasons = await self.db.fetch("""SELECT name, id FROM stats.seasons x
                                        ORDER BY x.name DESC""")
        return [dict(season) for season in seasons]


    async def get(self, season_id: int):
        return await self.db.fetchrow("""SELECT id, name FROM stats.seasons
                                        where id = $1 
                                        ORDER BY name asc""", season_id)


    async def update(self, season: Season):
        return await self.db.fetchval('UPDATE stats.seasons SET name = $2 WHERE id = $1 RETURNING id', season.id, season.name)
        


    async def delete(self, season_id: int):
        return await self.db.fetchval('DELETE FROM stats.seasons WHERE id = $1 RETURNING id', season_id)