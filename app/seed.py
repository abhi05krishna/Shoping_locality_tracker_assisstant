import json
import re
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
    if (not amount.is_finite() or amount < 0 or amount.as_tuple().exponent < -2
            or amount.adjusted() > 15):
        raise ValueError(f"Sample prices must be nonnegative, at most 16 whole rupee digits, and have at most two decimals: {value!r}")
    return int(amount * 100)


def load_sample_data(path=SEED_PATH):
    source = Path(path)
    try:
        data = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot read sample data at {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"Sample data at {source} must contain a JSON object.")
    if not isinstance(data.get("items"), list) or len(data["items"]) != 12:
        raise ValueError(f"Sample data at {source} must define exactly 12 catalog items.")
    if not isinstance(data.get("shops"), list) or not 3 <= len(data["shops"]) <= 4:
        raise ValueError(f"Sample data at {source} must define three or four shops.")

    for item in data["items"]:
        if not isinstance(item, dict):
            raise ValueError(f"Every item in {source} must be a JSON object.")
        if any(not isinstance(item.get(field), str) or not item[field].strip()
               for field in ("id", "name", "unit")):
            raise ValueError(f"Each item in {source} needs a nonempty ID, name, and unit.")
        quantity_rule = item.get("quantity_rule")
        if not isinstance(quantity_rule, str) or quantity_rule not in {"decimal", "whole"}:
            raise ValueError(f"{item['name']} in {source} needs a decimal or whole quantity rule.")
        if not isinstance(item.get("prices"), list) or len(item["prices"]) != 7:
            raise ValueError(f"{item['name']} in {source} needs exactly seven sample prices.")
        for price in item["prices"]:
            _price_paise(price)

    item_ids = {item["id"] for item in data["items"]}
    if len(item_ids) != 12:
        raise ValueError(f"Item IDs in {source} must be unique.")
    item_rules = {item["id"]: item["quantity_rule"] for item in data["items"]}

    shop_ids = set()
    for shop in data["shops"]:
        if not isinstance(shop, dict):
            raise ValueError(f"Every shop in {source} must be a JSON object.")
        if any(not isinstance(shop.get(field), str) or not shop[field].strip()
               for field in ("id", "name")):
            raise ValueError(f"Each shop in {source} needs a nonempty ID and name.")
        if shop["id"] in shop_ids:
            raise ValueError(f"Shop IDs in {source} must be unique.")
        shop_ids.add(shop["id"])
        if not isinstance(shop.get("pin"), str) or not re.fullmatch(r"[0-9]{4}", shop["pin"]):
            raise ValueError(f"{shop['name']} in {source} needs a four-digit sample PIN.")
        try:
            adjustment = Decimal(str(shop["price_adjustment"]))
        except (KeyError, InvalidOperation, TypeError, ValueError) as exc:
            raise ValueError(f"{shop['name']} in {source} has an invalid price adjustment.") from exc
        if not adjustment.is_finite() or adjustment.as_tuple().exponent < -2:
            raise ValueError(f"{shop['name']} in {source} needs a finite adjustment with at most two decimals.")
        stock_items = shop.get("stock")
        if not isinstance(stock_items, dict) or set(stock_items) != item_ids:
            raise ValueError(f"{shop['name']} in {source} needs stock and a low-stock limit for all 12 items.")
        for item_id, values in stock_items.items():
            if not isinstance(values, dict):
                raise ValueError(f"{shop['name']} in {source} has invalid stock data for {item_id}.")
            try:
                quantity = Decimal(str(values["quantity"]))
                limit = Decimal(str(values["low_stock_limit"]))
            except (KeyError, InvalidOperation, TypeError, ValueError) as exc:
                raise ValueError(f"{shop['name']} in {source} has invalid stock values for {item_id}.") from exc
            if not quantity.is_finite() or not limit.is_finite() or quantity < 0 or limit < 0:
                raise ValueError(f"Stock and limits in {source} must be finite and nonnegative.")
            if item_rules[item_id] == "whole" and (quantity != quantity.to_integral_value()
                                                     or limit != limit.to_integral_value()):
                raise ValueError(f"Whole-number items in {source} need integer stock and limits.")
    default_shop_id = data.get("default_shop_id")
    if not isinstance(default_shop_id, str) or default_shop_id not in shop_ids:
        raise ValueError(f"The default shop in {source} must match one of its shop IDs.")
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
