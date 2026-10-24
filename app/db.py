import sqlite3
from pathlib import Path

from flask import current_app, g


SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS shops (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    failed_pin_attempts INTEGER NOT NULL DEFAULT 0,
    locked_until INTEGER
);
CREATE TABLE IF NOT EXISTS items (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    unit TEXT NOT NULL,
    quantity_rule TEXT NOT NULL CHECK (quantity_rule IN ('decimal', 'whole'))
);
CREATE TABLE IF NOT EXISTS shop_items (
    shop_id TEXT NOT NULL REFERENCES shops(id) ON DELETE CASCADE,
    item_id TEXT NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    quantity_decimal TEXT NOT NULL,
    low_stock_limit_decimal TEXT NOT NULL,
    PRIMARY KEY (shop_id, item_id)
);
CREATE TABLE IF NOT EXISTS price_history (
    shop_id TEXT NOT NULL REFERENCES shops(id) ON DELETE CASCADE,
    item_id TEXT NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    price_date TEXT NOT NULL,
    price_paise INTEGER NOT NULL CHECK (price_paise >= 0),
    PRIMARY KEY (shop_id, item_id, price_date)
);
"""


def connect_db(database=None):
    path = Path(database or current_app.config["DATABASE"])
    # Create the parent on demand so a fresh checkout needs no manual folder step.
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def get_db():
    if "db" not in g:
        g.db = connect_db()
    return g.db


def close_db(_error=None):
    connection = g.pop("db", None)
    if connection is not None:
        connection.close()


def initialize_database(app):
    Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)
    from .seed import seed_if_empty

    with app.app_context():
        db = connect_db()
        try:
            db.executescript(SCHEMA)
            columns = {row["name"] for row in db.execute("PRAGMA table_info(shops)")}
            if "failed_pin_attempts" not in columns:
                db.execute("ALTER TABLE shops ADD COLUMN failed_pin_attempts INTEGER NOT NULL DEFAULT 0")
            if "locked_until" not in columns:
                db.execute("ALTER TABLE shops ADD COLUMN locked_until INTEGER")
            db.commit()
            seed_if_empty(db)
        finally:
            db.close()
    app.teardown_appcontext(close_db)
