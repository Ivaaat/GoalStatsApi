import asyncpg
from models import User

class UsersRepository:

    def __init__(self, db: asyncpg.Connection):
        self.db = db


    async def create(self, user: User):
        return await self.db.fetchval("""INSERT INTO stats.users (username, email, hashed_password, role) VALUES ($1, $2, $3, $4) ON CONFLICT (username, email) DO NOTHING RETURNING id""", 
                                      user.username, user.email, user.hashed_password, user.role)
    

    async def get(self, username: str):
        return await self.db.fetchrow("""select * from stats.users 
                                    where username = $1 """, username)