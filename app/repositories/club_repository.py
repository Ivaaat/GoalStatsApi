import asyncpg

class ClubRepository:
    def __init__(self, db: asyncpg.Connection):
        self.db = db
        self.pool: asyncpg.Pool

    async def create(self, data: dict):
        # Логика создания клуба
        pass

    async def get_all(self, championship_id):
        clubs = await self.db.fetch("""select t.name, t.id from stats.champs_teams ct  
                                    join stats.teams_info t on t.id = ct.team_id 
                                    where ct.champ_id = $1
                                    order by t.name asc""", championship_id)
        return [dict(club)for club in clubs]


    async def _get(self, club_id: int):
       club_stat = await self.db.fetch("""select * from stats.teams  
                                       join 
                                    where id = $1
                                       """, club_id)
       return [dict(club)for club in club_stat]


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



       # return [ for club in clubs] 
    

    async def get(self, club_id: int):
        async with self.pool.acquire() as connection:
            stat = await connection.fetchrow('''select
                                            t.name,
                                            COUNT(m.score) as games,
                                            SUM(case when m.total_home > m.total_away and m.home_team_id = t.id then 1 else 0 end) +
                                                                                SUM(case when m.total_away > m.total_home and m.away_team_id = t.id then 1 else 0 end) as wins,
                                            SUM(case when m.total_home = m.total_away then 1 else 0 end) as draws,
                                            SUM(case when m.total_home < m.total_away and m.home_team_id = t.id then 1 else 0 end) +
                                                                                SUM(case when m.total_away < m.total_home and m.away_team_id = t.id then 1 else 0 end) as losses,
                                            SUM(case when m.home_team_id = t.id then m.total_home else 0 end) +
                                                                                SUM(case when m.away_team_id = t.id then m.total_away else 0 end) as goals_for,
                                            SUM(case when m.away_team_id = t.id then m.total_home else 0 end) +
                                                                                SUM(case when m.home_team_id = t.id then m.total_away else 0 end) as goals_against,
                                            SUM(case when m.home_team_id = t.id then m.total_home - m.total_away else 0 end) +
                                                                                SUM(case when m.away_team_id = t.id then m.total_away - m.total_home else 0 end) as goal_difference,
                                            SUM(case when (m.total_home > m.total_away and m.home_team_id = t.id) or (m.total_away > m.total_home and m.away_team_id = t.id) then 3 else 0 end) +
                                                                                SUM(case when m.total_home = m.total_away then 1 else 0 end) as points,
                                            JSONB_OBJECT_AGG(m.id, jsonb_build_object('tour', 'Тур ' || m.tour, 'date', d.date, 'match', SPLIT_PART(m.link_title,
                                            ',', 1) || '  ' || (case when m.total_home is not null then m.total_home::text || ' : ' || m.total_away::text else '' end))) as calendar ,                           
                                            ci."name" as champ_name,
                                            s.name as season_name
                                        from
                                            stats.matches m
                                        join
                                                                                stats.teams_info t on
                                            (t.id = m.home_team_id
                                                or t.id = m.away_team_id)
                                        join stats.seas_champ_teams sct on
                                            t.id = sct.id_teams
                                        join stats.champs_info ci on
                                            sct.id_champ = ci.id
                                        join stats.seasons s on
                                            sct.id_season = s.id
                                        join stats.dates d on
                                            m.date_id = d.id
                                        where
                                            t.id = $1
                                        group by
                                            t.name,
                                            ci."name",
                                            s.name''', club_id)
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