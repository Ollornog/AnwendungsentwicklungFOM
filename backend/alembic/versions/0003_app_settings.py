"""app_settings: key/value store fuer Laufzeit-Einstellungen

Revision ID: 0003_app_settings
Revises: 0002_product_context_demand
Create Date: 2026-04-19 00:00:02
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0003_app_settings"
down_revision = "0002_product_context_demand"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "app_settings",
        sa.Column("key", sa.String(64), primary_key=True),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )


def downgrade() -> None:
    op.drop_table("app_settings")
