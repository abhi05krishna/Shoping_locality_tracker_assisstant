import hmac
import re
import time

from .seed import load_sample_data


PIN_PATTERN = re.compile(r"^[0-9]{4}$")
LOCKOUT_SECONDS = 30
MAX_ATTEMPTS = 5


def valid_pin_format(pin):
    return bool(PIN_PATTERN.fullmatch(pin or ""))


def authenticate_shop(db, shop_id, submitted_pin, now=None):
    """Compare a PIN on the server and persist per-shop throttling state."""
    now = int(time.time() if now is None else now)
    # Serialize simultaneous attempts so two requests cannot both miss the fifth try.
    db.execute("BEGIN IMMEDIATE")
    state = db.execute(
        "SELECT failed_pin_attempts, locked_until FROM shops WHERE id = ?", (shop_id,)
    ).fetchone()
    if state is None:
        db.rollback()
        return "invalid_shop"

    attempts = state["failed_pin_attempts"]
    locked_until = state["locked_until"]
    if locked_until is not None and locked_until > now:
        db.rollback()
        return "locked"
    if locked_until is not None:
        attempts, locked_until = 0, None
        db.execute(
            "UPDATE shops SET failed_pin_attempts = 0, locked_until = NULL WHERE id = ?",
            (shop_id,),
        )

    configured_pin = next(
        (shop["pin"] for shop in load_sample_data()["shops"] if shop["id"] == shop_id), None
    )
    if configured_pin is not None and hmac.compare_digest(submitted_pin, configured_pin):
        db.execute(
            "UPDATE shops SET failed_pin_attempts = 0, locked_until = NULL WHERE id = ?",
            (shop_id,),
        )
        db.commit()
        return "success"

    attempts += 1
    if attempts >= MAX_ATTEMPTS:
        db.execute(
            "UPDATE shops SET failed_pin_attempts = ?, locked_until = ? WHERE id = ?",
            (attempts, now + LOCKOUT_SECONDS, shop_id),
        )
        db.commit()
        return "locked"

    db.execute("UPDATE shops SET failed_pin_attempts = ? WHERE id = ?", (attempts, shop_id))
    db.commit()
    return "incorrect"
