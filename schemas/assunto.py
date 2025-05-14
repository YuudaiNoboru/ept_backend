from pydantic import BaseModel


class AssuntoBase(BaseModel):
    nome: str
    disciplina_id: int
    id_assunto_pai: int | None = None


class AssuntoCreate(AssuntoBase):
    pass


class AssuntoPublic(AssuntoBase):
    id: int
    subassuntos: list['AssuntoPublic'] | None = None

    class Config:
        from_attributes = True


class AssuntoUpdate(BaseModel):
    nome: str | None = None
    disciplina_id: int | None = None
    id_assunto_pai: int | None = None


class AssuntoSemSubassuntosPublic(AssuntoBase):
    id: int
    nome: str
    disciplina_id: int
    id_assunto_pai: int | None = None

    class Config:
        from_attributes = True
