"""Create expenses table

Revision ID: bae477d1dda8
Revises: a712689e906c
Create Date: 2026-08-17 21:03:41.595913

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bae477d1dda8'
down_revision: Union[str, None] = 'a712689e906c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'expenses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('date', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_expenses_title'), 'expenses', ['title'], unique=False)
    op.create_index(op.f('ix_expenses_category'), 'expenses', ['category'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_expenses_category'), table_name='expenses')
    op.drop_index(op.f('ix_expenses_title'), table_name='expenses')
    op.drop_table('expenses')
