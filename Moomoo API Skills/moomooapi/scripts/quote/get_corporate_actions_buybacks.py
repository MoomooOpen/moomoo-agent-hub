#!/usr/bin/env python3
"""
Get Buybacks

Function: Get buyback history for a stock (HK / A-shares) with pagination support;
          HK and A-share data are returned as separate lists with different field structures
Usage: python get_corporate_actions_buybacks.py [-h] [--next-key NEXT_KEY] [--num NUM] [--json] code

API Limits:
- Max 30 requests per 30 seconds
- Supports HK and A-share equities and funds

Parameter Description:
- code: Stock code, e.g. HK.00700
- --next-key: Pagination key; omit for first page; "-1" means no more data
- --num: Number of results per page, default 10, range 1-50

Return Field Description:
- data.next_key:         Pagination key; "-1" means no more data
- data.hk_buy_back_list: HK buyback list; each item contains publ_date_str/end_date_str/
                         buy_back_money/buy_back_sum/percentage/high_price/low_price/
                         cumulative_sum/cumulative_percentage/share_type
- data.a_buy_back_list:  A-share buyback list; each item contains advance_date_str/
                         start_date_str/end_date_str/buy_back_mode/buy_back_sum/
                         buy_back_money/percentage and other process date/amount fields
"""
import argparse
import json
import math
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
    format_big_number,
)

_SEP = "=" * 64
_DASH = "-" * 64


def _opt(val):
    if val is None or (isinstance(val, float) and math.isnan(val)) or val == "":
        return "-"
    return str(val)


def _fmt_money(val):
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return "-"
    try:
        return format_big_number(float(val))
    except (TypeError, ValueError):
        return "-"


def _fmt_pct(val):
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return "-"
    try:
        return f"{float(val):.6f}%"
    except (TypeError, ValueError):
        return "-"


def _fmt_price(val):
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return "-"
    try:
        return f"{float(val):.3f}"
    except (TypeError, ValueError):
        return "-"


def _fmt_range(lo, hi, fmt_fn):
    lo_str = fmt_fn(lo)
    hi_str = fmt_fn(hi)
    if lo_str == "-" and hi_str == "-":
        return "-"
    if lo_str == "-":
        return f"~{hi_str}"
    if hi_str == "-":
        return f"{lo_str}~"
    if lo_str == hi_str:
        return lo_str
    return f"{lo_str}~{hi_str}"


def _fmt_date_range(s, e):
    s_str = _opt(s)
    e_str = _opt(e)
    if s_str == "-" and e_str == "-":
        return "-"
    if s_str == "-":
        return e_str
    if e_str == "-":
        return s_str
    if s_str == e_str:
        return s_str
    return f"{s_str}~{e_str}"


def _build_hk_display_df(df):
    rows = []
    for _, row in df.iterrows():
        rows.append({
            "Publ Date Str":          _opt(row.get("publ_date_str")),
            "End Date Str":           _opt(row.get("end_date_str")),
            "Buy Back Money":         _fmt_money(row.get("buy_back_money")),
            "Buy Back Sum":           format_big_number(row.get("buy_back_sum")),
            "Percentage":             _fmt_pct(row.get("percentage")),
            "Price Range":            _fmt_range(row.get("low_price"), row.get("high_price"), _fmt_price),
            "Cumulative Sum":         format_big_number(row.get("cumulative_sum")),
            "Cumulative Percentage":  _fmt_pct(row.get("cumulative_percentage")),
            "Share Type":             _opt(row.get("share_type")),
        })
    return pd.DataFrame(rows)


