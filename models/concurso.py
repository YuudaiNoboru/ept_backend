from datetime import date, datetime

from sqlalchemy import ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.table_registry import table_registry


@table_registry.mapped_as_dataclass
class Concurso:
    __tablename__ = 'concursos'
    __table_args__ = (
        UniqueConstraint(
            'nome', 'id_user_created', name='uq_concurso_usuario'
        ),
    )

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    nome: Mapped[str] = mapped_column(nullable=False)
    data_prova: Mapped[date | None] = mapped_column(nullable=True)
    id_user_created: Mapped[int] = mapped_column(
        ForeignKey('users.id'), nullable=False
    )

    # Relacionamento
    user: Mapped['User'] = relationship(
        back_populates='concursos', init=False
    )

    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )
