import psycopg2
from googletrans import Translator

from psycopg2 import sql
from abc import ABC, abstractmethod
import re
import asyncpg
import asyncio
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
from datetime import datetime
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


class UpdateStrategy(ABC):
    @abstractmethod
    def update(self, db_handler, **kwargs):
        """Метод, который должен реализовываться в каждой стратегии для обновления данных."""
        pass

class DateUpdateStrategy(UpdateStrategy):
    data: Dict = {}

    @classmethod
    def update(cls, date: str, strategy: str):
        try:
            if strategy == 'day':
                date_update =  datetime.strptime(date, '%Y-%m-%d')
                data = DateUpdateDay.update(date)
            elif strategy == 'range':
                date_start = datetime.strptime(date[:10], '%Y-%m-%d')
                date_end = datetime.strptime(date[-10:], '%Y-%m-%d')
                data = DateUpdateRange.update(date[:10], date[-10:])
            elif strategy == 'toDay':
                
                data = DateUpdateToDay.update(date)
            else:
                data = DateUpdateAll.update()
        except ValueError:
            return print('Неверный формат даты')
        return data


class DateUpdateAll(DateUpdateStrategy):
    date: str = '1990-01-20'

    @classmethod
    def update(cls):
        date_start = sess.get('{}{}'.format(INITIAL_LINK, cls.date)).json()
        date_fetch = date_start['nav']['next']['date']
        flag = date_start['nav']['next']
        while flag:
            try:
                time.sleep(random.uniform(0.5, 2))
                try:
                    data = sess.get('{}{}'.format(INITIAL_LINK, date_fetch)).json()
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
    def update(date: str):
        try:
            data = sess.get('{}{}'.format(INITIAL_LINK, date)).json()
        except Exception as e:
            return
        if data['matches']['football']:
            DateUpdateStrategy.data[date] = data['matches']['football']


class DateUpdateToDay(DateUpdateStrategy):

    @staticmethod
    def update(date: str):
        today = datetime.today()
        today_str = today.date()
        date_update =  datetime.strptime(date, '%Y-%m-%d')
        direction = 'next'
        if today > date_update:
            direction = 'prev'
        data_today = sess.get('{}{}'.format(INITIAL_LINK, today_str)).json()
        date_fetch = data_today['nav'][direction]['date']
        if data_today['matches']['football']:
            DateUpdateStrategy.data[str(today_str)] = data_today['matches']['football']
        date_to =  datetime.strptime(date_fetch, '%Y-%m-%d')
        conditions = date_to >= date_update if direction == 'prev' else date_to <= date_update
        while conditions:
            #time.sleep(random.uniform(0.5, 2))
            try:
                data = sess.get('{}{}'.format(INITIAL_LINK, date_fetch)).json()
            except Exception as e:
                return
            date_fetch = data['nav'][direction]['date']
            date_to =  datetime.strptime(date_fetch, '%Y-%m-%d')
            if data['matches']['football']:
                DateUpdateStrategy.data[date_fetch] = data['matches']['football']
            conditions = date_to >= date_update if direction == 'prev' else date_to <= date_update


class DateUpdateRange(DateUpdateStrategy):
    def update(date: str):
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
        translator.translate(data['name_tournament'].lower().replace(' ', '_'), dest='en')
        season = ['', '']
        async with aiohttp.ClientSession() as session:
            async with session.get('{}{}'.format(MAIN_LINK, data['link'])) as response:
        #response = sess.get('{}{}'.format(MAIN_LINK, data['link']))
                if response.status_code == 200:
                    text = await response.text()
                    pattern = r"<script>document\.write\('<div>(.*)</div>'\)</script>"
                    match = re.search(pattern, text)
                    season = match.group(1).split('—')
        self.data = {
            'name': data['name_tournament'],
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
            'alias': translator.translate(data['name_tournament']).text.lower().replace(' ', '_')}


class MatchPrepare(StatPrepare):

    def __init__(self) -> None:
        self.data: dict = {}

    def prepare(self, data: List[Dict], id_old_champ: str, date: str):
        for match in data:
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
            "total_home": match.get("total_home"),
            "total_away": match.get("total_away"),
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
                DatePost.dates.update(response.json())   # Предполагается, что ответ в формате JSON
        #response =  sess.post(f'http://127.0.0.1:8000/api/matches/{data}').json()
        


class SeasonPost(StatPost):

    @classmethod
    def update(сls, data: str):
        sess.post('{DOMAIN}/api/seasons/', json = data)
        

class TeamPost(StatPost):
    clubs: List[Dict] = {}

    @classmethod
    def update(сls, data: str):
        for team in data.values():
            response = sess.post('{DOMAIN}/api/clubs/', json = team).json()
            if response['detail'].get('club'):
                TeamPost.clubs[response['detail']['club']['old_id']] = response['detail']['club']


class ChampPost(StatPost):
    champ: List[Dict] = {}

    @classmethod
    def update(сls, data: str):
        response = sess.post(f'{DOMAIN}/api/championships/', json = data).json()
        response['detail']['champ']
        ChampPost.champ[response['detail']['champ']['old_id']] = response['detail']['champ']
        
        
class MatchPost(StatPost):
    
    @classmethod
    def update(сls, data: Dict):
        for match in data.values():
            response = sess.put('{DOMAIN}/api/matches/', json = match)
            if response.status_code == 404:
                sess.post(f'{DOMAIN}/api/matches/', json = match)

class Updater:
    def __init__(self, season: SeasonPrepare, champ: ChampPrepare, team: TeamPrepare, matches:MatchPrepare, data: Dict):
        self.season = season
        self.champ = champ
        self.team = team
        self.matches = matches
        self.data = data

    async def update(self):
        for date, stat in self.data.items():
            #season_stat, champ_stat, team_stat, match_stat = self.season.prepare(stat),self.champ.prepare(stat), self.team.prepare(stat), self.matches.prepare(stat)
            #season_stat = self.season.prepare(stat)
            await DatePost.update(date)
            for tournaments in stat['tournaments'].values():
                self.season.prepare(tournaments)
                #SeasonPost.update(self.season.data)
                self.champ.prepare(tournaments)
                ChampPost.update(self.champ.data)
                self.team.prepare(tournaments['matches'])
                TeamPost.update(self.team.data)
                self.matches.prepare(tournaments['matches'], tournaments['id'], date)
                MatchPost.update(self.matches.data)

                


#DateUpdateStrategy.update(date = '2024-09-10', strategy = 'toDay')
DateUpdateStrategy.update(date = '2024-12-07', strategy = 'day')

updater = Updater(SeasonPrepare(), ChampPrepare(), TeamPrepare(), MatchPrepare(), DateUpdateStrategy.data)

asyncio.run(updater.update())



