from fastapi import APIRouter

from api.routes import auth, concurso, disciplina, users

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(disciplina.router)
api_router.include_router(concurso.router)
