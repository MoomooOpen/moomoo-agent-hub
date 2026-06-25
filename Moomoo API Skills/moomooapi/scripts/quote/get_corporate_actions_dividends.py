#!/usr/bin/env python3
"""
Get Dividends

Function: Get dividend history for a stock
Usage: python get_corporate_actions_dividends.py [-h] [--json] code

API Limits:
- Max 30 requests per 30 seconds
- Supports equities and funds

Parameter Description:
- code: Stock code, e.g. HK.00700

Return Field Description:
- data[]: Dividend list in reverse chronological order by announcement date; each item contains
          pub_date/statement/process (event status, HK/A-share equities and trusts only)/
          record_date (not available for ETFs)/ex_date/dividend_payable_date/
          fiscal_year (fiscal year, ETF only)
"""
import argparse
import json
import sys
import os as _os

sys.path.insert(0, _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..")))
from common import (
    create_quote_context,
    check_ret,
    safe_close,
    is_empty,
    df_to_records,
    disp_width,
)

_SEP = "=" * 64
_DASH = "-" * 64


def _opt(val):
    if val is None or val == "" or val == "--" or (isinstance(val, float) and val != val):
        return "-"
    return str(val)


def _trunc(s, max_chars):
    if len(s) <= max_chars:
        return s
    return s[:max_chars - 1] + "..."


def _print_left_table(columns, rows):
    widths = {col: disp_width(col) for col in columns}
    for row in rows:
        for col in columns:
            widths[col] = max(widths[col], disp_width(row.get(col, "-")))
    header = "  ".join(col + " " * max(0, widths[col] - disp_width(col)) for col in columns)
    print(header)
    for row in rows:
        cells = []
        for col in columns:
            s = row.get(col, "-")
            cells.append(s + " " * max(0, widths[col] - disp_width(s)))
        print("  ".join(cells))


def _build_display_rows(items):
    candidate_cols = ["Pub Date", "Statement", "Process", "Record Date", "Ex Date", "Payable Date", "Fiscal Year"]
    rows = []
    for item in items:
        row = {
            "Pub Date":     _opt(item.get("pub_date")),
            "Statement":    _trunc(_opt(item.get("statement", "")).strip() or "-", 50),
            "Process":      _opt(item.get("process")),
            "Record Date":  _opt(item.get("record_date")),
            "Ex Date":      _opt(item.get("ex_date")),
            "Payable Date": _opt(item.get("dividend_payable_date")),
            "Fiscal Year":  _opt(item.get("fiscal_year")),
        }
        rows.append(row)
    cols = [c for c in candidate_cols if any(r.get(c, "-") != "-" for r in rows)]
    return cols, rows


def get_corporate_actions_dividends(code, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        ret, data = ctx.get_corporate_actions_dividends(code)
        check_ret(ret, data, ctx, "get dividends")

        dividend_list = data.get("dividend_list", []) if isinstance(data, dict) else None
        no_data = is_empty(data) or not dividend_list
        if no_data:
            if output_json:
                print(json.dumps({"code": code, "data": {}}))
            else:
                print("No data")
            return

        if output_json:
            print(json.dumps({"code": code, "data": dividend_list}, ensure_ascii=False))
        else:
            print(_SEP)
            print(f"Dividends: {code}")
            print(_DASH)
            cols, rows = _build_display_rows(dividend_list)
            _print_left_table(cols, rows)
            print(_DASH)
            print(f"Count: {len(dividend_list)}")
            print(_SEP)

    except SystemExit:
        raise
    except Exception as e:
        if output_json:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))
        else:
            print(f"Error: {e}")
        sys.exit(1)
    finally:
        safe_close(ctx)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Get stock dividend history",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("code", help="Stock code, e.g. HK.00700")
    parser.add_argument("--json", action="store_true", dest="output_json",
                        help="Output in JSON format")
    args = parser.parse_args()
    get_corporate_actions_dividends(args.code, output_json=args.output_json)
