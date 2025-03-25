from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from api.deps import CurrentUser, GetSession
from models.disciplina import Disciplina
from schemas.disciplina import (
    DisciplinaCreate,
    DisciplinaList,
    DisciplinaPublic,
)

router = APIRouter(prefix='/disciplinas', tags=['disciplinas'])


@router.post(
    '/', status_code=HTTPStatus.CREATED, response_model=DisciplinaPublic
)
async def create_disciplina(
    disciplina: DisciplinaCreate,
    session: GetSession,
    current_user: CurrentUser,
):
    # Verifica se já existe a mesma disciplina para o mesmo usuário
    db_disciplina = await session.scalar(
        select(Disciplina).where(
            (Disciplina.nome == disciplina.nome)
            & (Disciplina.id_user_created == current_user.id)
        )
    )

    if db_disciplina:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Você já possui uma disciplina com este nome.',
        )

    try:
        db_disciplina = Disciplina(
            nome=disciplina.nome,
            id_user_created=current_user.id,  # Usa o ID do usuário autenticado
        )

        session.add(db_disciplina)
        await session.commit()
        await session.refresh(db_disciplina)

        return db_disciplina
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Erro ao criar disciplina.',
        )


@router.get('/', response_model=DisciplinaList)
async def read_disciplinas(session: GetSession, current_user: CurrentUser):
    # Retorna apenas as disciplinas do usuário autenticado
    result = await session.execute(
        select(Disciplina).where(Disciplina.id_user_created == current_user.id)
    )
    disciplinas = result.scalars().all()
    return {'disciplinas': disciplinas}


@router.get('/{disciplina_id}', response_model=DisciplinaPublic)
async def read_disciplina(
    disciplina_id: int, session: GetSession, current_user: CurrentUser
):
    db_disciplina = await session.scalar(
        select(Disciplina).where(
            (Disciplina.id == disciplina_id)
            & (Disciplina.id_user_created == current_user.id)
        )
    )

    if not db_disciplina:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Disciplina não encontrada.',
        )

    return db_disciplina


@router.put('/{disciplina_id}', response_model=DisciplinaPublic)
async def update_disciplina(
    disciplina_id: int,
    disciplina_update: DisciplinaCreate,
    session: GetSession,
    current_user: CurrentUser,
):
    db_disciplina = await session.scalar(
        select(Disciplina).where(
            (Disciplina.id == disciplina_id)
            & (Disciplina.id_user_created == current_user.id)
        )
    )

    if not db_disciplina:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Disciplina não encontrada.',
        )

    # Verifica se outro registro já tem o mesmo nome para o mesmo usuário
    existing_disciplina = await session.scalar(
        select(Disciplina).where(
            (Disciplina.nome == disciplina_update.nome)
            & (Disciplina.id_user_created == current_user.id)
            & (Disciplina.id != disciplina_id)
        )
    )

    if existing_disciplina:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Você já possui outra disciplina com este nome.',
        )

    db_disciplina.nome = disciplina_update.nome

    try:
        await session.commit()
        await session.refresh(db_disciplina)
        return db_disciplina
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Erro ao atualizar disciplina.',
        )


@router.delete('/{disciplina_id}', status_code=HTTPStatus.NO_CONTENT)
async def delete_disciplina(
    disciplina_id: int, session: GetSession, current_user: CurrentUser
):
    db_disciplina = await session.scalar(
        select(Disciplina).where(
            (Disciplina.id == disciplina_id)
            & (Disciplina.id_user_created == current_user.id)
        )
    )

    if not db_disciplina:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Disciplina não encontrada.',
        )

    await session.delete(db_disciplina)
    await session.commit()

    return None
