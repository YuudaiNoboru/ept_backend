from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session
from core.security import get_current_user
from models.usuario import Usuario

GetSession = Annotated[AsyncSession, Depends(get_session)]
OAuthForm = Annotated[OAuth2PasswordRequestForm, Depends()]
CurrentUser = Annotated[Usuario, Depends(get_current_user)]