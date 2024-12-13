import psycopg2
from googletrans import Translator

from psycopg2 import sql
from abc import ABC, abstractmethod
import re
import asyncpg
import asyncio
from asyncio import Semaphore
import aiofiles
import aiohttp
import ssl
import json
import datetime
import multiprocessing
import os
import asyncio
import time
import random
import requests
import os
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict
import json
from dotenv import load_dotenv


load_dotenv()
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

def generate_date_range(end_date_str):
    # Преобразование строковой даты в объект datetime
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    start_date = datetime.now()

    # Инициализация списка для хранения дат
    date_range = []

    # Генерация дат от текущей до конечной
    current_date = start_date
    while current_date <= end_date:
        date_range.append(current_date.strftime('%Y-%m-%d'))  # Добавление даты в нужном формате
        current_date += timedelta(days=1)  # Переход к следующему дню

    return date_range

class UpdateStrategy(ABC):
    @abstractmethod
    def update(self, db_handler, **kwargs):
        """Метод, который должен реализовываться в каждой стратегии для обновления данных."""
        pass

    async def get(date:str, semaphore:Semaphore):
        async with semaphore:
            async with aiohttp.ClientSession() as session:
                async with session.get('{}{}'.format(INITIAL_LINK, date)) as response:
                    if response.status:
                        result = await response.json()
                        if result.get('matches'):
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
                data = DateUpdateRange.update(date[:10], date[-10:])
            elif strategy == 'toDay':
                await DateUpdateToDay.update(date, semaphore)
            else:
                await  DateUpdateAll.update()
        except ValueError:
            return print('Неверный формат даты')


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
        dates = generate_date_range(date)
        await asyncio.gather(*[UpdateStrategy.get(date_up, semaphore) for date_up in dates])
        

        # today = datetime.today()
        # today_str = today.date()
        # date_update =  datetime.strptime(date, '%Y-%m-%d')
        # direction = 'next'
        # if today > date_update:
        #     direction = 'prev'
        # #data_today = sess.get('{}{}'.format(INITIAL_LINK, today_str)).json()
        #data_today = await UpdateStrategy.get(today_str)
        # date_fetch = data_today['nav'][direction]['date']
        # if data_today['matches']['football']:
        #     DateUpdateStrategy.data[str(today_str)] = data_today['matches']['football']
        # date_to =  datetime.strptime(date_fetch, '%Y-%m-%d')
        # conditions = date_to >= date_update if direction == 'prev' else date_to <= date_update
        # while conditions:
        #     #time.sleep(random.uniform(0.5, 2))
        #     try:
        #         #data = sess.get('{}{}'.format(INITIAL_LINK, date_fetch)).json()
        #         data = await UpdateStrategy.get(date_fetch)
        #         date_prev = date_fetch
        #     except Exception as e:
        #         return
        #     date_fetch = data['nav'][direction]['date']
        #     date_to =  datetime.strptime(date_fetch, '%Y-%m-%d')
        #     if data['matches']['football']:
        #         DateUpdateStrategy.data[date_prev] = data['matches']['football']
        #     conditions = date_to >= date_update if direction == 'prev' else date_to <= date_update


class DateUpdateRange(DateUpdateStrategy):
    async def update(date: str):
        pass



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
        translator = Translator()
        name = data.get('name_tournament') if data.get('name_tournament') else data.get('name')
        translator.translate(name.lower().replace(' ', '_'), dest='en')
        season = ['', '']
        async with aiohttp.ClientSession() as session:
            async with session.get('{}{}'.format(MAIN_LINK, data['link'])) as response:
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
            'alias': translator.translate(name).text.lower().replace(' ', '_')}


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
           self.data[match['id']] = {"old_id": match['id'],
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
            "date_id": DatePost.dates[date],
            "champ_id": ChampPost.champ[id_old_champ]['id'],
            "home_team_id": TeamPost.clubs[match['teams'][0]['id']]['id'],
            "away_team_id": TeamPost.clubs[match['teams'][1]['id']]['id']}


class StatPost(ABC):
    

    @classmethod
    @abstractmethod
    async def update(сls, data: str):
        pass


class DatePost(StatPost):
    dates: Dict[str, int] = {}


    @classmethod
    async def update(сls, data: str):
        async with aiohttp.ClientSession() as session:
            async with session.post(f'{DOMAIN}/api/matches/{data}', json=data) as response:
                response.raise_for_status()  # Проверка на ошибки HTTP
                DatePost.dates.update(await response.json())   # Предполагается, что ответ в формате JSON
        


class SeasonPost(StatPost):

    @classmethod
    async def update(сls, data: str):
        async with aiohttp.ClientSession() as session:
            await session.post(f'{DOMAIN}/api/seasons/', json = data)


class ChampPost(StatPost):
    champ: List[Dict] = {}

    @classmethod
    async def update(сls, data: str):
        async with aiohttp.ClientSession() as session:
            async with session.post(f'{DOMAIN}/api/championships/', json = data) as response:
                resp = await response.json()
                ChampPost.champ[resp['detail']['champ']['old_id']] = resp['detail']['champ']


class TeamPost(StatPost):
    clubs: List[Dict] = {}

    @classmethod
    async def update(сls, data: Dict):
        async with aiohttp.ClientSession() as session:
            async with session.post(f'{DOMAIN}/api/clubs/', json = data) as response:
                resp = await response.json()
                if resp['detail'].get('club'):
                    TeamPost.clubs[resp['detail']['club']['old_id']] = resp['detail']['club']


class MatchPost(StatPost):
    
    @classmethod
    async def update(сls, data: Dict):
        async with aiohttp.ClientSession() as session:
            async with session.put(f'{DOMAIN}/api/matches/', json = data) as response:
                resp = await response.json()
                if response.status == 404:
                    sess.post(f'{DOMAIN}/api/matches/', json = data)
                elif response.status == 422:
                    print()

class Updater:
    def __init__(self, data: Dict):
        self.data = data

    async def update(self):
        tasks = [DatePost.update(date_update) for date_update in list(self.data.keys())]
        await asyncio.gather(*tasks)
        for date, stat in self.data.items():
            for tournaments in stat['tournaments'].values():
                self.season, self.champ, self.team, self.matches = SeasonPrepare(), ChampPrepare(), TeamPrepare(), MatchPrepare() 
                await asyncio.gather(*[self.season.prepare(tournaments), self.champ.prepare(tournaments), self.team.prepare(tournaments['matches'])])
                tasks = []
                tasks.append(SeasonPost.update(self.season.data))
                tasks.append(ChampPost.update(self.champ.data))
                tasks.extend([TeamPost.update(team) for team in self.team.data.values()])
                await asyncio.gather(*tasks)
                await self.matches.prepare(tournaments['matches'], tournaments['id'], date)
                await asyncio.gather(*[MatchPost.update(match) for match in self.matches.data.values()])
            print("Update {}".format(date))
        

                
async def main():
    semaphore = asyncio.Semaphore(3)
    await DateUpdateStrategy.update(date = '2025-02-05', strategy = 'toDay', semaphore = semaphore)
    #await DateUpdateStrategy.update(date = '2024-12-30', strategy = 'day', semaphore = semaphore)
    updater = Updater(DateUpdateStrategy.data)
    await updater.update()

start = time.time()
asyncio.run(main())
print(time.time() - start)



