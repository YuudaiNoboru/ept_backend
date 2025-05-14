from pydantic import AfterValidator, BaseModel, EmailStr
from typing_extensions import Annotated

from core.validators import esta_em_branco


class UsuarioSchema(BaseModel):
    username: Annotated[str, AfterValidator(esta_em_branco)]
    email: EmailStr
    password: str


class UsuarioPublic(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True


class UsuarioList(BaseModel):
    users: list[UsuarioPublic]
