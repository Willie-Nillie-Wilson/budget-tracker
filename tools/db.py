"""
db.py — SQLite storage layer for the budget tracker (WAT tool).

What it does: creates the transactions table and provides deterministic
read/write helpers used by the Flask app and any script.

Inputs:  amounts (float), notes (str), categories (str), optional db path.
Outputs: transaction rows as dicts, totals as numbers/lists.

Run standalone to initialise the database:
    python tools/db.py            # creates budget.db with the schema
    python tools/db.py --demo     # also inserts a few sample rows
"""

import sqlite3
import os
from datetime import datetime

# Default database lives at the project root, next to app.py.
DEFAULT_DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "budget.db")


def get_connection(db_path=DEFAULT_DB):
    """Open a connection with row access by column name."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path=DEFAULT_DB):
    """Create the transactions table if it does not exist yet."""
    with get_connection(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                amount     REAL    NOT NULL,
                note       TEXT    NOT NULL,
                category   TEXT    NOT NULL,
                created_at TEXT    NOT NULL
            )
            """
        )
    return db_path


def add_transaction(amount, note, category, created_at=None, db_path=DEFAULT_DB):
    """Insert one transaction and return it as a dict."""
    created_at = created_at or datetime.now().isoformat(timespec="seconds")
    with get_connection(db_path) as conn:
        cur = conn.execute(
            "INSERT INTO transactions (amount, note, category, created_at) VALUES (?, ?, ?, ?)",
            (round(float(amount), 2), note, category, created_at),
        )
        new_id = cur.lastrowid
    return {
        "id": new_id,
        "amount": round(float(amount), 2),
        "note": note,
        "category": category,
        "created_at": created_at,
    }


def update_category(transaction_id, category, db_path=DEFAULT_DB):
    """Fix the category of an existing transaction. Returns True if a row changed."""
    with get_connection(db_path) as conn:
        cur = conn.execute(
            "UPDATE transactions SET category = ? WHERE id = ?",
            (category, transaction_id),
        )
        return cur.rowcount > 0


def list_transactions(limit=None, db_path=DEFAULT_DB):
    """Return transactions newest first, optionally capped to `limit`."""
    query = "SELECT id, amount, note, category, created_at FROM transactions ORDER BY id DESC"
    params = ()
    if limit is not None:
        query += " LIMIT ?"
        params = (int(limit),)
    with get_connection(db_path) as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(row) for row in rows]


def _month_prefix(year=None, month=None):
    """Build the 'YYYY-MM' prefix used to filter the current month."""
    now = datetime.now()
    year = year or now.year
    month = month or now.month
    return f"{year:04d}-{month:02d}"


def monthly_total(year=None, month=None, db_path=DEFAULT_DB):
    """Sum of all amounts in the given month (defaults to the current month)."""
    prefix = _month_prefix(year, month)
    with get_connection(db_path) as conn:
        row = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) AS total FROM transactions WHERE created_at LIKE ?",
            (prefix + "%",),
        ).fetchone()
    return round(row["total"], 2)


def totals_by_category(year=None, month=None, db_path=DEFAULT_DB):
    """Per-category spend for the month, highest first. Returns list of {name, amount}."""
    prefix = _month_prefix(year, month)
    with get_connection(db_path) as conn:
        rows = conn.execute(
            """
            SELECT category AS name, ROUND(SUM(amount), 2) AS amount
            FROM transactions
            WHERE created_at LIKE ?
            GROUP BY category
            ORDER BY amount DESC
            """,
            (prefix + "%",),
        ).fetchall()
    return [dict(row) for row in rows]


if __name__ == "__main__":
    import sys

    init_db()
    print(f"Initialised database at {DEFAULT_DB}")

    if "--demo" in sys.argv:
        add_transaction(12.50, "lunch", "Food")
        add_transaction(18.00, "grab to office", "Transport")
        add_transaction(9.00, "random thing", "Uncategorized")
        print("Inserted demo rows.")
        print("Monthly total:", monthly_total())
        print("By category:", totals_by_category())
