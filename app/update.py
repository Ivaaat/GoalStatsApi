from googletrans import Translator
from abc import ABC, abstractmethod
import re
import asyncpg
import asyncio
from asyncio import Semaphore
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
from dotenv import load_dotenv
import os
from config import get_ssl_context
from repositories import SeasonRepository, ChampionshipRepository, TeamRepository, MatchesRepository
from models import Championship, Team, Match

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

load_dotenv()
DB_USER= os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_HOST= os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
INITIAL_LINK= os.getenv('INITIAL_LINK')
MAIN_LINK = os.getenv('MAIN_LINK')
DOMAIN = os.getenv('DOMAIN')
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}
sess = requests.Session()
sess.headers.update(HEADERS)
MAX_RETRIES = 5
RETRY_DELAY = 30
SLEEP = 1

def generate_date_range(start_date = '', end_date_str = '2040-01-04'):
    if not start_date:
        start_date = datetime.now()
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    # Инициализация списка для хранения дат
    date_range = []
    current_date = start_date
    while current_date.date() <= end_date.date():
        date_range.append(current_date.strftime('%Y-%m-%d'))  # Добавление даты в нужном формате
        current_date += timedelta(days=1)  # Переход к следующему дню
    else:
        while current_date.date() >= end_date.date():
            date_range.append(current_date.strftime('%Y-%m-%d')) 
            current_date -= timedelta(days=1) 
    return date_range


class UpdateStrategy(ABC):
    @abstractmethod
    def update(self, db_handler, **kwargs):
        """Метод, который должен реализовываться в каждой стратегии для обновления данных."""
        pass

    async def get(date:str, semaphore:Semaphore):
        
        async with semaphore:
            async with aiohttp.ClientSession() as session:
                async with session.get('{}{}'.format(INITIAL_LINK, date), ssl=ssl_context) as response:
                    if response.status:
                        result = await response.json()
                        if result.get('matches'):
                            if result.get('matches').get('football'): 
                                DateUpdateStrategy.data[date] = result['matches']['football']


class DateUpdateStrategy(UpdateStrategy):
    data: Dict = {}

    @classmethod
    async def update(cls, date: str, strategy: str, semaphore:Semaphore):
        try:
            if strategy == 'day':
                datetime.strptime(date, '%Y-%m-%d')
                await DateUpdateDay.update(date)
            elif strategy == 'range':
                datetime.strptime(date[:10], '%Y-%m-%d')
                datetime.strptime(date[-10:], '%Y-%m-%d')
                await DateUpdateRange.update(date[:10], date[-10:], semaphore)
            elif strategy == 'toDay':
                await DateUpdateToDay.update(date, semaphore)
            else:
                await  DateUpdateAll.update()
        except ValueError as e:
            return print('Неверный формат даты {}'.format(e))


class DateUpdateAll(DateUpdateStrategy):
    date: str = '1990-01-20'

    @classmethod
    async def update(cls):
        date_start = sess.get('{}{}'.format(INITIAL_LINK, cls.date)).json()
        date_fetch = date_start['nav']['next']['date']
        flag = date_start['nav']['next']
        while flag:
            try:
                time.sleep(random.uniform(0.5, 2))
                try:
                    data = await cls.get(date_fetch)
                except Exception as e:
                    return
                flag = data['nav']['next']
                date_fetch = data['nav']['next']['date']
                if data['matches']['football']:
                    DateUpdateStrategy.data[cls.date] = data['matches']['football']
            except Exception as e:
                print(f'Error fetching HTML: {e}')


class DateUpdateDay(DateUpdateStrategy):

    @staticmethod
    async def update(date: str):
        try:
            data = sess.get('{}{}'.format(INITIAL_LINK, date)).json()
        except Exception as e:
            return
        if data['matches']['football']:
            DateUpdateStrategy.data[date] = data['matches']['football']


class DateUpdateToDay(DateUpdateStrategy):

    @staticmethod
    async def update(date: str, semaphore:Semaphore):
        dates = generate_date_range(end_date_str=date)
        await asyncio.gather(*[UpdateStrategy.get(date_up, semaphore) for date_up in dates])


class DateUpdateRange(DateUpdateStrategy):
    async def update(start_date: str, end_date_str: str, semaphore:Semaphore):
        dates = generate_date_range(start_date=start_date, end_date_str=end_date_str)
        await asyncio.gather(*[UpdateStrategy.get(date_up, semaphore) for date_up in dates])



class StatPrepare(ABC):
    
    @abstractmethod
    async def prepare(self, data: str):
        pass

class SeasonPrepare(StatPrepare):

    def __init__(self) -> None:
        self.data: dict = {}

    async def prepare(self, data: str):
        self.data = {'name': data['year']}
        


