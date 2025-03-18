from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from api.deps import CurrentUser, GetSession, OAuthForm
from core.security import (
    create_access_token,
    verify_password,
)
from models.users import User
from schemas.utils import Token

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/token', response_model=Token)
async def login_for_access_token(form_data: OAuthForm, session: GetSession):
    user = await session.scalar(
        select(User).where(User.email == form_data.username)
    )

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Email ou senha incorreta',
        )

    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Email ou senha incorreta',
        )

    acces_token = create_access_token(data={'sub': user.email})

    return {'access_token': acces_token, 'token_type': 'bearer'}


@router.post('/refresh_token', response_model=Token)
async def refresh_access_token(user: CurrentUser):
    new_access_token = create_access_token(data={'sub': user.email})

    return {'access_token': new_access_token, 'token_type': 'bearer'}
