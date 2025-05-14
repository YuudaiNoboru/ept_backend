from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey, UniqueConstraint, and_, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.assunto import Assunto
from models.base import Base

if TYPE_CHECKING:
    from models.concurso import Concurso
    from models.concurso_disciplina_assunto import ConcursoDisciplinaAssunto
    from models.usuario import Usuario


class Disciplina(Base):
    __tablename__ = 'disciplina'

    __table_args__ = (
        UniqueConstraint('nome', 'usuario_id', name='uq_disciplina_usuario'),
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
    assuntos: Mapped[List['Assunto']] = relationship(
        back_populates='disciplina',
        primaryjoin=and_(
            id == Assunto.disciplina_id, Assunto.id_assunto_pai.is_(None)
        ),
        cascade='all, delete-orphan',
        lazy='selectin',
        order_by=Assunto.nome,
    )
    concursos: Mapped[list['Concurso']] = relationship(
        secondary='concurso_disciplina',
        back_populates='disciplinas',
        lazy='selectin',
    )

    concurso_disciplina_assuntos: Mapped[List['ConcursoDisciplinaAssunto']] = (
        relationship(back_populates='disciplina')
    )

    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now(), onupdate=func.now()
    )
