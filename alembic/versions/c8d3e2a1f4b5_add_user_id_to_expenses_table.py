"""Add user_id to expenses and create users table if not exists

Revision ID: c8d3e2a1f4b5
Revises: bae477d1dda8
Create Date: 2026-08-18 01:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c8d3e2a1f4b5'
down_revision: Union[str, None] = 'bae477d1dda8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    # 1. Ensure users table exists
    if 'users' not in tables:
        op.create_table(
            'users',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('email', sa.String(), nullable=False),
            sa.Column('hashed_password', sa.String(), nullable=False),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
        op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # 2. Add user_id column and foreign key to expenses table
    columns = [col['name'] for col in inspector.get_columns('expenses')]
    if 'user_id' not in columns:
        # Add column (nullable=True initially to preserve existing rows)
        op.add_column('expenses', sa.Column('user_id', sa.Integer(), nullable=True))
        
        # Add foreign key constraint to users.id
        op.create_foreign_key(
            'fk_expenses_user_id_users',
            'expenses',
            'users',
            ['user_id'],
            ['id'],
            ondelete='CASCADE'
        )
        
        # Add index on user_id
        op.create_index(op.f('ix_expenses_user_id'), 'expenses', ['user_id'], unique=False)


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # 1. Drop user_id from expenses
    columns = [col['name'] for col in inspector.get_columns('expenses')]
    if 'user_id' in columns:
        op.drop_index(op.f('ix_expenses_user_id'), table_name='expenses')
        op.drop_constraint('fk_expenses_user_id_users', 'expenses', type_='foreignkey')
        op.drop_column('expenses', 'user_id')

    # 2. Drop users table if it exists
    tables = inspector.get_table_names()
    if 'users' in tables:
        op.drop_index(op.f('ix_users_id'), table_name='users')
        op.drop_index(op.f('ix_users_email'), table_name='users')
        op.drop_table('users')
