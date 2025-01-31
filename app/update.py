import sys
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
from googletrans import Translator
from abc import ABC, abstractmethod
import re
import asyncpg
import asyncio
import aiohttp
import ssl
import json
import datetime
import os
import asyncio
import time
import random
import requests
import os
from datetime import datetime, timedelta
from typing import List, Dict
import json
from typing import Union
import os
from repositories import SeasonRepository, ChampionshipRepository, TeamRepository, MatchesRepository
from models import Championship, Team, Match
from config import config
from db.database import get_pool

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}
sess = requests.Session()
sess.headers.update(HEADERS)
MAX_RETRIES = 5
RETRY_DELAY = 30
SLEEP = 1
SEMAPHORE = asyncio.Semaphore(3)


class DateGenerator(ABC):

    def __init__(self, date: str):
        self.date = date
        self.dates: List[str] = []

    @abstractmethod
    def create_date(self):
        pass

    def _generate_date_range(self, start_date = '', end_date_str = '2040-01-04'):
        if not start_date:
            start_date = datetime.now()
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        start_date = start_date.date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        current_date = start_date
        while current_date <= end_date:
            self.dates.append(current_date.strftime('%Y-%m-%d'))  # Добавление даты в нужном формате
            current_date += timedelta(days=1)  # Переход к следующему дню
        else:
            while start_date >= end_date:
                self.dates.append(start_date.strftime('%Y-%m-%d')) 
                start_date -= timedelta(days=1) 


class SingleDateGenerator(DateGenerator):

    
    async def create_date(self) -> List[str]:
        self.dates.append(self.date)
    

class UntilDateGenerator(DateGenerator):

  
    async def create_date(self) -> List[str]:
        self._generate_date_range(end_date_str=self.date)


class DateRangeGenerator(DateGenerator):


    def __init__(self, start_date: str, end_date_str: str = '1990-01-01'):
        self.start_date = start_date
        self.end_date_str = end_date_str
        self.dates = []


    async def create_date(self) -> List[str]:
        return self._generate_date_range(start_date= self.start_date, end_date_str=self.end_date_str)


class DataGeneratorFactory:
    

    @staticmethod
    def create_generator(date: str, strategy: str):
        try:
            if strategy == 'day':
                datetime.strptime(date, '%Y-%m-%d')
                return SingleDateGenerator(date)
            elif strategy == 'range':
                datetime.strptime(date[:10], '%Y-%m-%d')
                datetime.strptime(date[-10:], '%Y-%m-%d')
                return DateRangeGenerator(date[:10], date[-10:])
            elif strategy == 'toDay':
                datetime.strptime(date, '%Y-%m-%d')
                return UntilDateGenerator(date)
        except ValueError as e:
            print('Неверный формат даты {}'.format(e))
            sys.exit()
        




class Collector(ABC):

    def __init__(self, date_genarator: DateGenerator):
        self.data: Dict[str, Union[str, List[str]]] = {}
        self.dates = date_genarator.dates

    
    @abstractmethod
    async def collect(self):
        pass


    async def _collect_date(self, date: str):
        async with SEMAPHORE:
            async with aiohttp.ClientSession() as session:
                async with session.get('{}{}'.format(config.setting.initial_link, date), ssl=ssl_context) as response:
                    if response.status:
                        result = await response.json()
                        if result.get('matches'):
                            if result.get('matches').get('football'): 
                                self.data[date] = result['matches']['football']
                                return result


class DateCollector(Collector):
     
     async def collect(self):
        await self._collect_date(self.dates[0])
    

class RangeCollector(Collector):
     
     async def collect(self):
        asyncio.gather(*[self._collect_date(date) for date in self.dates])
        

class UntilCollector(Collector):
     
     async def collect(self):
        date_start = self.dates[0]
        if self.dates[0] > self.dates[-1]:
            direction = 'prev'         
        else:
            direction = 'next'   
        while date_start in self.dates:
            try:
                data = await self._collect_date(date_start)
                date_start = data['nav'][direction]['date']
            except TypeError as e:
                return print(f'Error fetching HTML: {e}')
                
         


    
