---
doc: prd
status: approved
---

# Local Shop Stock and Price Tracker — Product Requirements

A locally running stock and price tracker for students checking everyday items at local shops and shopkeepers updating those items.

Source: `scope.md > The Unique Kernel`, `The Core Loop`, `What "Working" Looks Like`, and `The POC Boundary`.

## The Core Journey

1. A buyer opens the public buyer page. The local-shop picker is at the top; the item cards below show the selected shop's item availability, price, and fixed unit. The buyer can change shops without logging in.
2. The buyer scans item cards. In-stock items show today's price and a green “In stock” badge. Low-but-available items look normal and tappable, show today's price and an amber “Few left” badge, and stay in their normal list position. Out-of-stock items remain available to open, appear dimmed with a grey “Out of stock” badge, show the last known price labeled “Last price,” and sort to the bottom.
3. The buyer opens an item to see its seven-day price chart. The seed history covers the seven dates ending on the current date. Today's displayed price carries forward the last saved price if the vendor has not updated it today. There is one price point per day per shop-item; saving again on the same day replaces today's point. “Price falling” appears only if today's price is below the average of the six preceding daily prices. If the six-day baseline is incomplete, the chart shows a clear no-history state and no trend label.
4. A shopkeeper opens the vendor page, selects a shop, and enters that shop's four-digit PIN. The shop's data stays hidden until a valid PIN is entered.
5. The shopkeeper selects an item, sees its fixed unit, enters today's price and current quantity, and presses Save. Access stays unlocked after saving until the shopkeeper switches shops or presses Lock. A valid save shows confirmation and a vendor-only “Low stock, restock soon” flag if quantity is at or below the fixed threshold.
6. The buyer returns to the public page and refreshes. The saved price and stock status appear, and the chart's point for today reflects the saved price. Zero quantity changes the buyer display to “Out of stock” and moves the item to the bottom.

## Screens and Layout

### Buyer page

A light-background Bento Grid layout: the header includes a visible “Vendor” link, the shop picker sits below it at the top, item cards follow, and a separate chart tile appears for the selected item. Cards use large, bold prices with a fixed unit, clear text badges, rounded corners, and green, amber, and grey accents. The buyer page is public and never requires the vendor PIN. Do not add search; the shop picker and item list are the POC browsing controls.

### Vendor page

One simple, phone-friendly tile. Before access, it contains the shop picker and large four-digit PIN input. After successful access, the tile shows item selection, the current price and quantity with fixed units, large price and quantity inputs, the vendor restock flag, a Save button, and a Lock button. The vendor remains unlocked after saving; switching shops or pressing Lock returns to the PIN screen. PIN errors stay on the PIN screen and do not expose shop data.

## Look and Feel

Use a light-mode-only clean Bento Grid style with rounded tiles, fresh green, amber, and grey, and large bold prices. Keep both surfaces readable and fast to use on a phone. Avoid glass blur, 3D effects, and animations. Inspired by the smooth, simple experience of Flipkart, Amazon, and Blinkit at a small local-shop scale (`scope.md > Inspiration & Identity`).

## Features and Behavior

### Buyer browsing and item details

- Provide a public item list for a selected local shop. The shop picker offers 3–4 sample shops.
- Each item card shows the item name, current availability, today's price and fixed unit, and the selling shop.
- Each card visibly offers “View price trend”; the whole card is clickable, and opening it scrolls directly to that item's chart tile.
- Show a “Price falling” chip on each card only when today's effective price is strictly below the average of the preceding six daily prices; incomplete history has no chip.
- Show exactly one stock state per item: green “In stock”; amber “Few left” when quantity is positive and at or below that shop-item's threshold; or grey “Out of stock” at zero.
- Keep low-stock cards in their normal list position. Dim and sort out-of-stock cards to the bottom while allowing them to open.
- For zero stock, show the last known price with the “Last price” label; do not present it as today's price.
- On item open, show a seven-day chart in a separate tile. The seven dates are generated relative to the current date and end today. If the vendor does not update an item today, today's price carries forward the most recently saved price. Keep exactly one price point per day per shop-item; another save on the same day replaces that day's point. The “Price falling” label is present only when today's price is lower than the arithmetic average of the preceding six daily prices. Incomplete comparison history means no label and a clear no-history message.
- On the opened item, show a “Cheapest today” badge when the selected shop has the lowest effective price among shops where that item is currently in stock; tied lowest prices qualify. Do not award the badge to an out-of-stock selected shop or compare its stale last price.
- If item data is unavailable, show a clear no-data message rather than a blank or misleading price.

