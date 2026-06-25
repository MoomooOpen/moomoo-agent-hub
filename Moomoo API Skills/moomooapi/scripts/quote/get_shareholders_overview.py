#!/usr/bin/env python3
"""
Get Shareholders Overview

Function: Get major shareholders (main_holder) and holding type (holder_type) data for a stock
          in a single request; passing period_id=0 or omitting it also returns the available
          report period list (holding_period)
Usage: python get_shareholders_overview.py [-h] [--period-id PERIOD_ID] [--json] code

API Limits:
- Max 30 requests per 30 seconds
- Supports HK and US equities and funds

Parameter Description:
- code: Stock code, e.g. HK.00700
- --period-id: Report period ID; pass 0 or omit to get latest data plus the available period list

Return Field Description:
- data.main_holder:     Major shareholder list; each item contains static_date_str/name/
                        holder_pct/holder_id
- data.holder_type:     Holding type list; same structure (holder_id is 0)
- data.holding_period:  Available report period list (first request only); each item contains
                        period_text/period_id
"""
import argparse
import json
import sys
import os as _os

import pandas as pd

sys.path.insert(0, _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..")))
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


def _fmt_pct(val):
    try:
        return f"{float(val):.2f}%"
    except (TypeError, ValueError):
        return str(val) if val is not None else ""


def get_shareholders_overview(code, period_id=None, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        ret, data = ctx.get_shareholders_overview(code, period_id=period_id)
        check_ret(ret, data, ctx, "get shareholders overview")

        main_holder_df = data.get("main_holder") if isinstance(data, dict) else None
        holder_type_df = data.get("holder_type") if isinstance(data, dict) else None
        hp_df = data.get("holding_period") if isinstance(data, dict) else None

        no_data = is_empty(data) or (
            is_empty(main_holder_df) and is_empty(holder_type_df) and is_empty(hp_df)
        )
        if no_data:
            if output_json:
                print(json.dumps({"code": code, "data": {}}, ensure_ascii=False))
            else:
                print("No data")
            return

        mh_rows = 0 if is_empty(main_holder_df) else len(main_holder_df)
        ht_rows = 0 if is_empty(holder_type_df) else len(holder_type_df)
        hp_rows = 0 if is_empty(hp_df) else len(hp_df)

        if output_json:
            print(json.dumps({"code": code, "data": {
                "main_holder": df_to_records(main_holder_df) if not is_empty(main_holder_df) else [],
                "holder_type": df_to_records(holder_type_df) if not is_empty(holder_type_df) else [],
                "holding_period": df_to_records(hp_df) if not is_empty(hp_df) else [],
            }}, ensure_ascii=False))
        else:
            print(_SEP)
            print(f"Shareholders Overview: {code}")

            print(_DASH)
            print("[Main Holder]")
            if not is_empty(main_holder_df):
                rows = []
                for _, row in main_holder_df.iterrows():
                    holder_id_val = row.get("holder_id")
                    if (holder_id_val is None
                            or (isinstance(holder_id_val, float) and pd.isna(holder_id_val))
                            or holder_id_val == 0):
                        hid_str = "-"
                    else:
                        hid_str = str(int(holder_id_val))
                    rows.append({
                        "Static Date Str":  str(row.get("static_date_str", "") or ""),
                        "Name":             str(row.get("name", "") or ""),
                        "Holder Pct":       _fmt_pct(row.get("holder_pct")),
                        "Holder Id":        hid_str,
                    })
                print_display_df(pd.DataFrame(rows), max_colwidth=30)
            else:
                print("(No data)")

            print(_DASH)
            print("[Holder Type]")
            if not is_empty(holder_type_df):
                rows = []
                for _, row in holder_type_df.iterrows():
                    rows.append({
                        "Static Date Str": str(row.get("static_date_str", "") or ""),
                        "Name":            str(row.get("name", "") or ""),
                        "Holder Pct":      _fmt_pct(row.get("holder_pct")),
                    })
                print_display_df(pd.DataFrame(rows), max_colwidth=30)
            else:
                print("(No data)")

            if hp_df is not None and not is_empty(hp_df):
                print(_DASH)
                print("Available report periods (holding_period):")
                h_rows = []
                for _, row in hp_df.iterrows():
                    h_rows.append({
                        "Period Text": str(row.get("period_text", "") or ""),
                        "Period Id":   str(row.get("period_id", "") or ""),
                    })
                print_display_df(pd.DataFrame(h_rows), max_colwidth=20)

            print(_DASH)
            print(f"Count: main_holder={mh_rows}  holder_type={ht_rows}  holding_period={hp_rows}")
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
    parser = argparse.ArgumentParser(description="Get shareholder holding overview")
    parser.add_argument("code", help="Stock code, e.g. HK.00700")
    parser.add_argument("--period-id", type=int, default=None, dest="period_id",
                        help="Report period ID; pass 0 or omit to get latest data plus the available period list")
    parser.add_argument("--json", action="store_true", dest="output_json",
                        help="Output in JSON format")
    args = parser.parse_args()

    get_shareholders_overview(
        args.code,
        period_id=args.period_id,
        output_json=args.output_json,
    )
