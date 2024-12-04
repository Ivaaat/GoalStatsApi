from fastapi import APIRouter
from models import Championship
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from dependencies import get_championship_repository
from repositories import ChampionshipRepository

router = APIRouter()

@router.post("/championships/")
async def create_championship(championship: Championship, conn=Depends(get_championship_repository)):
    # Логика создания нового чемпионата через репозиторий
    pass

@router.get("/championships/")
async def read_championships(season_id: int, champ: ChampionshipRepository = Depends(get_championship_repository)):
    championships = await champ.get_all(season_id)
    if championships:
        return JSONResponse(content = championships)
    else:
        raise HTTPException(status_code=404, detail="Championships not found")
    

@router.get("/championships/{championship_id}")
async def read_championship(championship_id: int, champ: ChampionshipRepository = Depends(get_championship_repository)):
    championship = await champ.get(championship_id)
    if championship:
        return JSONResponse(content = championship)
    else:
        raise HTTPException(status_code=404, detail=f"championship_id = {championship_id}  not found")

@router.put("/championships/{championship_id}")
async def update_championship(championship: Championship, conn=Depends(get_championship_repository)):
    # Логика обновления чемпионата
    pass

@router.delete("/championships/{championship_id}")
async def delete_championship(championship_id: int):
    # Логика удаления чемпионата
    pass