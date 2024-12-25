import asyncpg
from models import Team


class TeamRepository:
    def __init__(self, db: asyncpg.Connection):
        self.db = db
        self.pool: asyncpg.Pool


    async def create(self, team: Team):
        id_team = await self.db.fetchval("""SELECT id FROM stats.teams_info WHERE old_id = $1""", team.old_id)
        if id_team:
            team.id = id_team
            return None
        id_team_all = await self.db.fetchval("""INSERT INTO stats.teams (name) VALUES ($1) ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name RETURNING id""", team.name)
        id = await self.db.fetchval("""INSERT INTO stats.teams_info ("name", icon, old_id, team_id) 
                                    VALUES ($1,$2,$3,$4) RETURNING id""", 
                                    team.name,
                                    team.icon,
                                    team.old_id,
                                    id_team_all)
        team.id = id
        return id


    async def get_all(self, championship_id):
        Teams = await self.db.fetch("""select name, id from stats.teams_info 
                                    where champ_id = $1
                                    order by name asc""", championship_id)
        return [dict(Team)for Team in Teams]



    async def search(self, query: str):
        teams = await self.db.fetch(""" select
                                            x.team_name as name ,
                                            sum(ci.priority) as priority
                                        from
                                            stats.v_seas_champs_teams x
                                        join stats.champs_info ci on
                                            ci.id = x.champ_id
                                        where
                                            x.team_name ilike $1
                                        group by
                                            x.team_name
                                        order by
                                            priority desc,
                                            x.team_name desc
                                        limit 10""", '{}%'.format(query))
        return [team.get('name') for team in teams] 



    async def get(self, team_id: int):
        async with self.pool.acquire() as connection:
            stat = await connection.fetchrow('''SELECT * FROM stats.get_stat($1);''', team_id)
        return dict(stat)
    
    
    async def get_players(self, team_id: int):
        async with self.pool.acquire() as connection:
            players = await connection.fetchrow('''select
                                                JSONB_OBJECT_AGG(ps.id,
                                                ps.name) as players
                                            from
                                                stats.players_stats ps
                                            where
                                                ps.teams_id = $1''', team_id)
        return dict(players)



    async def update(self, team_id: int, data: dict):
        # Логика обновления клуба
        pass

    async def delete(self, team_id: int):
        # Логика удаления клуба
        pass