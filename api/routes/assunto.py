from fastapi import APIRouter, Depends, HTTPException
from http import HTTPStatus
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError

from api.deps import CurrentUser, GetSession
from models.assunto import Assunto
from models.disciplina import Disciplina
from schemas.assunto import AssuntoCreate, AssuntoPublic, AssuntoUpdate

route = APIRouter(prefix='/assunto', tags=['assunto'])


@route.post('/', status_code=HTTPStatus.CREATED, response_model=AssuntoPublic)
async def create_assunto(
    assunto: AssuntoCreate, session: GetSession, current_user: CurrentUser
):
    disciplina = await session.scalar(
        select(Disciplina).where(
            (Disciplina.id == assunto.id_disciplina)
            & (Disciplina.usuario_id == current_user.id)
        )
    )

    if not disciplina:
        HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Disciplina não encontrada',
        )

    if assunto.id_assunto_pai:
        assunto_pai = await session.scalar(
            select(Assunto).where(
                (Assunto.id == assunto.id_assunto_pai)
                & (Assunto.disciplina_id == assunto.id_disciplina)
            )
        )

        if not assunto_pai:
            HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Assunto pai não encontrado',
            )
    
    try:
        db_assunto 
