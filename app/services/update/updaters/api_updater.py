from abc import ABC, abstractmethod
from typing import List, Dict
import aiohttp
from config import config



class UpdateApi(ABC):
    
    def __init__(self, data) -> None:
        self.data = data
        self.update_match = {}

    @abstractmethod
    async def update(self, data: str):
        pass


class DateUpdateApi(UpdateApi):


    async def update(self, data: str):
        async with aiohttp.ClientSession() as session:
            for date in self.data.keys():
                async with session.post(f'{config.setting.domain}/api/matches/{data}', json=date) as response:
                    id = await response.json()
                    if id:
                        self.update_match[date] = id
        


class SeasonUpdateApi(UpdateApi):

    async def update(self, data: str):
        async with aiohttp.ClientSession() as session:
            await session.post(f'{config.setting.domain}/api/seasons/', json = data)


class ChampUpdateApi(UpdateApi):

    async def update(self, data: str):
        async with aiohttp.ClientSession() as session:
            async with session.post(f'{config.setting.domain}/api/championships/', json = data) as response:
                resp = await response.json()
                ChampUpdateApi.champ[resp['detail']['champ']['old_id']] = resp['detail']['champ']


class TeamUpdateApi(UpdateApi):

    async def update(self, data: Dict):
        async with aiohttp.ClientSession() as session:
            async with session.post(f'{config.setting.domain}/api/teams/', json = data) as response:
                resp = await response.json()
                if resp['detail'].get('team'):
                    TeamUpdateApi.teams[resp['detail']['team']['old_id']] = resp['detail']['team']


class MatchUpdateApi(UpdateApi):
    
    async def update(self, data: Dict):
        async with aiohttp.ClientSession() as session:
            async with session.put(f'{config.setting.domain}/api/matches/', json = data) as response:
                resp = await response.json()
                if response.status == 404:
                    await session.post(f'{config.setting.domain}/api/matches/', json = data)
                elif response.status == 422:
                    pass
