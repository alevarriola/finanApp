"""create_wallets_and_wallet_members

Revision ID: a74bf096f281
Revises: a2ad00ba5b58
Create Date: 2026-03-23 22:09:32.473923

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a74bf096f281'
down_revision: Union[str, None] = 'a2ad00ba5b58'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('wallets',
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('wallet_kind', sa.SmallInteger(), nullable=False),
    sa.Column('owner_id', sa.UUID(), nullable=False),
    sa.Column('currency', sa.String(length=10), nullable=False),
    sa.Column('initial_balance', sa.Numeric(precision=18, scale=2), nullable=False),
    sa.Column('is_archived', sa.Boolean(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_wallets_owner_id'), 'wallets', ['owner_id'], unique=False)
    op.create_table('wallet_members',
    sa.Column('wallet_id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('role', sa.SmallInteger(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['wallet_id'], ['wallets.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('wallet_id', 'user_id', name='uq_wallet_members_wallet_user')
    )
    op.create_index(op.f('ix_wallet_members_user_id'), 'wallet_members', ['user_id'], unique=False)
    op.create_index(op.f('ix_wallet_members_wallet_id'), 'wallet_members', ['wallet_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_wallet_members_wallet_id'), table_name='wallet_members')
    op.drop_index(op.f('ix_wallet_members_user_id'), table_name='wallet_members')
    op.drop_table('wallet_members')
    op.drop_index(op.f('ix_wallets_owner_id'), table_name='wallets')
    op.drop_table('wallets')
