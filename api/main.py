from fastapi import APIRouter

from api.routes import assunto, auth, concurso, disciplina, usuario

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(usuario.router)
api_router.include_router(disciplina.router)
api_router.include_router(concurso.router)
api_router.include_router(assunto.router)