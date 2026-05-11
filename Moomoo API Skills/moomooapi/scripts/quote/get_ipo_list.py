#!/usr/bin/env python3
"""
Get IPO List

Function: Get the IPO information list for a specified market
Usage: python get_ipo_list.py HK

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
    Market,
)


def get_ipo_list(market_str, output_json=False):
    ctx = None
    try:
        market_map = {
            "HK": Market.HK,
            "US": Market.US,
            "SH": Market.SH,
            "SZ": Market.SZ,
        }
        market = market_map.get(market_str.upper())
        if market is None:
            raise ValueError(f"Unsupported market: {market_str}, available options: {list(market_map.keys())}")

        ctx = create_quote_context()
        ret, data = ctx.get_ipo_list(market)
        check_ret(ret, data, ctx, "Get IPO list")

        if is_empty(data):
            if output_json:
                print(json.dumps({"market": market_str, "data": []}))
            else:
                print("No IPO data")
            return

        if output_json:
            print(json.dumps({"market": market_str, "data": df_to_records(data)}, ensure_ascii=False))
        else:
            print("=" * 70)
            print(f"IPO List - {market_str}")
            print("=" * 70)
            print(data.to_string(index=False))
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
    parser = argparse.ArgumentParser(description="Get IPO list")
    parser.add_argument("market", choices=["HK", "US", "SH", "SZ"], help="Market")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output in JSON format")
    args = parser.parse_args()
    get_ipo_list(args.market, args.output_json)
