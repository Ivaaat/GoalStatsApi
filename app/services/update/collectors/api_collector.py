from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Dict, Union
import random
import asyncio
import aiohttp
import ssl
from config import config
from services.update.collectors import Collector



SEMAPHORE = asyncio.Semaphore(3)
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

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
        self._generate_date_range(start_date= self.start_date, end_date_str=self.end_date_str)









class DateCollector(Collector):


    def __init__(self, date_genarator: Union[SingleDateGenerator,DateRangeGenerator, UntilDateGenerator]):
        super().__init__()
        self.dates: List[str] = []
        self.date_genarator = date_genarator
     

    @abstractmethod
    async def collect(self):
        await self.date_genarator.create_date()
        self.dates = self.date_genarator.dates
    

    async def _collect_date(self, date: str):
        async with SEMAPHORE:
            async with aiohttp.ClientSession() as session:
                async with session.get('{}{}'.format(config.setting.initial_link, date), ssl=ssl_context) as response:
                    await asyncio.sleep(random.uniform(1, 2))
                    if response.status:
                        result = await response.json()
                        if result.get('matches'):
                            if result.get('matches').get('football'): 
                                self.data[date] = result['matches']['football']
                                return result


class SingleDateCollector(DateCollector):
     
     async def collect(self):
        await super().collect()
        await self._collect_date(self.dates[0])


class RangeCollector(DateCollector):
     
     async def collect(self):
        await super().collect()
        asyncio.gather(*[self._collect_date(date) for date in self.dates])
        

class UntilCollector(DateCollector):
     
     async def collect(self):
        await super().collect()
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
                
         