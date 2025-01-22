from fastapi import APIRouter, Response
from models import Championship
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from dependencies import get_championship_repository, get_current_active_admin
from repositories import ChampionshipRepository
import asyncpg

router = APIRouter()

@router.post("/championships/")
async def create_championship(championship: Championship, rep: ChampionshipRepository = Depends(get_championship_repository), _: str = Depends(get_current_active_admin)):
    id = await rep.create(championship)
    if id:
        return JSONResponse(content={"message": "Champ created", "detail": {"champ": dict(championship)}}, status_code=201)
    else:
        raise HTTPException(status_code=409, detail={'errors': "Championat already exists.", 'champ': dict(championship)})


@router.get("/championships/")
async def get_championships_by_season_id(season_id: int, rep: ChampionshipRepository = Depends(get_championship_repository)):
    championships = await rep.get_all(season_id)
    if championships:
        return JSONResponse(content = championships)
    else:
        raise HTTPException(status_code=404, detail="Championships not found")
    

@router.get("/championships/{championship_id}", response_model=Championship)
async def get_championship(championship_id: int, rep: ChampionshipRepository = Depends(get_championship_repository)):
    championship = await rep.get(championship_id)
    if championship:
        return JSONResponse(content = dict(championship))
    else:
        raise HTTPException(status_code=404, detail=f"championship_id = {championship_id}  not found")


@router.put("/championships/")
async def update_championship(championship: Championship, rep: ChampionshipRepository=Depends(get_championship_repository), _: str = Depends(get_current_active_admin)):
    try:
        id = await rep.update(championship)
    except asyncpg.exceptions.UniqueViolationError:
        raise HTTPException(status_code=409, detail={'errors': "Championship already exists.", 'old_id': championship.old_id})
    if id:
        return JSONResponse(content={"message": "Championship update", 'сhampionship': dict(championship)}, status_code=200)
    else:
        raise HTTPException(status_code=404, detail={'errors': "Championship not found.", 'сhamp_id': championship.id})


@router.patch("/championships/")
async def update_field_championship(championship: Championship, rep: ChampionshipRepository=Depends(get_championship_repository), _: str = Depends(get_current_active_admin)):
    champ = Championship(**await rep.get(championship.id))
    if not champ:
        raise HTTPException(status_code=404, detail={'errors': "Championship not found.", 'сhamp_id': championship.id})
    update_data = championship.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(champ, key, value)
    await rep.update(champ)
    return JSONResponse(content={"message": "Championship update", 'сhampionship': dict(champ)}, status_code=200)


@router.delete("/championships/{championship_id}")
async def delete_championship(championship_id: int, rep: ChampionshipRepository=Depends(get_championship_repository), _: str = Depends(get_current_active_admin)):
    id = await rep.delete(championship_id)
    if id:
        return Response(status_code=204)
    else:
        raise HTTPException(status_code=404, detail={'errors': "Championship not found.", 'сhamp_id': championship_id})