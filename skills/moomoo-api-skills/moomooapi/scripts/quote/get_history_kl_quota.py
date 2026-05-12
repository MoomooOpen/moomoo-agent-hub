#!/usr/bin/env python3
"""
Get Historical Candlestick Quota

Function: Query historical Candlestick quota usage
Usage: python get_history_kl_quota.py
      python get_history_kl_quota.py --detail

API Limits:
- Max 60 requests per 30 seconds

Return Field Description:
- used_quota: Used quota
- remain_quota: Remaining quota
- detail_list (--detail): List of previously requested stock codes
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


def get_history_kl_quota(get_detail=False, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        ret, data = ctx.get_history_kl_quota(get_detail=get_detail)
        check_ret(ret, data, ctx, "Get Candlestick quota")

        if output_json:
            if hasattr(data, 'iloc'):
                print(json.dumps({"data": df_to_records(data)}, ensure_ascii=False))
            else:
                print(json.dumps({"data": data}, ensure_ascii=False))
        else:
            print("=" * 70)
            print("Historical Candlestick Quota")
            print("=" * 70)
            if hasattr(data, 'to_string'):
                print(data.to_string(index=False))
            else:
                print(f"  {data}")
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
    parser = argparse.ArgumentParser(description="Get historical Candlestick quota")
    parser.add_argument("--detail", action="store_true", help="Whether to return detailed stock list")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output in JSON format")
    args = parser.parse_args()
    get_history_kl_quota(get_detail=args.detail, output_json=args.output_json)
