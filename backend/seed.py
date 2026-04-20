"""Seed: legt einen Admin-User und Mock-Produkte an, falls noch keine existieren.

Aufruf (mit aktiver venv):
    python -m seed --username admin --password <pw>

--password ist optional: wenn der Admin-User schon existiert, wird das
bestehende Passwort nicht ueberschrieben. So kann install.sh idempotent
erneut laufen, ohne dass der Admin sein Passwort erneut eingeben muss.
"""
from __future__ import annotations

import argparse
import sys

from app.db import SessionLocal
from app.mock_data import MOCK_PRODUCTS, MOCK_USERS
from app.services import seeding


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", default="admin")
    parser.add_argument(
        "--password",
        default="",
        help="Passwort fuer den Admin-User. Nur noetig, wenn der User noch nicht existiert.",
    )
    args = parser.parse_args()

    with SessionLocal() as db:
        result = seeding.ensure_admin_and_mock_products(
            db,
            username=args.username,
            password=args.password,
            mock_products=MOCK_PRODUCTS,
            mock_users=MOCK_USERS,
        )

    if result.user_created:
        print(f"User '{args.username}' angelegt.")
    elif result.user_missing_password:
        print(
            f"[error] Admin-User '{args.username}' existiert nicht und kein Passwort angegeben.",
            file=sys.stderr,
        )
        return 2
    else:
        print(f"User '{args.username}' existiert bereits, Passwort unveraendert.")

    if result.products_added == 0:
        print("Alle Mock-Produkte existieren bereits, nichts zu tun.")
    else:
        print(
            f"{result.products_added} Mock-Produkt(e) angelegt "
            f"(insg. konfiguriert: {len(MOCK_PRODUCTS)})."
        )
    if result.extra_users_added:
        print(f"{result.extra_users_added} Demo-User angelegt (Team-Accounts).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
