"""llm_audit

Revision ID: 0008_llm_audit
Revises: 0007_drop_legacy_strategies
Create Date: 2026-04-22 20:00:00
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0008_llm_audit"
down_revision = "0007_drop_legacy_strategies"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "llm_audit",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("username", sa.String(64), nullable=False),
        sa.Column("kind", sa.String(16), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("response_raw", sa.Text(), nullable=True),
        sa.Column("success", sa.Boolean(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.CheckConstraint(
            "kind IN ('strategy','competitor')", name="llm_audit_kind_check"
        ),
    )
    op.create_index("ix_llm_audit_created_at", "llm_audit", ["created_at"])
    op.create_index("ix_llm_audit_user_id", "llm_audit", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_llm_audit_user_id", table_name="llm_audit")
    op.drop_index("ix_llm_audit_created_at", table_name="llm_audit")
    op.drop_table("llm_audit")
