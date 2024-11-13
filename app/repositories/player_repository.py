import asyncpg 
class PlayerRepository:
    def __init__(self, db: asyncpg.Connection):
        self.db = db

    async def create(self, data: dict):
        # Логика создания игрока
        pass

    async def get_all(self):
        # Логика получения всех игроков
        pass

    async def get(self, player_id: int):
        # Логика получения игрока по ID
        pass

    async def update(self, player_id: int, data: dict):
        # Логика обновления игрока
        pass

    async def delete(self, player_id: int):
        # Логика удаления игрока
        pass