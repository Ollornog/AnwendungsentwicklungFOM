"""api_rate_usage

Revision ID: 0006_api_rate_usage
Revises: 0005_drop_daily_usage
Create Date: 2026-04-20 00:00:01
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0006_api_rate_usage"
down_revision = "0005_drop_daily_usage"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "api_rate_usage",
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("day", sa.Date(), primary_key=True),
        sa.Column("count", sa.Integer(), nullable=False, server_default="0"),
        sa.CheckConstraint("count >= 0", name="api_rate_usage_count_non_negative"),
    )


def downgrade() -> None:
    op.drop_table("api_rate_usage")
