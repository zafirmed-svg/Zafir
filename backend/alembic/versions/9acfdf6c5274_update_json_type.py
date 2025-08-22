"""Update JSON type

Revision ID: 9acfdf6c5274
Revises: c657269a2f9d
Create Date: 2025-08-22 10:09:38.599170

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite
from sqlalchemy.types import TypeDecorator, TEXT
import json

class JSONType(TypeDecorator):
    impl = TEXT

    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)
        return value

# revision identifiers, used by Alembic.
revision: str = '9acfdf6c5274'
down_revision: Union[str, None] = 'c657269a2f9d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create a new table with the updated schema
    op.create_table('surgeons_new',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=True),
        sa.Column('specialty', sa.String(length=100), nullable=True),
        sa.Column('license_number', sa.String(length=50), nullable=True),
        sa.Column('contact_info', JSONType(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_surgeons_new_id'), 'surgeons_new', ['id'], unique=False)

    # Copy data from old table to new table
    conn = op.get_bind()
    conn.execute(sa.text('INSERT INTO surgeons_new SELECT id, name, specialty, license_number, contact_info, created_at FROM surgeons'))

    # Drop old table and rename new table
    op.drop_index(op.f('ix_surgeons_id'), table_name='surgeons')
    op.drop_table('surgeons')
    op.rename_table('surgeons_new', 'surgeons')
    op.create_index(op.f('ix_surgeons_id'), 'surgeons', ['id'], unique=False)


def downgrade() -> None:
    # Create a new table with the old schema
    op.create_table('surgeons_new',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=True),
        sa.Column('specialty', sa.String(length=100), nullable=True),
        sa.Column('license_number', sa.String(length=50), nullable=True),
        sa.Column('contact_info', sqlite.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_surgeons_new_id'), 'surgeons_new', ['id'], unique=False)

    # Copy data from current table to new table
    conn = op.get_bind()
    conn.execute(sa.text('INSERT INTO surgeons_new SELECT id, name, specialty, license_number, contact_info, created_at FROM surgeons'))

    # Drop current table and rename new table
    op.drop_index(op.f('ix_surgeons_id'), table_name='surgeons')
    op.drop_table('surgeons')
    op.rename_table('surgeons_new', 'surgeons')
    op.create_index(op.f('ix_surgeons_id'), 'surgeons', ['id'], unique=False)
