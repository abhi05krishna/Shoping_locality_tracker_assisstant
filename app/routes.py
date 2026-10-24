from datetime import date
from decimal import Decimal

from flask import Blueprint, render_template, request

from .db import get_db

bp = Blueprint("pages", __name__)


def format_rupees(paise):
    if paise is None:
        return None
    value = f"{Decimal(paise) / 100:.2f}"
    return value.rstrip("0").rstrip(".")


@bp.get("/")
def buyer():
    db = get_db()
    shops = db.execute("SELECT id, name FROM shops ORDER BY rowid").fetchall()
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
           WHERE si.shop_id = ?
           ORDER BY i.rowid""",
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
            "last_price": status == "out", "status": status,
            "status_label": status_label,
        })
    items.sort(key=lambda item: item["status"] == "out")
    return render_template(
        "buyer.html", shops=shops, items=items,
        selected_shop_id=selected_shop_id,
        selected_shop_name=next(shop["name"] for shop in shops if shop["id"] == selected_shop_id),
    )


@bp.get("/vendor")
def vendor_placeholder():
    return render_template("vendor.html"), 200
