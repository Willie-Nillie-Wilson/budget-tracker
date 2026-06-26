"""Unit tests for tools/parse_transaction.py"""
import pytest

from tools.parse_transaction import parse_transaction


def test_note_then_amount():
    assert parse_transaction("lunch 12.50") == {"amount": 12.50, "note": "lunch"}


def test_currency_symbol_in_front():
    assert parse_transaction("$12.50 coffee") == {"amount": 12.50, "note": "coffee"}


def test_integer_amount():
    assert parse_transaction("coffee 5") == {"amount": 5.0, "note": "coffee"}


def test_currency_word_prefix():
    assert parse_transaction("rm12.50 lunch") == {"amount": 12.50, "note": "lunch"}


def test_last_number_is_the_amount():
    # Multi-word note with the price at the end
    assert parse_transaction("uber to office 18") == {"amount": 18.0, "note": "uber to office"}


def test_amount_only_gives_empty_note():
    assert parse_transaction("20") == {"amount": 20.0, "note": ""}


def test_empty_input_raises():
    with pytest.raises(ValueError):
        parse_transaction("")


def test_no_number_raises():
    with pytest.raises(ValueError):
        parse_transaction("no number here")
