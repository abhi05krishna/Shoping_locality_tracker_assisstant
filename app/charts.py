from datetime import date, timedelta
from decimal import Decimal


def _format_rupees(paise):
    value = f"{Decimal(paise) / 100:.2f}"
    return value.rstrip("0").rstrip(".")


def prepare_seven_day_chart(db, shop_id, item_id, today=None):
    """Fill gaps in the requested date window from the latest preceding price."""
    today = today or date.today()
    first_day = today - timedelta(days=6)
    rows = db.execute(
        """SELECT price_date, price_paise FROM price_history
           WHERE shop_id = ? AND item_id = ? AND price_date <= ? ORDER BY price_date""",
        (shop_id, item_id, today.isoformat()),
    ).fetchall()
    by_date = {date.fromisoformat(row["price_date"]): row["price_paise"] for row in rows}
    previous = db.execute(
        """SELECT price_paise FROM price_history
           WHERE shop_id = ? AND item_id = ? AND price_date < ?
           ORDER BY price_date DESC LIMIT 1""",
        (shop_id, item_id, first_day.isoformat()),
    ).fetchone()
    carry_price = previous["price_paise"] if previous else None
    filled = False

    for offset in range(7):
        day = first_day + timedelta(days=offset)
        if day in by_date:
            carry_price = by_date[day]
        elif carry_price is not None:
            db.execute(
                """INSERT INTO price_history(shop_id, item_id, price_date, price_paise)
                   VALUES (?, ?, ?, ?)
                   ON CONFLICT(shop_id, item_id, price_date) DO NOTHING""",
                (shop_id, item_id, day.isoformat(), carry_price),
            )
            by_date[day] = carry_price
            filled = True
    if filled:
        db.commit()

    points = []
    for offset in range(7):
        day = first_day + timedelta(days=offset)
        paise = by_date.get(day)
        points.append({
            "date": day.isoformat(), "label": day.strftime("%a"),
            "day_of_month": day.strftime("%d"), "x": 28 + offset * 50, "paise": paise,
            "price": _format_rupees(paise) if paise is not None else None,
        })

    complete = all(point["paise"] is not None for point in points)
    falling = complete and points[-1]["paise"] * 6 < sum(point["paise"] for point in points[:-1])
    values = [point["paise"] for point in points if point["paise"] is not None]
    path_segments = []
    segment = []
    if values:
        low, high = min(values), max(values)
        if low == high:
            low -= 100
            high += 100
        span = high - low
        for index, point in enumerate(points):
            if point["paise"] is None:
                if segment:
                    path_segments.append(" ".join(segment))
                    segment = []
                continue
            x = point["x"]
            y = 105 - ((point["paise"] - low) / span * 70)
            point["x"], point["y"] = x, round(y, 1)
            coord = f"{x},{point['y']}"
            segment.append(("M" if not segment else "L") + coord)
        if segment:
            path_segments.append(" ".join(segment))

    return {
        "points": points, "path_segments": path_segments,
        "complete": complete, "falling": falling,
        "has_prices": bool(values),
    }
