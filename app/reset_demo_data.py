from pathlib import Path

from .db import SCHEMA, connect_db
from .seed import load_sample_data, seed_database


def main():
    print("Stop the app server before resetting demo data.")
    print("This replaces the local demo shops, stock, prices, and history.")
    answer = input("Reset demo data? [y/N] ").strip().lower()
    if answer not in {"y", "yes"}:
        print("Reset cancelled; no data was changed.")
        return 0

    database = Path(__file__).resolve().parent.parent / "instance" / "local_shop.sqlite3"
    database.parent.mkdir(parents=True, exist_ok=True)
    data = load_sample_data()
    db = connect_db(database)
    try:
        db.executescript(SCHEMA)
        seed_database(db, data)
    except Exception as exc:
        db.rollback()
        print(f"Reset failed; the database transaction was rolled back: {exc}")
        return 1
    finally:
        db.close()
    print("Demo data reset complete. Sample prices and history now use today's local date.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
