from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy import select


def esta_em_branco(texto: str) -> str:
    texto_sem_espaco = texto.strip()
    if texto_sem_espaco:
        return texto
    raise ValueError('O valor não pode conter apenas espaços.')


async def validar_entidades(session, model, usuario_id, ids, options=None):
    if not ids:
        return []

    stmt = select(model).where(
        model.id.in_(ids), model.usuario_id == usuario_id
    )

    if options:
        for option in options:
            stmt = stmt.options(option)

    result = await session.execute(stmt)

    entidades = result.scalars().all()

    if len(entidades) != len(ids):
        encontrados = {e.id for e in entidades}
        faltantes = set(ids) - encontrados
        raise HTTPException(
            HTTPStatus.NOT_FOUND,
            detail=f'{model.__name__} não encontrados: {faltantes}',
        )

    return entidades
