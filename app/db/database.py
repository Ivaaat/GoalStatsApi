
from contextlib import asynccontextmanager
from fastapi import FastAPI
from dotenv import load_dotenv
import os
import asyncpg
from config import get_ssl_context
from typing import AsyncIterator

load_dotenv()
DB_USER= os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_HOST= os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')



pool: asyncpg.Pool

@asynccontextmanager
async def lifespan(app: FastAPI):
    global pool
    pool = await asyncpg.create_pool(
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        host=DB_HOST, 
        port=DB_PORT,
        ssl=get_ssl_context()
    )
    app.state.pool = pool
    yield
    await pool.close()



async def get_database_connection() -> AsyncIterator[asyncpg.Connection]:
    global pool
    async with pool.acquire() as connection:
        yield connection

