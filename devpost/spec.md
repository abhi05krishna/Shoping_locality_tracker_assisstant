---
doc: spec
status: approved
---

# Local Shop Stock and Price Tracker — Technical Spec

## How This Works, In Plain Language

The app has one Python process running on the student's computer. Flask receives page requests, checks vendor input, and writes saved prices and quantities to a small SQLite database file. The browser gets finished HTML pages; React, a separate database server, and cloud services are not needed.

The sample-data JSON file is the recipe for the demo: shop names and sample PINs, the 12 fixed item units, each shop's sample stock and low-stock limit, and each price pattern. On first run, the app loads that recipe into SQLite. Before recording, `reset-demo-data` asks for confirmation (default is No); after confirmation it reloads the recipe and generates seven dates ending on the computer's current local date, so the chart and required demo states are ready again.

When a vendor saves, Flask checks the values and writes the new stock and today's price point to SQLite. Prices are stored as integer paise, never binary floats. A unique `(shop_id, item_id, price_date)` key keeps one price point per day; a second save replaces that day's value. When the buyer refreshes, Flask reads those saved rows and renders the updated card and SVG chart.

The configured PINs stay in `data/sample_data.json` and are read by Python on the server. The PIN the vendor types is sent to Flask over the local connection for checking; the configured PIN is never put in HTML, JavaScript, a browser response, or a session cookie. After a correct PIN, the signed Flask session remembers only the unlocked shop ID. These are demo PINs, not real credentials or full account security.

### Save-to-buyer flow

```text
Vendor page
  └─ POST entered price + quantity ──> Flask route
                                        ├─ validates input and shop access
                                        └─ SQLite transaction
                                             ├─ updates current stock
                                             └─ upserts (shop, item, date) price
                                                        │
Buyer refresh <── rendered HTML + SVG chart <── Flask reads SQLite
```

PRD refs: `prd.md > The Core Journey`, `Vendor access and stock updates`, `Buyer browsing and item details`, `Sample catalog, prices, and history`, and `Demo data reset`.

## The Core Journey Through the System

1. On first run, the app creates `instance/` automatically before opening `instance/local_shop.sqlite3`. `GET /` asks `app/routes.py` for the first sample shop and its listings; Jinja renders the item cards. The first seeded shop is chosen in `sample_data.json` so its first view includes a falling-price item, a few-left item, and an out-of-stock item.
2. The buyer changes the shop picker or opens an item. A normal page request reads that shop's records. For an item, `app/charts.py` prepares the latest seven consecutive dates and computes the falling-price label; the template draws the seven points as inline SVG.
3. On `/vendor`, the shop picker and four-digit PIN form are rendered without any configured PIN values. A POST sends the entered PIN to the server. Python compares it with the selected shop's PIN from the seed file. Failures and the 30-second lockout are recorded in SQLite. Success stores the authorized shop ID in Flask's signed session, not the PIN.
4. The authorized vendor selects an item and submits price and quantity to Flask. The server validates units, decimal rules, nonnegative values, and current authorization. One SQLite transaction updates inventory and inserts or replaces today's price point.
5. Flask returns a success message and keeps the vendor session open. The buyer refreshes `/`; the same SQLite data now renders the new stock status, today's price, and chart point. `Lock` or switching shops ends the vendor access for the old shop.
6. Before recording, stop the local server and run `reset-demo-data.cmd`. It asks `Reset demo data? [y/N]`; any answer other than `y` or `yes` cancels without changes. After confirmation, `app/reset_demo_data.py` recreates its shop-item records and rolling seven-day prices relative to the local date, resets demo PIN attempt counters, and reports completion.

PRD ref: `prd.md > The Core Journey` and `Vendor access and stock updates`.

## Stack

