from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.table_registry import table_registry


@table_registry.mapped_as_dataclass
class User:
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(
        init=False,
        primary_key=True,
    )
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    disciplinas: Mapped[list['Disciplina']] = relationship(
        back_populates='user', default_factory=list, init=False
    )
    concursos: Mapped[list['Concurso']] = relationship(
        back_populates='user',
        default_factory=list,
        init=False,
        foreign_keys='Concurso.id_user_created',
    )
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )
