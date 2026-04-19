"""product: context, monthly_demand, daily_usage

Revision ID: 0002_product_context_demand
Revises: 0001_initial
Create Date: 2026-04-19 00:00:01
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0002_product_context_demand"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "products",
        sa.Column("context", sa.Text(), nullable=False, server_default=""),
    )
    op.add_column(
        "products",
        sa.Column("monthly_demand", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "products",
        sa.Column("daily_usage", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_check_constraint(
        "products_monthly_demand_non_negative",
        "products",
        "monthly_demand >= 0",
    )
    op.create_check_constraint(
        "products_daily_usage_non_negative",
        "products",
        "daily_usage >= 0",
    )


def downgrade() -> None:
    op.drop_constraint("products_daily_usage_non_negative", "products", type_="check")
    op.drop_constraint("products_monthly_demand_non_negative", "products", type_="check")
    op.drop_column("products", "daily_usage")
    op.drop_column("products", "monthly_demand")
    op.drop_column("products", "context")
