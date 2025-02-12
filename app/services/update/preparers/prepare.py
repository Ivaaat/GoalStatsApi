from abc import ABC, abstractmethod
import requests
from config import config
import re
from typing import List, Dict, Union
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from services.update.collectors import Collector

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

sess = requests.Session()
sess.headers.update(HEADERS)

class StatPrepare(ABC):

    def __init__(self) -> None:
        self.data: dict = {}
    
    @abstractmethod
    async def prepare(self, data: str):
        pass

class SeasonPrepare(StatPrepare):

    

    def prepare(self, data: str):
        self.data[data['year']] = {'name': data['year']}
        


class TeamPrepare(StatPrepare):

    

    def prepare(self, champ_id:int, data: str):
        for teams in data:
            team1 = teams['teams'][0]
            self.data[team1['name']+str(team1['id'])] = {'name':team1['name'],
                                        'icon':team1['icon'],
                                        'old_id':team1['id'],
                                        'champ_id': champ_id}
            team2 = teams['teams'][1]
            self.data[team2['name']+str(team2['id'])] = {'name':team2['name'],
                                        'icon':team2['icon'],
                                        'old_id':team2['id'],
                                        'champ_id': champ_id}
            

class ChampPrepare(StatPrepare):

    

    def prepare(self, data: str):
        #translator = Translator()
        name = data.get('name_tournament') if data.get('name_tournament') else data.get('name')
        #translator.translate(name.lower().replace(' ', '_'), dest='en')
        season = ['', '']
        #async with aiohttp.ClientSession() as session:
            #async with session.get('{}{}'.format(config.setting.main_link, data['link']), ssl=ssl_context) as response:
        response = sess.get('{}{}'.format(config.setting.main_link, data['link']))
        if response.status_code == 200:
            text = response.text
            pattern = r"<script>document\.write\('<div>(.*)</div>'\)</script>"
            match = re.search(pattern, text)
            season = match.group(1).split('—')
        self.data[name] = {
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
            'alias': None,
            'season_id': data['year']
        }


class MatchPrepare(StatPrepare):


    def prepare(self, date: str, champ_id: int, matches: List[Dict]):
        for match in matches:
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
                "date_id": date,
                "champ_id": champ_id,
                "home_team_id": match['teams'][0]['id'],
                "away_team_id": match['teams'][1]['id']
            }


class DataPreparer:

    def __init__(self, collector: Collector) -> None:
        self.season = SeasonPrepare()
        self.champ = ChampPrepare()
        self.team = TeamPrepare()
        self.matches = MatchPrepare()
        self.tournaments: List[Dict[str, Union[str, List[str]]]] = collector.data
    

    def _prepare(self, date_tournaments: List[Dict[str, Union[str, List[str]]]]):
        for date, tournaments in date_tournaments.items():
            for tournament in tournaments['tournaments'].values():
                self.season.prepare(tournament)
                self.champ.prepare(tournament) 
                self.team.prepare(tournament['id'], tournament['matches'])
                self.matches.prepare(date, tournament['id'], tournament['matches'], )
        return (self.season.data, self.champ.data, self.team.data, self.matches.data)

    def prepare(self):
        if len(self.tournaments) < multiprocessing.cpu_count():
            self._prepare(self.tournaments)
        else:
            # with ThreadPoolExecutor() as executor:
            #     executor.map(self._prepare, [{date: tournaments} for date, tournaments in self.tournaments.items()])
            with ProcessPoolExecutor() as executor:
                result = executor.map(self._prepare, [{date: tournaments} for date, tournaments in self.tournaments.items()])
            for res in result:
                self.season.data.update(res[0])
                self.champ.data.update(res[1])
                self.team.data.update(res[2])
                self.matches.data.update(res[3])
                