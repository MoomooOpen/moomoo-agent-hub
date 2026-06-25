#!/usr/bin/env python3
"""
Get Short Interest

Function: Get short interest history for US or HK stocks, including short shares,
          short percent, days to cover, close price etc. with pagination support;
          SDK returns (ret, us_df, hk_df) — one will be populated based on the market
Usage: python get_short_interest.py [-h] [--next-key NEXT_KEY] [--num NUM] [--json] code

API Limits:
- Max 30 requests per 30 seconds
- Supports HK and US equities and funds
- Max 50 records per request, default 10

Parameter Description:
- code: Stock code, e.g. US.AAPL
- --next-key: Pagination key; omit for first page; "-1" means no more data
- --num: Number of results per page, default 10, range 1-50

Return Field Description:
- data.next_key:  Pagination key; "-1" means no more data
- data.items[]:   Short interest list (US or HK depending on stock market)
  US items contain: timestamp_str/shares_short/short_percent/avg_daily_share_volume/
                    days_to_cover/close_price/last_close_price
  HK items contain: timestamp/timestamp_str/close_price/last_close_price/
                    aggregated_short/aggregated_short_ratio
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

_SEP = "=" * 64
_DASH = "-" * 64


def _fmt_pct(val, decimals=2):
    try:
        return f"{float(val):.{decimals}f}%"
    except Exception:
        return "-"


def _fmt_price(val, decimals=3):
    try:
        return f"{float(val):.{decimals}f}"
    except Exception:
        return "-"


def get_short_interest(code, next_key=None, num=None, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        kwargs = {}
        if next_key is not None:
            kwargs["next_key"] = next_key
        if num is not None:
            kwargs["num"] = num
        ret, us_df, hk_df = ctx.get_short_interest(code, **kwargs)
        check_ret(ret, us_df, ctx, "get short interest")

        if is_empty(us_df) and is_empty(hk_df):
            if output_json:
                print(json.dumps({"code": code, "data": {}}))
            else:
                print("No data")
            return

        is_us = code.upper().startswith("US.")
        nk = us_df.attrs.get("next_key", "") if is_us else hk_df.attrs.get("next_key", "")

        if output_json:
            if is_us:
                records = df_to_records(us_df) if not us_df.empty else []
            else:
                records = df_to_records(hk_df) if not hk_df.empty else []
            print(json.dumps({"code": code, "data": {"next_key": nk, "items": records}},
                             ensure_ascii=False, default=str))
            return

        if is_us:
            row_count = len(us_df)
            print(_SEP)
            print(f"Short Interest: {code}")
            print(_DASH)
            if not us_df.empty:
                disp = us_df.copy()
                disp = disp.drop(columns=["timestamp"], errors="ignore")
                if "short_percent" in disp.columns:
                    disp["short_percent"] = disp["short_percent"].apply(
                        lambda x: _fmt_pct(x) if x is not None else "-")
                for col in ("shares_short", "avg_daily_share_volume"):
                    if col in disp.columns:
                        disp[col] = disp[col].apply(
                            lambda x: format_big_number(x) if x is not None else "-")
                if "days_to_cover" in disp.columns:
                    disp["days_to_cover"] = disp["days_to_cover"].apply(
                        lambda x: _fmt_price(x, decimals=2) if x is not None else "-")
                for col in ("close_price", "last_close_price"):
                    if col in disp.columns:
                        disp[col] = disp[col].apply(
                            lambda x: _fmt_price(x) if x is not None else "-")
                disp = disp.rename(columns={
                    "timestamp_str":         "Timestamp Str",
                    "shares_short":          "Shares Short",
                    "short_percent":         "Short Percent",
                    "avg_daily_share_volume": "Avg Daily Share Volume",
                    "days_to_cover":         "Days To Cover",
                    "close_price":           "Close Price",
                    "last_close_price":      "Last Close Price",
                })
                print_display_df(disp, max_colwidth=20)
            else:
                print("  No data")
        else:
            row_count = len(hk_df)
            print(_SEP)
            print(f"Short Interest: {code}")
            print(_DASH)
            if not hk_df.empty:
                disp = hk_df.copy()
                disp = disp.drop(columns=["timestamp"], errors="ignore")
                if "aggregated_short_ratio" in disp.columns:
                    disp["aggregated_short_ratio"] = disp["aggregated_short_ratio"].apply(
                        lambda x: _fmt_pct(x) if x is not None else "-")
                if "aggregated_short" in disp.columns:
                    disp["aggregated_short"] = disp["aggregated_short"].apply(
                        lambda x: format_big_number(x) if x is not None else "-")
                for col in ("close_price", "last_close_price"):
                    if col in disp.columns:
                        disp[col] = disp[col].apply(
                            lambda x: _fmt_price(x) if x is not None else "-")
                disp = disp.rename(columns={
                    "timestamp_str":         "Timestamp Str",
                    "aggregated_short":      "Aggregated Short",
                    "aggregated_short_ratio": "Aggregated Short Ratio",
                    "close_price":           "Close Price",
                    "last_close_price":      "Last Close Price",
                })
                print_display_df(disp, max_colwidth=20)
            else:
                print("  No data")

        nk_display = "End(-1)" if (not nk or nk == "-1") else str(nk)
        print(_DASH)
        print(f"Count: {row_count}   --next-key: {nk_display}")
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
    parser = argparse.ArgumentParser(
        description="Get short interest data with pagination support"
    )
    parser.add_argument("code", help="Stock code, e.g. US.AAPL")
    parser.add_argument("--next-key", default=None, dest="next_key",
                        help='Pagination key; omit for first page; "-1" means no more data')
    parser.add_argument("--num", type=int, default=None, dest="num",
                        help="Number of results per page, default 10, range 1-50")
    parser.add_argument("--json", action="store_true", dest="output_json",
                        help="Output in JSON format")
    args = parser.parse_args()
    get_short_interest(args.code, next_key=args.next_key, num=args.num,
                       output_json=args.output_json)
