from fastapi import APIRouter

from api.routes import auth, users

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
