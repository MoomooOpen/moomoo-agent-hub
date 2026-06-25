#!/usr/bin/env python3
"""
Get Shareholders Institutional

Function: Get institutional shareholder count and holding quantity history for a stock
          with pagination support
Usage: python get_shareholders_institutional.py [-h] [--next-key NEXT_KEY] [--num NUM] [--json] code

API Limits:
- Max 30 requests per 30 seconds
- Supports HK and US equities and funds

Parameter Description:
- code: Stock code, e.g. US.AAPL
- --next-key: Pagination key; omit for first page; "-1" means no more data
- --num: Number of results per page, default 10, range 1-50

Return Field Description:
- data.update_time / data.update_time_str: Data update timestamp and date (YYYY-MM-DD HH:MM:SS)
- data.next_key:   Pagination key; "-1" means no more data
- data.items[]:    Institutional holding list; each item contains period_text/
                   institution_quantity/institution_quantity_change/holder_quantity/
                   holder_quantity_change/holder_pct/holder_pct_change
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
    print_display_df,
    safe_int,
    format_big_number,
)

import pandas as pd

_SEP = "=" * 64
_DASH = "-" * 64


def _fmt_pct(val):
    if val is None:
        return "-"
    try:
        return f"{float(val):.2f}%"
    except (TypeError, ValueError):
        return "-"


def _build_institution_display_df(items):
    rows = []
    for _, row in items.iterrows():
        rows.append({
            "Period Text":               str(row.get("period_text") or "") or "-",
            "Institution Quantity":      safe_int(row.get("institution_quantity")),
            "Institution Quantity Change": safe_int(row.get("institution_quantity_change")),
            "Holder Quantity":           format_big_number(safe_int(row.get("holder_quantity"))),
            "Holder Quantity Change":    format_big_number(safe_int(row.get("holder_quantity_change"))),
            "Holder Pct":                _fmt_pct(row.get("holder_pct")),
            "Holder Pct Change":         _fmt_pct(row.get("holder_pct_change")),
        })
    return pd.DataFrame(rows)


def get_shareholders_institutional(code, next_key=None, num=None, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        ret, data = ctx.get_shareholders_institutional(code, next_key=next_key, num=num)
        check_ret(ret, data, ctx, "get shareholders institutional")

        if is_empty(data):
            if output_json:
                print(json.dumps({"code": code, "data": {
                    "next_key": "-1",
                    "update_time": 0, "update_time_str": "", "items": []
                }}, ensure_ascii=False))
            else:
                print("No data")
            return

        first = data.iloc[0]
        next_key_out = str(first.get("next_key") or "-1")
        _ut = first.get("update_time")
        update_time = int(_ut) if _ut is not None and not (isinstance(_ut, float) and pd.isna(_ut)) else 0
        update_time_str = str(first.get("update_time_str") or "")

        item_cols = [c for c in data.columns if c not in ("next_key", "update_time", "update_time_str")]
        items = data[item_cols]
        count = len(items)

        if output_json:
            print(json.dumps({
                "code": code,
                "data": {
                    "next_key": next_key_out,
                    "update_time": update_time,
                    "update_time_str": update_time_str,
                    "items": df_to_records(items),
                },
            }, ensure_ascii=False))
        else:
            print(_SEP)
            print(f"Shareholders Institutional: {code}"
                  + (f"  Updated: {update_time_str}" if update_time_str else ""))
            print(_DASH)
            print_display_df(_build_institution_display_df(items), max_colwidth=24)
            print(_DASH)
            nk_display = "End(-1)" if next_key_out == "-1" else next_key_out
            print(f"Count: {count}   --next-key: {nk_display}")
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
        description="Get institutional shareholder statistics with pagination support"
    )
    parser.add_argument("code", help="Stock code, e.g. US.AAPL")
    parser.add_argument("--next-key", default=None, dest="next_key",
                        help='Pagination key; omit for first page; "-1" means no more data')
    parser.add_argument("--num", type=int, default=None,
                        help="Number of results per page, default 10, range 1-50")
    parser.add_argument("--json", action="store_true", dest="output_json",
                        help="Output in JSON format")
    args = parser.parse_args()
    get_shareholders_institutional(args.code, next_key=args.next_key, num=args.num,
                                   output_json=args.output_json)
