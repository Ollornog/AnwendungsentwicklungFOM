"""drop products.daily_usage

Revision ID: 0005_drop_daily_usage
Revises: 0004_price_history_user
Create Date: 2026-04-20 00:00:00

Der fruehere Verbrauch/Tick wird durch Nachfrage/Monat ersetzt.
Lager-Simulation = monthly_demand / (28*24) pro Tick. Damit ist eine
einzige Variable fuer Preis und Lagerverbrauch zustaendig.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0005_drop_daily_usage"
down_revision = "0004_price_history_user"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("products_daily_usage_non_negative", "products", type_="check")
    op.drop_column("products", "daily_usage")


def downgrade() -> None:
    op.add_column(
        "products",
        sa.Column("daily_usage", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_check_constraint(
        "products_daily_usage_non_negative",
        "products",
        "daily_usage >= 0",
    )
