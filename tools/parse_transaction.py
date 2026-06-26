"""
parse_transaction.py — turn free text into {amount, note} (WAT tool).

What it does: pulls the price out of a plain-text log entry and treats the
rest as the description. Convention: the amount is the LAST number in the
string, so you type "what, then how much" — e.g. "lunch 12.50", "uber to
office 18". Currency symbols ($, rm, sgd, usd) are ignored.

Inputs:  a string like "coffee 4.50".
Outputs: {"amount": float, "note": str}. Raises ValueError if no number found.

Run standalone:
    python tools/parse_transaction.py "lunch 12.50"
"""

import re

# Matches an integer or decimal number, e.g. 12, 12.50, 4.5
_NUMBER = re.compile(r"\d+(?:\.\d+)?")
# Currency symbols/words to strip from the leftover note
_CURRENCY = re.compile(r"(?i)\b(?:rm|sgd|usd|myr)\b|\$")


def parse_transaction(text):
    """Parse 'note 12.50' into {'amount': 12.50, 'note': 'note'}."""
    if not text or not text.strip():
        raise ValueError("Empty input. Type something like 'lunch 12.50'.")

    matches = list(_NUMBER.finditer(text))
    if not matches:
        raise ValueError("No amount found. Include a number, e.g. 'lunch 12.50'.")

    # Convention: the LAST number is the amount.
    last = matches[-1]
    amount = round(float(last.group()), 2)

    # The note is everything except that number; strip currency symbols + tidy.
    note = text[: last.start()] + text[last.end():]
    note = _CURRENCY.sub("", note)
    note = re.sub(r"\s+", " ", note).strip(" -,:")

    return {"amount": amount, "note": note}


if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) < 2:
        print('Usage: python tools/parse_transaction.py "lunch 12.50"')
        sys.exit(1)

    text = " ".join(sys.argv[1:])
    try:
        print(json.dumps(parse_transaction(text)))
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
