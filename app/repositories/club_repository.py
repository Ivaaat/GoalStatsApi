import asyncpg

class ClubRepository:
    def __init__(self, db: asyncpg.Connection):
        self.db = db

    async def create(self, data: dict):
        # Логика создания клуба
        pass

    async def get_all(self, championship_id):
        clubs = await self.db.fetch("""select t.name, t.id from stats.champs_teams ct  
                                    join stats.teams_info t on t.id = ct.team_id 
                                    where ct.champ_id = $1
                                    order by t.name asc""", championship_id)
        return [dict(club)for club in clubs]


    async def get(self, club_id: int):
       club_stat = await self.db.fetch("""select * from stats.teams  
                                       join 
                                    where id = $1
                                       """, club_id)
       return [dict(club)for club in club_stat]


    async def search(self, query: str):
        clubs = await self.db.fetch("SELECT name FROM stats.teams WHERE name ILIKE $1 LIMIT 5", '{}%'.format(query))
        return [club.get('name') for club in clubs] 
    

    async def get_club(self, club_id: int):
        stat = await self.db.fetchrow('''SELECT
                                t.name,
                                COUNT(m.score) AS games,
                                SUM(CASE WHEN m.total_home > m.total_away AND m.home_team_id = t.id THEN 1 ELSE 0 END) +
                                SUM(CASE WHEN m.total_away > m.total_home AND m.away_team_id = t.id THEN 1 ELSE 0 END) AS wins,
                                SUM(CASE WHEN m.total_home = m.total_away THEN 1 ELSE 0 END) AS draws,
                                SUM(CASE WHEN m.total_home < m.total_away AND m.home_team_id = t.id THEN 1 ELSE 0 END) +
                                SUM(CASE WHEN m.total_away < m.total_home AND m.away_team_id = t.id THEN 1 ELSE 0 END) AS losses,
                                SUM(CASE WHEN m.home_team_id = t.id THEN m.total_home ELSE 0 END) +
                                SUM(CASE WHEN m.home_team_id = t.id THEN m.total_away ELSE 0 END) +
                                SUM(CASE WHEN m.home_team_id = t.id THEN m.total_home ELSE 0 END) AS goals_against,
                                SUM(CASE WHEN (m.total_home > m.total_away AND m.home_team_id = t.id) OR (m.total_away > m.total_home AND m.total_away = t.id) THEN 3 ELSE 0 END) +
                                SUM(CASE WHEN m.total_home = m.total_away THEN 1 ELSE 0 END) AS points,
                                SUM(CASE WHEN m.home_team_id = t.id THEN m.total_home - m.total_away ELSE 0 END) +
                                SUM(CASE WHEN m.away_team_id = t.id THEN m.total_away - m.total_home ELSE 0 END) AS goal_difference
                                FROM 
                                    stats.teams_info t
                                JOIN
                                    stats.matches m ON (t.id = m.home_team_id OR t.id = m.away_team_id)
                                where t.id = $1
                                GROUP BY
                                    t.name''', club_id)
        return dict(stat)


    async def update(self, club_id: int, data: dict):
        # Логика обновления клуба
        pass

    async def delete(self, club_id: int):
        # Логика удаления клуба
        pass