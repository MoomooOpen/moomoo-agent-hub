#!/usr/bin/env python3
"""
Get Watchlist Securities

Function: Get the list of securities in a specified watchlist group
Usage: python get_user_security.py "My Watchlist"

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


def get_user_security(group_name, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        ret, data = ctx.get_user_security(group_name)
        check_ret(ret, data, ctx, "get watchlist securities")

        if is_empty(data):
            if output_json:
                print(json.dumps({"group_name": group_name, "data": []}))
            else:
                print(f"Group \"{group_name}\" has no securities")
            return

        if output_json:
            print(json.dumps({"group_name": group_name, "data": df_to_records(data)}, ensure_ascii=False))
        else:
            print("=" * 70)
            print(f"Watchlist Securities - {group_name}")
            print("=" * 70)
            cols = [c for c in ['code', 'name', 'lot_size', 'stock_type'] if c in data.columns]
            print(data[cols].to_string(index=False))
            print(f"\nTotal {len(data)} securities")
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
    parser = argparse.ArgumentParser(description="Get watchlist securities")
    parser.add_argument("group_name", help="Watchlist group name")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output in JSON format")
    args = parser.parse_args()
    get_user_security(args.group_name, args.output_json)
