import hmac
import re
import secrets
import sqlite3
from datetime import date
from decimal import Decimal, InvalidOperation

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from .auth import authenticate_shop, valid_pin_format
from .charts import prepare_seven_day_chart
from .db import get_db

bp = Blueprint("pages", __name__)
PRICE_PATTERN = re.compile(r"^[0-9]{1,16}(?:\.[0-9]{1,2})?$")


def _csrf_token():
    token = session.get("_csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        session["_csrf_token"] = token
    return token


def _valid_csrf_token():
    expected = session.get("_csrf_token", "")
    supplied = request.form.get("csrf_token", "")
    return bool(expected and supplied and hmac.compare_digest(expected, supplied))


@bp.app_context_processor
def inject_csrf_token():
    return {"csrf_token": _csrf_token}


def format_rupees(paise):
    if paise is None:
        return None
    value = f"{Decimal(paise) / 100:.2f}"
    return value.rstrip("0").rstrip(".")


def format_quantity(value):
    number = Decimal(str(value))
    text = format(number, "f")
    return text.rstrip("0").rstrip(".") if "." in text else text


def _shops(db):
    return db.execute("SELECT id, name FROM shops ORDER BY rowid").fetchall()


def _render_vendor(db, shop_id, error=None, form_values=None):
    shops = _shops(db)
    selected = next((shop for shop in shops if shop["id"] == shop_id), shops[0] if shops else None)
    if selected is None:
        return render_template("vendor.html", shops=[], selected_shop_id="", error="No local shop data is available yet."), 503

    unlocked = session.get("vendor_shop_id") == selected["id"]
    items = []
    selected_item = None
    if unlocked:
        today = date.today().isoformat()
        rows = db.execute(
            """SELECT i.id, i.name, i.unit, i.quantity_rule,
                      si.quantity_decimal, si.low_stock_limit_decimal, p.price_paise
               FROM shop_items AS si
               JOIN items AS i ON i.id = si.item_id
               LEFT JOIN price_history AS p
                 ON p.shop_id = si.shop_id AND p.item_id = si.item_id
                AND p.price_date = (
                    SELECT MAX(ph.price_date) FROM price_history AS ph
                    WHERE ph.shop_id = si.shop_id AND ph.item_id = si.item_id AND ph.price_date <= ?
                )
               WHERE si.shop_id = ? ORDER BY i.rowid""",
            (today, selected["id"]),
        ).fetchall()
        for row in rows:
            quantity = Decimal(row["quantity_decimal"])
            limit = Decimal(row["low_stock_limit_decimal"])
            items.append({
                "id": row["id"], "name": row["name"], "unit": row["unit"],
                "quantity_rule": row["quantity_rule"],
                "quantity": format_quantity(quantity),
                "low_stock_limit": format_quantity(limit),
                "low_stock": quantity <= limit,
                "price_paise": row["price_paise"],
                "price": format_rupees(row["price_paise"]),
            })
        requested_item = request.args.get("item_id") or (form_values or {}).get("item_id")
        selected_item = next((item for item in items if item["id"] == requested_item), items[0] if items else None)
        if selected_item and form_values:
            selected_item = {**selected_item, **form_values}

    return render_template(
        "vendor.html", shops=shops, selected_shop_id=selected["id"],
        selected_shop_name=selected["name"], unlocked=unlocked,
        items=items, selected_item=selected_item, error=error,
        form_values=form_values or {},
    )


@bp.get("/")
def buyer():
    db = get_db()
    shops = _shops(db)
    if not shops:
        return render_template("buyer.html", shops=[], items=[], selected_shop_id="", error="No local shop data is available yet."), 503

    requested_shop = request.args.get("shop_id", "")
    shop_ids = {shop["id"] for shop in shops}
    selected_shop_id = requested_shop if requested_shop in shop_ids else shops[0]["id"]
    today = date.today().isoformat()
    rows = db.execute(
        """SELECT i.id, i.name, i.unit, si.quantity_decimal, si.low_stock_limit_decimal,
                  p.price_paise, p.price_date
           FROM shop_items AS si
           JOIN items AS i ON i.id = si.item_id
           LEFT JOIN price_history AS p
             ON p.shop_id = si.shop_id AND p.item_id = si.item_id
            AND p.price_date = (
                SELECT MAX(ph.price_date) FROM price_history AS ph
                WHERE ph.shop_id = si.shop_id AND ph.item_id = si.item_id AND ph.price_date <= ?
            )
           WHERE si.shop_id = ? ORDER BY i.rowid""",
        (today, selected_shop_id),
    ).fetchall()

    items = []
    for row in rows:
        quantity = Decimal(row["quantity_decimal"])
        limit = Decimal(row["low_stock_limit_decimal"])
        if quantity == 0:
            status, status_label = "out", "Out of stock"
        elif quantity <= limit:
            status, status_label = "few", "Few left"
        else:
            status, status_label = "in", "In stock"
        items.append({
            "id": row["id"], "name": row["name"], "unit": row["unit"],
            "price": format_rupees(row["price_paise"]),
            "price_paise": row["price_paise"],
            "last_price": status == "out", "status": status,
            "status_label": status_label,
        })
    items.sort(key=lambda item: item["status"] == "out")

    # Card chips and the selected chart use the same read-time trend calculation.
    charts = {}
    for item in items:
        item_chart = prepare_seven_day_chart(db, selected_shop_id, item["id"])
        item["falling"] = item_chart["falling"]
        charts[item["id"]] = item_chart

    selected_item_id = request.args.get("item_id", "")
    selected_item = next((item for item in items if item["id"] == selected_item_id), None)
    chart = charts.get(selected_item_id) if selected_item else None
    comparable_prices = db.execute(
        """SELECT si.item_id, si.quantity_decimal, p.price_paise
           FROM shop_items AS si
           JOIN price_history AS p
             ON p.shop_id = si.shop_id AND p.item_id = si.item_id
            AND p.price_date = (
                SELECT MAX(ph.price_date) FROM price_history AS ph
                WHERE ph.shop_id = si.shop_id AND ph.item_id = si.item_id AND ph.price_date <= ?
            )""",
        (today,),
    ).fetchall()
    in_stock_prices = {}
    for row in comparable_prices:
        if Decimal(row["quantity_decimal"]) > 0 and row["price_paise"] is not None:
            in_stock_prices.setdefault(row["item_id"], []).append(row["price_paise"])
    for item in items:
        prices = in_stock_prices.get(item["id"], [])
        item["cheapest_today"] = bool(
            item["status"] != "out" and item["price_paise"] is not None
            and prices and item["price_paise"] == min(prices)
        )
    for item in items:
        item["selected"] = item["id"] == selected_item_id
    selected_shop_name = next(shop["name"] for shop in shops if shop["id"] == selected_shop_id)
    return render_template("buyer.html", shops=shops, items=items,
                           selected_shop_id=selected_shop_id, selected_shop_name=selected_shop_name,
                           selected_item=selected_item, chart=chart)


@bp.get("/vendor")
def vendor():
    db = get_db()
    shops = _shops(db)
    shop_ids = {shop["id"] for shop in shops}
    requested = request.args.get("shop_id")
    authorized_shop = session.get("vendor_shop_id")
    if requested in shop_ids:
        selected_shop_id = requested
        if authorized_shop and authorized_shop != selected_shop_id:
            session.pop("vendor_shop_id", None)
    elif authorized_shop in shop_ids:
        selected_shop_id = authorized_shop
    elif shops:
        selected_shop_id = shops[0]["id"]
    else:
        selected_shop_id = ""
    return _render_vendor(db, selected_shop_id)


@bp.post("/vendor/unlock")
def vendor_unlock():
    db = get_db()
    shop_id = request.form.get("shop_id", "")
    pin = request.form.get("pin", "")
    if not _valid_csrf_token():
        valid_shop = db.execute("SELECT 1 FROM shops WHERE id = ?", (shop_id,)).fetchone()
        return _render_vendor(db, shop_id if valid_shop else "",
                              error="This form expired. Refresh the page and try again."), 400
    valid_shop = db.execute("SELECT 1 FROM shops WHERE id = ?", (shop_id,)).fetchone()
    if not valid_shop:
        session.pop("vendor_shop_id", None)
        return redirect(url_for("pages.vendor"))
    if not valid_pin_format(pin):
        return _render_vendor(db, shop_id, error="Enter your 4-digit shop PIN"), 400

    result = authenticate_shop(db, shop_id, pin)
    if result == "success":
        session["vendor_shop_id"] = shop_id
        return redirect(url_for("pages.vendor", shop_id=shop_id))
    if result == "locked":
        error = "Too many attempts. Try again in 30 seconds."
    else:
        error = "Incorrect PIN. Please try again."
    return _render_vendor(db, shop_id, error=error), 401


@bp.post("/vendor/lock")
def vendor_lock():
    if not _valid_csrf_token():
        shop_id = session.get("vendor_shop_id", "")
        return _render_vendor(get_db(), shop_id,
                              error="This form expired. Refresh the page and try again."), 400
    shop_id = session.pop("vendor_shop_id", "")
    return redirect(url_for("pages.vendor", shop_id=shop_id or None))


def _parse_price(raw):
    value = (raw or "").strip()
    if not value:
        raise ValueError("Enter today's price.")
    if value.startswith("-"):
        raise ValueError("Price cannot be negative.")
    if not PRICE_PATTERN.fullmatch(value):
        raise ValueError("Enter a price with up to 16 whole rupee digits and two decimal places.")
    rupees, _, fraction = value.partition(".")
    return int(rupees) * 100 + int((fraction + "00")[:2])


def _parse_quantity(raw, quantity_rule):
    value = (raw or "").strip()
    if not value:
        raise ValueError("Enter the current stock quantity.")
    if len(value) > 40:
        raise ValueError("Enter a stock quantity with at most 40 characters.")
    try:
        quantity = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError("Enter a valid stock quantity.") from exc
    if not quantity.is_finite() or quantity < 0:
        raise ValueError("Stock quantity cannot be negative.")
    if not re.fullmatch(r"\d+(?:\.\d+)?", value):
        raise ValueError("Enter a valid stock quantity.")
    if quantity_rule == "whole" and not re.fullmatch(r"\d+", value):
        raise ValueError("Eggs must be entered as a whole number of dozens.")
    return quantity


def _quantity_text(quantity):
    text = format(quantity, "f")
    return text.rstrip("0").rstrip(".") if "." in text else text


@bp.post("/vendor/save")
def vendor_save():
    db = get_db()
    shop_id = request.form.get("shop_id", "")
    item_id = request.form.get("item_id", "")
    if not _valid_csrf_token():
        authorized_shop = session.get("vendor_shop_id", "")
        return _render_vendor(db, authorized_shop,
                              error="This form expired. Refresh the page and try again."), 400
    if not shop_id or session.get("vendor_shop_id") != shop_id:
        session.pop("vendor_shop_id", None)
        return redirect(url_for("pages.vendor", shop_id=shop_id or None))

    item = db.execute(
        """SELECT i.name, i.quantity_rule, si.low_stock_limit_decimal
           FROM items AS i JOIN shop_items AS si ON si.item_id = i.id
           WHERE i.id = ? AND si.shop_id = ?""",
        (item_id, shop_id),
    ).fetchone()
    if item is None:
        return _render_vendor(db, shop_id, error="Choose an item from this local shop."), 400

    form_values = {"item_id": item_id, "price_input": request.form.get("price", ""),
                   "quantity_input": request.form.get("quantity", "")}
    try:
        price_paise = _parse_price(form_values["price_input"])
        quantity = _parse_quantity(form_values["quantity_input"], item["quantity_rule"])
    except ValueError as exc:
        return _render_vendor(db, shop_id, error=str(exc), form_values=form_values), 400

    today = date.today().isoformat()
    try:
        db.execute("BEGIN IMMEDIATE")
        db.execute("UPDATE shop_items SET quantity_decimal = ? WHERE shop_id = ? AND item_id = ?",
                   (_quantity_text(quantity), shop_id, item_id))
        db.execute(
            """INSERT INTO price_history(shop_id, item_id, price_date, price_paise)
               VALUES (?, ?, ?, ?)
               ON CONFLICT(shop_id, item_id, price_date)
               DO UPDATE SET price_paise = excluded.price_paise""",
            (shop_id, item_id, today, price_paise),
        )
        db.commit()
    except sqlite3.Error:
        db.rollback()
        return _render_vendor(db, shop_id, error="Could not save the update. Please try again."), 500

    flash(f"Saved {item['name']}. The buyer page will show the update after refresh.", "success")
    return redirect(url_for("pages.vendor", shop_id=shop_id, item_id=item_id))
