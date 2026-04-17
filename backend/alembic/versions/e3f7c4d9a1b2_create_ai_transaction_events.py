"""create ai transaction events

Revision ID: e3f7c4d9a1b2
Revises: d7e2f1a3b856
Create Date: 2026-04-17

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "e3f7c4d9a1b2"
down_revision: str | None = "d7e2f1a3b856"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "ai_transaction_events",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("raw_text", sa.String(length=500), nullable=False),
        sa.Column("parsed_output", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("validated_output", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("final_output", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("model_name", sa.String(length=100), nullable=True),
        sa.Column("status", sa.SmallInteger(), nullable=False),
        sa.Column("corrected_fields", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("transaction_id", sa.UUID(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["transaction_id"], ["transactions.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ai_transaction_events_user_id", "ai_transaction_events", ["user_id"])
    op.create_index(
        "ix_ai_transaction_events_transaction_id",
        "ai_transaction_events",
        ["transaction_id"],
    )


def downgrade() -> None:
    op.drop_table("ai_transaction_events")