### Vendor access and stock updates

- The shopkeeper chooses a shop and enters its four-digit PIN. A shop change resets the PIN screen; a PIN for one shop never unlocks another.
- Empty or non-four-digit PIN input shows “Enter your 4-digit shop PIN” before checking.
- A wrong PIN keeps the shopkeeper on the PIN screen, clears the input, returns focus to it, and shows “Incorrect PIN. Please try again.” It reveals no shop data and changes no stock or price.
- After five incorrect attempts, lock the PIN screen for 30 seconds and show “Too many attempts. Try again in 30 seconds.” Re-enable PIN entry after the cooldown. This is a basic attempt limit, not a full account security system.
- After access, let the shopkeeper select one of the shop's sample items and enter the current price and stock quantity. Units are fixed per item and cannot be selected or changed by the vendor. Decimal quantities are accepted for kg and litre items; eggs per dozen accept whole numbers only.
- Price and quantity are required. Reject negative values. Accept zero quantity as valid. Allow up to two decimal places for rupee prices; accept fractional stock quantities for kg and litre items, while eggs per dozen require a whole number.
- Pressing Save with valid input persists the new current values and shows a clear success confirmation. If a price is saved more than once on the same day, replace that shop-item's existing point for today. An invalid form shows the relevant field-level message and does not save.
- Keep the vendor unlocked after saving. The vendor can continue updating items in that shop until switching shops or pressing Lock; either action returns to the PIN screen.
- Show a vendor-only “Low stock, restock soon” flag when remaining quantity is at or below the fixed threshold for that shop-item record. Vendors can update quantity but cannot change the threshold.
- Saving a quantity of zero succeeds and immediately changes the buyer-visible item state to out of stock after the buyer refreshes.

### Sample catalog, prices, and history

- Include 12 sample items: tomatoes, onions, potatoes, bananas, green chillies, milk, cooking oil, rice, atta, sugar, dal, and eggs.
- Fixed units: tomatoes, onions, potatoes, bananas, green chillies, rice, atta, sugar, and dal per kg; milk and cooking oil per litre; eggs per dozen. Show price with the ₹ symbol and unit on both buyer and vendor pages, for example “₹40 / kg.”
- Seed 3–4 local shops, realistic but clearly sample prices that differ slightly by shop, and a seven-day price history generated relative to the current date. On first open, the buyer view must show at least one falling-price item, one “Few left” item, and one out-of-stock item.
- Include a fixed low-stock threshold per shop-item record in that item's unit. Price values are whole rupees or have at most two decimal places. Quantity is entered in the fixed item unit; kg and litre quantities may be fractional (for example, 2.5 kg or 1.5 L), while eggs per dozen use whole numbers.
- Store one price point per day per shop-item. Carry the most recently saved price forward for today when no update is entered; a same-day vendor save replaces today's existing point instead of creating a duplicate.
- Keep the sample catalog, units, price history, shop-specific sample prices, and low-stock limits together in one place so changing a sample item's definition does not require editing scattered records. The data-file/storage mechanism is decided in `4-spec`.

### Theme and persistence

- Use light mode only; dark mode is out of scope.
- Run the app locally only. Persist vendor price and stock updates so they remain after app restart; a buyer sees the updated values on refresh. No cloud service or deployment is part of this product (`scope.md > The POC Boundary` and `Explicitly Cut`).

### Demo data reset

- Provide a simple `reset-demo-data` command for recording the demo.
- Before replacing local demo shops, stock, prices, or history, ask for confirmation with a safe default of No. Canceling leaves the database unchanged; confirming restores the curated sample data.
- Running it replaces the current sample shops, stock quantities, prices, and price history with the curated sample data. Generate the seven-day history relative to the current date, with at least one falling-price item, one “Few left” item, and one out-of-stock item visible on first open after reset.
- Report clearly when the reset completes. The command operates on local demo data only.