class CollectorFactory:

    @staticmethod
    def create_collector(date_genarator: Union[SingleDateGenerator,DateRangeGenerator, UntilDateGenerator]):
        if isinstance(date_genarator, SingleDateGenerator):
            return DateCollector(date_genarator)
        elif isinstance(date_genarator, DateRangeGenerator):
            return RangeCollector(date_genarator)
        elif isinstance(date_genarator, UntilDateGenerator):
            return UntilCollector(date_genarator)
        
        


class StatPrepare(ABC):

    def __init__(self) -> None:
        self.data: dict = {}
    
    @abstractmethod
    async def prepare(self, data: str):
        pass

class SeasonPrepare(StatPrepare):

    

    def prepare(self, data: str):
        self.data[data['year']] = {'name': data['year']}
        


class TeamPrepare(StatPrepare):

    

    def prepare(self, data: str):
        for teams in data:
            team1 = teams['teams'][0]
            self.data[team1['name']] = {'name':team1['name'],
                                        'icon':team1['icon'],
                                        'old_id':team1['id']}
            team2 = teams['teams'][1]
            self.data[team2['name']] = {'name':team2['name'],
                                        'icon':team2['icon'],
                                        'old_id':team2['id']}
            

class ChampPrepare(StatPrepare):

    

    def prepare(self, data: str):
        #translator = Translator()
        name = data.get('name_tournament') if data.get('name_tournament') else data.get('name')
        #translator.translate(name.lower().replace(' ', '_'), dest='en')
        season = ['', '']
        #async with aiohttp.ClientSession() as session:
            #async with session.get('{}{}'.format(config.setting.main_link, data['link']), ssl=ssl_context) as response:
        response = sess.get('{}{}'.format(config.setting.main_link, data['link']))
        if response.status_code == 200:
            text = response.text
            pattern = r"<script>document\.write\('<div>(.*)</div>'\)</script>"
            match = re.search(pattern, text)
            season = match.group(1).split('—')
        self.data[name] = {
            'name': name,
            'country': None,
            'priority': data['priority'],
            'img': data['img'],
            'old_id': data['id'],
            'link': data['link'],
            'is_active': data['is_active'],
            'is_top': data['is_top'],
            'start_date': season[0],
            'end_date': season[1],
            'is_cup': None,
            #'alias': translator.translate(name).text.lower().replace(' ', '_')}
            'alias': None,
            'season_id': data['year']
        }


class MatchPrepare(StatPrepare):


    def prepare(self, date: str, champ_id: int, matches: List[Dict]):
        for match in matches:
           score = match.get('score')
           totalHome = totalAway = None
           if score:
               totalHome = score.get('totalHome', None)
               totalAway = score.get('totalAway', None)
           self.data[match['id']] = {
               "old_id": match['id'],
                "section": match["section"],
                "link": match.get("link"),
                "time": match.get("time"),
                "groups": match.get("group"),
                "flags":  match.get("flags"),
                "result":  match.get("result"),
                "status": match.get("status"),
                "pub_date":match.get("pub_date"),
                "score": match.get("score"),
                "total_home": totalHome,
                "total_away": totalAway,
                "roundforltandmc": match.get("roundforltandmc"),
                "tour": match.get("tour"),
                "periods": match.get("periods"),
                "time_str": match.get("time_str"),
                "link_title": match.get("link_title"),
                "date_id": date,
                "champ_id": champ_id,
                "home_team_id": match['teams'][0]['id'],
                "away_team_id": match['teams'][1]['id']
            }


class DataPreparer:

    def __init__(self, collector: Collector) -> None:
        self.season = SeasonPrepare()
        self.champ = ChampPrepare()
        self.team = TeamPrepare()
        self.matches = MatchPrepare()
        self.tournaments: List[Dict[str, Union[str, List[str]]]] = collector.data
    

    def _prepare(self, date_tournaments: List[Dict[str, Union[str, List[str]]]]):
        for date, tournaments in date_tournaments.items():
            for tournament in tournaments['tournaments'].values():
                self.season.prepare(tournament)
                self.champ.prepare(tournament) 
                self.team.prepare(tournament['matches'])
                self.matches.prepare(date, tournament['id'], tournament['matches'], )
        return (self.season.data, self.champ.data, self.team.data)

    def prepare(self):
        if len(self.tournaments) < multiprocessing.cpu_count():
                self._prepare(self.tournaments)
        else:
            with ThreadPoolExecutor() as executor:
                results = executor.map(self._prepare, self.tournaments)

