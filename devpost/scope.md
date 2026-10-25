---
doc: scope
status: approved
---

# Local Shop Stock and Price Tracker

A small, mobile-friendly app that connects a local shop's quick stock and price update to what a student sees before deciding where to shop.

## The Unique Kernel
A shopkeeper updates an item's current price and quantity in seconds, and a buyer can see that same update alongside a short price trend before leaving home.

## Who It's For
Students living independently in a new city who want to check everyday items before making a trip, and small shopkeepers who want a simple alternative to tracking stock on paper.

## The Core Loop
A buyer opens a public page, chooses one of a few local shops, checks an item's availability and today's price, and opens its seven-day chart. A shopkeeper selects their shop and enters its PIN, then updates that item's price and quantity on the vendor page. After refreshing, the buyer sees the saved update and today's chart point. The shopkeeper can also spot low stock for restocking.

## Inspiration & Identity
The learner wants the smooth, clean feel of Flipkart, Amazon, or Blinkit at a much smaller scale. Phone-first use, clear status and save feedback, and a fast vendor update are central. Use the wording “local shop.” The references guide the experience only; this is not a full marketplace.

## Why This Matters to the Learner
For students managing academics and daily errands in a new city, checking local stock can avoid wasted trips. Lightweight shop records can replace pen-and-paper tracking and make restocking needs easier to spot.

## What "Working" Looks Like
In a short demo, a student checks tomatoes at a selected local shop and sees the current price, stock status, and a seven-day trend. The chart includes today and the six preceding days. It shows “Price falling” only when today's price is lower than the average of those previous six daily prices; matching cards also show that cue. The buyer can identify which in-stock local shop ties for the lowest current price. The shopkeeper selects their shop, enters its PIN, and updates the tomato price and quantity in under 30 seconds on a phone-sized screen. After returning to the buyer page and refreshing, the student sees the saved price and stock status, and the chart includes today's point. The vendor flow validates input, reports errors clearly, confirms a successful save, and flags low quantity for restocking.

## The POC Boundary
- A public buyer page with 10–15 everyday sample items and 3–4 sample local shops.
- A vendor page with a shop picker and simple per-shop PIN. No full account system.
- Pre-filled seven-day price history, with today's price and the six preceding daily prices shown on the chart.
- The “Price falling” label appears only when today's price is below the average of the preceding six days. If that history is incomplete, show a clear no-data state and no trend label.
- Cards identify “Price falling” items and show “Cheapest today” when the selected shop ties for the lowest price among shops with stock; out-of-stock shops do not qualify.
- Fixed low-stock limits are seeded in the sample data for each shop-item record; vendors can update quantities but do not configure thresholds.
- Input validation, clear errors and no-data states, and visible save confirmation.
- Clean, mobile-friendly screens and a vendor update that takes under 30 seconds.
- Run locally only, with persistent local storage so updates remain after the app restarts. No cloud service or deployment is required; the specific storage mechanism will be chosen in the technical spec.
- During technical planning, explain the data-storage and update flow, workflow organization, and meaningful alternatives to support the learner's system-design goal.

## Later
More shops or items, stronger vendor accounts, and broader restocking or demand insights can follow if the proof of concept works.

## Explicitly Cut
- Payments, orders, and delivery: the core proof is checking local availability and prices.
- Maps, GPS, notifications, and recommendations: a local-shop picker is enough to demonstrate the stock and price check.
- Search and item filtering: the small fixed catalog is browsed directly; buyers choose a local shop from the picker.
- Multiple user roles and a full marketplace: the proof needs a public buyer view and a simple per-shop vendor update path.
- Cloud hosting or deployment: local-only operation is sufficient for this proof of concept.
