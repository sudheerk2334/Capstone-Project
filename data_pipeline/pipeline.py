"""
Zepto catalog ETL pipeline.

Run:
    python data_pipeline/pipeline.py
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "zepto_catalog.db"


@dataclass(frozen=True)
class Product:
    product_id: str
    name: str
    category: str
    price: float
    stock_qty: int


SOURCE_DATA = [
    Product("P001", "Fresh Milk 1L", "Dairy", 62.0, 45),
    Product("P002", "Brown Bread", "Bakery", 48.0, 32),
    Product("P003", "Bananas 1kg", "Fruits", 55.0, 70),
    Product("P004", "Basmati Rice 5kg", "Staples", 520.0, 18),
    Product("P005", "Tomato 1kg", "Vegetables", 42.0, 90),
    Product("P006", "Potato 1kg", "Vegetables", 38.0, 85),
    Product("P007", "Eggs 12 Pack", "Dairy", 96.0, 40),
    Product("P008", "Orange Juice 1L", "Beverages", 115.0, 25),
]


def validate(records: Iterable[Product]) -> list[Product]:
    clean = []
    seen = set()

    for row in records:
        if row.product_id in seen:
            continue
        if not row.name.strip() or not row.category.strip():
            continue
        if row.price < 0 or row.stock_qty < 0:
            continue
        seen.add(row.product_id)
        clean.append(row)

    return clean


def transform(records: Iterable[Product]) -> list[Product]:
    return [
        Product(
            product_id=r.product_id.strip().upper(),
            name=" ".join(r.name.split()),
            category=r.category.strip().title(),
            price=round(float(r.price), 2),
            stock_qty=int(r.stock_qty),
        )
        for r in records
    ]


def load(records: Iterable[Product], db_path: Path = DB_PATH) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute("DROP TABLE IF EXISTS products")
        conn.execute(
            """
            CREATE TABLE products (
                product_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                price REAL NOT NULL,
                stock_qty INTEGER NOT NULL,
                loaded_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.executemany(
            """
            INSERT INTO products(product_id, name, category, price, stock_qty)
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                (r.product_id, r.name, r.category, r.price, r.stock_qty)
                for r in records
            ],
        )
        conn.commit()


def quality_report(db_path: Path = DB_PATH) -> dict:
    with sqlite3.connect(db_path) as conn:
        total, nulls, negative_prices = conn.execute(
            """
            SELECT
                COUNT(*),
                SUM(CASE WHEN product_id IS NULL OR name IS NULL THEN 1 ELSE 0 END),
                SUM(CASE WHEN price < 0 THEN 1 ELSE 0 END)
            FROM products
            """
        ).fetchone()

        categories = conn.execute(
            "SELECT category, COUNT(*) FROM products GROUP BY category ORDER BY category"
        ).fetchall()

    return {
        "rows_loaded": total,
        "null_critical_fields": nulls or 0,
        "negative_prices": negative_prices or 0,
        "categories": dict(categories),
    }


def main() -> None:
    validated = validate(SOURCE_DATA)
    transformed = transform(validated)
    load(transformed)
    report = quality_report()

    print("ETL completed successfully.")
    print(json_like(report))


def json_like(value):
    import json
    return json.dumps(value, indent=2)


if __name__ == "__main__":
    main()
