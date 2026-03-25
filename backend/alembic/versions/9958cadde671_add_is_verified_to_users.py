"""add_is_verified_to_users

Revision ID: 9958cadde671
Revises: d7e2f1a3b856
Create Date: 2026-03-25 11:31:09.870792

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '9958cadde671'
down_revision: Union[str, None] = 'd7e2f1a3b856'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('is_verified', sa.Boolean(), nullable=False, server_default=sa.text('false')))


def downgrade() -> None:
    op.drop_column('users', 'is_verified')