class TeamPrepare(StatPrepare):

    def __init__(self) -> None:
        self.data: dict = {}

    async def prepare(self, data: str):
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

    def __init__(self) -> None:
        self.data: dict = {} 
    

    async def prepare(self, data: str):
        #translator = Translator()
        name = data.get('name_tournament') if data.get('name_tournament') else data.get('name')
        #translator.translate(name.lower().replace(' ', '_'), dest='en')
        season = ['', '']
        async with aiohttp.ClientSession() as session:
            async with session.get('{}{}'.format(MAIN_LINK, data['link']), ssl=ssl_context) as response:
        #response = sess.get('{}{}'.format(MAIN_LINK, data['link']))
                if response.status == 200:
                    text = await response.text()
                    pattern = r"<script>document\.write\('<div>(.*)</div>'\)</script>"
                    match = re.search(pattern, text)
                    season = match.group(1).split('—')
        self.data = {
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
            'alias': None
        }


class MatchPrepare(StatPrepare):

    def __init__(self) -> None:
        self.data: dict = {}

    async def prepare(self, data: List[Dict], id_old_champ: str, date: str):
        for match in data:
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
                "date_id": DateUpdateDatabase.dates[date],
                "champ_id": ChampUpdateDatabase.champ[id_old_champ]['id'],
                "home_team_id": TeamUpdateDatabase.teams[match['teams'][0]['id']]['id'],
                "away_team_id": TeamUpdateDatabase.teams[match['teams'][1]['id']]['id']
            }


class StatUpdatePost(ABC):
    

    @classmethod
    @abstractmethod
    async def update(сls, data: str):
        pass


class DateUpdatePost(StatUpdatePost):
    dates: Dict[str, int] = {}


    @classmethod
    async def update(сls, data: str):
        async with aiohttp.ClientSession() as session:
            async with session.post(f'{DOMAIN}/api/matches/{data}', json=data) as response:
                response.raise_for_status()  # Проверка на ошибки HTTP
                DateUpdatePost.dates.update(await response.json())   # Предполагается, что ответ в формате JSON
        


class SeasonUpdatePost(StatUpdatePost):

    @classmethod
    async def update(сls, data: str):
        async with aiohttp.ClientSession() as session:
            await session.post(f'{DOMAIN}/api/seasons/', json = data)


class ChampUpdatePost(StatUpdatePost):
    champ: List[Dict] = {}

    @classmethod
    async def update(сls, data: str):
        async with aiohttp.ClientSession() as session:
            async with session.post(f'{DOMAIN}/api/championships/', json = data) as response:
                resp = await response.json()
                ChampUpdatePost.champ[resp['detail']['champ']['old_id']] = resp['detail']['champ']


class TeamUpdatePost(StatUpdatePost):
    teams: List[Dict] = {}

    @classmethod
    async def update(сls, data: Dict):
        async with aiohttp.ClientSession() as session:
            async with session.post(f'{DOMAIN}/api/teams/', json = data) as response:
                resp = await response.json()
                if resp['detail'].get('team'):
                    TeamUpdatePost.teams[resp['detail']['team']['old_id']] = resp['detail']['team']


class MatchUpdatePost(StatUpdatePost):
    
    @classmethod
    async def update(сls, data: Dict):
        async with aiohttp.ClientSession() as session:
            async with session.put(f'{DOMAIN}/api/matches/', json = data) as response:
                resp = await response.json()
                if response.status == 404:
                    sess.post(f'{DOMAIN}/api/matches/', json = data)
                elif response.status == 422:
                    pass


class StatUpdateDatabase(ABC):
    pool: asyncpg.Pool
    

    @classmethod
    @abstractmethod
    async def update(сls, data: str):
        pass


class DateUpdateDatabase(StatUpdateDatabase):
    dates: Dict[str, int] = {}


    @classmethod
    async def update(сls, data: str):
        async with сls.pool.acquire() as conn:
            rep = MatchesRepository(conn)
            id = await rep.create_date(data)
            if id:
                сls.dates.update({data:id})
        

class SeasonUpdateDatabase(StatUpdateDatabase):


    @classmethod
    async def update(сls, data: str):
        async with сls.pool.acquire() as conn:
            rep = SeasonRepository(conn)
            await rep.create(data['name'])


class ChampUpdateDatabase(StatUpdateDatabase):
    champ: List[Dict] = {}

    @classmethod
    async def update(сls, data: Dict):
        async with сls.pool.acquire() as conn:
            rep = ChampionshipRepository(conn)
            champ = Championship(**data)
            await rep.create(champ)
            сls.champ[champ.old_id] = dict(champ)


class TeamUpdateDatabase(StatUpdateDatabase):
    teams: List[Dict] = {}

    @classmethod
    async def update(сls, data: Dict):
        async with сls.pool.acquire() as conn:
            rep = TeamRepository(conn)
            team = Team(**data)
            await rep.create(team)
            сls.teams[team.old_id] = dict(team)


