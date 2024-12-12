from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.cors import CORSMiddleware
import uvicorn
from controllers import season_router, championship_router, club_router, player_router, statistics_router, match_router
from db import lifespan


app = FastAPI(lifespan=lifespan)

app.include_router(season_router, prefix="/api", tags=["seasons"])
app.include_router(championship_router, prefix="/api", tags=["championships"])
app.include_router(club_router, prefix="/api", tags=["clubs"])
app.include_router(player_router, prefix="/api", tags=["players"])
app.include_router(match_router, prefix="/api", tags=["matches"])
app.include_router(statistics_router, prefix="/api", tags=["statistics"])

# Настройка CORS 
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация шаблонов
templates = Jinja2Templates(directory="./app/templates/")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("templates.html", {"request": request})



if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)