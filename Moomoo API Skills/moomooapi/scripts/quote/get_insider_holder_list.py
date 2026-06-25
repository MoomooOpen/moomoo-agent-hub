#!/usr/bin/env python3
"""
Get Insider Holder List

Function: Get insider (executives/directors/major shareholders) holding list for a US stock;
          first page additionally returns insider statistics summary
Usage: python get_insider_holder_list.py [-h] [--next-key NEXT_KEY] [--num NUM] [--json] code

API Limits:
- Max 30 requests per 30 seconds
- Supports US equities and funds
- First page additionally returns insider statistics (total/bought/sold count); subsequent pages do not

Parameter Description:
- code: Stock code, e.g. US.AAPL
- --next-key: Pagination key; omit for first page; "-1" means no more data
- --num: Number of results per page, default 10, range 1-20

Return Field Description:
- data.all_count:            Total record count
- data.next_key:             Pagination key; "-1" means no more data
- data.insider_total_count:  Total insider count (first page only)
- data.insider_bought_count: Total insiders who bought (first page only)
- data.insider_sold_count:   Total insiders who sold (first page only)
- data.items[]:              Insider holder list; each item contains holder_id/name/title/
                             holder_quantity/holder_pct
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
    format_big_number,
)

import pandas as pd

_SEP = "=" * 64
_DASH = "-" * 64


def _build_display_df(data):
    rows = []
    any_large_qty = any(
        (r.get("holder_quantity") is not None
         and not pd.isna(r.get("holder_quantity"))
         and abs(float(r.get("holder_quantity") or 0)) >= 10000)
        for _, r in data.iterrows()
    )
    for _, row in data.iterrows():
        qty_raw = row.get("holder_quantity")
        pct_raw = row.get("holder_pct")
        qty_display = (
            "-" if qty_raw is None or (isinstance(qty_raw, float) and pd.isna(qty_raw))
            else (format_big_number(qty_raw) if any_large_qty else str(int(qty_raw)))
        )
        pct_display = (
            "-" if pct_raw is None or (isinstance(pct_raw, float) and pd.isna(pct_raw))
            else f"{float(pct_raw):.2f}%"
        )
        _hid = row.get("holder_id")
        rows.append({
            "Holder Id":  int(_hid) if _hid is not None and not pd.isna(_hid) else 0,
            "Name":       str(row.get("name") or "") or "-",
            "Title":      str(row.get("title") or "") or "-",
            "Holder Quantity": qty_display,
            "Holder Pct": pct_display,
        })
    return pd.DataFrame(rows)


def get_insider_holder_list(code, next_key=None, num=None, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        ret, data = ctx.get_insider_holder_list(code, next_key=next_key, num=num)
        check_ret(ret, data, ctx, "get insider holder list")

        first = data.iloc[0] if (not is_empty(data)) else None
        _ac = first.get("all_count") if first is not None else None
        all_count = int(_ac) if _ac is not None and not (isinstance(_ac, float) and pd.isna(_ac)) else 0
        ret_next_key = str(first.get("next_key", -1)) if first is not None else "-1"
        insider_total = None
        insider_bought = None
        insider_sold = None
        if first is not None:
            _rt = first.get("insider_total_count")
            if _rt is not None and not (isinstance(_rt, float) and pd.isna(_rt)):
                insider_total = int(_rt)
            _rb = first.get("insider_bought_count")
            if _rb is not None and not (isinstance(_rb, float) and pd.isna(_rb)):
                insider_bought = int(_rb)
            _rs = first.get("insider_sold_count")
            if _rs is not None and not (isinstance(_rs, float) and pd.isna(_rs)):
                insider_sold = int(_rs)

        row_count = len(data) if not is_empty(data) else 0
        next_key_display = "End(-1)" if ret_next_key == "-1" else ret_next_key

        if output_json:
            if is_empty(data):
                records = []
            else:
                records = df_to_records(data)
                top_fields = {"all_count", "next_key", "insider_total_count",
                              "insider_bought_count", "insider_sold_count"}
                for r in records:
                    for f in top_fields:
                        r.pop(f, None)
            inner = {
                "all_count": all_count,
                "next_key": ret_next_key,
                "items": records,
            }
            if insider_total is not None:
                inner["insider_total_count"] = insider_total
                inner["insider_bought_count"] = insider_bought
                inner["insider_sold_count"] = insider_sold
            print(json.dumps({"code": code, "data": inner}, ensure_ascii=False))
        else:
            if is_empty(data) and insider_total is None:
                print("No data")
            else:
                print(_SEP)
                print(f"Insider Holder List: {code}")
                print(_DASH)
                if insider_total is not None:
                    print(f"Insider Summary (first page): Total={insider_total}  "
                          f"Bought={insider_bought}  Sold={insider_sold}")
                    print(_DASH)
                if is_empty(data):
                    print("No data")
                else:
                    print_display_df(_build_display_df(data), max_colwidth=30)
                print(_DASH)
                print(f"Count: {row_count}   --next-key: {next_key_display}")
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
        description="Get insider holder list (US stocks only) with pagination support"
    )
    parser.add_argument("code", help="Stock code, e.g. US.AAPL")
    parser.add_argument("--next-key", default=None, dest="next_key",
                        help='Pagination key; omit for first page; "-1" means no more data')
    parser.add_argument("--num", type=int, default=None,
                        help="Number of results per page, default 10, range 1-20")
    parser.add_argument("--json", action="store_true", dest="output_json",
                        help="Output in JSON format")
    args = parser.parse_args()
    get_insider_holder_list(args.code, next_key=args.next_key, num=args.num, output_json=args.output_json)
