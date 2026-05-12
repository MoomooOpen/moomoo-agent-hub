#!/usr/bin/env python3
"""
Get Option Expiration Dates

Function: Retrieve the list of option expiration dates for a given underlying stock
Usage: python get_option_expiration_date.py HK.00700

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


def get_option_expiration_date(code, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        ret, data = ctx.get_option_expiration_date(code)
        check_ret(ret, data, ctx, "get option expiration dates")

        if is_empty(data):
            if output_json:
                print(json.dumps({"code": code, "data": []}))
            else:
                print("No option expiration date data")
            return

        if output_json:
            print(json.dumps({"code": code, "data": df_to_records(data)}, ensure_ascii=False))
        else:
            print("=" * 70)
            print(f"Option Expiration Dates - {code}")
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
    parser = argparse.ArgumentParser(description="Get option expiration date list")
    parser.add_argument("code", help="Underlying stock code, e.g. HK.00700 or US.AAPL")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output in JSON format")
    args = parser.parse_args()
    get_option_expiration_date(args.code, args.output_json)
