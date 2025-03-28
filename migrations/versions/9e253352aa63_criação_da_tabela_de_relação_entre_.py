"""Criação da tabela de relação entre concurso e disciplina.

Revision ID: 9e253352aa63
Revises: b653fb3c93fa
Create Date: 2025-03-26 14:51:13.431620

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9e253352aa63'
down_revision: Union[str, None] = 'b653fb3c93fa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('concurso_disciplina',
    sa.Column('concurso_id', sa.Integer(), nullable=False),
    sa.Column('disciplina_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['concurso_id'], ['concurso.id'], ),
    sa.ForeignKeyConstraint(['disciplina_id'], ['disciplina.id'], ),
    sa.PrimaryKeyConstraint('concurso_id', 'disciplina_id'),
    sa.UniqueConstraint('concurso_id', 'disciplina_id', name='uq_concurso_disciplina')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('concurso_disciplina')
    # ### end Alembic commands ###
