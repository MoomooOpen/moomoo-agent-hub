#!/usr/bin/env python3
"""
Get Earnings Price Move

Function: Get stock price performance data around earnings dates for multiple periods
Usage: python get_financials_earnings_price_move.py [-h] [--period-count N] [--json] code

API Limits:
- Max 30 requests per 30 seconds
- Supports HK and US equities

Parameter Description:
- code: Stock code, e.g. HK.00700
- --period-count: Number of earnings periods, default 10, range 1-50

Return Field Description:
- data.period_count: Total number of earnings periods
- data.items[]: Flattened list; each row contains period metadata
  (fiscal_year/financial_type/period_text/pub_trading_day_str/pub_type/price_info_index)
  and daily quotes (day_offset/trading_day_str/close_price/open_price/highest_price/
  lowest_price/last_close_price/option_iv/option_hv)
"""
import argparse
import json
import math
import sys
import os as _os
sys.path.insert(0, _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..")))
import pandas as pd
from common import (
    create_quote_context,
    check_ret,
    safe_close,
    is_empty,
    df_to_records,
    print_display_df,
)

_SEP = "=" * 64
_DASH = "-" * 64

_PUB_TYPE_MAP = {0: "Unknown", 1: "Pre-Market", 2: "After-Market", 3: "During-Market"}


def _fmt_float(v, decimals=3):
    if v is None:
        return "-"
    if isinstance(v, float) and math.isnan(v):
        return "-"
    try:
        return f"{float(v):.{decimals}f}"
    except (TypeError, ValueError):
        return "-"


def _day_offset_str(val):
    try:
        v = int(val)
    except (TypeError, ValueError):
        return "-"
    if v < 0:
        return f"{v} days"
    if v == 0:
        return "Day 0"
    return f"+{v} days"


def _pub_type_str(val):
    try:
        v = int(val)
    except (TypeError, ValueError):
        return "-"
    if v == 0:
        return "-"
    label = _PUB_TYPE_MAP.get(v)
    return label if label is not None else str(v)


def _build_display_df(data: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in data.iterrows():
        rows.append({
            "Period Text":         str(row.get("period_text", "") or ""),
            "Pub Trading Day Str": str(row.get("pub_trading_day_str", "") or ""),
            "Pub Type":            _pub_type_str(row.get("pub_type")),
            "Day Offset":          _day_offset_str(row.get("day_offset")),
            "Trading Day Str":     str(row.get("trading_day_str", "") or ""),
            "Close Price":         _fmt_float(row.get("close_price")),
            "Open Price":          _fmt_float(row.get("open_price")),
            "Highest Price":       _fmt_float(row.get("highest_price")),
            "Lowest Price":        _fmt_float(row.get("lowest_price")),
            "Last Close Price":    _fmt_float(row.get("last_close_price")),
            "Option IV":           _fmt_float(row.get("option_iv"), decimals=2),
            "Option HV":           _fmt_float(row.get("option_hv"), decimals=2),
        })
    return pd.DataFrame(rows)


def get_financials_earnings_price_move(code, period_count=None, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        kwargs = {}
        if period_count is not None:
            kwargs["period_count"] = period_count
        ret, data = ctx.get_financials_earnings_price_move(code, **kwargs)
        check_ret(ret, data, ctx, "get earnings price move")

        if is_empty(data):
            if output_json:
                print(json.dumps({"code": code, "data": {}}, ensure_ascii=False))
            else:
                print("No data")
            return

        if output_json:
            print(json.dumps({
                "code": code,
                "data": {
                    "period_count": period_count,
                    "items": df_to_records(data, limit=500),
                },
            }, ensure_ascii=False, default=str))
        else:
            print(_SEP)
            print(f"Earnings Price Move: {code}")
            print(_DASH)
            print_display_df(_build_display_df(data), max_colwidth=24)
            print(_DASH)
            n_periods = data["period_text"].nunique() if "period_text" in data.columns else len(data)
            print(f"Total {n_periods} periods")
            print(_SEP)

    except Exception as e:
        if output_json:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))
        else:
            print(f"Error: {e}")
        sys.exit(1)
    finally:
        safe_close(ctx)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get stock price performance around earnings dates")
    parser.add_argument("code", help="Stock code, e.g. HK.00700")
    parser.add_argument("--period-count", type=int, default=None, metavar="N",
                        help="Number of earnings periods, default 10, range 1-50")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output in JSON format")
    args = parser.parse_args()
    get_financials_earnings_price_move(args.code, period_count=args.period_count, output_json=args.output_json)