| Choice | Why it fits | Alternative and tradeoff |
|---|---|---|
| Python 3.13.5 | Already installed in this workspace; familiar to the learner and compatible with the selected Flask line. | Installing a newer runtime adds setup without helping this proof of concept. |
| Flask 3.1.3 | One small local server handles routes, HTML templates, forms, static files, and the reset command. The Flask 3.1.x documentation supports Python 3.9 and newer; the official changelog lists 3.1.3. | FastAPI or a larger full-stack framework brings features this two-page local app does not need. |
| Jinja templates + HTML/CSS + light vanilla JS | Server-rendered pages avoid a frontend build pipeline. CSS handles the Bento Grid; one small JS file persists the optional theme choice. | React is familiar and strong for component-heavy interfaces, but React/Vite adds a Node toolchain and a separate frontend build/dev-server path; React is intentionally out to protect the schedule. |
| SQLite through Python `sqlite3` | A local disk database persists updates without running another service. A composite unique key enforces one price per shop-item-day. | JSON-only live storage is simpler at first but makes reliable updates and uniqueness constraints harder. SQLite stays small and has transactions. |
| Inline SVG chart | Seven points can be rendered directly by the server with no chart package, network request, or JavaScript chart state. | Chart.js would add convenient chart interactions that the seven-day chart does not need. |
| One JSON sample-data file | Keeps item units, shop PINs, per-shop sample values, thresholds, and trend patterns together for easy edits and repeatable reset. | Scattered Python constants are harder to maintain as one sample item definition. |

The official Flask 3.1.3 changelog and installation guidance, Flask template/static-file guidance, Python SQLite and virtual-environment references, and the browser SVG reference are linked under **External Services and Dependencies**.

## Where It Runs and How Someone Tries It

- **Runtime:** local Windows computer, one Flask process bound only to `127.0.0.1`; no LAN access, API keys, cloud services, or deployment.
- **Prerequisite:** Python 3.13.5 is installed in the current workspace. `setup.cmd` creates `.venv` and installs the pinned Flask dependency once.
- **Start:** run `run.cmd`, then open `http://127.0.0.1:5000/` for the public buyer page or `http://127.0.0.1:5000/vendor` for the vendor page.
- **Reset for recording:** stop the server, run `reset-demo-data.cmd`, confirm with `y`/`yes`, then run `run.cmd`. The reset command first prints “Stop the app server before resetting demo data.” It then asks for confirmation, prints a completion message, and reseeds history relative to today's local date; declining leaves the database untouched.
- **Submission:** record the short demo video from the local app and publish the public GitHub repository. Deployment is optional; it does not replace the video or repository.
- Flask's built-in server is suitable for this local demo and is not the production deployment server described in Flask's docs.

## Look and Feel

Implement the approved Bento Grid style with responsive CSS: light background, rounded tiles, fresh green/amber/grey status colors, and bold prominent prices. The buyer header has a clear, visible “Vendor” link. Keep badge wording visible so meaning does not depend on color alone. On phones, stack the shop picker, cards, and selected item's chart tile. Do not add search; buyers browse the small catalog directly and choose a shop from the picker. The vendor form uses large fields and a clear Save button, plus the required Lock control. Avoid blur, 3D, and animation. Dark mode is optional and last in the build sequence; if included, use one toggle and `localStorage` to remember it. If time is short, omit the theme script and retain the light theme.

PRD ref: `prd.md > Screens and Layout` and `Look and Feel`.

## Components

### Flask app and page routes — `app/__init__.py`, `app/routes.py`

Create the Flask app, register page/form routes, open database connections per request, and render buyer/vendor templates. The buyer header links directly to `/vendor`; do not add a search control. Use `GET /` for the buyer view, `GET /vendor` for vendor selection/access, and POST routes for unlock, save, and lock. After save, use a redirect back to the vendor page with a success message; the buyer reads the new values on refresh.

Implements `prd.md > The Core Journey`, `Buyer browsing and item details`, and `Vendor access and stock updates`.

### Data access — `app/db.py`

