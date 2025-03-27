from datetime import date, datetime
from typing import Optional

from pydantic import AfterValidator, BaseModel
from typing_extensions import Annotated

from core.validators import esta_em_branco
from schemas.disciplina import DisciplinaPublic
from schemas.assunto import AssuntoPublic


class ConcursoBase(BaseModel):
    nome: Annotated[str, AfterValidator(esta_em_branco)]
    data_prova: Optional[date] = None


class ConcursoCreate(ConcursoBase):
    disciplinas_ids: list[int] | None = None
    assuntos_ids: list[int] | None = None


class ConcursoPublic(ConcursoBase):
    id: int
    created_at: datetime
    updated_at: datetime
    disciplinas: list[DisciplinaPublic] | None = None
    assuntos: list[AssuntoPublic] | None = None

    class Config:
        from_attributes = True


class ConcursoList(BaseModel):
    concursos: list[ConcursoPublic]


class ConcursoUpdate(BaseModel):
    nome: Annotated[str | None, AfterValidator(esta_em_branco)] = None
    data_prova: date | None = None
    disciplinas_ids: list[int] | None = None
