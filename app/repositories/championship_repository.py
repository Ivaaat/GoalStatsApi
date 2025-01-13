import asyncpg
from models import Championship

class ChampionshipRepository:
    def __init__(self, db: asyncpg.Connection):
        self.db = db

    async def create(self, championat: Championship):
        id_champ = await self.db.fetchval("""SELECT id FROM stats.champs_info WHERE old_id = $1""", championat.old_id)
        if id_champ:
            championat.id = id_champ
            return None
        championat.champ_id = await self.db.fetchval("""INSERT INTO stats.champs (name) VALUES ($1) ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name RETURNING id""", championat.name)
        championat.id = await self.db.fetchval("""INSERT INTO stats.champs_info ("name", priority, img, old_id, link, is_active, is_top, start_date, end_date, is_cup, country, alias, champ_id, season_id) 
                                    VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14) ON CONFLICT (old_id) DO NOTHING RETURNING id""", 
                                    championat.name,
                                    championat.priority,
                                    championat.img,
                                    championat.old_id,
                                    championat.link,
                                    championat.is_active,
                                    championat.is_top,
                                    championat.start_date,
                                    championat.end_date,
                                    championat.is_cup,
                                    championat.country,
                                    championat.alias,
                                    championat.champ_id,
                                    championat.season_id)
        return championat.id


    async def get_all(self, season_id):
        champs = await self.db.fetch("""SELECT id, name FROM stats.champs_info
                                        where season_id = $1 
                                        ORDER BY name asc""", season_id)
        return [dict(champ) for champ in champs]


    async def get(self, championship_id: int):
        return await self.db.fetchrow("""SELECT * FROM stats.champs_info
                                    where id = $1 
                                    ORDER BY name asc""", championship_id)


    async def update(self, championat: Championship):
        id = await self.db.fetchval("""UPDATE stats.champs_info 
                                        SET 
                                            name = $1,
                                            priority = $2,
                                            img = $3,
                                            old_id = $4,
                                            link = $5,
                                            is_active = $6,
                                            is_top = $7,
                                            start_date = $8,
                                            end_date = $9,
                                            is_cup = $10,
                                            country = $11,
                                            alias = $12,
                                            champ_id = $13,
                                            season_id = $14
                                        WHERE id = $15
                                        RETURNING id;""", 
                                    championat.name,
                                    championat.priority,
                                    championat.img,
                                    championat.old_id,
                                    championat.link,
                                    championat.is_active,
                                    championat.is_top,
                                    championat.start_date,
                                    championat.end_date,
                                    championat.is_cup,
                                    championat.country,
                                    championat.alias,
                                    championat.champ_id,
                                    championat.season_id,
                                    championat.id
                                    )
        return id


    async def delete(self, championship_id: int):
        return await self.db.fetchval('DELETE FROM stats.champs_info WHERE id = $1 RETURNING id', championship_id)