#!/usr/bin/env python3
"""
Get Daily Short Volume

Function: Get daily short selling volume, ratio and price history for US or HK stocks
          with pagination support; SDK returns (ret, us_df, hk_df) — one will be populated
          based on the market
Usage: python get_daily_short_volume.py [-h] [--next-key NEXT_KEY] [--num NUM] [--json] code

API Limits:
- Max 30 requests per 30 seconds
- Supports HK and US equities and funds

Parameter Description:
- code: Stock code, e.g. US.AAPL
- --next-key: Pagination key; omit for first page; "-1" means no more data
- --num: Number of results per page, default 10, range 1-50

Return Field Description:
- data.next_key:               Pagination key; "-1" means no more data
- data.aggregated_short:       Aggregate short position shares (HK only)
- data.aggregated_short_ratio: Ratio to free float shares, value before % sign (HK only)
- data.new_time_str:           Latest data date string (HK only, YYYY-MM-DD)
- data.items[]:                Short volume list (US or HK depending on stock market)
  US items contain: timestamp_str/total_shares_short/nasdaq_shares_short/nyse_shares_short/
                    short_percent/volume/close_price/last_close_price/daily_trade_avg_ratio
  HK items contain: timestamp/timestamp_str/shares_traded/turnover/short_sell_shares_traded/
                    short_sell_turnover/open_price/close_price/last_close_price/daily_trade_avg_ratio
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


def get_daily_short_volume(code, next_key=None, num=None, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        kwargs = {}
        if next_key is not None:
            kwargs["next_key"] = next_key
        if num is not None:
            kwargs["num"] = num
        ret, us_df, hk_df = ctx.get_daily_short_volume(code, **kwargs)
        check_ret(ret, us_df, ctx, "get daily short volume")

        if is_empty(us_df) and is_empty(hk_df):
            if output_json:
                print(json.dumps({"code": code, "data": {}}))
            else:
                print("No data")
            return

        market = code.upper().split(".")[0] if "." in code else ""
        is_us = market == "US"

        if is_us:
            nk = us_df.attrs.get("next_key", "")
        else:
            nk = hk_df.attrs.get("next_key", "")

        if output_json:
            if is_us:
                records = df_to_records(us_df) if not us_df.empty else []
                print(json.dumps({
                    "code": code,
                    "data": {"next_key": nk, "items": records},
                }, ensure_ascii=False, default=str))
            else:
                attrs = hk_df.attrs if hasattr(hk_df, "attrs") else {}
                records = df_to_records(hk_df) if not hk_df.empty else []
                print(json.dumps({
                    "code": code,
                    "data": {
                        "next_key": nk,
                        "aggregated_short": attrs.get("aggregated_short"),
                        "aggregated_short_ratio": attrs.get("aggregated_short_ratio"),
                        "new_time_str": attrs.get("new_time_str"),
                        "items": records,
                    },
                }, ensure_ascii=False, default=str))
            return

        if is_us:
            print(_SEP)
            print(f"Daily Short Volume: {code}")
            print(_DASH)
            if not us_df.empty:
                disp = us_df.copy()
                disp = disp.drop(columns=["timestamp"], errors="ignore")
                for col in ["short_percent", "daily_trade_avg_ratio"]:
                    if col in disp.columns:
                        disp[col] = disp[col].apply(lambda x: _fmt_pct(x) if x is not None else "-")
                for col in ["total_shares_short", "nasdaq_shares_short", "nyse_shares_short", "volume"]:
                    if col in disp.columns:
                        disp[col] = disp[col].apply(lambda x: format_big_number(x) if x is not None else "-")
                for col in ["close_price", "last_close_price"]:
                    if col in disp.columns:
                        disp[col] = disp[col].apply(lambda x: f"{float(x):.3f}" if x is not None else "-")
                disp = disp.rename(columns={
                    "timestamp_str":         "Timestamp Str",
                    "total_shares_short":    "Total Shares Short",
                    "nasdaq_shares_short":   "Nasdaq Shares Short",
                    "nyse_shares_short":     "Nyse Shares Short",
                    "short_percent":         "Short Percent",
                    "volume":                "Volume",
                    "close_price":           "Close Price",
                    "last_close_price":      "Last Close Price",
                    "daily_trade_avg_ratio": "Daily Trade Avg Ratio",
                })
                print_display_df(disp, max_colwidth=18)
            else:
                print("  No data")
        else:
            attrs = hk_df.attrs if hasattr(hk_df, "attrs") else {}
            agg_short = attrs.get("aggregated_short")
            agg_ratio = attrs.get("aggregated_short_ratio")
            new_time = attrs.get("new_time_str")
            print(_SEP)
            print(f"Daily Short Volume: {code}")
            print(_DASH)
            if any(v is not None for v in [agg_short, agg_ratio, new_time]):
                if agg_short is not None:
                    print(f"  Aggregated Short:       {format_big_number(agg_short)}")
                if agg_ratio is not None:
                    print(f"  Aggregated Short Ratio: {_fmt_pct(agg_ratio)}")
                if new_time:
                    print(f"  New Time Str:           {new_time}")
                print()
            if not hk_df.empty:
                disp = hk_df.copy()
                disp = disp.drop(columns=["timestamp"], errors="ignore")
                if "daily_trade_avg_ratio" in disp.columns:
                    disp["daily_trade_avg_ratio"] = disp["daily_trade_avg_ratio"].apply(
                        lambda x: _fmt_pct(x) if x is not None else "-"
                    )
                for col in ["shares_traded", "turnover", "short_sell_shares_traded", "short_sell_turnover"]:
                    if col in disp.columns:
                        disp[col] = disp[col].apply(lambda x: format_big_number(x) if x is not None else "-")
                for col in ["open_price", "close_price", "last_close_price"]:
                    if col in disp.columns:
                        disp[col] = disp[col].apply(lambda x: f"{float(x):.3f}" if x is not None else "-")
                disp = disp.rename(columns={
                    "timestamp_str":            "Timestamp Str",
                    "shares_traded":            "Shares Traded",
                    "turnover":                 "Turnover",
                    "short_sell_shares_traded": "Short Sell Shares Traded",
                    "short_sell_turnover":      "Short Sell Turnover",
                    "open_price":               "Open Price",
                    "close_price":              "Close Price",
                    "last_close_price":         "Last Close Price",
                    "daily_trade_avg_ratio":    "Daily Trade Avg Ratio",
                })
                print_display_df(disp, max_colwidth=16)
            else:
                print("  No data")

        row_count = len(us_df) if is_us else len(hk_df)
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
        description="Get daily short selling volume data with pagination support"
    )
    parser.add_argument("code", help="Stock code, e.g. US.AAPL")
    parser.add_argument("--next-key", default=None, dest="next_key",
                        help='Pagination key; omit for first page; "-1" means no more data')
    parser.add_argument("--num", type=int, default=None, dest="num",
                        help="Number of results per page, default 10, range 1-50")
    parser.add_argument("--json", action="store_true", dest="output_json",
                        help="Output in JSON format")
    args = parser.parse_args()
    get_daily_short_volume(args.code, next_key=args.next_key, num=args.num,
                           output_json=args.output_json)
