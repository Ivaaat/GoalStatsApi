import sys
from abc import ABC, abstractmethod
import asyncio

sys.path.append('D:\\vs_code\\GoalStatsApi\\app\\')

import time
from typing import Union
from services.update.preparers import DataPreparer
from services.update.factories import CollectorFactory
from services.update.updaters import *
from db.database import get_pool


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
            await self.team_update.update(conn)
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
        self.date_update = DateUpdateApi(prepare.tournaments)
        self.season_update = SeasonUpdateApi(prepare.season.data)
        self.champ_update = ChampUpdateApi(prepare.champ.data)
        self.team_update = TeamUpdateApi(prepare.team.data)
        self.match_update = MatchUpdateApi(prepare.matches.data)


    # async def update(self):
    #     tasks = [DateUpdateApi.update(date_update) for date_update in list(self.data.keys())]
    #     await asyncio.gather(*tasks)
    #     for date, stat in self.data.items():
    #         for tournaments in stat['tournaments'].values():
    #             self.season, self.champ, self.team, self.matches = SeasonPrepare(), ChampPrepare(), TeamPrepare(), MatchPrepare() 
    #             await asyncio.gather(*[self.season.prepare(tournaments), self.champ.prepare(tournaments), self.team.prepare(tournaments['matches'])])
    #             tasks = []
    #             tasks.append(SeasonUpdateApi.update(self.season.data))
    #             tasks.append(ChampUpdateApi.update(self.champ.data))
    #             tasks.extend([TeamUpdateApi.update(team) for team in self.team.data.values()])
    #             await asyncio.gather(*tasks)
    #             await self.matches.prepare(tournaments['matches'], tournaments['id'], date)
    #             await asyncio.gather(*[MatchUpdateApi.update(match) for match in self.matches.data.values()])
    #         print("Update {}".format(date))
        

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
    facade = UpdateFacade('2025-01-30')
    asyncio.run(facade.run())
    print(time.time() - start)



