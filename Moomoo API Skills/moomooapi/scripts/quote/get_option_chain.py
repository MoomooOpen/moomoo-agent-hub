#!/usr/bin/env python3
"""
Get Option Chain

Function: Retrieve the option chain data for a given underlying stock
Usage: python get_option_chain.py HK.00700 --start 2024-01-01 --end 2024-12-31

API limits:
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


def get_option_chain(code, start=None, end=None, option_type=None, option_cond_type=None, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        kwargs = {}
        if start:
            kwargs["start"] = start
        if end:
            kwargs["end"] = end
        if option_type:
            kwargs["option_type"] = option_type
        if option_cond_type:
            kwargs["option_cond_type"] = option_cond_type

        ret, data = ctx.get_option_chain(code, **kwargs)
        check_ret(ret, data, ctx, "get option chain")

        if is_empty(data):
            if output_json:
                print(json.dumps({"code": code, "data": []}))
            else:
                print("No option chain data")
            return

        if output_json:
            print(json.dumps({"code": code, "data": df_to_records(data)}, ensure_ascii=False))
        else:
            print("=" * 70)
            print(f"Option Chain - {code}")
            print("=" * 70)
            cols = [c for c in ['code', 'name', 'option_type', 'strike_price',
                                'strike_time', 'last_price'] if c in data.columns]
            print(data[cols].to_string(index=False))
            print(f"\nTotal {len(data)} records")
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
    parser = argparse.ArgumentParser(description="Get option chain")
    parser.add_argument("code", help="Underlying stock code, e.g. HK.00700 or US.AAPL")
    parser.add_argument("--start", default=None, help="Start date yyyy-MM-dd")
    parser.add_argument("--end", default=None, help="End date yyyy-MM-dd")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output in JSON format")
    args = parser.parse_args()
    get_option_chain(args.code, start=args.start, end=args.end, output_json=args.output_json)
