from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import bcrypt
from jose import jwt
from datetime import datetime, timedelta
import datetime as dt
from config import config

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

class AuthService:

        # Функция для хеширования паролей
        def hash_password(self, password: str) -> str:
            return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        # Функция для проверки пароля
        def verify_password(self, plain_password: str, hashed_password: str) -> bool:
            return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

        # Функция для создания JWT токена
        def create_access_token(self, data: dict, expires_delta: timedelta = None):
            to_encode = data.copy()
            if expires_delta:
                expire = datetime.now(dt.UTC)+ expires_delta
            else:
                expire = datetime.now(dt.UTC) + timedelta(minutes=15)
            to_encode.update({"exp": expire})
            encoded_jwt = jwt.encode(to_encode, config.setting.secret_key, algorithm=config.setting.algorithm)
            return encoded_jwt
