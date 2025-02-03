from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import  timedelta
from dependencies import get_users_repository, get_current_active_user, get_current_user
from repositories import UsersRepository
from models import User
from services.auth import AuthService
from config import config


router = APIRouter()
auth_service = AuthService()



# Создание пользователя
@router.post("/create/")
async def create_user(user: User, rep: UsersRepository = Depends(get_users_repository)):
    user.hashed_password = auth_service.hash_password(user.hashed_password)
    id = await rep.create(user)
    if id:
        return JSONResponse(content={"message": "User created", "detail": {"user": dict(user)}}, status_code=201)
    else:
        raise HTTPException(status_code=409, detail={"error": "User already exists.", "user": dict(user)})

# Аутентификация пользователя и получение токена
@router.post("/token")
async def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), rep: UsersRepository = Depends(get_users_repository)):
    user = await rep.get(form_data.username)
    if not user or not auth_service.verify_password(form_data.password, user['hashed_password']):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password",
                            headers={"WWW-Authenticate": "Bearer"})
    access_token_expires = timedelta(minutes=int(config.setting.access_token_expire_minutes))
    access_token = auth_service.create_access_token(data={"sub": user['username'], "role": user['role']},
                                        expires_delta=access_token_expires)
    # Устанавливаем токен в куки
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return {"access_token": access_token, "token_type": "bearer"}
