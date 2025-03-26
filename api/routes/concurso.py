from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from api.deps import CurrentUser, GetSession
from core.utils import update_schema
from models.concurso import Concurso
from models.disciplina import Disciplina
from schemas.concurso import (
    ConcursoCreate,
    ConcursoList,
    ConcursoPublic,
    ConcursoUpdate,
)
from schemas.utils import Message

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
            & (Concurso.usuario_id == current_user.id)
        )
    )

    if existing_concurso:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Você já possui um concurso com este nome.',
        )

    disciplinas = []
    if concurso.disciplinas_ids:
        stmt = select(Disciplina).where(
            Disciplina.id.in_(concurso.disciplinas_ids),
            Disciplina.usuario_id == current_user.id,
        )
        result = await session.execute(stmt)
        disciplinas = result.scalars().all()

        found_ids = {d.id for d in disciplinas}
        if len(found_ids) != len(concurso.disciplinas_ids):
            missing_ids = set(concurso.disciplinas_ids) - found_ids
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f'Disciplinas não encontradas: {missing_ids}',
            )

    try:
        db_concurso = Concurso(
            nome=concurso.nome,
            data_prova=concurso.data_prova,
            usuario_id=current_user.id,
            disciplinas=disciplinas,
        )

        session.add(db_concurso)
        await session.commit()
        await session.refresh(db_concurso, ['disciplinas'])

        return db_concurso
    except IntegrityError as e:
        print('teste')
        print(f'Integrity Error: {str(e)}')
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Erro ao criar concurso.',
        )


@router.get('/', response_model=ConcursoList)
async def read_concursos(session: GetSession, current_user: CurrentUser):
    result = await session.execute(
        select(Concurso).where(Concurso.usuario_id == current_user.id)
    )
    concursos = result.scalars().all()
    return {'concursos': concursos}


@router.get('/{concurso_id}', response_model=ConcursoPublic)
async def read_concurso(
    concurso_id: int, session: GetSession, current_user: CurrentUser
):
    db_concurso = await session.scalar(
        select(Concurso).where(
            (Concurso.id == concurso_id)
            & (Concurso.usuario_id == current_user.id)
        )
    )

    if not db_concurso:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Concurso não encontrado.',
        )

    return db_concurso


@router.put('/{concurso_id}', response_model=ConcursoPublic)
async def update_concurso(
    concurso_id: int,
    concurso_update: ConcursoUpdate,
    session: GetSession,
    current_user: CurrentUser,
):
    db_concurso = await session.scalar(
        select(Concurso).where(
            (Concurso.id == concurso_id)
            & (Concurso.usuario_id == current_user.id)
        )
    )

    if not db_concurso:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Concurso não encontrado.',
        )

    # Verifica se outro registro já tem o mesmo nome para o mesmo usuário
    if concurso_update.nome:
        existing_concurso = await session.scalar(
            select(Concurso).where(
                (Concurso.nome == concurso_update.nome)
                & (Concurso.usuario_id == current_user.id)
                & (Concurso.id != concurso_id)
            )
        )

        if existing_concurso:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Você já possui outro concurso com este nome.',
            )

    if concurso_update.disciplinas_ids is not None:
        stmt = select(Disciplina).where(
            Disciplina.id.in_(concurso_update.disciplinas_ids),
            Disciplina.usuario_id == current_user.id,
        )
        result = await session.execute(stmt)
        novas_disciplinas = result.scalars().all()

        if len(novas_disciplinas) != len(concurso_update.disciplinas_ids):
            encontrados = {d.id for d in novas_disciplinas}
            faltantes = [
                id
                for id in concurso_update.disciplinas_ids
                if id not in encontrados
            ]
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f'Disciplinas não encontradas: {faltantes}',
            )

        db_concurso.disciplinas = novas_disciplinas

    db_concurso = update_schema(schema=concurso_update, model=db_concurso)
    db_concurso.updated_at = func.now()

    try:
        await session.commit()
        await session.refresh(db_concurso, ['disciplinas', 'updated_at'])
        return db_concurso
    except IntegrityError:
        raise HTTPException(
            await session.rollback(),
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Erro ao atualizar concurso.',
        )


@router.delete('/{concurso_id}', response_model=Message)
async def delete_concurso(
    concurso_id: int, session: GetSession, current_user: CurrentUser
):
    db_concurso = await session.scalar(
        select(Concurso).where(
            (Concurso.id == concurso_id)
            & (Concurso.usuario_id == current_user.id)
        )
    )

    if not db_concurso:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Concurso não encontrada.',
        )

    await session.delete(db_concurso)
    await session.commit()

    return Message(message='Concurso deletado com sucesso.')
