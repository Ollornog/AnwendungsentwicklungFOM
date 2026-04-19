"""price_history.user_id

Revision ID: 0004_price_history_user
Revises: 0003_app_settings
Create Date: 2026-04-19 00:00:03
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0004_price_history_user"
down_revision = "0003_app_settings"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # nullable=True, damit bestehende Eintraege nicht blockieren. Neu
    # geschriebene Eintraege setzen user_id im Confirm-Endpoint.
    op.add_column(
        "price_history",
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.create_index("ix_price_history_user_id", "price_history", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_price_history_user_id", table_name="price_history")
    op.drop_column("price_history", "user_id")
