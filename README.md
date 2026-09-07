# Currency Converter

A simple, dependency-free Python CLI tool that converts between currencies
and looks up exchange rates, using the free [Frankfurter](https://www.frankfurter.app/)
API (rates published by the European Central Bank).

No API key, no signup, no third-party libraries required.

## Features

- ✅ Convert an amount from one currency to another
- ✅ Look up the current exchange rate without converting an amount
- ✅ Historical rates for any past date
- ✅ List all supported currency codes and names
- ✅ Raw JSON output option, for piping into other scripts
- ✅ Clear error messages for invalid currency codes or connection issues

## Requirements

- Python 3.7+
- No external dependencies (uses `urllib` from the standard library)
- An internet connection (this tool calls a live exchange rate API)

## Usage

```bash
python currency_converter.py <amount> <from_currency> <to_currency> [options]
```

### Options

| Flag       | Description                                                          |
|------------|------------------------------------------------------------------------|
| `--rate`   | Show the current exchange rate (1 unit) between two currencies, e.g. `--rate USD NGN` |
| `--date`   | Use historical rates for this date (`YYYY-MM-DD`) instead of the latest rate |
| `--list`   | List all supported currency codes and their names                      |
| `--json`   | Print raw JSON instead of a formatted summary                          |

### Examples

**Convert an amount:**
```bash
python currency_converter.py 100 USD NGN
```
```
100.0 USD = 155025.0 NGN  (rates as of 2026-09-06)
```

**Just check the current rate (no amount):**
```bash
python currency_converter.py --rate USD NGN
```
```
1 USD = 1550.25 NGN  (as of 2026-09-06)
```

**Historical rate on a specific date:**
```bash
python currency_converter.py 100 USD EUR --date 2024-01-15
```

**List all supported currencies:**
```bash
python currency_converter.py --list
```

**Raw JSON output:**
```bash
python currency_converter.py 100 USD NGN --json
```

## Limitations

- Frankfurter covers major world currencies (USD, EUR, GBP, NGN, JPY, etc.)
  but not every currency in existence — run `--list` to see the full set.

## Running tests

```bash
python -m unittest discover tests
```