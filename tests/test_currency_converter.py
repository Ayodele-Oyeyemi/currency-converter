"""
Tests for currency_converter.py.

These tests mock all network calls (via unittest.mock), so they run offline
and don't depend on the real Frankfurter API being reachable.

Run with:
    python -m unittest discover tests
or:
    python tests/test_currency_converter.py
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from currency_converter import convert_amount, get_rate, list_currencies


class TestGetRate(unittest.TestCase):
    @patch("currency_converter.fetch_json")
    def test_latest_rate(self, mock_fetch):
        mock_fetch.return_value = {"amount": 1.0, "base": "USD", "date": "2026-09-06", "rates": {"NGN": 1550.25}}
        data = get_rate("usd", "ngn")
        self.assertEqual(data["rates"]["NGN"], 1550.25)

        called_url = mock_fetch.call_args[0][0]
        self.assertIn("latest", called_url)
        self.assertIn("from=USD", called_url)
        self.assertIn("to=NGN", called_url)

    @patch("currency_converter.fetch_json")
    def test_historical_rate(self, mock_fetch):
        mock_fetch.return_value = {"amount": 1.0, "base": "USD", "date": "2024-01-15", "rates": {"EUR": 0.91}}
        get_rate("USD", "EUR", date="2024-01-15")

        called_url = mock_fetch.call_args[0][0]
        self.assertIn("2024-01-15", called_url)
        self.assertNotIn("latest", called_url)


class TestConvertAmount(unittest.TestCase):
    @patch("currency_converter.fetch_json")
    def test_conversion(self, mock_fetch):
        mock_fetch.return_value = {"amount": 100.0, "base": "USD", "date": "2026-09-06", "rates": {"NGN": 155025.0}}
        data = convert_amount(100, "usd", "ngn")
        self.assertEqual(data["rates"]["NGN"], 155025.0)

        called_url = mock_fetch.call_args[0][0]
        self.assertIn("amount=100", called_url)
        self.assertIn("from=USD", called_url)
        self.assertIn("to=NGN", called_url)

    @patch("currency_converter.fetch_json")
    def test_conversion_with_date(self, mock_fetch):
        mock_fetch.return_value = {"amount": 50.0, "base": "GBP", "date": "2023-06-01", "rates": {"USD": 62.0}}
        convert_amount(50, "GBP", "USD", date="2023-06-01")

        called_url = mock_fetch.call_args[0][0]
        self.assertIn("2023-06-01", called_url)


class TestListCurrencies(unittest.TestCase):
    @patch("currency_converter.fetch_json")
    def test_list(self, mock_fetch):
        mock_fetch.return_value = {"USD": "United States Dollar", "EUR": "Euro"}
        currencies = list_currencies()
        self.assertIn("USD", currencies)
        self.assertEqual(currencies["EUR"], "Euro")


if __name__ == "__main__":
    unittest.main()
