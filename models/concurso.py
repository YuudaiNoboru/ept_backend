from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import ForeignKey, UniqueConstraint, and_, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.assunto import Assunto
from models.base import Base
from models.concurso_disciplina_assunto import ConcursoDisciplinaAssunto


class Concurso(Base):
    __tablename__ = 'concurso'
    __table_args__ = (
        UniqueConstraint('nome', 'usuario_id', name='uq_concurso_usuario'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(nullable=False)
    data_prova: Mapped[Optional[date]] = mapped_column(nullable=True)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey('usuario.id'), nullable=False
    )

    usuario: Mapped['Usuario'] = relationship(back_populates='concursos')

    disciplinas: Mapped[Optional[List['Disciplina']]] = relationship(
        secondary='concurso_disciplina',
        back_populates='concursos',
        lazy='selectin',
    )

    concurso_disciplina_assuntos: Mapped[List['ConcursoDisciplinaAssunto']] = (
        relationship(
            back_populates='concurso',
            cascade='all, delete-orphan',
            lazy='selectin',
        )
    )

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now(), onupdate=func.now()
    )
