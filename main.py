from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.cors import CORSMiddleware
import uvicorn
import asyncpg
from contextlib import asynccontextmanager


app = FastAPI()

# Настройка CORS (если необходимо)
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация шаблонов
templates = Jinja2Templates(directory=".")

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("templates.html", {"request": request})

# Пример данных
seasons = ["2022/2023", "2023/2024"]
championships = {
    "2022/2023": ["Россия", "Испания", "Италия"],
    "2023/2024": ["Россия", "Испания", "Италия"]
}

clubs_data = {
    ("Россия", "2022/2023"): ["Спартак", "ЦСКА", "Зенит"],
    ("Испания", "2022/2023"): ["Реал Мадрид", "Барселона", "Атлетико Мадрид"],
    ("Италия", "2022/2023"): ["Ювентус", "Интер", "Милан"],
    ("Россия", "2023/2024"): ["Спартак", "ЦСКА", "Зенит"],
    ("Испания", "2023/2024"): ["Реал Мадрид", "Барселона", "Атлетико Мадрид"],
    ("Италия", "2023/2024"): ["Ювентус", "Интер", "Милан"],
    # Добавьте данные для других сезонов и чемпионатов...
}

statistics_data = {
    ("Спартак", "2022/2023"): {"matches_played": 30, "wins": 18, "draws": 7, "losses": 5},
    ("ЦСКА", "2022/2023"): {"matches_played": 30, "wins": 20, "draws": 5, "losses": 5},
    ("Реал Мадрид", "2023/2024"): {"matches_played": 30, "wins": 19, "draws": 8, "losses": 3},
    ("Спартак", "2023/2024"): {"matches_played": 31, "wins": 18, "draws": 7, "losses": 5},
    ("ЦСКА", "2022/2023"): {"matches_played": 30, "wins": 20, "draws": 5, "losses": 5},
    ("Зенит", "2022/2023"): {"matches_played": 30, "wins": 19, "draws": 8, "losses": 3},
    
    # Добавьте статистику для других клубов
}

async def get_db_connection():
    conn = await asyncpg.connect(
        user='postgres',
        password='postgres',
        database='postgres',
        host='localhost',  # или IP-адрес
        port=5432          # порт по умолчанию
    )
    await conn.execute('SET search_path TO championat;')
    return conn

#@asynccontextmanager
async def get_database_connection():
    conn = await asyncpg.connect(
        user='postgres',
        password='postgres',
        database='postgres',
        host='localhost',  # или IP-адрес
        port=5432          # порт по умолчанию
    )
    try:
        yield conn
    finally:
        await conn.close()


@app.get("/api/seasons")
async def get_seasons():
    return JSONResponse(content=seasons)

@app.get("/api/championships")
async def get_championships(season: str):
    return JSONResponse(content=championships.get(season, []))

@app.get("/api/clubs")
#async def get_clubs(season: str, championship: str, conn=Depends(get_database_connection)):
async def get_clubs(season: str, championship: str):
    #clubs = await conn.fetchrow(season, championship)
    clubs = clubs_data.get((championship, season), [])
    return JSONResponse(content=clubs)

@app.get("/api/clubs")
async def get_all_clubs():
    """Получение всех клубов."""
    all_clubs = set()
    for championship in statistics_data:
        for season in statistics_data[championship]:
            all_clubs.update(statistics_data[championship][season])
    return list(all_clubs)

@app.get("/api/search/clubs")
async def search_clubs(query: str, conn=Depends(get_database_connection)):
    """Поиск клубов по названию."""
    if not query:
        return []  # Возвращаем пустой список, если запрос пустой
    #clubs = await conn.fetch("SELECT name FROM championat.teams WHERE name ILIKE $1 LIMIT 5", '{}%'.format(query))
    #unique_clubs = set()
    for club in clubs:
        #if query.lower() in championship[0].lower():
        for season in statistics_data[championship]:
            # Добавляем только те клубы, которые содержат строку запроса
            unique_clubs.add(club.get('name'))
    matching_clubs = list(unique_clubs)
    return matching_clubs # Возвращаем уникальные клубы

@app.get("/api/statistics")
async def get_statistics(club: str, season: str):
    return statistics_data.get((club, season), {})

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
