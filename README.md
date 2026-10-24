# Mandi Nearby

A small local demo that lets a buyer check sample prices and stock at a few local shops. A vendor update flow and seven-day price chart are the next build slices.

## Run on Windows

1. Install Python 3.13 or newer.
2. Run `setup.cmd` once.
3. Run `run.cmd` and open [http://127.0.0.1:5000/](http://127.0.0.1:5000/).

The app runs on this computer only. SQLite data is stored persistently under the ignored `instance/` folder, which the app creates on first run.

## Demo PINs — sample values only

These PINs are public sample values for the local demo. They are not real credentials and must not be reused for any real account:

| Local shop | Demo PIN (sample value only) |
|---|---:|
| Campus Corner Local Shop | `1357` |
| Market Lane Local Shop | `2468` |
| Station Road Local Shop | `9753` |

The app checks the configured PIN on the server. The vendor page does not receive these configured values.

## Reset the demo

Stop the running server first. Then run `reset-demo-data.cmd` and type `y` to confirm. The safe default is No; declining leaves existing demo data unchanged. Reset restores the curated sample shop data and seven-day history relative to the current date.

## Project notes

- `devpost/scope.md`, `devpost/prd.md`, and `devpost/spec.md` are the approved planning documents.
- Prices shown in the seed data are illustrative sample prices; stock and trend examples are curated for the demo.
- Buyer browsing is public. Ordering, payments, delivery, maps, and notifications are outside this small local project.
