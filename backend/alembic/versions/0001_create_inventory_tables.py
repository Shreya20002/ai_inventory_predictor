"""Create inventory and stock prediction tables

Revision ID: 0001_create_inventory_tables
Revises:
Create Date: 2026-03-15 00:00:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0001_create_inventory_tables"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "inventory",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("stock_code", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("unit_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("current_stock_level", sa.Integer(), nullable=False),
        sa.Column("last_sold_date", sa.DateTime(timezone=False), nullable=True),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("stock_code"),
    )
    op.create_index(op.f("ix_inventory_stock_code"), "inventory", ["stock_code"], unique=True)

    op.create_table(
        "stock_predictions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("stock_code", sa.String(length=50), nullable=False),
        sa.Column("dead_stock_probability", sa.Float(), nullable=False),
        sa.Column("is_dead_stock", sa.Boolean(), nullable=False),
        sa.Column("suggested_discount", sa.Integer(), server_default="0", nullable=False),
        sa.Column("last_updated", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["stock_code"], ["inventory.stock_code"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("stock_code"),
    )
    op.create_index(
        "ix_stock_predictions_is_dead_stock",
        "stock_predictions",
        ["is_dead_stock"],
        unique=False,
    )
    op.create_index(
        "ix_stock_predictions_last_updated",
        "stock_predictions",
        ["last_updated"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_stock_predictions_last_updated", table_name="stock_predictions")
    op.drop_index("ix_stock_predictions_is_dead_stock", table_name="stock_predictions")
    op.drop_table("stock_predictions")
    op.drop_index(op.f("ix_inventory_stock_code"), table_name="inventory")
    op.drop_table("inventory")
