from datetime import datetime
import sys
from typing import Union
from services.update.collectors import SingleDateGenerator, DateRangeGenerator, UntilDateGenerator, SingleDateCollector, RangeCollector, UntilCollector


class DataGeneratorFactory:
    

    @staticmethod
    def create_generator(date: str):
        try:
            if len(date) == 10:
                datetime.strptime(date, '%Y-%m-%d')
                return SingleDateGenerator(date)
            elif len(date) == 21:
                datetime.strptime(date[:10], '%Y-%m-%d')
                datetime.strptime(date[-10:], '%Y-%m-%d')
                return DateRangeGenerator(date[:10], date[-10:])
            elif len(date) == 11 and date.startswith('-'):
                datetime.strptime(date[1:], '%Y-%m-%d')
                return UntilDateGenerator(date[1:])
            else:
                raise ValueError
        except ValueError as e:
            print('Неверный формат даты {}'.format(e))
            sys.exit()


class DateCollectorFactory:

    @staticmethod
    def create_collector(date_genarator: Union[SingleDateGenerator,DateRangeGenerator, UntilDateGenerator]):
        if isinstance(date_genarator, SingleDateGenerator):
            return SingleDateCollector(date_genarator)
        elif isinstance(date_genarator, DateRangeGenerator):
            return RangeCollector(date_genarator)
        elif isinstance(date_genarator, UntilDateGenerator):
            return UntilCollector(date_genarator)
        
class CollectorFactory:

    @staticmethod
    def create_collector(strategy_collect:str, *args:tuple):
        if strategy_collect == 'date':
            date_genarator = DataGeneratorFactory.create_generator(args[0])
            return DateCollectorFactory.create_collector(date_genarator)
        else:
            #заглушка для других стратегий
            sys.exit()