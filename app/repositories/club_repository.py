import asyncpg
from models import Club


class ClubRepository:
    def __init__(self, db: asyncpg.Connection):
        self.db = db
        self.pool: asyncpg.Pool


    async def create(self, club: Club):
        id_team = await self.db.fetchval("""SELECT id FROM stats.teams_info WHERE old_id = $1""", club.old_id)
        if id_team:
            club.id = id_team
            return None
        id_team_all = await self.db.fetchval("""INSERT INTO stats.teams (name) VALUES ($1) ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name RETURNING id""", club.name)
        id = await self.db.fetchval("""INSERT INTO stats.teams_info ("name", icon, old_id, team_id) 
                                    VALUES ($1,$2,$3,$4) RETURNING id""", 
                                    club.name,
                                    club.icon,
                                    club.old_id,
                                    id_team_all)
        return id


    async def get_all(self, championship_id):
        clubs = await self.db.fetch("""select name, id from stats.teams_info 
                                    where champ_id = $1
                                    order by name asc""", championship_id)
        return [dict(club)for club in clubs]



    async def search(self, query: str):
        clubs = await self.db.fetch(""" select
                                            t.name,
                                            sum(ci.priority) as priority
                                        from
                                            stats.teams t
                                        join stats.teams_info ti on
                                            t.id = ti.team_id
                                        join stats.champs_teams ct on
                                            ti.id = ct.team_id
                                        join stats.champs_info ci on
                                            ct.champ_id = ci.id
                                        where
                                            t.name ilike $1
                                        group by
                                            t.name
                                        order by
                                            priority desc, t.name desc
                                        limit 10""", '{}%'.format(query))
        return [club.get('name') for club in clubs] 



    async def get(self, club_id: int):
        async with self.pool.acquire() as connection:
            stat = await connection.fetchrow('''SELECT * FROM stats.get_stat($1);''', club_id)
        return dict(stat)
    
    
    async def get_players(self, club_id: int):
        async with self.pool.acquire() as connection:
            players = await connection.fetchrow('''select
                                                JSONB_OBJECT_AGG(ps.id,
                                                ps.name) as players
                                            from
                                                stats.players_stats ps
                                            where
                                                ps.teams_id = $1''', club_id)
        return dict(players)



    async def update(self, club_id: int, data: dict):
        # Логика обновления клуба
        pass

    async def delete(self, club_id: int):
        # Логика удаления клуба
        pass