from datetime import date, datetime
from typing import Optional

from sqlalchemy import ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


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

    disciplinas: Mapped[list['Disciplina']] = relationship(
        secondary='concurso_disciplina',
        back_populates='concursos',
        lazy='selectin'
    )

    assuntos_relacionados: Mapped[list['ConcursoDisciplinaAssunto']] = relationship(
        back_populates='concurso',
        cascade='all, delete-orphan',
        lazy='selectin'
    )

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now(), onupdate=func.now()
    )

    @property
    def assuntos(self):
        return [rel.assunto for rel in self.assuntos_relacionados]
