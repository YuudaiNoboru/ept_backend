from datetime import datetime

from sqlalchemy import ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class Disciplina(Base):
    __tablename__ = 'disciplina'

    __table_args__ = (
        UniqueConstraint(
            'nome', 'usuario_id', name='uq_disciplina_usuario'
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )
    nome: Mapped[str] = mapped_column(nullable=False)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey('usuario.id'), nullable=False
    )
    usuario: Mapped['Usuario'] = relationship(
        back_populates='disciplinas',
    )
    assuntos: Mapped[list['Assunto']] = relationship(
        back_populates='disciplina',
        cascade='all, delete-orphan'
    )
    concursos: Mapped[list['Concurso']] =relationship(
        secondary='concurso_disciplina', back_populates='disciplinas'
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now(), onupdate=func.now()
    )
