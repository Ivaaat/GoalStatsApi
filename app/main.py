from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
import uvicorn
from controllers import season_router, championship_router, team_router, player_router, statistics_router, match_router, tasks_router, users_router
from db import lifespan
import os


app = FastAPI(lifespan=lifespan)


app.include_router(users_router)
app.include_router(tasks_router, prefix="/api", tags=["tasks"])
app.include_router(season_router, prefix="/api", tags=["seasons"])
app.include_router(championship_router, prefix="/api", tags=["championships"])
app.include_router(team_router, prefix="/api", tags=["teams"])
app.include_router(player_router, prefix="/api", tags=["players"])
app.include_router(match_router, prefix="/api", tags=["matches"])
#app.include_router(statistics_router, prefix="/api", tags=["statistics"])

# Настройка CORS 
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
base_dir = os.path.dirname(os.path.abspath(__file__)) 
templates_dir = os.path.join(base_dir, "templates")
app.mount("/static", StaticFiles(directory=templates_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("templates.html", {"request": request})


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
