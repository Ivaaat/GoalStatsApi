from typing import List, Dict
from abc import ABC, abstractmethod
import asyncpg
from repositories import SeasonRepository, ChampionshipRepository, TeamRepository, MatchesRepository
from models import Championship, Team, Match


class UpdateDatabase(ABC):
    pool: asyncpg.Pool

    def __init__(self, data) -> None:
        self.data = data
        self.update_match = {}
    

    @abstractmethod
    async def update(self, data: str):
        pass


class DateUpdateDatabase(UpdateDatabase):


    async def update(self, conn, **kwargs):
            rep = MatchesRepository(conn)
            for date in self.data.keys():
                id = await rep.create_date(date)
                if id:
                    self.update_match[date] = id
        

class SeasonUpdateDatabase(UpdateDatabase):


    async def update(self, conn):
        
            rep = SeasonRepository(conn)
            for season in self.data.values():
                id = await rep.create(season['name'])
                if not id:
                    id = await rep.get_name(season['name'])
                self.update_match[season['name']] = id


class ChampUpdateDatabase(UpdateDatabase):

    async def update(self, conn, **kwargs):

            rep = ChampionshipRepository(conn)
            for data in self.data.values():
                champ = Championship(**data)
                champ.season_id = kwargs['season'][champ.season_id]
                id = await rep.create(champ)
                if not id:
                    await rep.update(champ)
                self.update_match[champ.old_id] = champ.id


class TeamUpdateDatabase(UpdateDatabase):

    async def update(self, conn, **kwargs):
            rep = TeamRepository(conn)
            for data in self.data.values():
                team = Team(**data)
                team.champ_id= kwargs['champ'][team.champ_id]
                id = await rep.create(team)
                if not id:
                     await rep.update(team)
                self.update_match[team.old_id] = team.id
                


class MatchUpdateDatabase(UpdateDatabase):
    
    async def update(self, conn, **kwargs):
            rep = MatchesRepository(conn)
            for data in self.data.values():
                match = Match(**data)
                match.date_id = kwargs['date'][match.date_id]
                match.champ_id = kwargs['champ'][match.champ_id]
                match.home_team_id = kwargs['team'][match.home_team_id]
                match.away_team_id = kwargs['team'][match.away_team_id]
                if not await rep.create(match):
                    await rep.update(match)