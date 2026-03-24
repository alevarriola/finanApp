"""create categories and transactions

Revision ID: c3d1e8f4a920
Revises: a74bf096f281
Create Date: 2026-03-24

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "c3d1e8f4a920"
down_revision: str | None = "a74bf096f281"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "categories",
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("category_kind", sa.SmallInteger(), nullable=False),
        sa.Column("color", sa.String(7), nullable=False, server_default="#94a3b8"),
        sa.Column("user_id", sa.UUID(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_categories_user_id", "categories", ["user_id"])

    op.create_table(
        "transactions",
        sa.Column("wallet_id", sa.UUID(), nullable=False),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("transaction_kind", sa.SmallInteger(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("created_by_id", sa.UUID(), nullable=True),
        sa.Column("category_id", sa.UUID(), nullable=True),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["wallet_id"], ["wallets.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_transactions_wallet_id", "transactions", ["wallet_id"])
    op.create_index("ix_transactions_category_id", "transactions", ["category_id"])
    op.create_index("ix_transactions_created_by_id", "transactions", ["created_by_id"])

    op.execute("""
        INSERT INTO categories (id, name, category_kind, color, created_at) VALUES
            (gen_random_uuid(), 'Groceries',        2, '#4ade80', now()),
            (gen_random_uuid(), 'Food & Dining',    2, '#fb923c', now()),
            (gen_random_uuid(), 'Transport',        2, '#60a5fa', now()),
            (gen_random_uuid(), 'Housing & Rent',   2, '#a78bfa', now()),
            (gen_random_uuid(), 'Health',           2, '#f87171', now()),
            (gen_random_uuid(), 'Phone & Internet', 2, '#94a3b8', now()),
            (gen_random_uuid(), 'Entertainment',    2, '#f472b6', now()),
            (gen_random_uuid(), 'Shopping',         2, '#fbbf24', now()),
            (gen_random_uuid(), 'Education',        2, '#34d399', now()),
            (gen_random_uuid(), 'Utilities',        2, '#38bdf8', now()),
            (gen_random_uuid(), 'Travel',           2, '#818cf8', now()),
            (gen_random_uuid(), 'Pets',             2, '#a3e635', now()),
            (gen_random_uuid(), 'Other Expense',    2, '#94a3b8', now()),
            (gen_random_uuid(), 'Salary',           1, '#4ade80', now()),
            (gen_random_uuid(), 'Freelance',        1, '#60a5fa', now()),
            (gen_random_uuid(), 'Transfer',         1, '#94a3b8', now()),
            (gen_random_uuid(), 'Gift',             1, '#f472b6', now()),
            (gen_random_uuid(), 'Investment',       1, '#fbbf24', now()),
            (gen_random_uuid(), 'Other Income',     1, '#94a3b8', now())
    """)


def downgrade() -> None:
    op.drop_table("transactions")
    op.drop_table("categories")
