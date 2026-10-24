---
doc: checklist
status: approved
---

# Build Checklist

Build mode: fast

Timing plan: Finish slices 1 and 2 tonight (2026-10-24, Asia/Calcutta); finish slices 3 and 4 tomorrow (2026-10-25, Asia/Calcutta); add the small buyer comparison slice before preparing the final submission with several hours to spare. The exact Devpost deadline date and time zone still need to be supplied. Dark mode is out of scope; the app map remains optional.

## Slices

- [x] **1. Open a seeded buyer page, reset the demo, and connect the public repo**
  Becomes usable: A local Windows app starts with the default shop, 12 catalog items, current sample prices and stock states; the buyer can switch among local shops. The first run creates `instance/` and its persistent database automatically, and the public GitHub remote is connected for milestone pushes.
  Why now: This bootstraps the app inside a real buyer behavior, proving the canonical JSON-to-SQLite pipeline and first-run setup before vendor writes depend on it.
  PRD ref: `prd.md > The Core Journey`, `prd.md > Buyer browsing and item details`, `prd.md > Sample catalog, prices, and history`, `prd.md > Demo data reset`
  Spec ref: `spec.md > Where It Runs and How Someone Tries It`, `spec.md > Seed loader and reset command`, `spec.md > Buyer cards and SVG chart`, `spec.md > Data Model`, `spec.md > File Structure`
  Build: Initialize the local Git repository, verify ignore rules and private files, create and connect a public GitHub repository, and push the approved planning documents; scaffold Flask and the Windows setup/run commands; create the canonical 12-item/3–4-shop JSON seed including sample PINs and fixed low-stock limits; automatically create `instance/`, initialize SQLite, and seed on first run; show the selected shop and item price/stock cards; add the confirmed reset command with stop-server reminder; write README setup instructions and list the demo PINs as sample values only.
  Verify (mechanical): Confirm the GitHub remote is public and points to this repository; inspect pushed files to ensure the three planning docs are present and `learner-profile.md`, `.env`, and the database are absent; with no `instance/` folder, run setup and start commands; confirm the folder/database and seeded records appear, buyer route returns successfully, all sample PINs in the README are explicitly labeled sample-only, and reset prints its reminder, cancels on No, then reseeds relative dates/states on confirmation.
  Learner check: Open the buyer page on a phone-sized window, switch shops, and check whether prices and stock states make it clear where you could shop today.
  Commit: `Build seeded local buyer browsing`

- [x] **2. Update stock and price as a vendor, then see it as a buyer**
  Becomes usable: A shopkeeper unlocks one shop, saves a valid price and quantity, and the public buyer page shows the saved values after refresh; the vendor remains unlocked until Lock or shop switch.
  Why now: This is the unique end-to-end kernel: the shopkeeper's entry becomes the buyer's current information through the same persistent database.
  PRD ref: `prd.md > The Core Journey`, `prd.md > Vendor access and stock updates`, `prd.md > Buyer browsing and item details`, `prd.md > States and Boundaries`
  Spec ref: `spec.md > Vendor PIN gate and session`, `spec.md > Vendor update form`, `spec.md > Data access`, `spec.md > Data Model`
  Build: Replace the “Local shops” header pill with a visible “Vendor” link to `/vendor`, without adding search; add server-side per-shop PIN check, malformed/wrong PIN messages and SQLite lockout, signed shop session, Lock/shop-switch behavior, vendor item form, unit-aware validation, atomic stock update and same-day price upsert, and buyer refresh rendering.
  Verify (mechanical): Exercise valid and invalid PIN, five-failure lockout, Lock and shop switching; save valid price/quantity and verify SQLite contains one row for the shop-item-date key and the buyer response shows the new stock and price; confirm invalid submissions leave data unchanged.
  Learner check: Unlock a sample shop, change one item's price and quantity, save, then refresh the buyer page and confirm the same shop shows your update.
  Commit: `Complete vendor-to-buyer update flow`

- [x] **3. Read a reliable seven-day price trend**
  Becomes usable: Opening an item shows seven consecutive local dates, a readable SVG chart, and “Price falling” only under the approved today-versus-previous-six-day-average rule.
  Why now: The chart depends on the now-working persistent save path. Filling missing dates at read time also exercises how reliable views can be derived from sparse stored events.
  PRD ref: `prd.md > Buyer browsing and item details`, `prd.md > Sample catalog, prices, and history`, `prd.md > States and Boundaries`
  Spec ref: `spec.md > Buyer cards and SVG chart`, `spec.md > Seed loader and reset command`, `spec.md > Data Model`
  Build: Add chart item selection, read-time carry-forward from the latest preceding saved price with idempotent persistence, seven-point SVG rendering, incomplete-history messaging, and falling-price comparison.
  Verify (mechanical): Inspect a chart with a missing date and confirm read-time filling creates only one row per date; verify the displayed seven dates and calculated label for falling, flat/rising, and incomplete histories.
  Learner check: Open the seeded falling-price item and describe what the line and label tell you about whether today is a good time to buy.
  Commit: `Add seven-day price trend`

