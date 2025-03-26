from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class Assunto(Base):
    __tablename__ = 'assunto'

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(nullable=False)
    disciplina_id: Mapped[int] = mapped_column(ForeignKey('disciplina.id'))
    usuario_id: Mapped[int] = mapped_column(ForeignKey('usuario.id'))

    id_assunto_pai: Mapped[int | None] = mapped_column(
        ForeignKey('assunto.id'),
        nullable=True
    )

    disciplina: Mapped['Disciplina'] = relationship(back_populates='assuntos')

    subassunto: Mapped[list['Assunto']] = relationship(
        back_populates='subassuntos',
        remote_side=[id]
    )

    __table_args__ = (
        UniqueConstraint(
            'nome',
            'disciplina_id',
            'usuario_id',
            name='uq_assunto_disciplina_usuario'
        ),
    )
