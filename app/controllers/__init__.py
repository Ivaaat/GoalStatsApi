from .season_controller import router as season_router
from .championship_controller import router as championship_router
from .team_controller import router as team_router
from .player_controller import router as player_router
from .statistics_controller import router as statistics_router
from .matches_controller import router as match_router
from .tasks_controller import router as tasks_router
from .users_controller import router as users_router

__all__ = ["season_router", "championship_router","team_router","player_router","statistics_router","season_router", "match_router", "tasks_router", "users_router"]

