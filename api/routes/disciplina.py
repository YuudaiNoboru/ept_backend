from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from api.deps import CurrentUser, GetSession
from core.utils import update_schema
from models.assunto import Assunto
from models.concurso_disciplina import ConcursoDisciplina
from models.disciplina import Disciplina
from schemas.disciplina import (
    DisciplinaCreate,
    DisciplinaList,
    DisciplinaPublic,
    DisciplinaUpdate,
    DisciplinaWithAssuntos,
    DisciplinaWithTotalAssuntoPublic,
)
from schemas.utils import Message

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
            & (Disciplina.usuario_id == current_user.id)
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
            usuario_id=current_user.id,  # Usa o ID do usuário autenticado
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
        select(Disciplina).where(Disciplina.usuario_id == current_user.id)
    )
    disciplinas = result.scalars().all()
    return {'disciplinas': disciplinas}


@router.get(
    '/{disciplina_id}', response_model=DisciplinaWithTotalAssuntoPublic
)
async def read_disciplina(
    disciplina_id: int, session: GetSession, current_user: CurrentUser
):
    disciplina = await session.scalar(
        select(Disciplina).where(
            (Disciplina.id == disciplina_id)
            & (Disciplina.usuario_id == current_user.id)
        )
    )

    if not disciplina:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Disciplina não encontrada',
        )

    total_assuntos = await session.scalar(
        select(func.count(Assunto.id)).where(
            Assunto.disciplina_id == disciplina_id
        )
    )

    disciplina.total_assuntos = total_assuntos

    return disciplina


@router.get('/{disciplina_id}/assuntos', response_model=DisciplinaWithAssuntos)
async def read_disciplina_assunto(
    disciplina_id: int, session: GetSession, current_user: CurrentUser
):
    db_disciplina = await session.scalar(
        select(Disciplina)
        .options(
            selectinload(Disciplina.assuntos)
            .selectinload(Assunto.subassuntos)
            # Se necessário, adicione mais níveis:
            .selectinload(Assunto.subassuntos)
            .selectinload(Assunto.subassuntos)
            .selectinload(Assunto.subassuntos)
        )
        .where(
            (Disciplina.id == disciplina_id)
            & (Disciplina.usuario_id == current_user.id)
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
    disciplina_update: DisciplinaUpdate,
    session: GetSession,
    current_user: CurrentUser,
):
    db_disciplina = await session.scalar(
        select(Disciplina).where(
            (Disciplina.id == disciplina_id)
            & (Disciplina.usuario_id == current_user.id)
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
            & (Disciplina.usuario_id == current_user.id)
            & (Disciplina.id != disciplina_id)
        )
    )

    if existing_disciplina:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Você já possui outra disciplina com este nome.',
        )

    db_disciplina = update_schema(
        schema=disciplina_update, model=db_disciplina
    )

    try:
        await session.commit()
        await session.refresh(db_disciplina)
        return db_disciplina
    except IntegrityError as e:
        print(e)
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Erro ao atualizar disciplina.',
        )


@router.delete('/{disciplina_id}', response_model=Message)
async def delete_disciplina(
    disciplina_id: int, session: GetSession, current_user: CurrentUser
):
    db_disciplina = await session.scalar(
        select(Disciplina).where(
            (Disciplina.id == disciplina_id)
            & (Disciplina.usuario_id == current_user.id)
        )
    )

    if not db_disciplina:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Disciplina não encontrada.',
        )

    vinculado = await session.scalar(
        select(ConcursoDisciplina)
        .where(ConcursoDisciplina.disciplina_id == disciplina_id)
        .limit(1)
    )

    if vinculado:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Não é possível alterar disciplina vinculada a um concurso.',
        )

    await session.delete(db_disciplina)
    await session.commit()

    return Message(message='Disciplina deletada com sucesso.')
