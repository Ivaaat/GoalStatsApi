from models import Team
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from dependencies import get_team_repository, get_current_active_admin
from repositories import TeamRepository
import asyncio
import json
import asyncpg

router = APIRouter()

@router.post("/teams/")
async def create_team(team: Team, rep: TeamRepository = Depends(get_team_repository), _: str = Depends(get_current_active_admin)):
    """Создает новую команду."""
    id = await rep.create(team)
    if id:
        return JSONResponse(content={"message": "Team created", "detail": {"team": dict(team)}}, status_code=201)
    else:
        raise HTTPException(status_code=409, detail={"error": "Team already exists.", "team": dict(team)})


@router.get("/teams/")
async def get_teams_by_championship_id(championship_id: int, team: TeamRepository = Depends(get_team_repository)):
    """Возвращает все команды чемпионата по его id."""
    teams = await team.get_all(championship_id)
    if teams:
        return JSONResponse(content = teams)
    else:
        raise HTTPException(status_code=404, detail="Teams not found")


@router.get("/teams/{team_id}", response_model = Team)
async def get_team(team_id: int, rep: TeamRepository = Depends(get_team_repository)):
    """Возвращает команду ее id."""
    team = await rep.get(team_id)
    if team:
        return team
    else:
        raise HTTPException(status_code=404, detail="Team not found")


@router.get("/teams/{team_id}/statistics")
async def get_team(request: Request, team_id: int, team: TeamRepository = Depends(get_team_repository)):
    team.pool = request.app.state.pool
    team_stat, players = await asyncio.gather(team.get_stat(team_id), team.get_players(team_id))
    team_stat['calendar'] = json.loads(team_stat['calendar'])
    team_stat['players'] = json.loads(players['players']) if players.get('players') else ''
    if team_stat:
        return JSONResponse(content = team_stat)
    else:
        raise HTTPException(status_code=404, detail="Team not found")
   

@router.get("/teams/search/")
async def search_teams(query: str, team: TeamRepository = Depends(get_team_repository)):
    if not query:
        raise HTTPException(status_code=404, detail="Not query")
    teams = await team.search(query)
    if teams:
        return JSONResponse(content = teams)
    else:
        raise HTTPException(status_code=404, detail="Teams not found")
   

@router.put("/teams/")
async def update_team(team: Team, rep: TeamRepository = Depends(get_team_repository), _: str = Depends(get_current_active_admin)):
    try:
        id = await rep.update(team)
    except asyncpg.exceptions.UniqueViolationError:
        raise HTTPException(status_code=409, detail={'errors': "Team already exists.", 'old_id': team.old_id})
    if id:
        return JSONResponse(content={"message": "Team update", 'team': dict(team)}, status_code=200)
    else:
        raise HTTPException(status_code=404, detail={'errors': "Team not found.", 'team_id': team.id})
    

@router.patch("/teams/")
async def update_field_championship(team: Team, rep: TeamRepository=Depends(get_team_repository), _: str = Depends(get_current_active_admin)):
    team_stat = Team(**await rep.get_stat(team.id))
    if not team_stat:
        raise HTTPException(status_code=404, detail={'errors': "Team not found.", 'team_id': team.id})
    update_data = team.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(team_stat, key, value)
    await rep.update(team_stat)
    return JSONResponse(content={"message": "Team update", 'team': dict(team_stat)}, status_code=200)


@router.delete("/teams/{team_id}")
async def delete_team(team_id: int, rep: TeamRepository = Depends(get_team_repository), _: str = Depends(get_current_active_admin)):
    id = await rep.delete(team_id)
    if id:
        return Response(status_code=204)
    else:
        raise HTTPException(status_code=404, detail={'errors': "Team not found.", 'team_id': team_id})