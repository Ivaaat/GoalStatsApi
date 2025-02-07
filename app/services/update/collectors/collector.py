from abc import ABC, abstractmethod
from typing import List, Dict, Union


class Collector(ABC):

    def __init__(self):
        self.data: Dict[str, Union[str, List[str]]] = {}

    
    @abstractmethod
    async def collect(self):
        pass