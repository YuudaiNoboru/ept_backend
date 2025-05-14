from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base
from models.concurso import Concurso
from models.disciplina import Disciplina


class Usuario(Base):
    __tablename__ = 'usuario'

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    disciplinas: Mapped[list['Disciplina']] = relationship(
        back_populates='usuario',
    )
    concursos: Mapped[list['Concurso']] = relationship(
        back_populates='usuario',
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now(), onupdate=func.now()
    )
