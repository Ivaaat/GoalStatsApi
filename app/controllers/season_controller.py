from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import JSONResponse
from dependencies import get_season_repository
from repositories import SeasonRepository
from models import Season
import asyncpg
from update import UpdateFactory
import asyncio

router = APIRouter()

@router.post("/seasons/")
async def create_season(season: Season, rep: SeasonRepository = Depends(get_season_repository)):
    id = await rep.create(season.name)
    if id:
        return JSONResponse(content={"message": "Season created", 'seson_id': id}, status_code=201)
    else:
        raise HTTPException(status_code=409, detail="Season already exists.")


@router.get("/seasons/", response_model=list[Season])
async def get_seasons(season: SeasonRepository = Depends(get_season_repository)):
    updater = UpdateFactory('db', '2025-01-20')
    asyncio.run(updater.run())
    seasons = await season.get_all()
    if seasons:
        return JSONResponse(content = seasons)
    else:
        raise HTTPException(status_code=404, detail="Seasons not found")


@router.get("/seasons/{season_id}", response_model=Season)
async def get_season(season_id: int, rep: SeasonRepository = Depends(get_season_repository)) :
    season = await rep.get(season_id)
    if season:
        return JSONResponse(content = dict(season))
    else:
        raise HTTPException(status_code=404, detail="Season not found")


@router.put("/seasons/", response_model=Season)
async def update_season(season: Season, rep: SeasonRepository = Depends(get_season_repository)):
    try:
        id = await rep.update(season)
    except asyncpg.exceptions.UniqueViolationError:
        raise HTTPException(status_code=409, detail={'errors': "Season already exists.", 'season_name': season.name})
    if id:
        return JSONResponse(content={"message": "Season update", 'season': dict(season)}, status_code=200)
    else:
        raise HTTPException(status_code=404, detail={'errors': "Season not found.", 'season_id': season.id})


@router.delete("/seasons/{season_id}")
async def delete_season(season_id: int, rep: SeasonRepository = Depends(get_season_repository)):
    id = await rep.delete(season_id)
    if id:
        return Response(status_code=204)
    else:
        raise HTTPException(status_code=404, detail={'errors': "Season not found.", 'season_id': season_id})