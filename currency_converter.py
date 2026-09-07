#!/usr/bin/env python3
"""
currency_converter.py

A simple CLI tool to convert between currencies and look up exchange rates,
using the free Frankfurter API (backed by European Central Bank rates).
No API key or signup required.

Supports:
  - Converting an amount from one currency to another
  - Looking up the current exchange rate between two currencies (no amount)
  - Historical rates for a specific date (YYYY-MM-DD)
  - Listing all supported currency codes
  - JSON output (for piping into other tools/scripts)

Usage examples:
  # Convert 100 USD to NGN
  python currency_converter.py 100 USD NGN

  # Just show the current rate (1 unit) between two currencies
  python currency_converter.py --rate USD NGN

  # Historical rate on a specific date
  python currency_converter.py 100 USD EUR --date 2024-01-15

  # List all supported currency codes
  python currency_converter.py --list

  # Raw JSON output
  python currency_converter.py 100 USD NGN --json
"""

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE_URL = "https://api.frankfurter.app"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Convert between currencies using live (or historical) exchange rates."
    )
    parser.add_argument(
        "amount", type=float, nargs="?", default=None,
        help="Amount to convert (omit when using --rate or --list)",
    )
    parser.add_argument(
        "from_currency", type=str, nargs="?", default=None,
        help="Currency code to convert from (e.g. USD)",
    )
    parser.add_argument(
        "to_currency", type=str, nargs="?", default=None,
        help="Currency code to convert to (e.g. NGN)",
    )
    parser.add_argument(
        "--rate", nargs=2, metavar=("FROM", "TO"), default=None,
        help="Show the current exchange rate (1 unit) between two currencies",
    )
    parser.add_argument(
        "--date", type=str, default=None,
        help="Use historical rates for this date (YYYY-MM-DD) instead of the latest rate",
    )
    parser.add_argument(
        "--list", action="store_true",
        help="List all supported currency codes and their names",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Print raw JSON instead of a formatted summary",
    )
    return parser.parse_args()


def fetch_json(url: str) -> dict:
    """Fetch a URL and return parsed JSON, or exit with a clear error message."""
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print("Error: one of the currency codes or the date given is not valid.")
        else:
            print(f"Error: the exchange rate service returned an error ({e.code}).")
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Error: could not reach the exchange rate service ({e.reason}).")
        print("Check your internet connection and try again.")
        sys.exit(1)
    except json.JSONDecodeError:
        print("Error: received an unexpected response from the exchange rate service.")
        sys.exit(1)


def list_currencies():
    url = f"{BASE_URL}/currencies"
    return fetch_json(url)


def get_rate(from_currency: str, to_currency: str, date: str = None) -> dict:
    date_part = date if date else "latest"
    params = urllib.parse.urlencode({"from": from_currency.upper(), "to": to_currency.upper()})
    url = f"{BASE_URL}/{date_part}?{params}"
    return fetch_json(url)


def convert_amount(amount: float, from_currency: str, to_currency: str, date: str = None) -> dict:
    date_part = date if date else "latest"
    params = urllib.parse.urlencode({
        "amount": amount,
        "from": from_currency.upper(),
        "to": to_currency.upper(),
    })
    url = f"{BASE_URL}/{date_part}?{params}"
    return fetch_json(url)


def print_currency_list(currencies: dict):
    print(f"Supported currencies ({len(currencies)}):\n")
    for code in sorted(currencies):
        print(f"  {code} - {currencies[code]}")


def print_rate(data: dict, from_currency: str, to_currency: str):
    rate = data.get("rates", {}).get(to_currency.upper())
    date = data.get("date", "unknown")
    if rate is None:
        print(f"Error: could not find a rate for {to_currency.upper()}.")
        sys.exit(1)
    print(f"1 {from_currency.upper()} = {rate} {to_currency.upper()}  (as of {date})")


def print_conversion(data: dict, amount: float, from_currency: str, to_currency: str):
    result = data.get("rates", {}).get(to_currency.upper())
    date = data.get("date", "unknown")
    if result is None:
        print(f"Error: could not find a rate for {to_currency.upper()}.")
        sys.exit(1)
    print(f"{amount} {from_currency.upper()} = {result} {to_currency.upper()}  (rates as of {date})")


def main():
    args = parse_args()

    if args.list:
        currencies = list_currencies()
        if args.json:
            print(json.dumps(currencies, indent=2))
        else:
            print_currency_list(currencies)
        return

    if args.rate:
        from_currency, to_currency = args.rate
        data = get_rate(from_currency, to_currency, args.date)
        if args.json:
            print(json.dumps(data, indent=2))
        else:
            print_rate(data, from_currency, to_currency)
        return

    if args.amount is None or not args.from_currency or not args.to_currency:
        print("Error: provide an amount and two currency codes, e.g.:")
        print("  python currency_converter.py 100 USD NGN")
        print("Or use --rate FROM TO, or --list. Run with -h for full help.")
        sys.exit(1)

    data = convert_amount(args.amount, args.from_currency, args.to_currency, args.date)
    if args.json:
        print(json.dumps(data, indent=2))
    else:
        print_conversion(data, args.amount, args.from_currency, args.to_currency)


if __name__ == "__main__":
    main()