Create `instance/` automatically with parent creation enabled before the first SQLite connection, then create the SQLite schema on first run, enable foreign keys, and provide small functions for reading a shop's inventory/history and saving an update in one transaction. The `price_history` table has a unique key over `(shop_id, item_id, price_date)`; use SQLite upsert on that exact shop-item-date key so same-day saves replace the single point. Store prices only as integer paise (₹40.25 becomes 4025), never as binary floats, to keep two-decimal rupee arithmetic exact. Store fractional quantities and thresholds as normalized decimal strings, parse and compare them with Python `Decimal`, and format them using the fixed unit.

Implements `prd.md > Vendor access and stock updates`, `Sample catalog, prices, and history`, and `Theme and persistence`.

### Seed loader and reset command — `data/sample_data.json`, `app/seed.py`, `app/reset_demo_data.py`

`sample_data.json` is the only editable source for shops, demo PINs, items, units, per-shop stock, per-shop thresholds, sample price patterns, and the default buyer shop. Seed prices as strings with up to two decimal places, then convert to integer paise before inserting them into SQLite. The seed loader validates catalog shape before writing it.

On a missing/empty database, create `instance/` if needed and seed the local DB automatically. Before reset, print “Stop the app server before resetting demo data.”, state that current local demo shops, stock, prices, and history will be replaced, then ask `Reset demo data? [y/N]`; any response other than `y` or `yes` cancels without changes. After confirmation, clear and reseed only this demo database in one transaction. Map the seven price values onto the local dates from `today - 6 days` through today. Choose price patterns and initial quantities so the default buyer shop visibly demonstrates falling, few-left, and out-of-stock states. When a buyer requests the chart's latest seven dates, fill any missing calendar dates forward from the latest preceding saved price at read time and persist the carry-forward rows idempotently. When a vendor saves, upsert today's point using `(shop_id, item_id, price_date)` so today's point is replaced rather than duplicated.

PIN strings in the JSON are sample values only, never real credentials. List the demo PINs in the README and label them clearly as sample values only. Do not copy PINs into templates, JavaScript, logs, or browser responses.

Implements `prd.md > Sample catalog, prices, and history`, `Demo data reset`, and `States and Boundaries`.

### Vendor PIN gate and session — `app/auth.py`, `app/routes.py`

Validate that PIN input contains exactly four digits before comparison. Compare the entered value on the server against the selected shop's PIN in the seed data. Keep the wrong-attempt counter and `locked_until` in SQLite per shop, so refreshing or restarting the server cannot bypass that shop's cooldown. After the fifth wrong PIN, block that shop for 30 seconds; after cooldown clear that shop's attempt count. Keep the vendor unlocked after Save using Flask's signed session, which stores only the authorized shop ID. A shop change or Lock clears the authorized shop from the session and returns to PIN entry. Do not pass seed PINs to Jinja context or serialize them to the browser.

Flask's default session cookie is signed, not encrypted; its only value here is a non-secret shop ID. A per-run random signing key means a server restart requires the vendor to enter the PIN again. The local-only four-digit demo PIN is not production authentication.

Implements `prd.md > Vendor access and stock updates` and `States and Boundaries`.

### Buyer cards and SVG chart — `app/charts.py`, `app/templates/buyer.html`, `app/static/css/app.css`

Read shop-specific listings and the latest seven dates from SQLite. At chart read time, fill missing dates from the latest preceding saved price and persist those carry-forward rows idempotently; if today's row is missing, carry forward the last saved price. Calculate the average of the preceding six daily prices; show “Price falling” only when today's price is strictly lower. Render one inline SVG line chart with labels and a readable no-history state when the comparison baseline is incomplete. Render stock state by quantity: zero is out of stock; positive quantity at/below the fixed threshold is few left; above threshold is in stock. Sort out-of-stock cards last and label their displayed value “Last price.”

Implements `prd.md > Buyer browsing and item details` and `Sample catalog, prices, and history`.

