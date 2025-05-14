from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class ConcursoAssunto(Base):
    __tablename__ = 'concurso_assunto'

    concurso_id: Mapped[int] = mapped_column(
        ForeignKey('concurso.id', ondelete='CASCADE'),
        primary_key=True,
    )
    assunto_id: Mapped[int] = mapped_column(
        ForeignKey('assunto.id', ondelete='CASCADE'), primary_key=True
    )

    __table_args__ = (
        UniqueConstraint(
            'concurso_id',
            'assunto_id',
            name='uq_concurso_assunto',
        ),
    )
