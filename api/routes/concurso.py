from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from api.deps import CurrentUser, GetSession
from core.utils import update_schema
from core.validators import validar_entidades
from models.assunto import Assunto
from models.concurso import Concurso
from models.disciplina import Disciplina
from schemas.concurso import (
    ConcursoAssuntoPublic,
    ConcursoCreate,
    ConcursoDisciplinaPublic,
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

    # Busca e valida disciplinas
    disciplinas = await validar_entidades(
        session, Disciplina, current_user.id, concurso.disciplinas_ids
    )

    # Busca e valida assuntos
    assuntos = await validar_entidades(
        session,
        Assunto,
        current_user.id,
        concurso.assuntos_ids,
        options=[selectinload(Assunto.subassuntos)],
    )

    # Valida assuntos x disciplinas
    disciplinas_ids = {d.id for d in disciplinas}
    for assunto in assuntos:
        if assunto.disciplina_id not in disciplinas_ids:
            raise HTTPException(
                HTTPStatus.BAD_REQUEST,
                detail=(
                    f'Assunto {assunto.id} não pertence às disciplinas '
                    'selecionadas'
                ),
            )

    db_concurso = Concurso(
        nome=concurso.nome,
        data_prova=concurso.data_prova,
        usuario_id=current_user.id,
        disciplinas=disciplinas,
        assuntos=assuntos,
    )

    session.add(db_concurso)
    await session.commit()
    await session.refresh(db_concurso, ['disciplinas', 'assuntos'])
    return db_concurso


@router.get('/', response_model=ConcursoList)
async def read_concursos(session: GetSession, current_user: CurrentUser):
    result = await session.execute(
        select(Concurso).where(Concurso.usuario_id == current_user.id)
    )
    concursos = result.scalars().all()
    return {'concursos': concursos}


@router.get('/{concurso_id}', response_model=ConcursoDisciplinaPublic)
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


@router.get('/{concurso_id}/assuntos', response_model=ConcursoAssuntoPublic)
async def read_concurso_assunto(
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

    novas_disciplinas = None
    novos_assuntos = None

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

    # Processa assuntos se fornecidos
    if concurso_update.assuntos_ids is not None:
        stmt = select(Assunto).where(
            Assunto.id.in_(concurso_update.assuntos_ids),
            Assunto.usuario_id == current_user.id,
        )
        result = await session.execute(stmt)
        novos_assuntos = result.scalars().all()

        if len(novos_assuntos) != len(concurso_update.assuntos_ids):
            encontrados = {assunto.id for assunto in novos_assuntos}
            faltantes = [
                id
                for id in concurso_update.assuntos_ids
                if id not in encontrados
            ]
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f'Assuntos não encontrados: {faltantes}',
            )

        # Valida que assuntos pertencem às disciplinas
        # Se disciplinas foram atualizadas, usa as novas; senão,
        # usa as existentes
        disciplinas_ids = (
            {d.id for d in novas_disciplinas}
            if novas_disciplinas is not None
            else {d.id for d in db_concurso.disciplinas}
        )

        for assunto in novos_assuntos:
            if assunto.disciplina_id not in disciplinas_ids:
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    detail=(
                        f'Assunto {assunto.id} não pertence às disciplinas'
                        ' selecionadas'
                    ),
                )
    # Atualiza o modelo apenas se disciplinas ou assuntos foram fornecidos
    if novas_disciplinas is not None:
        db_concurso.disciplinas = novas_disciplinas

    if novos_assuntos is not None:
        db_concurso.assuntos = novos_assuntos

    db_concurso = update_schema(schema=concurso_update, model=db_concurso)
    db_concurso.updated_at = func.now()

    try:
        await session.commit()
        await session.refresh(
            db_concurso, ['disciplinas', 'assuntos', 'updated_at']
        )
        return db_concurso
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
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
            detail='Concurso não encontrado.',
        )

    await session.delete(db_concurso)
    await session.commit()

    return Message(message='Concurso deletado com sucesso.')
