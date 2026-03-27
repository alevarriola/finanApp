"""add name_es to categories

Revision ID: b4f2a7c1d935
Revises: 9958cadde671
Create Date: 2026-03-27

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "b4f2a7c1d935"
down_revision: str | None = "9958cadde671"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("categories", sa.Column("name_es", sa.String(100), nullable=True))

    op.execute("""
        UPDATE categories SET name_es = CASE name
            WHEN 'Groceries'        THEN 'Supermercado'
            WHEN 'Food & Dining'    THEN 'Comida y restaurantes'
            WHEN 'Transport'        THEN 'Transporte'
            WHEN 'Housing & Rent'   THEN 'Vivienda y alquiler'
            WHEN 'Health'           THEN 'Salud'
            WHEN 'Phone & Internet' THEN 'Telefono e internet'
            WHEN 'Entertainment'    THEN 'Entretenimiento'
            WHEN 'Shopping'         THEN 'Compras'
            WHEN 'Education'        THEN 'Educacion'
            WHEN 'Utilities'        THEN 'Servicios'
            WHEN 'Travel'           THEN 'Viajes'
            WHEN 'Pets'             THEN 'Mascotas'
            WHEN 'Other Expense'    THEN 'Otros gastos'
            WHEN 'Salary'           THEN 'Salario'
            WHEN 'Freelance'        THEN 'Freelance'
            WHEN 'Transfer'         THEN 'Transferencia'
            WHEN 'Gift'             THEN 'Regalo'
            WHEN 'Investment'       THEN 'Inversion'
            WHEN 'Other Income'     THEN 'Otros ingresos'
        END
        WHERE user_id IS NULL
    """)


def downgrade() -> None:
    op.drop_column("categories", "name_es")
