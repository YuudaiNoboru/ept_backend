from datetime import date, datetime
from typing import Optional

from pydantic import AfterValidator, BaseModel
from typing_extensions import Annotated

from core.validators import esta_em_branco
from schemas.assunto import AssuntoSemSubassuntosPublic
from schemas.disciplina import (
    DisciplinaPublic,
    DisciplinaWithAssuntos,
)


class ConcursoBase(BaseModel):
    nome: Annotated[str, AfterValidator(esta_em_branco)]
    data_prova: Optional[date] = None


class ConcursoCreate(ConcursoBase):
    disciplinas_ids: list[int] | None = None
    assuntos_ids: list[int] | None = None


class ConcursoPublicList(ConcursoBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConcursoPublic(ConcursoBase):
    id: int
    created_at: datetime
    updated_at: datetime
    disciplinas: list[DisciplinaWithAssuntos | None] = []

    class Config:
        from_attributes = True


class ConcursoDisciplinaPublic(ConcursoBase):
    id: int
    created_at: datetime
    updated_at: datetime
    disciplinas: list[DisciplinaPublic | None] = []

    class Config:
        from_attributes = True


class ConcursoAssuntoPublic(ConcursoBase):
    id: int
    created_at: datetime
    updated_at: datetime
    assuntos: list[AssuntoSemSubassuntosPublic | None] = []

    class Config:
        from_attributes = True


class ConcursoList(BaseModel):
    concursos: list[ConcursoPublicList]


class ConcursoUpdate(BaseModel):
    nome: Annotated[str | None, AfterValidator(esta_em_branco)] = None
    data_prova: date | None = None
    disciplinas_ids: list[int] | None = None
    assuntos_ids: list[int] | None = None