### Vendor editor — `app/templates/vendor.html`, `app/routes.py`, `app/db.py`

Render a single tile for shop selection/PIN, then item selection and price/quantity form after server authorization. Validate every field again on the server: required, nonnegative price/quantity, no more than two price decimals, fractional quantities for kg/litre items, whole-number dozens for eggs. Zero quantity is valid. On valid submit, update stock and the one point for today's price atomically. Show a confirmation and vendor-only low-stock flag; do not close the session after Save. Provide Lock to clear access.

Implements `prd.md > Vendor access and stock updates`.

### Local theme — `app/static/js/theme.js`, `app/static/css/app.css`

Only if time remains after the core loop and polish: add a light/dark toggle and save the selection in browser `localStorage`. It does not affect shop data or the database. This component is the first to cut if timing slips.

Implements optional behavior from `prd.md > Look and Feel` and `Theme and persistence`.

## Data Model

| Table/source | Fields and role | Persistence/update |
|---|---|---|
| `data/sample_data.json` | Canonical seed definitions: shop IDs/names/sample PINs; item IDs/names/unit/quantity precision; per-shop-item seed quantity, threshold, and seven relative price values; initial buyer shop. | Versioned with the project. The reset command reads it; the app server uses it to check sample PINs. |
| `shops` | `id`, `name`, `failed_pin_attempts`, `locked_until`. No PIN column. | SQLite; server-side failed-attempt counter and cooldown timestamp are kept per shop and reset after cooldown or demo reset. |
| `items` | `id`, `name`, fixed `unit`, quantity rule (`decimal` or `whole`). | Seeded from JSON. |
| `shop_items` | `shop_id`, `item_id`, `quantity_decimal`, `low_stock_limit_decimal`; composite primary key. | Seeded from JSON; vendor save changes quantity. |
| `price_history` | `shop_id`, `item_id`, `price_date` (local ISO date), integer `price_paise`; unique `(shop_id,item_id,price_date)`. Prices are never binary floats. | Seeded from JSON and updated by upsert on `(shop_id,item_id,price_date)`. A same-day save replaces the existing point. Rows persist across app restarts. |
| Flask signed session | `vendor_shop_id` only; never the PIN. | Browser cookie signed by the server key; remains unlocked through Save, and clears on Lock, shop switch, or server restart. |
| Browser `localStorage` | Optional theme preference only. | Per browser, independent of shop data; omit if dark mode is cut. |

## File Structure

```text
mandi-tracker/
├── app/
│   ├── __init__.py               # Flask app factory and first-run setup
│   ├── routes.py                 # buyer, vendor, unlock, save, and lock routes
│   ├── db.py                     # schema, reads, transactions, upsert
│   ├── auth.py                   # server-side PIN validation and session helpers
│   ├── seed.py                   # sample-data validation and local-date seeding
│   ├── charts.py                 # date window, trend rule, SVG point data
│   ├── reset_demo_data.py        # reset-demo-data command target
│   ├── templates/
│   │   ├── base.html             # shared shell, status messages
│   │   ├── buyer.html            # shop picker, cards, item chart tile
│   │   └── vendor.html           # PIN gate and vendor update tile
│   └── static/
│       ├── css/app.css           # responsive Bento Grid and status styles
│       └── js/theme.js           # optional last-priority dark-mode toggle
├── data/
│   └── sample_data.json          # one editable seed source; sample PINs stay server-side
├── instance/
│   └── local_shop.sqlite3        # generated on first run; instance/ is created automatically and DB is ignored by Git
├── setup.cmd                     # create .venv and install dependencies
├── run.cmd                       # start Flask bound to 127.0.0.1
├── reset-demo-data.cmd           # confirm, then run Python reseed command
├── run.py                        # Flask entry point for the CLI
├── requirements.txt              # Flask==3.1.3
├── README.md                     # Windows setup/run/record/reset instructions
├── .gitignore                    # ignore .venv, instance DB, caches, environment secrets; leave plans tracked
└── devpost/                      # planning artifacts; not application runtime
```

