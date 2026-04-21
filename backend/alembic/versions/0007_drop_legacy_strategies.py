"""Legacy-Strategien 'rule' und 'llm' entfernen

Revision ID: 0007_drop_legacy_strategies
Revises: 0006_api_rate_usage
Create Date: 2026-04-20 00:00:02
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0007_drop_legacy_strategies"
down_revision = "0006_api_rate_usage"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Zunaechst bestehende Zeilen mit den abgeschafften Strategien
    # entfernen – der neue Check-Constraint wuerde sie sonst abweisen.
    # Parallel fliegen die an den Produkten haengenden Strategien raus
    # (Produkt bleibt, hat danach keine aktive Strategie mehr; der User
    # muss eine Fixpreis- oder Formel-Strategie neu setzen).
    op.execute("DELETE FROM pricing_strategies WHERE kind IN ('rule','llm')")

    op.drop_constraint(
        "pricing_strategies_kind_check", "pricing_strategies", type_="check"
    )
    op.create_check_constraint(
        "pricing_strategies_kind_check",
        "pricing_strategies",
        "kind IN ('fix','formula')",
    )


def downgrade() -> None:
    op.drop_constraint(
        "pricing_strategies_kind_check", "pricing_strategies", type_="check"
    )
    op.create_check_constraint(
        "pricing_strategies_kind_check",
        "pricing_strategies",
        "kind IN ('fix','formula','rule','llm')",
    )
