from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from api.deps import CurrentUser, GetSession
from core.utils import update_schema
from models.assunto import Assunto
from models.concurso_disciplina_assunto import ConcursoDisciplinaAssunto
from models.disciplina import Disciplina
from schemas.assunto import AssuntoCreate, AssuntoPublic, AssuntoUpdate
from schemas.utils import Message

router = APIRouter(prefix='/assunto', tags=['assunto'])


@router.post('/', status_code=HTTPStatus.CREATED, response_model=AssuntoPublic)
async def create_assunto(
    assunto: AssuntoCreate, session: GetSession, current_user: CurrentUser
):
    disciplina = await session.scalar(
        select(Disciplina).where(
            (Disciplina.id == assunto.disciplina_id)
            & (Disciplina.usuario_id == current_user.id)
        )
    )

    if not disciplina:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Disciplina não encontrada',
        )

    if assunto.id_assunto_pai:
        assunto_pai = await session.scalar(
            select(Assunto).where(
                (Assunto.id == assunto.id_assunto_pai)
                & (Assunto.disciplina_id == assunto.disciplina_id)
            )
        )

        if not assunto_pai:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Assunto pai não encontrado',
            )

    try:
        db_assunto = Assunto(
            nome=assunto.nome,
            disciplina_id=assunto.disciplina_id,
            usuario_id=current_user.id,
            id_assunto_pai=assunto.id_assunto_pai,
        )

        session.add(db_assunto)
        await session.commit()
        await session.refresh(db_assunto)
        return db_assunto
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Já existe um assunto com este nome para esta disciplina.',
        )


@router.get('/{assunto_id}', response_model=AssuntoPublic)
async def read_assunto(
    assunto_id: int, session: GetSession, current_user: CurrentUser
):
    assunto = await session.scalar(
        select(Assunto)
        .options(
            selectinload(Assunto.subassuntos)
            .selectinload(Assunto.subassuntos)
            .selectinload(Assunto.subassuntos)
            .selectinload(Assunto.subassuntos)
        )
        .where(
            (Assunto.id == assunto_id)
            & (Assunto.usuario_id == current_user.id)
        )
    )

    if not assunto:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Assunto não encontrato.'
        )

    return assunto


@router.delete(
    '/{assunto_id}', status_code=HTTPStatus.OK, response_model=Message
)
async def delete_assunto(
    assunto_id: int, session: GetSession, current_user: CurrentUser
):
    assunto = await session.scalar(
        select(Assunto).where(
            (Assunto.id == assunto_id)
            & (Assunto.usuario_id == current_user.id)
        )
    )

    if not assunto:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Assunto não encontrado'
        )

    vinculado = await session.scalar(
        select(ConcursoDisciplinaAssunto)
        .where(ConcursoDisciplinaAssunto.assunto_id == assunto_id)
        .limit(1)
    )

    if vinculado:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Não é possivel excluir assunto vinculado a um concurso',
        )

    tem_subassunto = await session.scalar(
        select(Assunto).where(Assunto.id_assunto_pai == assunto_id).limit(1)
    )

    if tem_subassunto:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Não é possivel excluir assunto que possui subassunto.',
        )

    await session.delete(assunto)
    await session.commit()

    return Message(message='Concurso deletado com sucesso.')


@router.put('/{assunto_id}', response_model=AssuntoPublic)
async def update_assunto(
    assunto_id: int,
    assunto_update: AssuntoUpdate,
    session: GetSession,
    current_user: CurrentUser,
):
    # Busca o assunto a ser atualizado, garantindo que ele pertença ao usuário autenticado
    db_assunto = await session.scalar(
        select(Assunto).where(
            (Assunto.id == assunto_id)
            & (Assunto.usuario_id == current_user.id)
        )
    )

    if not db_assunto:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Assunto não encontrado.',
        )

    # Se for informado nova disciplina, verifique se a mesma existe e pertence ao usuário
    if (
        assunto_update.disciplina_id is not None
        and assunto_update.disciplina_id != db_assunto.disciplina_id
    ):
        disciplina = await session.scalar(
            select(Disciplina).where(
                (Disciplina.id == assunto_update.disciplina_id)
                & (Disciplina.usuario_id == current_user.id)
            )
        )
        if not disciplina:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Disciplina informada não encontrada.',
            )

    # Se for informado novo assunto pai, verifica se ele existe e pertence à mesma disciplina
    if assunto_update.id_assunto_pai is not None:
        # Evita que o assunto seja pai de si mesmo
        if assunto_update.id_assunto_pai == assunto_id:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Um assunto não pode ser pai de si mesmo.',
            )

        assunto_pai = await session.scalar(
            select(Assunto).where(
                (Assunto.id == assunto_update.id_assunto_pai)
                & (
                    Assunto.disciplina_id
                    == (
                        assunto_update.disciplina_id
                        or db_assunto.disciplina_id
                    )
                )
            )
        )
        if not assunto_pai:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Assunto pai não encontrado.',
            )

    # Verifica conflito de nome para a mesma disciplina e usuário, se o nome for alterado
    if (
        assunto_update.nome is not None
        and assunto_update.nome != db_assunto.nome
    ):
        conflito = await session.scalar(
            select(Assunto).where(
                (Assunto.nome == assunto_update.nome)
                & (
                    Assunto.disciplina_id
                    == (
                        assunto_update.disciplina_id
                        or db_assunto.disciplina_id
                    )
                )
                & (Assunto.usuario_id == current_user.id)
                & (Assunto.id != assunto_id)
            )
        )
        if conflito:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Já existe um assunto com este nome para esta disciplina.',
            )

    # Atualiza os atributos do assunto utilizando a função utilitária (update_schema)
    db_assunto = update_schema(schema=assunto_update, model=db_assunto)

    try:
        await session.commit()
        await session.refresh(db_assunto)
        # Opcional: carregar os subassuntos se necessário
        await session.refresh(db_assunto, attribute_names=['subassuntos'])
        return db_assunto
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Erro ao atualizar o assunto.',
        )