- [x] **4. Make the core flow phone-friendly and close PRD edge cases**
  Becomes usable: Buyer and vendor screens are clear on a phone-sized viewport, and success, validation, empty-history, out-of-stock, and error states give plain next steps.
  Why now: Polish comes after behavior is complete, so styling supports real content and states rather than masking gaps.
  PRD ref: `prd.md > Screens and Layout`, `prd.md > Look and Feel`, `prd.md > Vendor access and stock updates`, `prd.md > States and Boundaries`
  Spec ref: `spec.md > Look and Feel`, `spec.md > Important Failure Modes`, `spec.md > Manual Verification Checklist`
  Build: Finish responsive Bento Grid styles, touch-friendly vendor controls, accessible labels and visible text badges; include a visible “View price trend” cue on each whole-card link and navigate directly to the chart anchor; address findings from the complete manual verification list without expanding the cut scope.
  Verify (mechanical): Run every manual verification checklist item in `spec.md`; inspect buyer and vendor layouts at a phone-sized viewport and confirm no horizontal overflow or unreadable status state; verify every item card has the visible cue and its link targets `#price-trend`.
  Learner check: Try the buyer and vendor journeys at phone width, including zero stock and a validation error, and report anything that slows you down or reads unclearly.
  Commit: `Polish mobile flow and verify PRD states`

- [x] **5. Compare today's prices and surface falling trends on cards**
  Becomes usable: Opening an item shows whether the selected local shop is cheapest among shops with stock, and cards make falling-price items visible without opening each chart.
  Why now: It builds directly on the existing seven-day calculation and price records, adding a compact buyer cue before the submission recording.
  PRD ref: `prd.md > Buyer browsing and item details`
  Spec ref: `spec.md > Buyer cards and SVG chart`, `spec.md > Manual Verification Checklist`
  Build: Reuse the approved six-day comparison to add a “Price falling” chip to matching item cards; compare effective prices for the opened item across shops with positive stock and show “Cheapest today” for the selected shop when tied for lowest. Keep search, accounts, and dark mode out of scope.
  Verify (mechanical): Check falling and non-falling items against their six-day prices; vary shop prices to prove the lowest in-stock shop gets the badge, ties qualify, and an out-of-stock shop cannot get it. Confirm buyer browsing and vendor saves still work.
  Learner check: Open the same item in two local shops and compare the “Cheapest today” and “Price falling” cues.
  Commit: `Show buyer price comparison cues`

- [ ] **6. Prepare the public project submission**
  Becomes usable: The public repository contains the finished app, README, reset command, and the three approved planning docs; the demo recording and a reviewed project description are ready alongside it.
  Why now: The app must be verified before recording; keeping submission work last ensures the repository and demo show the actual finished behavior.
  PRD ref: `prd.md > What We're Building`, `prd.md > Demo data reset`
  Spec ref: `spec.md > Where It Runs and How Someone Tries It`, `spec.md > File Structure`, `spec.md > Manual Verification Checklist`
  Build: Recheck the public repository contents and generated-file ignores; confirm the `reset-demo-data` command and all three planning docs are included; use reset to prepare the date-relative demo states; guide the learner through recording the working buyer-to-vendor flow, including the buyer comparison cues, and placing the resulting demo recording in the public repository; prepare a concise project description for learner review and save the approved text in the repo.
  Verify (mechanical): Inspect the public remote contents and README; confirm `devpost/scope.md`, `devpost/prd.md`, `devpost/spec.md`, and `reset-demo-data.cmd` are present; verify the linked recording opens and the saved description matches the learner-approved text.
  Learner check: Open the public repository and the demo recording, then confirm they show the project you intend to submit and explain it accurately.
  Commit: `Prepare public demo submission`

## Hands-on Checkpoints

- [x] Early usable behavior explored — learner checked desktop and phone-sized layouts, confirmed shop switching and differing prices, and reported the layout looks good.
- [ ] Final kick-the-tires exploration and feedback completed — after slice 5, try the full buyer/vendor flow, awkward inputs, and report what should change.

## Final Review

- [ ] Revision: Learner requested a hands-on recheck of chart discovery after slice 4: each card visibly says “View price trend”, the full card navigates to the chart anchor, and “Price falling” is near the chart title.
- [x] Revision: Add the learner-requested “Cheapest today” opened-item badge and “Price falling” item-card chips; verify the defined comparison rules and keep search, accounts, and dark mode out of scope.
- [ ] Final review complete — feedback resolved and learner confirms ready to ship

## Code Tour and App Map

- [ ] Learning activity complete — trace one tomato update through the route, database transaction, and refreshed buyer render, connecting the pipeline and architecture to the learner's goal.
- [ ] Optional edit and transfer reflection addressed — offer one safe edit or transfer question during the wrap-up; record the learner's actual choice.
- [ ] Optional after submission is ready: `devpost/app-map.html` generated from finished code, checked, and shown, including a project-grounded practice to reuse

Activity and evidence: [record what actually happened after the build]
Route and stops: [record actual files, functions, and stops]
Edit outcome: [record tried/kept/reverted/declined/not applicable and verification]
Reflection: [offered/answered/declined/already covered — personal answer belongs only in ignored profile]
Activity mode: [live app and editor, explicit static fallback, focused alternative, prior practice, or recap]

## Revisions

- Added slice 5 before submission for the opened-item “Cheapest today” badge and card-level “Price falling” chips, as requested after slice 4.
