from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from dependencies import get_season_repository
from repositories import SeasonRepository
from models import Season

router = APIRouter()

@router.post("/seasons/")
async def create_championship(season_info: dict):
    # Логика создания нового чемпионата через репозиторий
    pass

@router.get("/seasons/")
async def read_championships(season: SeasonRepository = Depends(get_season_repository)):
    seasons = await season.get_all()
    if seasons:
        return JSONResponse(content = seasons)
    else:
        raise HTTPException(status_code=404, detail="Seasons not found")

@router.get("/seasons/{season_id}")
async def read_championship(season_id: int):
    # Логика получения чемпионата по ID
    pass

@router.put("/seasons/{season_id}")
async def update_championship(season_id: int, season_info: dict):
    # Логика обновления чемпионата
    pass

@router.delete("/seasons/{season_id}")
async def delete_championship(season_id: int):
    # Логика удаления чемпионата
    pass