from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class ConcursoDisciplinaAssunto(Base):
    __tablename__ = 'concurso_disciplina_assunto'

    concurso_id: Mapped[int] = mapped_column(ForeignKey('concurso.id'), primary_key=True)
    disciplina_id: Mapped[int] = mapped_column(ForeignKey('disciplina.id'), primary_key=True)
    assunto_id: Mapped[int] = mapped_column(ForeignKey('assunto.id'), primary_key=True)

    __table_args__ = (
        UniqueConstraint(
            'concurso_id',
            'disciplina_id',
            'assunto_id',
            name='uq_concurso_disciplina_assunto'
        ),
    )
