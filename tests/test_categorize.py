"""Unit tests for tools/categorize.py (uses the real config/categories.json)."""
from tools.categorize import categorize, category_names, UNCATEGORIZED


def test_food_keyword():
    assert categorize("lunch") == "Food"


def test_transport_keyword():
    assert categorize("grab to office") == "Transport"


def test_entertainment_keyword():
    assert categorize("netflix") == "Entertainment"


def test_case_insensitive():
    assert categorize("LUNCH at noon") == "Food"


def test_no_match_is_uncategorized():
    assert categorize("random thing") == UNCATEGORIZED


def test_empty_note_is_uncategorized():
    assert categorize("") == UNCATEGORIZED


def test_category_names_includes_uncategorized():
    names = category_names()
    assert "Food" in names
    assert UNCATEGORIZED in names
