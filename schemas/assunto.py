from pydantic import BaseModel, model_validator
from models.assunto import Assunto


class AssuntoBase(BaseModel):
    nome: str
    disciplina_id: int
    id_assunto_pai: int | None = None


class AssuntoCreate(AssuntoBase):
    pass


class AssuntoPublic(AssuntoBase):
    id: int
    subassuntos: list['AssuntoPublic'] | None = None

    @model_validator(mode='before')
    @classmethod
    def load_subassuntos(cls, data):
        if isinstance(data, Assunto):
            # Força o carregamento dos subassuntos se necessário
            if data.subassuntos is not None:
                return {
                    **data.__dict__,
                    'subassuntos': data.subassuntos
                }
        return data

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
