import asyncpg

class ChampionshipRepository:
    def __init__(self, db: asyncpg.Connection):
        self.db = db

    async def create(self, data: dict):
        # Логика создания чемпионата
        pass

    async def get_all(self, season_id):
        champs = await self.db.fetch("""SELECT c.id, c.name FROM stats.seasons_champs s
                                join stats.champs c on c.id = s.league_id 
                                where s.season_id = $1 and c.is_top 
                                ORDER BY c.name asc""", season_id)
        return [dict(champ)for champ in champs]

    async def get(self, championship_id: int):
        data = await self.db.fetch("""SELECT * FROM stats.champs
                                where id = $1 and c.is_top 
                                ORDER BY c.name asc""", championship_id)
        return data

    async def update(self, championship_id: int, data: dict):
        # Логика обновления чемпионата
        pass

    async def delete(self, championship_id: int):
        # Логика удаления чемпионата
        pass