class UpdateApi(ABC):
    

    @classmethod
    @abstractmethod
    async def update(сls, data: str):
        pass


class DateUpdateApi(UpdateApi):
    dates: Dict[str, int] = {}


    @classmethod
    async def update(сls, data: str):
        async with aiohttp.ClientSession() as session:
            async with session.post(f'{config.setting.domain}/api/matches/{data}', json=data) as response:
                response.raise_for_status()  # Проверка на ошибки HTTP
                DateUpdateApi.dates.update(await response.json())   # Предполагается, что ответ в формате JSON
        


class SeasonUpdateApi(UpdateApi):

    @classmethod
    async def update(сls, data: str):
        async with aiohttp.ClientSession() as session:
            await session.post(f'{config.setting.domain}/api/seasons/', json = data)


class ChampUpdateApi(UpdateApi):
    champ: List[Dict] = {}

    @classmethod
    async def update(сls, data: str):
        async with aiohttp.ClientSession() as session:
            async with session.post(f'{config.setting.domain}/api/championships/', json = data) as response:
                resp = await response.json()
                ChampUpdateApi.champ[resp['detail']['champ']['old_id']] = resp['detail']['champ']


class TeamUpdateApi(UpdateApi):
    teams: List[Dict] = {}

    @classmethod
    async def update(сls, data: Dict):
        async with aiohttp.ClientSession() as session:
            async with session.post(f'{config.setting.domain}/api/teams/', json = data) as response:
                resp = await response.json()
                if resp['detail'].get('team'):
                    TeamUpdateApi.teams[resp['detail']['team']['old_id']] = resp['detail']['team']


class MatchUpdateApi(UpdateApi):
    
    @classmethod
    async def update(сls, data: Dict):
        async with aiohttp.ClientSession() as session:
            async with session.put(f'{config.setting.domain}/api/matches/', json = data) as response:
                resp = await response.json()
                if response.status == 404:
                    sess.post(f'{config.setting.domain}/api/matches/', json = data)
                elif response.status == 422:
                    pass


class UpdateDatabase(ABC):
    pool: asyncpg.Pool

    def __init__(self, data) -> None:
        self.data = data
        self.update_match = {}
    

    @abstractmethod
    async def update(self, data: str):
        pass


class DateUpdateDatabase(UpdateDatabase):


    async def update(self, **kwargs):
        async with self.pool.acquire() as conn:
            rep = MatchesRepository(conn)
            for date in self.data.keys():
                id = await rep.create_date(date)
                if id:
                    self.update_match[date] = id
        

class SeasonUpdateDatabase(UpdateDatabase):


    async def update(self):
        async with self.pool.acquire() as conn:
            rep = SeasonRepository(conn)
            for season in self.data.values():
                id = await rep.create(season['name'])
                if not id:
                    id = await rep.get_name(season['name'])
                self.update_match[season['name']] = id


class ChampUpdateDatabase(UpdateDatabase):

    async def update(self, **kwargs):

        async with self.pool.acquire() as conn:
            rep = ChampionshipRepository(conn)
            for data in self.data.values():
                champ = Championship(**data)
                champ.season_id = kwargs['season'][champ.season_id]
                await rep.create(champ)
                self.update_match[champ.old_id] = champ.id


class TeamUpdateDatabase(UpdateDatabase):

    async def update(self):
        async with self.pool.acquire() as conn:
            rep = TeamRepository(conn)
            for data in self.data.values():
                team = Team(**data)
                await rep.create(team)
                self.update_match[team.old_id] = team.id


class MatchUpdateDatabase(UpdateDatabase):
    
    async def update(self, **kwargs):
        async with self.pool.acquire() as conn:
            rep = MatchesRepository(conn)
            for data in self.data.values():
                match = Match(**data)
                match.date_id = kwargs['date'][match.date_id]
                match.champ_id = kwargs['champ'][match.champ_id]
                match.home_team_id = kwargs['team'][match.home_team_id]
                match.away_team_id = kwargs['team'][match.away_team_id]
                if not await rep.create(match):
                    await rep.update(match)
                    

