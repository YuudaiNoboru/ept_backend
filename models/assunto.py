from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from models.concurso_disciplina_assunto import ConcursoDisciplinaAssunto
    from models.disciplina import Disciplina


class Assunto(Base):
    __tablename__ = 'assunto'

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(nullable=False)
    disciplina_id: Mapped[int] = mapped_column(ForeignKey('disciplina.id'))
    usuario_id: Mapped[int] = mapped_column(ForeignKey('usuario.id'))

    id_assunto_pai: Mapped[Optional[int]] = mapped_column(
        ForeignKey('assunto.id'), nullable=True
    )

    disciplina: Mapped['Disciplina'] = relationship(back_populates='assuntos')

    subassuntos: Mapped[List['Assunto']] = relationship(
        back_populates='assunto_pai',
        cascade='all, delete-orphan',
        lazy='selectin',
        join_depth=5,
    )

    assunto_pai: Mapped[Optional['Assunto']] = relationship(
        back_populates='subassuntos', remote_side=[id], lazy='selectin'
    )

    concurso_disciplina_assuntos: Mapped[List['ConcursoDisciplinaAssunto']] = (
        relationship(back_populates='assunto')
    )

    __table_args__ = (
        UniqueConstraint(
            'nome',
            'disciplina_id',
            'usuario_id',
            name='uq_assunto_disciplina_usuario',
        ),
    )
