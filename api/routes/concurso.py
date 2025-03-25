from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from api.deps import CurrentUser, GetSession
from models.concurso import Concurso
from schemas.concurso import ConcursoCreate, ConcursoList, ConcursoPublic

router = APIRouter(prefix='/concursos', tags=['concursos'])


@router.post(
    '/', status_code=HTTPStatus.CREATED, response_model=ConcursoPublic
)
async def create_concurso(
    concurso: ConcursoCreate, session: GetSession, current_user: CurrentUser
):
    # Verifica se já existe um concurso com o mesmo nome para o usuário
    existing_concurso = await session.scalar(
        select(Concurso).where(
            (Concurso.nome == concurso.nome)
            & (Concurso.id_user_created == current_user.id)
        )
    )

    if existing_concurso:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Você já possui um concurso com este nome.',
        )

    try:
        db_concurso = Concurso(
            nome=concurso.nome,
            data_prova=concurso.data_prova,
            id_user_created=current_user.id,
        )

        session.add(db_concurso)
        await session.commit()
        await session.refresh(db_concurso)

        return db_concurso
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Erro ao criar concurso.',
        )


@router.get('/', response_model=ConcursoList)
async def read_concursos(session: GetSession, current_user: CurrentUser):
    result = await session.execute(
        select(Concurso).where(Concurso.id_user_created == current_user.id)
    )
    concursos = result.scalars().all()
    return {'concursos': concursos}


@router.get('/{concurso_id}', response_model=ConcursoPublic)
async def read_disciplina(
    concurso_id: int, session: GetSession, current_user: CurrentUser
):
    db_concurso = await session.scalar(
        select(Concurso).where(
            (Concurso.id == concurso_id)
            & (Concurso.id_user_created == current_user.id)
        )
    )

    if not db_concurso:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Concurso não encontrado.',
        )

    return db_concurso


@router.put('/{concurso_id}', response_model=ConcursoPublic)
async def update_disciplina(
    concurso_id: int,
    concurso_update: ConcursoCreate,
    session: GetSession,
    current_user: CurrentUser,
):
    db_concurso = await session.scalar(
        select(Concurso).where(
            (Concurso.id == concurso_id)
            & (Concurso.id_user_created == current_user.id)
        )
    )

    if not db_concurso:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Concurso não encontrado.',
        )

    # Verifica se outro registro já tem o mesmo nome para o mesmo usuário
    existing_concurso = await session.scalar(
        select(Concurso).where(
            (Concurso.nome == concurso_update.nome)
            & (Concurso.id_user_created == current_user.id)
            & (Concurso.id != concurso_id)
        )
    )

    if existing_concurso:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Você já possui outro concurso com este nome.',
        )

    db_concurso.nome = concurso_update.nome

    try:
        await session.commit()
        await session.refresh(db_concurso)
        return db_concurso
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Erro ao atualizar concurso.',
        )


@router.delete('/{concurso_id}', status_code=HTTPStatus.NO_CONTENT)
async def delete_disciplina(
    concurso_id: int, session: GetSession, current_user: CurrentUser
):
    db_concurso = await session.scalar(
        select(Concurso).where(
            (Concurso.id == concurso_id)
            & (Concurso.id_user_created == current_user.id)
        )
    )

    if not db_concurso:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Concurso não encontrada.',
        )

    await session.delete(db_concurso)
    await session.commit()

    return None