## External Services and Dependencies

No external service, account, API key, or network API is required at runtime.

- [Flask 3.1.x Quickstart](https://flask.palletsprojects.com/en/stable/quickstart/) — routes, templates, and local app entry point.
- [Flask installation and dependency docs](https://flask.palletsprojects.com/en/stable/installation/) — Flask includes Jinja and supports Python 3.9+; the project's version pin is Flask 3.1.3.
- [Flask 3.1.3 changelog](https://flask.palletsprojects.com/en/stable/changes/) — release reference.
- [Python `sqlite3`](https://docs.python.org/3/library/sqlite3.html) — local disk database through the standard library, no separate process.
- [Python `venv`](https://docs.python.org/3/library/venv.html) — isolated Windows dependencies.
- [Python `json`](https://docs.python.org/3/library/json.html) — reading the canonical sample-data file.
- [MDN SVG reference](https://developer.mozilla.org/en-US/docs/Web/SVG) — inline SVG chart elements.
- React was considered but omitted; the [React setup guide](https://react.dev/learn/build-a-react-app-from-scratch) describes using a build tool such as Vite for a local React app, which would add setup not needed for these screens.

## Important Failure Modes

- **Port 5000 is busy** → show Flask's clear startup error; use the documented local fallback port 5001 and open `http://127.0.0.1:5001/`.
- **Invalid JSON or missing sample data** → stop seeding, print the file path and actionable parse/validation message, and do not partially clear an existing database.
- **SQLite write error or locked database** → rollback the update/reset transaction and show a plain error; instruct the user to stop the app before running reset.
- **No recent price history** → show available chart data and “No price history yet”; do not show “Price falling.”
- **Incorrect PIN or lockout** → show the PRD's exact message, keep shop data hidden, and leave stock/price unchanged.

## What Was Simplified and Why

- **Server-rendered Flask pages** instead of React/Vite + a separate API server — the buyer/vendor flow is small and the learner prioritized Windows reliability and one local process; the tradeoff is less client-side component reuse.
- **SQLite** instead of a hosted database — persistent data and unique daily-price constraints without service setup; the tradeoff is no shared multi-device data, which is outside the local-only POC.
- **Inline SVG** instead of a chart dependency — enough for seven points and works offline; the tradeoff is no built-in zoom or elaborate chart interactions.
- **Sample PIN gate** instead of account authentication — demonstrates shop-specific updates locally; the tradeoff is explicitly not production security.
- **Resettable seeded records** instead of real shop integrations — makes the demo reproducible and its statuses guaranteed; values are labeled sample data.
- **Dark mode last and optional** — preserves time for the end-to-end loop and polish.

## Build Sequence for `5-build`

| Order | Task | Rough estimate |
|---:|---|---:|
| 1 | Bootstrap the local app as a usable seeded buyer page: create the public GitHub remote and push the approved planning docs; first-run database creation, sample JSON, shop picker/cards, reset command, setup/run scripts, and README. | 80 min |
| 2 | Complete the end-to-end vendor-to-buyer update: PIN checks and lockout, signed session, validated vendor save, transactional same-day upsert, and buyer refresh. | 65 min |
| 3 | Add the seven-day SVG trend, read-time carry-forward with persisted gaps, falling-price comparison, and no-history state. | 40 min |
| 4 | Make the core flow phone-friendly and resolve PRD edge cases through the manual checklist. | 55 min |
| 5 | Optional remembered dark mode. **First to cut if time is short.** | 20 min |
| 6 | Prepare the public submission: verify the repo contains the three planning docs and reset command, create the demo recording, and save a learner-reviewed project description. | 60 min |

Estimated active work: **5 hours 20 minutes** with dark mode and **5 hours** without it. Estimates are rough and include the public remote and submission artifacts; the demo recording time varies with retakes. Tasks 1–2 establish the seed-to-buyer view and complete the core vendor-save loop before the chart and polish.

## Manual Verification Checklist

Derived from `prd.md > The Core Journey`, `Buyer browsing and item details`, `Vendor access and stock updates`, `Sample catalog, prices, and history`, `Demo data reset`, and `States and Boundaries`.

- [ ] On first open, the default shop shows all 12 items with fixed unit prices and at least one falling-price, one “Few left,” and one out-of-stock example.
- [ ] Changing the buyer shop changes the listed shop data; buyer access remains public.
- [ ] Normal, few-left, and out-of-stock labels and order are correct. Out-of-stock cards show “Last price,” sort to the bottom, and still open their chart.
- [ ] The chart contains seven consecutive local dates ending today; a missing date is filled and persisted at read time from the latest preceding saved price.
- [ ] “Price falling” appears only when today's price is below the average of the previous six points; incomplete history shows no trend label.
- [ ] A same-day save replaces the shop-item's price point for today; there is still only one point for that date.
- [ ] Empty/malformed/wrong PIN paths show the specified messages; wrong PIN never reveals shop data or changes it. After five wrong attempts, access is blocked for 30 seconds. PIN values are absent from rendered page source and browser responses.
- [ ] After successful PIN entry, Save keeps the vendor unlocked; switching shops or pressing Lock returns to PIN entry.
- [ ] Empty and negative price/quantity values are rejected; zero quantity saves; fractional kg and litre quantities save; eggs per dozen reject decimals.
- [ ] A valid vendor save shows confirmation, the vendor-only low-stock cue is correct, and buyer refresh shows the updated price/quantity/status and today's chart point.
- [ ] With the server stopped, run `reset-demo-data.cmd`; it prints a reminder to stop the server before asking for confirmation. Choosing No leaves the database unchanged; confirming restores the three required buyer states with dates relative to today and reports completion.
- [ ] Starting with no `instance/` directory creates it automatically and initializes the persistent database.
- [ ] README lists each demo PIN and clearly labels the values as samples only.
- [ ] Close and relaunch the app; saved vendor updates persist. If dark mode was implemented, its preference persists too.
- [ ] On Windows, `setup.cmd` works once and `run.cmd` starts the app at `http://127.0.0.1:5000/` without a second service.

## Decisions and Open Issues

- **Learner-approved:** Flask, SQLite, server-rendered HTML/CSS, light vanilla JavaScript, inline SVG charts, one JSON seed file, local-only operation, no React.
- **Learner-requested:** one diagram of vendor-save data flow, an ordered core-first task list, a manual checklist based on PRD behavior, and server-only PIN checking from seed data.
- **Derived implementation choices:** Flask 3.1.3 with the available Python 3.13.5; SQLite in `instance/`; one local development process on loopback; `.cmd` wrappers for Windows; daily price uniqueness in SQLite; signed session stores shop ID only; update failure rolls back.
- **Git boundary:** Ignore `.venv/` and `instance/local_shop.sqlite3` plus SQLite journal files. Keep `devpost/scope.md`, `devpost/prd.md`, and `devpost/spec.md` trackable; do not add a broad `devpost/` ignore rule. The learner-profile ignore remains separate.
- **Learning focus:** the learner wants to understand architecture and data pipelines. The diagram and journey trace clarify how `sample_data.json` seeds SQLite, how the vendor POST updates it, and how buyer refresh renders the same record. During `5-build`, trace one tomato update through those steps and relate the code files to this section.
- The workspace currently has no Git repository initialized. Task 1 creates the local repository, with `devpost/scope.md`, `devpost/prd.md`, and `devpost/spec.md` left visible to Git; the database and `.venv/` are ignored. No broad `devpost/` ignore is added.
- No consequential decisions remain open before review. The exact sample values and PIN strings will be authored in `sample_data.json` during the build; they are demo values only.
