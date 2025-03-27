from typing import Optional

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class Assunto(Base):
    __tablename__ = 'assunto'

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(nullable=False)
    disciplina_id: Mapped[int] = mapped_column(ForeignKey('disciplina.id'))
    usuario_id: Mapped[int] = mapped_column(ForeignKey('usuario.id'))

    id_assunto_pai: Mapped[Optional[int]] = mapped_column(
        ForeignKey('assunto.id'),
        nullable=True
    )

    disciplina: Mapped['Disciplina'] = relationship(back_populates='assuntos')

    subassuntos: Mapped[list['Assunto']] = relationship(
        back_populates='assunto_pai',
        foreign_keys='[Assunto.id_assunto_pai]',
        cascade='all, delete-orphan',
        lazy='selectin',
        overlaps="assunto_pai,subassuntos"  # Adicione esta linha
    )

    assunto_pai: Mapped[Optional['Assunto']] = relationship(
        back_populates='subassuntos',
        foreign_keys=[id_assunto_pai],  # Esclarece qual coluna é a FK
        remote_side=[id],
        lazy='selectin'
    )

    __table_args__ = (
        UniqueConstraint(
            'nome',
            'disciplina_id',
            'usuario_id',
            name='uq_assunto_disciplina_usuario'
        ),
    )