class MatchUpdateDatabase(StatUpdateDatabase):
    
    @classmethod
    async def update(сls, data: Dict):
        async with сls.pool.acquire() as conn:
            rep = MatchesRepository(conn)
            match = Match(**data)
            if not await rep.create(match):
                await rep.update(match)
                    

class Updater(ABC):

    @abstractmethod
    def __init__(self, data: Dict):
        self.data = data

    @abstractmethod
    async def update(self):
        pass

    async def prepare_data_for_tournaments(self, tournaments):
        # Создание экземпляров подготовителей
        self.season = SeasonPrepare()
        self.champ = ChampPrepare()
        self.team = TeamPrepare()
        self.matches = MatchPrepare()

        # Подготовка данных
        await asyncio.gather(
            *[self.season.prepare(tournament) for tournament in tournaments],
            *[self.champ.prepare(tournament) for tournament in tournaments],
            *[self.team.prepare(tournament['matches']) for tournament in tournaments]
        )
    

    async def update_tournaments_data(self, tournaments, date):
        tasks = [
            SeasonUpdatePost.update(self.season.data),
            ChampUpdatePost.update(self.champ.data),
            *[TeamUpdatePost.update(team) for team in self.team.data.values()]
        ]
        
        await asyncio.gather(*tasks)

        # Подготовка и обновление матчей
        for tournament in tournaments:
            await self.matches.prepare(tournament['matches'], tournament['id'], date)
            await asyncio.gather(*[MatchUpdatePost.update(match) for match in self.matches.data.values()])


class UpdaterDatabase(Updater):
    def __init__(self, data: Dict):
        self.data = data


    async def update(self):
        StatUpdateDatabase.pool = await asyncpg.create_pool(
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            host=DB_HOST, 
            port=DB_PORT,
            ssl=get_ssl_context()
        )
        tasks = [DateUpdateDatabase.update(date_update) for date_update in list(self.data.keys())]
        await asyncio.gather(*tasks)
        for date, stat in self.data.items():
            for tournaments in stat['tournaments'].values():
                self.season, self.champ, self.team, self.matches = SeasonPrepare(), ChampPrepare(), TeamPrepare(), MatchPrepare() 
                await asyncio.gather(*[self.season.prepare(tournaments), self.champ.prepare(tournaments), self.team.prepare(tournaments['matches'])])
                tasks = []
                tasks.append(SeasonUpdateDatabase.update(self.season.data))
                tasks.append(ChampUpdateDatabase.update(self.champ.data))
                tasks.extend([TeamUpdateDatabase.update(team) for team in self.team.data.values()])
                await asyncio.gather(*tasks)
                await self.matches.prepare(tournaments['matches'], tournaments['id'], date)
                await asyncio.gather(*[MatchUpdateDatabase.update(match) for match in self.matches.data.values()])
            print("Update {}".format(date))
        await StatUpdateDatabase.pool.close()
        

class UpdaterPost(Updater):
    def __init__(self, data: Dict):
        self.data = data

    async def update(self):
        tasks = [DateUpdatePost.update(date_update) for date_update in list(self.data.keys())]
        await asyncio.gather(*tasks)
        for date, stat in self.data.items():
            for tournaments in stat['tournaments'].values():
                self.season, self.champ, self.team, self.matches = SeasonPrepare(), ChampPrepare(), TeamPrepare(), MatchPrepare() 
                await asyncio.gather(*[self.season.prepare(tournaments), self.champ.prepare(tournaments), self.team.prepare(tournaments['matches'])])
                tasks = []
                tasks.append(SeasonUpdatePost.update(self.season.data))
                tasks.append(ChampUpdatePost.update(self.champ.data))
                tasks.extend([TeamUpdatePost.update(team) for team in self.team.data.values()])
                await asyncio.gather(*tasks)
                await self.matches.prepare(tournaments['matches'], tournaments['id'], date)
                await asyncio.gather(*[MatchUpdatePost.update(match) for match in self.matches.data.values()])
            print("Update {}".format(date))
        

class UpdateFactory:

    def __init__(self, strategy, date: str) -> None:
        self.strategy = strategy
        self.updater: Union[UpdaterPost, UpdaterDatabase]
        self.date = date
        

    async def run(self):
        semaphore = asyncio.Semaphore(3)
        await DateUpdateStrategy.update(date = self.date, strategy = 'toDay', semaphore = semaphore)
        #await DateUpdateStrategy.update(date = '2025-02-17-2026-01-01', strategy = 'range', semaphore = semaphore)
        if self.strategy == 'post':
            updater = UpdaterPost(DateUpdateStrategy.data)
        elif self.strategy == 'db':
             updater = UpdaterDatabase(DateUpdateStrategy.data)
        if updater:
            await updater.update()
            return 'Update {}'.format(list(updater.data.keys()))



if __name__ == '__main__':
    start = time.time()
    updater = UpdateFactory('db', '2025-01-20')
    asyncio.run(updater.run())
    print(time.time() - start)



