# Mandi Nearby

Mandi Nearby is a small, local-only demo for checking sample prices and stock at nearby local shops. Buyers can compare shop availability and prices before leaving home. Vendors can update an item's price and quantity, then see that update on the public buyer page after refresh.

## What works

- Public buyer page with a picker for three sample local shops and a fixed 12-item catalog.
- Today’s effective price and unit, plus **In stock**, **Few left**, or **Out of stock** status on each item card.
- **Price falling** card and chart cues when today's price is below the average of the previous six daily prices. The chart shows seven dates ending today; missing dates carry the last saved price forward.
- **Cheapest today** on a shop's card and opened chart when that shop ties for or has the lowest effective price among shops where the item is in stock. Out-of-stock shops are excluded.
- Vendor page protected by a sample PIN per shop. A vendor can change an item's price and current quantity; the buyer sees the saved values after refresh. Low vendor stock is flagged for restocking.
- Mobile-friendly pages, form validation, visible save/error messages, and confirmed demo-data reset.

## Run on Windows

Prerequisite: install Python 3.13 or newer and make sure `python` is available in Command Prompt or PowerShell. Internet access is needed once to install Flask; the running app makes no network/API calls.

```bat
setup.cmd
run.cmd
```

Open [http://127.0.0.1:5000/](http://127.0.0.1:5000/) for the buyer page or [http://127.0.0.1:5000/vendor](http://127.0.0.1:5000/vendor) for vendor updates. If port 5000 is busy, `run.cmd` starts on port 5001; open [http://127.0.0.1:5001/](http://127.0.0.1:5001/) in that case. The process binds to `127.0.0.1`, so it is accessible only from this computer.

The app creates `instance/` automatically and stores persistent SQLite data in `instance/local_shop.sqlite3`. Those runtime files are ignored by Git and remain on this computer across restarts. The JSON catalog in `data/sample_data.json` is the canonical source for the sample items, units, shop PINs, stock, limits, and seed price patterns. Editing that file does not overwrite an existing database; use the reset command to reload it.

## Buyer flow

1. Open the buyer page and choose a local shop.
2. Scan item cards for today's price, fixed unit, availability, price trend, and the **Cheapest today** chip where it applies.
3. Select any card to open its seven-day chart. The page scrolls the chart into view. An out-of-stock item remains available to inspect, but shows its last price rather than presenting it as today's price.

The comparison uses the latest saved price on or before today for each shop-item. **Price falling** requires a complete seven-day history and a strictly lower price today than the average of the prior six days. Tied lowest in-stock shops all qualify as **Cheapest today**.

## Vendor flow

1. Open `/vendor`, choose the shop, and enter its four-digit sample PIN.
2. Select an item, enter today's price in rupees and current quantity in the fixed unit, then save.
3. Refresh the buyer page for that shop to see the updated price and stock status.

Prices must be nonnegative, with up to 16 whole rupee digits and at most two decimal places. Quantities can be zero; kg and litre quantities may be fractional, while eggs are entered as whole dozens. A same-day price save replaces that shop-item's existing point for today. A vendor remains unlocked until changing shops or pressing **Lock**.

### Demo PINs — sample values only

These are public sample values for this demo. They are not real credentials and must never be reused for a real account.

| Local shop | Demo PIN (sample value only) |
|---|---:|
| Campus Corner Local Shop | `1357` |
| Market Lane Local Shop | `2468` |
| Station Road Local Shop | `9753` |

The server checks the PIN from the seed file; configured PIN values are not sent to the browser. The sample PINs are intentionally visible in this public repository.

## Reset sample data

Stop the server first. Run:

```bat
reset-demo-data.cmd
```

The command reminds you to stop the server and asks for confirmation (`y` or `yes`). The default is No; declining leaves the database unchanged. Confirming restores the curated shops, prices, stock states, and seven-day history relative to the current local date. This reset replaces local demo data.

## Data flow and architecture

```text
Vendor form --POST--> Flask validates session, CSRF token, price, and quantity
                           |
                           v
                    SQLite transaction
                    - update stock
                    - upsert today's shop-item price
                           |
Buyer refresh <-- Flask reads SQLite and renders cards plus SVG chart
```

Flask and Jinja render the pages on the server. SQLite stores prices as integer paise and enforces one price row per shop-item-date. The seven-day SVG chart is generated by Python; a small vanilla JavaScript file scrolls the selected chart tile into view. No React, external database, cloud service, payment, order, delivery, search, or user-account system is included.

## Security and demo limits

This is a local proof of concept, not a production inventory or authentication system. Demo PINs are intentionally public and weak; do not enter real shop credentials, personal information, or sensitive inventory data. Vendor forms use signed sessions, server-side validation, per-shop throttling, and CSRF tokens, but the sample PIN gate is not full account security. Data is stored locally without encryption or cloud backup.

## Manual smoke check

- Switch among local shops and confirm the listed prices differ.
- Open a falling-price item and a non-falling item; compare the chip with the chart and confirm the chart scrolls into view.
- Compare the same item across shops; confirm only shops tied for the lowest in-stock price show **Cheapest today**. An out-of-stock shop should not qualify.
- Save a vendor price and quantity, refresh the buyer page, and confirm the update. Try zero stock and a negative value; zero should save as out of stock, while a negative value should be rejected.
- Try an invalid PIN and five failed PIN attempts; confirm the data stays hidden and the short lockout message appears. Submit a vendor form without its session token and confirm it is rejected without changing data.
- Run `reset-demo-data.cmd` with the server stopped and verify the confirmation prompt and the seeded demo states.

There is no separate automated test command in this proof of concept. The build checklist and technical verification steps are in [`devpost/checklist.md`](devpost/checklist.md); the approved scope, PRD, and architecture spec are in `devpost/scope.md`, `devpost/prd.md`, and `devpost/spec.md`.
