"""
app.py — Flask delivery layer for the budget tracker.

This is the thin web layer: it wires the deterministic tools (db,
parse_transaction, categorize) to a small JSON API and serves the dashboard.
All real logic lives in tools/ — this file only routes requests.

Run it:
    python app.py            # then open http://localhost:5000

API:
    GET  /api/summary              -> totals + category breakdown + recent
    POST /api/log {text}           -> parse, categorize, store one transaction
    PATCH /api/transaction/<id> {category} -> fix a category
"""

import os
import socket
from functools import wraps

from flask import Flask, request, jsonify, render_template, Response
from jinja2 import TemplateNotFound

from tools import db
from tools.parse_transaction import parse_transaction
from tools.categorize import categorize, category_names


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        password = os.environ.get("APP_PASSWORD")
        if password:
            auth = request.authorization
            if not auth or auth.password != password:
                return Response(
                    "Unauthorized", 401,
                    {"WWW-Authenticate": 'Basic realm="Budget"'}
                )
        return f(*args, **kwargs)
    return decorated

app = Flask(__name__)

# Make sure the table exists before serving any request.
db.init_db()


@app.route("/")
@require_auth
def index():
    """Serve the dashboard. Frontend arrives in Phase 4; until then, a note."""
    try:
        return render_template("index.html")
    except TemplateNotFound:
        return "Budget tracker API is running. The dashboard UI arrives in Phase 4.", 200


@app.route("/api/summary")
@require_auth
def summary():
    """Everything the dashboard needs in one call."""
    return jsonify(
        {
            "total": db.monthly_total(),
            "period": "this month",
            "categories": db.totals_by_category(),
            "recent": db.list_transactions(limit=10),
            "available_categories": category_names(),
        }
    )


@app.route("/api/log", methods=["POST"])
@require_auth
def log_transaction():
    """Parse free text, categorize it, store it. Returns the new transaction."""
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()

    try:
        parsed = parse_transaction(text)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    category = categorize(parsed["note"])
    transaction = db.add_transaction(parsed["amount"], parsed["note"], category)
    return jsonify(transaction), 201


@app.route("/api/transaction/<int:transaction_id>", methods=["PATCH"])
@require_auth
def fix_category(transaction_id):
    """Re-assign a transaction's category (the 'fix it' control)."""
    data = request.get_json(silent=True) or {}
    category = (data.get("category") or "").strip()

    if category not in category_names():
        return jsonify({"error": f"Unknown category: {category!r}"}), 400

    if not db.update_category(transaction_id, category):
        return jsonify({"error": f"No transaction with id {transaction_id}"}), 404

    return jsonify({"id": transaction_id, "category": category})


def _lan_ip():
    """Best-effort detection of this machine's wifi/LAN IP for phone access."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))  # no packets sent; just picks the outbound interface
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


if __name__ == "__main__":
    PORT = 5000
    ip = _lan_ip()
    print("\n  Budget tracker is running. Press Ctrl+C to stop.")
    print(f"  On this computer:  http://localhost:{PORT}")
    print(f"  On your phone:     http://{ip}:{PORT}   (must be on the same wifi)\n")
    # host=0.0.0.0 listens on all interfaces so the phone can reach it.
    # debug=False is intentional: never expose the Werkzeug debugger on the network.
    app.run(host="0.0.0.0", port=PORT, debug=False)
