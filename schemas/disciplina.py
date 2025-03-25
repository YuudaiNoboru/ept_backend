from datetime import datetime

from pydantic import BaseModel

from schemas.users import UserPublic


class DisciplinaBase(BaseModel):
    nome: str


class DisciplinaCreate(DisciplinaBase):
    pass


class DisciplinaPublic(DisciplinaBase):
    id: int
    id_user_created: int
    user: UserPublic
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DisciplinaList(BaseModel):
    disciplinas: list[DisciplinaPublic]
