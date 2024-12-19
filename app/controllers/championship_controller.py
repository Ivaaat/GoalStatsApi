from fastapi import APIRouter
from models import Championship
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from dependencies import get_championship_repository
from repositories import ChampionshipRepository

router = APIRouter()

@router.post("/championships/")
async def create_championship(championship: Championship, rep: ChampionshipRepository = Depends(get_championship_repository)):
    id = await rep.create(championship)
    if id:
        return JSONResponse(content={"message": "Champ created", "detail": {"champ": dict(championship)}}, status_code=201)
    else:
        raise HTTPException(status_code=409, detail={'errors': "Championat already exists.", 'champ': dict(championship)})


@router.get("/championships/")
async def read_championships(season_id: int, rep: ChampionshipRepository = Depends(get_championship_repository)):
    championships = await rep.get_all(season_id)
    if championships:
        return JSONResponse(content = championships)
    else:
        raise HTTPException(status_code=404, detail="Championships not found")
    

@router.get("/championships/{championship_id}", response_model=Championship)
async def read_championship(championship_id: int, rep: ChampionshipRepository = Depends(get_championship_repository)):
    championship = await rep.get(championship_id)
    if championship:
        return JSONResponse(content = dict(championship))
    else:
        raise HTTPException(status_code=404, detail=f"championship_id = {championship_id}  not found")


@router.put("/championships/{championship_id}")
async def update_championship(championship: Championship, rep: ChampionshipRepository=Depends(get_championship_repository)):
    # Логика обновления чемпионата
    pass


@router.patch("/championships/{championship_id}")
async def update_championship(championship: Championship, rep: ChampionshipRepository=Depends(get_championship_repository)):
    # Логика обновления чемпионата
    pass


@router.delete("/championships/{championship_id}")
async def delete_championship(championship_id: int, rep: ChampionshipRepository=Depends(get_championship_repository)):
    # Логика удаления чемпионата
    pass