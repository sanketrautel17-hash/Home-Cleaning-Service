# Routers Package
# Contains FastAPI route handlers for all API endpoints

from core.apis.routers.auth_router import router as auth_router
from core.apis.routers.user_router import router as user_router

__all__ = ["auth_router", "user_router"]
