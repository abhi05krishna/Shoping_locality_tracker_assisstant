import json
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path

from flask import current_app


SEED_PATH = Path(__file__).resolve().parent.parent / "data" / "sample_data.json"


def _price_paise(value):
    try:
        amount = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError(f"Invalid sample price: {value!r}") from exc
    if not amount.is_finite() or amount < 0 or amount.as_tuple().exponent < -2:
        raise ValueError(f"Sample prices must be nonnegative with at most two decimals: {value!r}")
    return int(amount * 100)


def load_sample_data(path=SEED_PATH):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot read sample data at {path}: {exc}") from exc
    if not isinstance(data.get("items"), list) or len(data["items"]) != 12:
        raise ValueError("Sample data must define exactly 12 catalog items.")
    if not isinstance(data.get("shops"), list) or not 3 <= len(data["shops"]) <= 4:
        raise ValueError("Sample data must define three or four shops.")
    item_ids = {item["id"] for item in data["items"]}
    if len(item_ids) != 12 or data.get("default_shop_id") not in {shop["id"] for shop in data["shops"]}:
        raise ValueError("Sample item IDs must be unique and the default shop must exist.")
    for item in data["items"]:
        if len(item.get("prices", [])) != 7:
            raise ValueError(f"{item['name']} needs exactly seven sample price values.")
        for price in item["prices"]:
            _price_paise(price)
    for shop in data["shops"]:
        if set(shop.get("stock", {})) != item_ids:
            raise ValueError(f"Shop {shop.get('name', shop.get('id'))} must have stock and a low-stock limit for all 12 items.")
        for values in shop["stock"].values():
            quantity = Decimal(str(values["quantity"]))
            limit = Decimal(str(values["low_stock_limit"]))
            if not quantity.is_finite() or not limit.is_finite() or quantity < 0 or limit < 0:
                raise ValueError("Sample quantities and low-stock limits must be finite and nonnegative.")
    return data


def seed_database(db, data, today=None):
    today = today or date.today()
    db.execute("DELETE FROM price_history")
    db.execute("DELETE FROM shop_items")
    db.execute("DELETE FROM items")
    db.execute("DELETE FROM shops")

    db.executemany("INSERT INTO shops(id, name) VALUES (?, ?)",
                    [(shop["id"], shop["name"]) for shop in data["shops"]])
    db.executemany("INSERT INTO items(id, name, unit, quantity_rule) VALUES (?, ?, ?, ?)",
                    [(item["id"], item["name"], item["unit"], item["quantity_rule"])
                     for item in data["items"]])

    for shop in data["shops"]:
        for item in data["items"]:
            stock = shop["stock"][item["id"]]
            db.execute(
                "INSERT INTO shop_items(shop_id, item_id, quantity_decimal, low_stock_limit_decimal) VALUES (?, ?, ?, ?)",
                (shop["id"], item["id"], str(stock["quantity"]), str(stock["low_stock_limit"])),
            )
            adjustment = Decimal(str(shop["price_adjustment"]))
            for offset, price in enumerate(item["prices"]):
                price_paise = _price_paise(Decimal(str(price)) + adjustment)
                price_day = today - timedelta(days=6 - offset)
                db.execute(
                    "INSERT INTO price_history(shop_id, item_id, price_date, price_paise) VALUES (?, ?, ?, ?)",
                    (shop["id"], item["id"], price_day.isoformat(), price_paise),
                )
    db.commit()


def seed_if_empty(db):
    if db.execute("SELECT 1 FROM shops LIMIT 1").fetchone() is not None:
        return
    data = load_sample_data()
    seed_database(db, data)
    current_app.logger.info("Initialized local database with sample shops and prices.")
