#!/usr/bin/env python3
"""
Get Real-Time Quote

Function: Get real-time quote data for subscribed stocks
Usage: python get_stock_quote.py HK.00700 US.AAPL

API Limits:
- Must subscribe to QUOTE type via subscribe interface first
- Built-in 3-second wait after subscription; returns empty data if exceeded

Return Field Notes:
- last_price: Last traded price
- open_price/high_price/low_price/prev_close_price: Open/High/Low/Previous Close
- volume: Trading volume
- turnover: Trading turnover
- amplitude: Amplitude (percentage, 20 corresponds to 20%)
- turnover_rate: Turnover rate (percentage)
- suspension: True indicates trading halt
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
    SubType,
)


def get_stock_quote(codes, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        ret, msg = ctx.subscribe(codes, [SubType.QUOTE])
        check_ret(ret, msg, ctx, "subscribe quote")

        ret, data = ctx.get_stock_quote(codes)
        check_ret(ret, data, ctx, "get real-time quote")

        if is_empty(data):
            if output_json:
                print(json.dumps({"data": []}))
            else:
                print("No data")
            return

        if output_json:
            print(json.dumps({"data": df_to_records(data)}, ensure_ascii=False))
        else:
            cols = [c for c in ['code', 'name', 'last_price', 'open_price', 'high_price',
                                'low_price', 'volume', 'turnover'] if c in data.columns]
            print("=" * 70)
            print("Real-Time Quote")
            print("=" * 70)
            print(data[cols].to_string(index=False))
            print("=" * 70)

    except Exception as e:
        if output_json:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))
        else:
            print(f"Error: {e}")
        sys.exit(1)
    finally:
        safe_close(ctx)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get real-time quote (subscription required)")
    parser.add_argument("codes", nargs="+", help="Stock codes, e.g. HK.00700")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output in JSON format")
    args = parser.parse_args()
    get_stock_quote(args.codes, args.output_json)
