from fastapi import Depends
from db import get_database_connection
from repositories import ChampionshipRepository, SeasonRepository, TeamRepository, PlayerRepository, StatisticsRepository, MatchesRepository, UsersRepository
from fastapi import Depends, HTTPException, status, Cookie, Request
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from services.auth_service import AuthService
from typing import Union
from config import config

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

async def get_championship_repository(connection=Depends(get_database_connection)) -> ChampionshipRepository:
    return ChampionshipRepository(connection)

async def get_season_repository(connection=Depends(get_database_connection)) -> SeasonRepository:
    return SeasonRepository(connection)

async def get_team_repository(connection=Depends(get_database_connection)) -> TeamRepository:
    return TeamRepository(connection)

async def get_player_repository(connection=Depends(get_database_connection)) -> PlayerRepository:
    return PlayerRepository(connection)

async def get_stat_repository(connection=Depends(get_database_connection)) -> StatisticsRepository:
    return StatisticsRepository(connection)

async def get_match_repository(connection=Depends(get_database_connection)) -> MatchesRepository:
    return MatchesRepository(connection)

async def get_users_repository(connection=Depends(get_database_connection)) -> UsersRepository:
    return UsersRepository(connection)


# Зависимость для проверки прав доступа
def get_current_user(token: str = Depends(oauth2_scheme), access_token: str = Cookie(None)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if token:
        pass
    elif not token and access_token:
        token = access_token
    else:
        raise credentials_exception
    try:
        payload = jwt.decode(token, config.setting.secret_key, algorithms=[config.setting.algorithm])
        username = payload.get("sub")
        role = payload.get("role")
        if username is None:
            raise credentials_exception 
        return username, role
    except JWTError:
        raise credentials_exception


# Проверка прав доступа для администраторов
def get_current_active_user(request: Request ,current_user: Union[tuple, None] = Depends(get_current_user)):
    username, role = current_user
    if role not in ['user', 'admin']:
        raise HTTPException(status_code=403, detail="You do not have access to this resource.")
    return username


def get_current_active_admin(request: Request, current_user: Union[tuple, None] = Depends(get_current_user)):
    username, role = current_user
    if role != 'admin':
        raise HTTPException(status_code=403, detail="You do not have access to this resource.")
    return username

