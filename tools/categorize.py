"""
categorize.py — assign a category to a note via keyword rules (WAT tool).

What it does: lowercases the note and checks it against the keyword map in
config/categories.json. The first category with a matching keyword wins.
No match -> "Uncategorized".

Inputs:  a note string, optional path to the config file.
Outputs: a category name (str).

Run standalone:
    python tools/categorize.py "grab to office"
"""

import json
import os

UNCATEGORIZED = "Uncategorized"

# config/categories.json lives at the project root, alongside app.py.
DEFAULT_CONFIG = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "categories.json"
)


def load_categories(config_path=DEFAULT_CONFIG):
    """Return the {category: [keywords]} map from the config file."""
    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["categories"]


def category_names(config_path=DEFAULT_CONFIG):
    """Return the list of valid category names, with Uncategorized appended."""
    names = list(load_categories(config_path).keys())
    if UNCATEGORIZED not in names:
        names.append(UNCATEGORIZED)
    return names


def categorize(note, config_path=DEFAULT_CONFIG):
    """Match a note to a category by keyword. Falls back to Uncategorized."""
    if not note:
        return UNCATEGORIZED

    text = note.lower()
    for category, keywords in load_categories(config_path).items():
        for keyword in keywords:
            if keyword.lower() in text:
                return category
    return UNCATEGORIZED


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print('Usage: python tools/categorize.py "grab to office"')
        sys.exit(1)

    note = " ".join(sys.argv[1:])
    print(categorize(note))
