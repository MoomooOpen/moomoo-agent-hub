#!/usr/bin/env python3
"""
Get Rehabilitation (Adjustment Factor)

Function: Get the list of adjustment factors for a stock
Usage: python get_rehab.py HK.00700

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


def get_rehab(code, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        ret, data = ctx.get_rehab(code)
        check_ret(ret, data, ctx, "get adjustment factor")

        if is_empty(data):
            if output_json:
                print(json.dumps({"code": code, "data": []}))
            else:
                print("No adjustment factor data")
            return

        if output_json:
            print(json.dumps({"code": code, "data": df_to_records(data)}, ensure_ascii=False))
        else:
            print("=" * 70)
            print(f"Adjustment Factor - {code}")
            print("=" * 70)
            print(data.to_string(index=False))
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
    parser = argparse.ArgumentParser(description="Get adjustment factor")
    parser.add_argument("code", help="Stock code, e.g. HK.00700")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output in JSON format")
    args = parser.parse_args()
    get_rehab(args.code, args.output_json)
