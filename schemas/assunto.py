from pydantic import BaseModel


class AssuntoBase(BaseModel):
    nome: str
    id_disciplina: int
    id_assunto_pai: int | None = None


class AssuntoCreate(AssuntoBase):
    pass


class AssuntoPublic(AssuntoBase):
    id: int
    id_user_created: int
    subassuntos: list['AssuntoPublic' | None] = []

    class Config:
        from_attributes = True


class AssuntoUpdate(BaseModel):
    nome: str | None = None
    id_disciplina: int | None = None
    id_assunto_pai: int | None = None
