from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
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
    if club_stat:
        return JSONResponse(content = club_stat)
    raise HTTPException(status_code=404, detail="Club not found")

# # Создание нового клуба
# @router.post("/statistics/clubs/")
# async def create_club(club: Club):
#     club_id = max(clubs.keys()) + 1
#     clubs[club_id] = club.dict()
#     return {"club_id": club_id, **club.dict()}

# # Обновление существующего клуба
# @router.put("/statistics/clubs/{club_id}")
# async def update_club(club_id: int, club: Club):
#     if club_id in clubs:
#         clubs[club_id] = club.dict()
#         return {"club_id": club_id, **club.dict()}
#     raise HTTPException(status_code=404, detail="Club not found")

# # Удаление клуба
# @router.delete("/statistics/clubs/{club_id}")
# async def delete_club(club_id: int):
#     if club_id in clubs:
#         del clubs[club_id]
#         return {"message": "Club deleted successfully"}
#     raise HTTPException(status_code=404, detail="Club not found")

# # Аналогично для игроков

# # Получение статистики по игроку
# @router.get("/statistics/players/{player_id}")
# async def read_statistics_player(player_id: int):
#     player = players.get(player_id)
#     if player:
#         return {"player_id": player_id, "statistics": "Statistics related to the player"}
#     raise HTTPException(status_code=404, detail="Player not found")

# # Создание нового игрока
# @router.post("/statistics/players/")
# async def create_player(player: Player):
#     player_id = max(players.keys()) + 1
#     players[player_id] = player.dict()
#     return {"player_id": player_id, **player.dict()}

# # Обновление существующего игрока
# @router.put("/statistics/players/{player_id}")
# async def update_player(player_id: int, player: Player):
#     if player_id in players:
#         players[player_id] = player.dict()
#         return {"player_id": player_id, **player.dict()}
#     raise HTTPException(status_code=404, detail="Player not found")

# # Удаление игрока
# @router.delete("/statistics/players/{player_id}")
# async def delete_player(player_id: int):
#     if player_id in players:
#         del players[player_id]
#         return {"message": "Player deleted successfully"}
#     raise HTTPException(status_code=404, detail="Player not found")