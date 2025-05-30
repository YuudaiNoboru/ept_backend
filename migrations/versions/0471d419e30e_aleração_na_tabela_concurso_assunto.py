"""Aleração na tabela concurso_assunto

Revision ID: 0471d419e30e
Revises: c0f83f203a8c
Create Date: 2025-05-14 12:45:50.087494

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0471d419e30e'
down_revision: Union[str, None] = 'c0f83f203a8c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('concurso_assunto',
    sa.Column('concurso_id', sa.Integer(), nullable=False),
    sa.Column('assunto_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['assunto_id'], ['assunto.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['concurso_id'], ['concurso.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('concurso_id', 'assunto_id'),
    sa.UniqueConstraint('concurso_id', 'assunto_id', name='uq_concurso_assunto')
    )
    op.drop_table('concurso_disciplina_assunto')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('concurso_disciplina_assunto',
    sa.Column('concurso_id', sa.INTEGER(), nullable=False),
    sa.Column('disciplina_id', sa.INTEGER(), nullable=False),
    sa.Column('assunto_id', sa.INTEGER(), nullable=False),
    sa.ForeignKeyConstraint(['assunto_id'], ['assunto.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['concurso_id'], ['concurso.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['disciplina_id'], ['disciplina.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('concurso_id', 'disciplina_id', 'assunto_id'),
    sa.UniqueConstraint('concurso_id', 'disciplina_id', 'assunto_id', name='uq_concurso_disciplina_assunto')
    )
    op.drop_table('concurso_assunto')
    # ### end Alembic commands ###
