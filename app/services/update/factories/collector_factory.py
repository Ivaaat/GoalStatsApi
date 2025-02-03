from datetime import datetime
import sys
from typing import Union
from services.update.collectors import SingleDateGenerator, DateRangeGenerator, UntilDateGenerator, SingleDateCollector, RangeCollector, UntilCollector


class DataGeneratorFactory:
    

    @staticmethod
    def create_generator(date: str, strategy: str = 'toDay'):
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