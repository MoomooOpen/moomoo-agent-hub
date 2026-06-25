#!/usr/bin/env python3
"""
Get Shareholders Holding Changes

Function: Get shareholder holding change records (increase/decrease/initiate/close out)
          with pagination support
Usage: python get_shareholders_holding_changes.py [-h] [--next-key NEXT_KEY] [--num NUM] [--sort-type SORT_TYPE] [--sort-column SORT_COLUMN] [--filter-type FILTER_TYPE] [--json] code

API Limits:
- Max 30 requests per 30 seconds
- Supports HK and US equities and funds
- Pagination supported, default 10 per page, max 50

Parameter Description:
- code: Stock code, e.g. HK.00700
- --next-key: Pagination key; omit for first page; "-1" means no more data
- --num: Number of results per page, default 10, range 1-50
- --sort-type: Sort direction: 1=Desc (default), 2=Asc
- --sort-column: Sort field: 62=Share Change Num (default), 63=Holding Date, 64=Ratio Change,
                 65=Change Amount, 66=Holder Pct
- --filter-type: Filter type: 0=All (default), 1=Increase, 2=Decrease, 3=New In, 4=Close Out

Return Field Description:
- data.next_key:  Pagination key; "-1" means no more data
- data.items[]:   Holding change record list; each item contains period_text/name/holder_id/
                  holder_type/holder_type_id/holding_date_str/share_change_num/
                  shares_change_price/share_ratio/share_ratio_change/share_num
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


def _fmt_pct(val):
    try:
        return f"{float(val):.2f}%"
    except (TypeError, ValueError):
        return str(val) if val is not None else "-"


def _build_display_df(data):
    rows = []
    for _, row in data.iterrows():
        period_text = str(row.get("period_text") or "") or "-"
        name = str(row.get("name") or "") or "-"
        holder_id = row.get("holder_id")
        share_change_num = row.get("share_change_num")
        shares_change_price = row.get("shares_change_price")
        share_ratio = row.get("share_ratio")
        holder_type = str(row.get("holder_type") or "") or "-"
        holder_type_id = row.get("holder_type_id")
        holding_date_str = str(row.get("holding_date_str") or "") or "-"
        share_ratio_change = row.get("share_ratio_change")
        share_num = row.get("share_num")

        rows.append({
            "Period Text":         period_text,
            "Name":                name,
            "Holder Id":           str(holder_id) if holder_id is not None else "-",
            "Share Change Num":    format_big_number(share_change_num) if share_change_num is not None else "-",
            "Shares Change Price": format_big_number(shares_change_price) if shares_change_price is not None else "-",
            "Share Ratio":         _fmt_pct(share_ratio) if share_ratio is not None else "-",
            "Holder Type":         f"{holder_type}({holder_type_id})" if holder_type_id is not None else holder_type,
            "Holding Date Str":    holding_date_str,
            "Share Ratio Change":  _fmt_pct(share_ratio_change) if share_ratio_change is not None else "-",
            "Share Num":           format_big_number(share_num) if share_num is not None else "-",
        })
    return pd.DataFrame(rows)


def get_shareholders_holding_changes(code, next_key=None, num=None, sort_type=None,
                                     sort_column=None, filter_type=None, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        ret, data = ctx.get_shareholders_holding_changes(
            code, next_key=next_key, num=num,
            sort_type=sort_type, sort_column=sort_column, filter_type=filter_type
        )
        check_ret(ret, data, ctx, "get shareholders holding changes")

        page_next_key = "-1"
        if not is_empty(data):
            page_next_key = str(data.iloc[0].get("next_key", -1)) if len(data) > 0 else "-1"

        next_key_display = "End(-1)" if page_next_key == "-1" else page_next_key
        row_count = len(data) if not is_empty(data) else 0

        if output_json:
            if is_empty(data):
                records = []
            else:
                records = df_to_records(data)
                for r in records:
                    r.pop("next_key", None)
            payload = {"code": code, "data": {"next_key": page_next_key, "items": records}}
            print(json.dumps(payload, ensure_ascii=False))
        else:
            if is_empty(data):
                print("No data")
            else:
                print(_SEP)
                print(f"Shareholders Holding Changes: {code}")
                print(_DASH)
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
        description="Get shareholder holding change list with pagination support"
    )
    parser.add_argument("code", help="Stock code, e.g. HK.00700")
    parser.add_argument("--next-key", default=None, dest="next_key",
                        help='Pagination key; omit for first page; "-1" means no more data')
    parser.add_argument("--num", type=int, default=None,
                        help="Number of results per page, default 10, range 1-50")
    parser.add_argument("--sort-type", type=int, default=None, dest="sort_type",
                        help="Sort direction: 1=Desc (default), 2=Asc")
    parser.add_argument("--sort-column", type=int, default=None, dest="sort_column",
                        help="Sort field: 62=Share Change Num (default), 63=Holding Date, "
                             "64=Ratio Change, 65=Change Amount, 66=Holder Pct")
    parser.add_argument("--filter-type", type=int, default=None, dest="filter_type",
                        help="Filter type: 0=All (default), 1=Increase, 2=Decrease, 3=New In, 4=Close Out")
    parser.add_argument("--json", action="store_true", dest="output_json",
                        help="Output in JSON format")
    args = parser.parse_args()
    get_shareholders_holding_changes(
        args.code,
        next_key=args.next_key,
        num=args.num,
        sort_type=args.sort_type,
        sort_column=args.sort_column,
        filter_type=args.filter_type,
        output_json=args.output_json,
    )
