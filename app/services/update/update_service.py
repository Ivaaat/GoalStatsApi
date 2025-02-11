import sys
from abc import ABC, abstractmethod
import asyncio
import time
from typing import Union
from services.update.preparers import DataPreparer
from services.update.factories import CollectorFactory
from services.update.updaters import *
from db.database import get_pool
from config import config
import requests


class Updater(ABC):

    date_update: Union[DateUpdateDatabase, DateUpdateApi]
    season_update: Union[SeasonUpdateDatabase, SeasonUpdateApi]
    champ_update: Union[ChampUpdateDatabase, ChampUpdateApi]
    team_update: Union[TeamUpdateDatabase, TeamUpdateApi]
    match_update: Union[MatchUpdateDatabase, MatchUpdateApi]


    @abstractmethod
    async def update(self):
        async with UpdateDatabase.pool.acquire() as conn:
            await self.date_update.update(conn) 
            await self.season_update.update(conn)
            await self.champ_update.update(conn, season = self.season_update.update_match)
            await self.team_update.update(conn, champ = self.champ_update.update_match)
            await self.match_update.update(conn, date = self.date_update.update_match, 
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
        auth = {
            "username": config.setting.user_admin,
            "password": config.setting.user_admin_password
        }
        response = requests.post(f'{config.setting.domain}/token', data=auth)
        UpdateApi.headers = {
            "Authorization": f"Bearer {response.json()['access_token']}"
        }

        self.date_update = DateUpdateApi(prepare.tournaments)
        self.season_update = SeasonUpdateApi(prepare.season.data)
        self.champ_update = ChampUpdateApi(prepare.champ.data)
        self.team_update = TeamUpdateApi(prepare.team.data)
        self.match_update = MatchUpdateApi(prepare.matches.data)


    async def update(self):
        await self.date_update.update() 
        await self.season_update.update()
        await self.champ_update.update(season = self.season_update.update_match)
        await self.team_update.update()
        await self.match_update.update(date = self.date_update.update_match, 
                                    champ = self.champ_update.update_match, 
                                    team = self.team_update.update_match)
        print("Update {}".format(', '.join(self.date_update.data.keys())))


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

    def __init__(self, *args:tuple, strategy_collect:str='date', strategy_update='db') -> None:
        self.collector = CollectorFactory.create_collector(strategy_collect, *args)
        self.prepare = DataPreparer(self.collector)
        self.updater =  UpdateFactory.create_updater(self.prepare,strategy_update)

    async def run(self):
        #await profile(self.collector.collect, 'await self.collector.collect()')
        await self.collector.collect()
        #await profile(self.prepare.prepare ,'self.prepare.prepare()')
        self.prepare.prepare()
        #await profile(self.updater.update,'await self.updater.update()')
        await self.updater.update()
        return 'Completed'



async def profile(func, sep):
    import cProfile, io
    pr = cProfile.Profile()
    pr.enable()
    await func()
    with open(f'profile_results.txt_{sep}', 'w') as f:
        # Перенаправляем вывод в строковый буфер
        pr_str = io.StringIO()
        sys.stdout = pr_str  # Перенаправляем стандартный вывод
        pr.print_stats(sort='time')  # Выводим статистику в буфер
        sys.stdout = sys.__stdout__  # Возвращаем стандартный вывод
        # Записываем результаты в файл
        f.write(pr_str.getvalue())
        pr_str.close()
    pr.disable()  # Отключаем профилирование


if __name__ == '__main__':
    start = time.time()
    facade = UpdateFacade('2025-02-11')
    asyncio.run(facade.run())
    print(time.time() - start)



