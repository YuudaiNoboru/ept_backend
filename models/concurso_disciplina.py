from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class ConcursoDisciplina(Base):
    __tablename__ = 'concurso_disciplina'

    concurso_id: Mapped[int] = mapped_column(
        ForeignKey('concurso.id'), primary_key=True
    )
    disciplina_id: Mapped[int] = mapped_column(
        ForeignKey('disciplina.id'), primary_key=True
    )

    __table_args__ = (
        UniqueConstraint(
            'concurso_id', 'disciplina_id', name='uq_concurso_disciplina'
        ),
    )
