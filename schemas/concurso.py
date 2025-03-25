from datetime import date, datetime

from pydantic import BaseModel


class ConcursoBase(BaseModel):
    nome: str
    data_prova: date | None


class ConcursoCreate(ConcursoBase):
    pass


class ConcursoPublic(ConcursoBase):
    id: int
    id_user_created: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConcursoList(BaseModel):
    concursos: list[ConcursoPublic]