class Updater(ABC):

    date_update = Union[DateUpdateDatabase, DateUpdateApi]
    season_update = Union[SeasonUpdateDatabase, SeasonUpdateApi]
    champ_update = Union[ChampUpdateDatabase, ChampUpdateApi]
    team_update = Union[TeamUpdateDatabase, TeamUpdateApi]
    match_update = Union[MatchUpdateDatabase, MatchUpdateApi]


    @abstractmethod
    async def update(self):
        await self.date_update.update() 
        await self.season_update.update()
        await self.champ_update.update(season = self.season_update.update_match)
        await self.team_update.update()
        await self.match_update.update(date = self.date_update.update_match, 
                                       champ = self.champ_update.update_match, 
                                       team = self.team_update.update_match)
        print("Update {}".format(', '.join(self.date_update.data.keys())))

   

class DatabaseUpdaterService(Updater):

    def __init__(self, prepare: DataPreparer) -> None:
        self.date_update = DateUpdateDatabase(prepare.tournaments)
        self.season_update = SeasonUpdateDatabase(prepare.season.data)
        self.champ_update = ChampUpdateDatabase(prepare.champ.data)
        self.team_update = TeamUpdateDatabase(prepare.team.data)
        self.match_update = MatchUpdateDatabase(prepare.matches.data)


    async def update(self):
        UpdateDatabase.pool = await get_pool()
        await super().update()
        await UpdateDatabase.pool.close()
        

class APIUpdaterService(Updater):


    def __init__(self, prepare: DataPreparer) -> None:
        self.date_update = DateUpdateApi(prepare.tournaments)
        self.season_update = SeasonUpdateApi(prepare.season.data)
        self.champ_update = ChampUpdateApi(prepare.champ.data)
        self.team_update = TeamUpdateApi(prepare.team.data)
        self.match_update = MatchUpdateApi(prepare.matches.data)


    async def update(self):
        tasks = [DateUpdateApi.update(date_update) for date_update in list(self.data.keys())]
        await asyncio.gather(*tasks)
        for date, stat in self.data.items():
            for tournaments in stat['tournaments'].values():
                self.season, self.champ, self.team, self.matches = SeasonPrepare(), ChampPrepare(), TeamPrepare(), MatchPrepare() 
                await asyncio.gather(*[self.season.prepare(tournaments), self.champ.prepare(tournaments), self.team.prepare(tournaments['matches'])])
                tasks = []
                tasks.append(SeasonUpdateApi.update(self.season.data))
                tasks.append(ChampUpdateApi.update(self.champ.data))
                tasks.extend([TeamUpdateApi.update(team) for team in self.team.data.values()])
                await asyncio.gather(*tasks)
                await self.matches.prepare(tournaments['matches'], tournaments['id'], date)
                await asyncio.gather(*[MatchUpdateApi.update(match) for match in self.matches.data.values()])
            print("Update {}".format(date))
        

class UpdateFactory:

        
    @staticmethod
    def create_updater(prepare: DataPreparer, strategy: str):
        if strategy == 'api':
            updater = APIUpdaterService(prepare)
        elif strategy == 'db':
             updater = DatabaseUpdaterService(prepare)
        if updater:
            return updater

class UpdateFacade:

    def __init__(self, date: str, strategy_collect:str='toDay', strategy_update='db') -> None:
        self.date_generator = DataGeneratorFactory.create_generator(date, strategy_collect)
        self.collector = CollectorFactory.create_collector(self.date_generator)
        self.prepare = DataPreparer(self.collector)
        self.updater =  UpdateFactory.create_updater(self.prepare,strategy_update)

    async def run(self):
        await self.date_generator.create_date()
        await self.collector.collect()
        self.prepare.prepare()
        await self.updater.update()
        print()


if __name__ == '__main__':
    start = time.time()
    facade = UpdateFacade('2025-01-31')
    
    asyncio.run(facade.run())
    print(time.time() - start)



