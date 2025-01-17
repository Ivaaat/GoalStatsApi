from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from dependencies import get_stat_repository, get_team_repository
from repositories import StatisticsRepository, TeamRepository
from models import Season
import json

router = APIRouter()

# Получение статистики по сезону
@router.get("/statistics/seasons/{season_id}")
async def read_statistics_season(season_id: int, stat: StatisticsRepository = Depends(get_stat_repository)):
    season = stat.get(season_id)
    if season:
        return JSONResponse(content = season)
    raise HTTPException(status_code=404, detail="Season stat not found")

# Создание нового сезона
@router.post("/statistics/seasons/")
async def create_season(season: Season):
    pass

# Обновление существующего сезона
@router.put("/statistics/seasons/{season_id}")
async def update_season(season_id: int, season: Season):
    pass
# Удаление сезона
@router.delete("/statistics/seasons/{season_id}")
async def delete_season(season_id: int):
    pass

# Аналогично для чемпионатов

# Получение статистики по чемпионату
@router.get("/statistics/championships/{championship_id}")
async def read_statistics_championship(championship_id: int):
   pass

# # Создание нового чемпионата
# @router.post("/statistics/championships/")
# async def create_championship(championship: Championship):
#     pass

# # Обновление существующего чемпионата
# @router.put("/statistics/championships/{championship_id}")
# async def update_championship(championship_id: int, championship: Championship):
#     if championship_id in championships:
#         championships[championship_id] = championship.dict()
#         return {"championship_id": championship_id, **championship.dict()}
#     raise HTTPException(status_code=404, detail="Championship not found")

# # Удаление чемпионата
# @router.delete("/statistics/championships/{championship_id}")
# async def delete_championship(championship_id: int):
#     if championship_id in championships:
#         del championships[championship_id]
#         return {"message": "Championship deleted successfully"}
#     raise HTTPException(status_code=404, detail="Championship not found")

# # Аналогично для клубов

# Получение статистики по клубу
@router.get("/statistics/")
async def read_statistics_club(team_name: str, stat: StatisticsRepository = Depends(get_stat_repository)):
    team_stat = await stat.get_team(team_name)
    team_ret = {}
    for team in team_stat:
        club_st = dict(team)
        team_ret[club_st['season_name']] = json.loads(club_st['champ_name_id_team'])
    if team_ret:
        return JSONResponse(content = team_ret)
    else:
        raise HTTPException(status_code=404, detail="Club not found")

# Получение статистики по клубу
@router.get("/statistics/{season_id}")
async def read_statistics_club(club_id: int, club: TeamRepository = Depends(get_team_repository)):
    club_stat = await club._get(club_id)
    asd : str  = ""
    if club_stat:
        return JSONResponse(content = club_stat)
    raise HTTPException(status_code=404, detail="Club not found")

