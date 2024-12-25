from models import Team
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from dependencies import get_team_repository
from repositories import TeamRepository
import asyncio
import json

router = APIRouter()

@router.post("/teams/")
async def create_team(team: Team, rep: TeamRepository = Depends(get_team_repository)):
    id = await rep.create(team)
    if id:
        return JSONResponse(content={"message": "Team created", "detail": {"team": dict(team)}}, status_code=201)
    else:
        raise HTTPException(status_code=409, detail={"error": "Team already exists.", "team": dict(team)})


@router.get("/teams/")
async def get_teams(championship_id: int, Team: TeamRepository = Depends(get_team_repository)):
    Teams = await Team.get_all(championship_id)
    if Teams:
        return JSONResponse(content = Teams)
    else:
        raise HTTPException(status_code=404, detail="Teams not found")


@router.get("/teams/{team_id}/statistics")
async def get_team(request: Request, team_id: int, team: TeamRepository = Depends(get_team_repository)):
    team.pool = request.app.state.pool
    team_stat, players = await asyncio.gather(team.get(team_id), team.get_players(team_id))
    team_stat['calendar'] = json.loads(team_stat['calendar'])
    team_stat['players'] = json.loads(players['players']) if players.get('players') else ''
    if team_stat:
        return JSONResponse(content = team_stat)
    else:
        raise HTTPException(status_code=404, detail="Team not found")
   

@router.get("/teams/search/")
async def search_teams(query: str, team: TeamRepository = Depends(get_team_repository)):
    """Поиск клубов по названию."""
    if not query:
        raise HTTPException(status_code=404, detail="Not query")
    teams = await team.search(query)
    if teams:
        return JSONResponse(content = teams)
    else:
        raise HTTPException(status_code=404, detail="Teams not found")
   

@router.put("/teams/{team_id}")
async def update_team(team_id: int, team_info: dict):
    # Логика обновления клуба
    pass

@router.delete("/teams/{team_id}")
async def delete_team(team_id: int):
    # Логика удаления клуба
    pass