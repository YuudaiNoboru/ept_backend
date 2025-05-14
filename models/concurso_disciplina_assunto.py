from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from models.assunto import Assunto
    from models.concurso import Concurso
    from models.concurso_disciplina_assunto import ConcursoDisciplinaAssunto
    from models.disciplina import Disciplina


class ConcursoDisciplinaAssunto(Base):
    __tablename__ = 'concurso_disciplina_assunto'

    concurso_id: Mapped[int] = mapped_column(
        ForeignKey('concurso.id', ondelete='CASCADE'),
        primary_key=True,
    )
    disciplina_id: Mapped[int] = mapped_column(
        ForeignKey('disciplina.id', ondelete='CASCADE'), primary_key=True
    )
    assunto_id: Mapped[int] = mapped_column(
        ForeignKey('assunto.id', ondelete='CASCADE'), primary_key=True
    )

    disciplina: Mapped['Disciplina'] = relationship(
        back_populates='concurso_disciplina_assuntos'
    )
    assunto: Mapped['Assunto'] = relationship(
        back_populates='concurso_disciplina_assuntos'
    )
    concurso: Mapped['Concurso'] = relationship(
        back_populates='concurso_disciplina_assuntos'
    )

    __table_args__ = (
        UniqueConstraint(
            'concurso_id',
            'disciplina_id',
            'assunto_id',
            name='uq_concurso_disciplina_assunto',
        ),
    )
