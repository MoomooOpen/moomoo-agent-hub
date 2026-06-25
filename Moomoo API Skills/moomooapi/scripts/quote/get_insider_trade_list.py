#!/usr/bin/env python3
"""
Get Insider Trade List

Function: Get insider (executives/directors/major shareholders) trade records for a US stock,
          with optional holder filter and pagination support
Usage: python get_insider_trade_list.py [-h] [--holder-id HOLDER_ID] [--next-key NEXT_KEY] [--num NUM] [--json] code

API Limits:
- Max 30 requests per 30 seconds
- Supports US equities and funds

Parameter Description:
- code: Stock code, e.g. US.AAPL
- --holder-id: Holder object ID; omit to query all insiders; can be obtained from
               GetInsiderHolderList (3241) or from this API's returned holder_id
- --next-key: Pagination key; omit for first page; "-1" means no more data
- --num: Number of results per page, default 10, range 1-50

Return Field Description:
- data.all_count: Total record count
- data.next_key:  Pagination key; "-1" means no more data
- data.items[]:   Insider trade list; each item contains holder_id/name/title/
                  transaction_type/trade_shares/min_price/max_price/min_trade_date/
                  min_trade_date_str/max_trade_date/max_trade_date_str/
                  security_holder_quantity/is_proposed_sale_of_securities/
                  security_description/source_group_name
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
    any_large_shares = any(
        (r.get("trade_shares") is not None
         and not (isinstance(r.get("trade_shares"), float) and pd.isna(r.get("trade_shares")))
         and abs(float(r.get("trade_shares") or 0)) >= 10000)
        for _, r in data.iterrows()
    )
    any_large_qty = any(
        (r.get("security_holder_quantity") is not None
         and not (isinstance(r.get("security_holder_quantity"), float) and pd.isna(r.get("security_holder_quantity")))
         and abs(float(r.get("security_holder_quantity") or 0)) >= 10000)
        for _, r in data.iterrows()
    )
    for _, row in data.iterrows():
        minp_raw = row.get("min_price")
        maxp_raw = row.get("max_price")
        minp_null = minp_raw is None or (isinstance(minp_raw, float) and pd.isna(minp_raw))
        maxp_null = maxp_raw is None or (isinstance(maxp_raw, float) and pd.isna(maxp_raw))
        minp = float(minp_raw) if not minp_null else 0.0
        maxp = float(maxp_raw) if not maxp_null else 0.0

        if minp <= 0 and maxp <= 0:
            price_range = "N/A"
        elif minp == maxp or maxp <= 0:
            price_range = f"{minp:.3f}"
        elif minp <= 0:
            price_range = f"{maxp:.3f}"
        else:
            price_range = f"{minp:.3f}~{maxp:.3f}"

        mind = str(row.get("min_trade_date_str") or "").strip()
        maxd = str(row.get("max_trade_date_str") or "").strip()
        if not mind and not maxd:
            date_range = "N/A"
        elif mind == maxd or not maxd:
            date_range = mind
        elif not mind:
            date_range = maxd
        else:
            date_range = f"{mind}~{maxd}"

        is_plan = row.get("is_proposed_sale_of_securities")
        is_plan_nan = is_plan is None or (isinstance(is_plan, float) and pd.isna(is_plan))

        shares_raw = row.get("trade_shares")
        shares_nan = shares_raw is None or (isinstance(shares_raw, float) and pd.isna(shares_raw))
        shares_display = (
            "-" if shares_nan
            else (format_big_number(int(shares_raw)) if any_large_shares else str(int(shares_raw)))
        )

        qty_raw = row.get("security_holder_quantity")
        qty_nan = qty_raw is None or (isinstance(qty_raw, float) and pd.isna(qty_raw))
        qty_display = (
            "-" if qty_nan
            else (format_big_number(int(qty_raw)) if any_large_qty else str(int(qty_raw)))
        )

        _hid = row.get("holder_id")
        rows.append({
            "Holder Id":          int(_hid or 0) if not (isinstance(_hid, float) and pd.isna(_hid or 0)) else "-",
            "Name":               str(row.get("name") or "") or "-",
            "Title":              str(row.get("title") or "") or "-",
            "Transaction Type":   str(row.get("transaction_type") or "") or "-",
            "Trade Shares":       shares_display,
            "Holder Quantity":    qty_display,
            "Price Range":        price_range,
            "Date Range":         date_range,
            "Is Proposed Sale":   ("Yes" if is_plan else "No") if not is_plan_nan else "-",
            "Security Desc":      str(row.get("security_description") or "") or "-",
            "Source Group Name":  str(row.get("source_group_name") or "") or "-",
        })
    return pd.DataFrame(rows)


def get_insider_trade_list(code, holder_id=None, num=None, next_key=None, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        ret, data = ctx.get_insider_trade_list(code, holder_id=holder_id, num=num, next_key=next_key)
        check_ret(ret, data, ctx, "get insider trade list")

        all_count = data.attrs.get("all_count") if hasattr(data, "attrs") else None
        ret_next_key = str(data.attrs.get("next_key", "-1")) if hasattr(data, "attrs") else "-1"
        all_count = int(all_count) if all_count is not None else 0
        row_count = len(data) if not is_empty(data) else 0
        next_key_display = "End(-1)" if ret_next_key == "-1" else ret_next_key

        if output_json:
            records = [] if is_empty(data) else df_to_records(data)
            print(json.dumps({
                "code": code,
                "data": {
                    "all_count": all_count,
                    "next_key": ret_next_key,
                    "items": records,
                },
            }, ensure_ascii=False))
        else:
            if is_empty(data):
                print("No data")
            else:
                print(_SEP)
                print(f"Insider Trade List: {code}")
                print(_DASH)
                print_display_df(_build_display_df(data), max_colwidth=22)
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
        description="Get insider trade list (US stocks only) with pagination support"
    )
    parser.add_argument("code", help="Stock code, e.g. US.AAPL")
    parser.add_argument("--holder-id", type=int, default=None, dest="holder_id",
                        help="Holder object ID; omit to query all insiders; "
                             "can be obtained from GetInsiderHolderList (3241) or this API")
    parser.add_argument("--next-key", default=None, dest="next_key",
                        help='Pagination key; omit for first page; "-1" means no more data')
    parser.add_argument("--num", type=int, default=None,
                        help="Number of results per page, default 10, range 1-50")
    parser.add_argument("--json", action="store_true", dest="output_json",
                        help="Output in JSON format")
    args = parser.parse_args()
    get_insider_trade_list(
        args.code, holder_id=args.holder_id,
        num=args.num, next_key=args.next_key, output_json=args.output_json,
    )
