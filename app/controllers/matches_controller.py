from models import Match
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import JSONResponse
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


@router.get("/matches/{match_id}", response_model=Match)
async def get_match(match_id: int, rep: MatchesRepository = Depends(get_match_repository)):
    match = await rep.get(match_id)
    if match:
        return match
    else:
        raise HTTPException(status_code=404, detail=f"Match  not found,  match_id = {match_id}")


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
    

@router.delete("/matches/{match_id}")
async def delete_match(match_id: int, rep: MatchesRepository = Depends(get_match_repository)):
    id = await rep.delete(match_id)
    if id:
        return Response(status_code=204)
    else:
        raise HTTPException(status_code=404, detail={'errors': "Match not found.", 'match_id': match_id})