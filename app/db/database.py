from contextlib import asynccontextmanager
from fastapi import FastAPI
import asyncpg
from config import get_ssl_context, config
from typing import AsyncIterator



pool: asyncpg.Pool

@asynccontextmanager
async def lifespan(app: FastAPI):
    global pool
    pool = await asyncpg.create_pool(
        user=config.db.user,
        password=config.db.password,
        database=config.db.name,
        host=config.db.host, 
        port=config.db.port,
        ssl=get_ssl_context()
    )
    app.state.pool = pool
    yield
    await pool.close()


async def get_pool() -> asyncpg.Pool: 
    return await asyncpg.create_pool(
        user=config.db.user,
        password=config.db.password,
        database=config.db.name,
        host=config.db.host, 
        port=config.db.port,
        ssl=get_ssl_context()
    )


async def get_database_connection() -> AsyncIterator[asyncpg.Connection]:
    global pool
    async with pool.acquire() as connection:
        yield connection

