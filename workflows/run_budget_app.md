# Run the Budget Tracker

## Objective
Start the budget tracker and use it from your computer or your phone.

## Inputs
- Python 3 installed
- Dependencies installed once: `pip install -r requirements.txt`

## Steps
1. Open a terminal in the project folder.
2. Run:
   ```
   python app.py
   ```
3. The terminal prints two links, e.g.:
   ```
   On this computer:  http://localhost:5000
   On your phone:     http://192.168.1.42:5000   (must be on the same wifi)
   ```
4. **On your computer:** open the `localhost` link in any browser.
5. **On your phone:** make sure the phone is on the **same wifi** as the PC, then open the phone link in your mobile browser. Tip: add it to your home screen for one-tap access.
6. Leave the terminal open while you use the app. Press **Ctrl+C** to stop.

## How to use it
- Type a transaction in the middle box: `lunch 12.50`, `grab to office 18`, `netflix 15.90`.
- Rule: put the **amount last** (or have just one number). `$`, `rm`, `sgd` are ignored.
- The app pulls out the price and files it into a category by keyword.
- If it guesses wrong (or lands in **Uncategorized**), tap the small category dropdown on that row to fix it.

## Outputs
- All data is stored locally in `budget.db` (SQLite) at the project root. This file is gitignored and never leaves your machine.

## Editing categories
- Open `config/categories.json`.
- Each category has a list of keywords. Add your real merchants, e.g. put your usual coffee spot under **Food**, your ride app under **Transport**.
- Matching is case-insensitive substring. The first category with a matching keyword wins; categories higher in the file are checked first.
- No restart-safe caching: changes take effect on the next transaction you log (the config is read fresh each time).

## Edge cases / notes
- **Phone can't connect?** Confirm both devices are on the same wifi. Some routers block device-to-device traffic ("AP/client isolation") — disable that, or use the PC only. Windows Firewall may also prompt the first time; allow Python on private networks.
- **No number in the entry** (e.g. `coffee`) → the app shows an inline error and logs nothing. Include an amount.
- **Wrong amount parsed?** Remember the amount is the *last* number. `spent 100 on 2 shirts` reads `2` as the amount — rephrase to `2 shirts 100`.
- **Reset everything:** stop the app and delete `budget.db`. It is recreated empty on next start.
- **Seed demo data:** `python tools/db.py --demo` inserts a few sample rows for testing.
- **Run the tests:** `python -m pytest tests/`.

## Why debug mode is off
`app.py` runs with `debug=False` on purpose. Because the app binds to all network interfaces for phone access, leaving Flask's interactive debugger on would let anyone on the wifi run code on your PC. Keep it off.
