#!/usr/bin/env python3
"""
Get Market State

Function: Query the trading status of the market a given stock belongs to (open/closed/pre-market/after-hours, etc.)
Usage: python get_market_state.py HK.00700 US.AAPL

API limits:
- Max 10 requests per 30 seconds
- Max 400 stock codes per request
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
    safe_get,
    format_enum,
)


def get_market_state(codes, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        ret, data = ctx.get_market_state(codes)
        check_ret(ret, data, ctx, "get market state")

        if is_empty(data):
            if output_json:
                print(json.dumps({"data": []}))
            else:
                print("No data")
            return

        records = []
        for i in range(len(data)):
            row = data.iloc[i] if hasattr(data, "iloc") else data[i]
            records.append({
                "code": safe_get(row, "code", default="N/A"),
                "stock_name": safe_get(row, "stock_name", default=""),
                "market_state": format_enum(safe_get(row, "market_state", default="")),
            })

        if output_json:
            print(json.dumps({"data": records}, ensure_ascii=False))
        else:
            print("=" * 50)
            print("Market State")
            print("=" * 50)
            for r in records:
                print(f"  {r['code']:<15} {r['stock_name']:<10} State: {r['market_state']}")
            print("=" * 50)

    except Exception as e:
        if output_json:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))
        else:
            print(f"Error: {e}")
        sys.exit(1)
    finally:
        safe_close(ctx)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get market state")
    parser.add_argument("codes", nargs="+", help="Stock codes, e.g. HK.00700 US.AAPL")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output in JSON format")
    args = parser.parse_args()
    get_market_state(args.codes, args.output_json)
