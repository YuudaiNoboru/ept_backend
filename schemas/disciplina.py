from datetime import datetime
from typing import Annotated

from pydantic import AfterValidator, BaseModel

from core.validators import esta_em_branco
from schemas.assunto import AssuntoPublic


class DisciplinaBase(BaseModel):
    nome: Annotated[str, AfterValidator(esta_em_branco)]


class DisciplinaCreate(DisciplinaBase):
    pass


class DisciplinaPublic(DisciplinaBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DisciplinaWithTotalAssuntoPublic(DisciplinaPublic):
    total_assuntos: int


class DisciplinaWithAssuntos(DisciplinaPublic):
    assuntos: list[AssuntoPublic | None] = []


class DisciplinaList(BaseModel):
    disciplinas: list[DisciplinaPublic]


class DisciplinaUpdate(BaseModel):
    nome: Annotated[str | None, AfterValidator(esta_em_branco)] = None
