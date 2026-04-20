"""Mock-Produkte fuer Demo.

Zentral gehalten, damit das Seed-Skript (backend/seed.py) und der
DB-Reset-Endpoint (app/routers/settings.py) auf dieselben Daten
zugreifen. Aenderungen hier wirken in beiden Pfaden.
"""
from __future__ import annotations

from decimal import Decimal

MOCK_PRODUCTS: list[dict] = [
    {
        "name": "Sneaker Classic",
        "category": "Schuhe",
        "cost_price": Decimal("29.90"),
        "stock": 42,
        "competitor_price": Decimal("59.00"),
        "monthly_demand": 80,
        "context": (
            "Klassischer Lifestyle-Sneaker fuer Freizeit und Alltag. Der Wettbewerb "
            "liegt je nach Marke zwischen 50 und 80 EUR, wir positionieren uns "
            "preiswert und erwarten gleichmaessigen Absatz ueber den Monat."
        ),
        "strategy": {
            "kind": "formula",
            "config": {"expression": "cost_price * 1.8"},
        },
    },
    {
        "name": "Basic T-Shirt",
        "category": "Bekleidung",
        "cost_price": Decimal("4.50"),
        "stock": 120,
        "competitor_price": Decimal("14.90"),
        "monthly_demand": 200,
        "context": (
            "Einfaches Baumwoll-T-Shirt, hoher Durchsatz. Preiskaempfe in der "
            "Kategorie sind ueblich; bei niedrigem Lager Premium-Marge, "
            "sonst knapp unter dem Wettbewerb."
        ),
        "strategy": {
            "kind": "formula",
            "config": {
                "expression": "(stock < 20) * (cost_price * 2.5) + (stock >= 20) * (competitor_price - 1)"
            },
        },
    },
    {
        "name": "Kaffeebohnen 1kg",
        "category": "Lebensmittel",
        "cost_price": Decimal("9.80"),
        "stock": 30,
        "competitor_price": Decimal("18.50"),
        "monthly_demand": 60,
        "context": (
            "Hochwertige Arabica-Bohnen, 1kg. Kundenstamm ist qualitaetsbewusst, "
            "Premium-Marken im Wettbewerb kosten 18-22 EUR. Nachfrage steigt "
            "gegen Monatsende (Gehaltseingang)."
        ),
        "strategy": {
            "kind": "formula",
            "config": {"expression": "cost_price * 1.8 + (day >= 20) * 0.5"},
        },
    },
    {
        "name": "Yoga-Matte Premium",
        "category": "Sport",
        "cost_price": Decimal("12.40"),
        "stock": 25,
        "competitor_price": Decimal("39.90"),
        "monthly_demand": 45,
        "context": (
            "Rutschfeste Yoga-Matte, 6mm, Naturkautschuk. Wettbewerb 35-45 EUR. "
            "Kuendet sich abends ab 18 Uhr ein hoeherer Absatz an (Feierabend-Sport)."
        ),
        "strategy": {
            "kind": "formula",
            "config": {"expression": "cost_price * 2.5 + (hour >= 18) * 2"},
        },
    },
    {
        "name": "USB-C Ladekabel 1m",
        "category": "Elektronik",
        "cost_price": Decimal("1.20"),
        "stock": 200,
        "competitor_price": Decimal("7.99"),
        "monthly_demand": 320,
        "context": (
            "Standard-USB-C-Ladekabel, hohe Stueckzahlen. Preisdumping in der "
            "Kategorie ist Alltag, Marge kommt ueber Volumen. Bei knappem "
            "Lager keinen Rabatt geben."
        ),
        "strategy": {
            "kind": "formula",
            "config": {"expression": "competitor_price - (stock >= 30) * 1"},
        },
    },
    {
        "name": "Bio-Apfelsaft 1L",
        "category": "Lebensmittel",
        "cost_price": Decimal("1.80"),
        "stock": 80,
        "competitor_price": Decimal("3.49"),
        "monthly_demand": 140,
        "context": (
            "Demeter-zertifizierter Apfelsaft, regional. Wettbewerb in Bio-Maerkten "
            "3-4 EUR. Tagesnachfrage konstant, kein klares Tagesprofil."
        ),
        "strategy": {
            "kind": "fix",
            "config": {"amount": "3.29"},
        },
    },
    {
        "name": "Bluetooth-Kopfhoerer Lite",
        "category": "Elektronik",
        "cost_price": Decimal("18.00"),
        "stock": 60,
        "competitor_price": Decimal("49.00"),
        "monthly_demand": 75,
        "context": (
            "Einsteiger-In-Ear-Kopfhoerer, 8h Akku. Wettbewerb 40-60 EUR. "
            "Bei niedrigem Lager Premium-Aufschlag, sonst Wettbewerb minus 2 EUR."
        ),
        "strategy": {
            "kind": "formula",
            "config": {
                "expression": "competitor_price - 2 + (stock < 20) * 8"
            },
        },
    },
    {
        "name": "Notebook A5 dotted",
        "category": "Buero",
        "cost_price": Decimal("2.80"),
        "stock": 150,
        "competitor_price": Decimal("9.95"),
        "monthly_demand": 90,
        "context": (
            "Punktraster-Notizbuch A5, Hardcover, 200 Seiten. Wettbewerb 8-12 EUR. "
            "Stetige Nachfrage, kleiner Peak Anfang Monat (Planungs-Trend)."
        ),
        "strategy": {
            "kind": "formula",
            "config": {
                "expression": "cost_price * 3 + (day < 5) * 1"
            },
        },
    },
]
