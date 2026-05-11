#!/usr/bin/env python3
"""
Get Reference Stock List

Function: Get warrants, futures, and other data associated with the underlying stock
Usage: python get_referencestock_list.py HK.00700 WARRANT

API Limits:
- Max 60 requests per 30 seconds

Parameter Notes:
- reference_type: WARRANT (warrants), FUTURE (futures)
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
    SecurityReferenceType,
)


def get_referencestock_list(code, reference_type, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        type_map = {
            "WARRANT": SecurityReferenceType.WARRANT,
            "FUTURE": SecurityReferenceType.FUTURE,
        }
        sec_type = type_map.get(reference_type.upper())
        if sec_type is None:
            raise ValueError(f"Unsupported reference type: {reference_type}, options: {list(type_map.keys())}")

        ret, data = ctx.get_referencestock_list(code, sec_type)
        check_ret(ret, data, ctx, "get reference stock list")

        if is_empty(data):
            if output_json:
                print(json.dumps({"code": code, "reference_type": reference_type, "data": []}))
            else:
                print("No reference data")
            return

        if output_json:
            print(json.dumps({"code": code, "reference_type": reference_type, "data": df_to_records(data)}, ensure_ascii=False))
        else:
            print("=" * 70)
            print(f"Reference Data - {code} ({reference_type})")
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
    parser = argparse.ArgumentParser(description="Get reference stock data (warrants/futures, etc.)")
    parser.add_argument("code", help="Stock code, e.g. HK.00700")
    parser.add_argument("reference_type", choices=["WARRANT", "FUTURE"], help="Reference type")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output in JSON format")
    args = parser.parse_args()
    get_referencestock_list(args.code, args.reference_type, args.output_json)
