import asyncpg
from models import Match
from datetime import datetime
import json


class MatchesRepository:
    def __init__(self, db: asyncpg.Connection):
        self.db = db


    async def create(self, match: Match):
        try:
            id = await self.db.fetchval("""INSERT INTO stats.matches (old_id,section,link,time,groups,flags,result,status,pub_date,score,total_home,total_away,roundforltandmc,tour,periods,time_str,link_title,date_id,champ_id,home_team_id,away_team_id) 
                                        VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,$16,$17,$18,$19,$20,$21) ON CONFLICT (old_id) DO NOTHING RETURNING id""", 
                                        match.old_id,
                                        match.section,
                                        match.link,
                                        match.time,
                                        json.dumps(match.groups, ensure_ascii=False) if match.groups else '{}',
                                        json.dumps(match.flags, ensure_ascii=False) if match.flags else '{}',
                                        json.dumps(match.result, ensure_ascii=False) if match.result else '{}',
                                        json.dumps(match.status, ensure_ascii=False) if match.status else '{}',
                                        datetime.fromtimestamp(match.pub_date),
                                        json.dumps(match.score, ensure_ascii=False) if match.score else '{}',
                                        match.total_home,
                                        match.total_away,
                                        match.roundforltandmc,
                                        match.tour,
                                        json.dumps(match.periods, ensure_ascii=False) if match.periods else '{}',
                                        match.time_str,
                                        match.link_title,
                                        match.date_id,
                                        match.champ_id,
                                        match.home_team_id,
                                        match.away_team_id)
            return id
        except asyncpg.UniqueViolationError:
            return await self.update(match)
    

    async def create_date(self, date:str):
        id = await self.db.fetchval("""INSERT INTO stats.dates (date) VALUES ($1)  ON CONFLICT (date) DO UPDATE SET date = $1 RETURNING id""", date)
        return id


    async def get(self, match_id: int):
        data = await self.db.fetch("""SELECT * FROM stats.matches
                                where id = $1 """, match_id)
        return data


    async def update(self, match: Match):
        id = await self.db.fetchval("""UPDATE stats.matches 
                                        SET section = $2, 
                                            link = $3, 
                                            time = $4, 
                                            groups = $5, 
                                            flags = $6, 
                                            result = $7, 
                                            status = $8, 
                                            pub_date = $9, 
                                            score = $10, 
                                            total_home = $11, 
                                            total_away = $12, 
                                            roundforltandmc = $13, 
                                            tour = $14, 
                                            periods = $15, 
                                            time_str = $16, 
                                            link_title = $17, 
                                            date_id = $18, 
                                            champ_id = $19, 
                                            home_team_id = $20, 
                                            away_team_id = $21 
                                        WHERE old_id = $1 RETURNING id""", 
                                    match.old_id,
                                    match.section,
                                    match.link,
                                    match.time,
                                    json.dumps(match.groups, ensure_ascii=False) if match.groups else '{}',
                                    json.dumps(match.flags, ensure_ascii=False) if match.flags else '{}',
                                    json.dumps(match.result, ensure_ascii=False) if match.result else '{}',
                                    json.dumps(match.status, ensure_ascii=False) if match.status else '{}',
                                    datetime.fromtimestamp(match.pub_date),
                                    json.dumps(match.score, ensure_ascii=False) if match.score else '{}',
                                    match.total_home,
                                    match.total_away,
                                    match.roundforltandmc,
                                    match.tour,
                                    json.dumps(match.periods, ensure_ascii=False) if match.periods else '{}',
                                    match.time_str,
                                    match.link_title,
                                    match.date_id,
                                    match.champ_id,
                                    match.home_team_id,
                                    match.away_team_id)
        return id


    async def delete(self, match_id: int):
        return await self.db.fetchval('DELETE FROM stats.matches WHERE id = $1 RETURNING id', match_id)