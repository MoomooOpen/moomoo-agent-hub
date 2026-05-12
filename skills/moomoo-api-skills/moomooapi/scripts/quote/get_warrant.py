#!/usr/bin/env python3
"""
Get Warrant List

Function: Get the list of warrants/CBBCs for a specified underlying stock
Usage: python get_warrant.py HK.00700

API Limits:
- Max 60 requests per 30 seconds
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
)


def get_warrant(stock_owner, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        ret, data = ctx.get_warrant(stock_owner=stock_owner)
        # data is a tuple: (DataFrame, has_next, total_count)
        if isinstance(data, tuple):
            df, has_next, total_count = data
        else:
            df, has_next, total_count = data, False, 0
        check_ret(ret, df, ctx, "get warrant list")

        if is_empty(df):
            if output_json:
                print(json.dumps({"stock_owner": stock_owner, "data": []}))
            else:
                print("No warrant data")
            return

        if output_json:
            result = {"stock_owner": stock_owner, "total_count": total_count, "data": df_to_records(df)}
            print(json.dumps(result, ensure_ascii=False))
        else:
            print("=" * 70)
            print(f"Warrants/CBBCs - Underlying: {stock_owner} (Total: {total_count})")
            print("=" * 70)
            cols = [c for c in ['stock', 'name', 'type', 'strike_price',
                                'maturity_time', 'cur_price', 'volume', 'turnover',
                                'implied_volatility', 'premium', 'effective_leverage'] if c in df.columns]
            print(df[cols].to_string(index=False))
            print(f"\nShowing {len(df)} of {total_count} records")
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
    parser = argparse.ArgumentParser(description="Get warrants/CBBCs list")
    parser.add_argument("stock_owner", help="Underlying stock code, e.g. HK.00700")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output in JSON format")
    args = parser.parse_args()
    get_warrant(args.stock_owner, args.output_json)
