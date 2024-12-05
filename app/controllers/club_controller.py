from models import Club
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from dependencies import get_club_repository
from repositories import ClubRepository
import asyncio
import json

router = APIRouter()

@router.post("/clubs/")
async def create_club(club_info: dict):
    # Логика создания нового клуба через репозиторий
    pass


@router.get("/clubs/")
async def read_clubs(championshipId: int, club: ClubRepository = Depends(get_club_repository)):
    clubs = await club.get_all(championshipId)
    if clubs:
        return JSONResponse(content = clubs)
    else:
        raise HTTPException(status_code=404, detail="Clubs not found")


@router.get("/clubs/{club_id}/statistics")
async def read_club(request: Request, club_id: int, club: ClubRepository = Depends(get_club_repository)):
    club.pool = request.app.state.pool
    club_stat, players = await asyncio.gather(club.get(club_id), club.get_players(club_id))
    club_stat['calendar'] = json.loads(club_stat['calendar'])
    club_stat['players'] = json.loads(players['players'])
    if club_stat:
        return JSONResponse(content = club_stat)
    else:
        raise HTTPException(status_code=404, detail="Club not found")
   

@router.get("/clubs/search/")
async def search_clubs(query: str, club: ClubRepository = Depends(get_club_repository)):
    """Поиск клубов по названию."""
    if not query:
        raise HTTPException(status_code=404, detail="Not query")
    clubs = await club.search(query)
    if clubs:
        return JSONResponse(content = clubs)
    else:
        raise HTTPException(status_code=404, detail="Clubs not found")
   

@router.put("/clubs/{club_id}")
async def update_club(club_id: int, club_info: dict):
    # Логика обновления клуба
    pass

@router.delete("/clubs/{club_id}")
async def delete_club(club_id: int):
    # Логика удаления клуба
    pass