from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from api.deps import GetSession
from core.security import get_password_hasd
from models.usuario import Usuario
from schemas.usuario import UsuarioList, UsuarioPublic, UsuarioSchema

router = APIRouter(prefix='/users', tags=['users'])


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UsuarioPublic)
async def created_user(user: UsuarioSchema, session: GetSession):
    db_user = await session.scalar(
        select(Usuario).where(
            (Usuario.username == user.username) | (Usuario.email == user.email)
        )
    )

    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Username já existe.',
            )
        elif db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT, detail='Email já existe.'
            )

    hashed_password = get_password_hasd(user.password)

    db_user = Usuario(
        email=user.email,
        username=user.username,
        password=hashed_password,
    )

    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user


@router.get('/', response_model=UsuarioList)
async def read_users(session: GetSession):
    result = await session.execute(select(Usuario))
    users = result.scalars().all()
    return {'users': users}