## States and Boundaries

- **First open:** Show the sample local shops and 12-item catalog with seeded prices, fixed units, stock quantities, low-stock limits, and seven-day histories generated relative to today. Initial buyer data includes a falling-price item, a “Few left” item, and an out-of-stock item.
- **Out of stock:** Keep the item visible and chart accessible; dim it, show grey “Out of stock,” show “Last price,” and sort it to the bottom.
- **Low stock:** Keep the card tappable in its ordinary position, show amber “Few left,” and show today's price. The vendor sees “Low stock, restock soon.”
- **No or incomplete price history:** Show the chart's available data and a clear no-history message; do not show the falling-price label without the six preceding daily prices needed for comparison.
- **Invalid vendor PIN:** Show the appropriate format or incorrect-PIN message without revealing shop data or changing buyer-visible data.
- **PIN lockout:** After five wrong attempts, block entry for 30 seconds and show the cooldown message; allow entry again when it ends.
- **Invalid vendor form:** Empty price/quantity and negative values are rejected with a clear field message; no invalid values are saved. Zero quantity is allowed.
- **Successful vendor save:** Show confirmation; persist the values. A zero quantity becomes out of stock for the buyer after refresh. A second save for the same shop-item on the same day replaces today's point.
- **Reset demo data:** Restore the seeded shop records, stock, prices, and current-date-relative history; the first buyer view again includes the three required demo states.
- **Vendor session:** Access remains unlocked after Save until the vendor switches shops or presses Lock.
- **Restart:** Vendor updates remain saved. The app remains local-only.

## Product Decisions

- Buyer status language differs from the vendor's restock language because the buyer is deciding whether to make a trip, while the vendor needs a to-do cue.
- Buyers need not log in. Vendor access uses a shop picker and a simple per-shop four-digit PIN, not full accounts.
- The 7-day trend label compares today's price with the average of the preceding six days; incomplete history does not produce a trend claim. Seed dates are generated relative to the current date, today carries forward the last saved price when untouched, and a same-day save replaces that shop-item's single point for today.
- The sample catalog has exactly 12 items; bananas are the fixed fruit item and bread is excluded.
- Item units are fixed, shown beside prices, and are not editable in the vendor flow to prevent unit mistakes.
- The sample catalog and fixed shop-item limits should be maintained together in one source; the specific format is a technical-spec decision.
- The app runs locally with persistent data, without cloud hosting or deployment.
- Dark mode is optional and is the first feature to cut if time is short; light mode remains the default.
- A `reset-demo-data` command restores the demo shops, stock, prices, and date-relative history before recording.

## What We're Building

A locally running, persistent, phone-friendly buyer and vendor experience with a public shop-filtered item list, item price charts, vendor PIN flow, stock and price updates, buyer and vendor stock states, low-stock flags, sample history and data, validation, clear empty/error/success states, a `reset-demo-data` command, and a persistent light-mode default. Dark mode is out of scope.

## Deferred From the POC

- Full vendor accounts, registration, PIN reset, and stronger access controls: simple shop-specific PINs prove the vendor update flow within the small local demo.
- More than 12 sample items or 4 shops: the seeded catalog is enough to demonstrate the buyer and vendor loop.
- Orders, payment, delivery, maps, GPS, notifications, recommendations, search, and broad demand analytics: none is needed to prove local stock and price visibility (`scope.md > Explicitly Cut`).
- Cloud sync, hosting, and deployment: the product is explicitly local-only.

## Possible Later Enhancements

Add richer vendor reporting or a larger catalog if the initial local update loop proves useful. Consider stronger vendor account management only if the product moves beyond a local proof of concept.

## Non-Goals

- A public marketplace, checkout, payments, orders, or delivery.
- Buyer accounts or saved lists.
- GPS-based discovery or notifications.
- Full account security or multi-role administration.
- Cloud-hosted or multi-device synchronization.

## Open Questions

- None blocking product definition. The specific local storage and sample-data file format are intentionally left to `4-spec`.
