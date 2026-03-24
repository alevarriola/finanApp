"""create invitations

Revision ID: d7e2f1a3b856
Revises: c3d1e8f4a920
Create Date: 2026-03-24

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "d7e2f1a3b856"
down_revision: str | None = "c3d1e8f4a920"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "invitations",
        sa.Column("wallet_id", sa.UUID(), nullable=False),
        sa.Column("invited_by_id", sa.UUID(), nullable=True),
        sa.Column("invited_email", sa.String(255), nullable=False),
        sa.Column("role", sa.SmallInteger(), nullable=False),
        sa.Column("token", sa.UUID(), nullable=False),
        sa.Column("status", sa.SmallInteger(), nullable=False, server_default="1"),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["invited_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["wallet_id"], ["wallets.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token"),
    )
    op.create_index("ix_invitations_wallet_id", "invitations", ["wallet_id"])
    op.create_index("ix_invitations_invited_email", "invitations", ["invited_email"])


def downgrade() -> None:
    op.drop_table("invitations")
