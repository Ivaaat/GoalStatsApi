from fastapi import APIRouter

router = APIRouter()

@router.post("/players/")
async def create_player(player_info: dict):
    # Логика создания нового игрока через репозиторий
    pass

@router.get("/players/")
async def read_players():
    # Логика получения всех игроков
    pass

@router.get("/players/{player_id}")
async def read_player(player_id: int):
    # Логика получения игрока по ID
    pass

@router.put("/players/{player_id}")
async def update_player(player_id: int, player_info: dict):
    # Логика обновления игрока
    pass

@router.delete("/players/{player_id}")
async def delete_player(player_id: int):
    # Логика удаления игрока
    pass