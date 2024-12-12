from fastapi import APIRouter
from models import Match
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from dependencies import get_match_repository
from repositories import MatchesRepository

router = APIRouter()

@router.post("/matches/")
async def create_match(match: Match, rep: MatchesRepository = Depends(get_match_repository)):
    id = await rep.create(match)
    if id:
        return JSONResponse(content={"message": "Match created", 'match_id': id}, status_code=201)
    else:
        raise HTTPException(status_code=409, detail={'errors': "Match already exists.", 'match_old': match.old_id})


@router.put("/matches/")
async def update_match(match: Match, rep: MatchesRepository = Depends(get_match_repository)):
    id = await rep.update(match)
    if id:
        return JSONResponse(content={"message": "Match update", 'match_id': id}, status_code=200)
    else:
        raise HTTPException(status_code=404, detail={'errors': "Match not found.", 'match_old': match.old_id})

@router.post("/matches/{date}")
async def create_date(date: str, rep: MatchesRepository = Depends(get_match_repository)):
    id = await rep.create_date(date)
    if id:
        return JSONResponse(content = {date:id})
    else:
        raise HTTPException(status_code=409, detail={'errors': "Match already exists.", 'match_id': id})

@router.get("/matches/")
async def read_match(season_id: int, champ: MatchesRepository = Depends(get_match_repository)):
    championships = await champ.get_all(season_id)
    if championships:
        return JSONResponse(content = championships)
    else:
        raise HTTPException(status_code=404, detail="Match not found")
    

@router.get("/matches/{match_id}")
async def read_match(match_id: int, rep: MatchesRepository = Depends(get_match_repository)):
    championship = await rep.get(match_id)
    if championship:
        return JSONResponse(content = championship)
    else:
        raise HTTPException(status_code=404, detail=f"match_id = {match_id}  not found")

@router.put("/matches/{match_id}")
async def update_match(match: Match, rep: MatchesRepository = Depends(get_match_repository)):
    id = await rep.update(match)
    if id:
        return match
    else:
        raise HTTPException(status_code=409, detail="Match already exists.")


@router.delete("/matches/{championship_id}")
async def delete_match(championship_id: int):
    # Логика удаления чемпионата
    pass