def _build_a_display_df(df):
    rows = []
    for _, row in df.iterrows():
        rows.append({
            "Change Reg Date Str":  _opt(row.get("change_reg_date_str")),
            "Change Date Str":      _opt(row.get("change_date_str")),
            "Event Process":        _opt(row.get("event_proce_desc")),
            "Advance Date Str":     _opt(row.get("advance_date_str")),
            "Meet Pass Date Str":   _opt(row.get("meet_pass_date_str")),
            "Period":               _fmt_date_range(row.get("start_date_str"), row.get("end_date_str")),
            "Pay Date Str":         _opt(row.get("pay_date_str")),
            "Seller":               _opt(row.get("seller")),
            "Buy Back Mode":        _opt(row.get("buy_back_mode")),
            "Share Type":           _opt(row.get("share_type")),
            "Buy Back Sum":         format_big_number(row.get("buy_back_sum")),
            "Buy Back Money":       _fmt_money(row.get("buy_back_money")),
            "Percentage":           _fmt_pct(row.get("percentage")),
            "Value Range":          _fmt_range(row.get("value_floor"), row.get("value_ceiling"), _fmt_money),
            "Price Range":          _fmt_range(row.get("price_floor"), row.get("price_ceiling"), _fmt_price),
            "Volume Range":         _fmt_range(row.get("volume_floor"), row.get("volume_ceiling"), format_big_number),
        })
    return pd.DataFrame(rows)


def _nk_display(nk):
    if nk == "-1" or nk is None:
        return "End(-1)"
    return str(nk)


def get_corporate_actions_buybacks(code, next_key=None, num=None, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        ret, data = ctx.get_corporate_actions_buybacks(code, next_key=next_key, num=num)
        check_ret(ret, data, ctx, "get buybacks")

        if is_empty(data):
            if output_json:
                print(json.dumps({"code": code, "data": {
                    "next_key": "-1", "hk_buy_back_list": [], "a_buy_back_list": []
                }}))
            else:
                print("No data")
            return

        nk = data.get("next_key", "-1") if isinstance(data, dict) else "-1"
        hk_df = data.get("hk_buy_back_list") if isinstance(data, dict) else None
        a_df = data.get("a_buy_back_list") if isinstance(data, dict) else None

        if hk_df is None or not isinstance(hk_df, pd.DataFrame):
            hk_df = pd.DataFrame()
        if a_df is None or not isinstance(a_df, pd.DataFrame):
            a_df = pd.DataFrame()

        hk_empty = hk_df.empty
        a_empty = a_df.empty
        total_count = (0 if hk_empty else len(hk_df)) + (0 if a_empty else len(a_df))

        if output_json:
            print(json.dumps({
                "code": code,
                "data": {
                    "next_key": nk,
                    "hk_buy_back_list": df_to_records(hk_df) if not hk_empty else [],
                    "a_buy_back_list": df_to_records(a_df) if not a_empty else [],
                },
            }, ensure_ascii=False, default=str))
        else:
            if hk_empty and a_empty:
                print("No data")
            else:
                print(_SEP)
                print(f"Buybacks: {code}")
                print(_DASH)
                if not hk_empty:
                    print(f"HK Buybacks ({len(hk_df)} records)")
                    print(_DASH)
                    print_display_df(_build_hk_display_df(hk_df), max_colwidth=30)
                    if not a_empty:
                        print(_DASH)
                if not a_empty:
                    print(f"A-Share Buybacks ({len(a_df)} records)")
                    print(_DASH)
                    print_display_df(_build_a_display_df(a_df), max_colwidth=24)
                print(_DASH)
                print(f"Count: {total_count}  --next-key: {_nk_display(nk)}")
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
        description="Get stock buyback history with pagination support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("code", help="Stock code, e.g. HK.00700")
    parser.add_argument("--next-key", default=None, dest="next_key",
                        help='Pagination key; omit for first page; "-1" means no more data')
    parser.add_argument("--num", type=int, default=None,
                        help="Number of results per page, default 10, range 1-50")
    parser.add_argument("--json", action="store_true", dest="output_json",
                        help="Output in JSON format")
    args = parser.parse_args()

    get_corporate_actions_buybacks(
        args.code,
        next_key=args.next_key,
        num=args.num,
        output_json=args.output_json,
    )
