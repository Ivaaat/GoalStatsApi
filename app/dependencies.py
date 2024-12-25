from fastapi import Depends
from db import get_database_connection
from repositories import ChampionshipRepository, SeasonRepository, TeamRepository, PlayerRepository, StatisticsRepository, MatchesRepository

async def get_championship_repository(connection=Depends(get_database_connection)) -> ChampionshipRepository:
    return ChampionshipRepository(connection)

async def get_season_repository(connection=Depends(get_database_connection)) -> SeasonRepository:
    return SeasonRepository(connection)

async def get_team_repository(connection=Depends(get_database_connection)) -> TeamRepository:
    return TeamRepository(connection)

async def get_player_repository(connection=Depends(get_database_connection)) -> PlayerRepository:
    return PlayerRepository(connection)

async def get_stat_repository(connection=Depends(get_database_connection)) -> StatisticsRepository:
    return StatisticsRepository(connection)

async def get_match_repository(connection=Depends(get_database_connection)) -> MatchesRepository:
    return MatchesRepository(connection)

