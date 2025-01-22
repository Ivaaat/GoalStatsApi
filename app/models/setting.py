from pydantic_settings import BaseSettings, SettingsConfigDict
import os 


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="/app/.env", env_file_encoding="utf-8", extra="ignore"
    )
   
    domain: str
    initial_link: str
    main_link: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: str



class DB(Settings):
    model_config = SettingsConfigDict(env_prefix="DB_")
    user: str
    password:str
    name:str
    host:str
    port:str 


class SSL(Settings):
    model_config = SettingsConfigDict(env_prefix="SSL_")
    root_certfile:str
    certfile:str
    keyfile:str


setting = Settings()