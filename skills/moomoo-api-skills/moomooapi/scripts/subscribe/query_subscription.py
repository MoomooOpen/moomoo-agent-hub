#!/usr/bin/env python3
"""
Query subscription status

Function: Query currently subscribed stocks and data types
Usage: python query_subscription.py

API limitations:
- No special rate limiting
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
)


def query_subscription(is_all_conn=True, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        ret, data = ctx.query_subscription(is_all_conn=is_all_conn)
        check_ret(ret, data, ctx, "Query subscription")

        # data structure: {"total_used": int, "remain": int, "own_used": int, "sub_list": {SubType: [code_list]}}
        total_used = data.get("total_used", 0) if isinstance(data, dict) else 0
        remain = data.get("remain", 0) if isinstance(data, dict) else 0
        own_used = data.get("own_used", 0) if isinstance(data, dict) else 0
        sub_list = data.get("sub_list", {}) if isinstance(data, dict) else {}

        sub_result = {}
        if isinstance(sub_list, dict):
            for k, v in sub_list.items():
                key = str(k).split(".")[-1] if hasattr(k, "name") else str(k)
                sub_result[key] = v if isinstance(v, list) else [v]

        if output_json:
            print(json.dumps({
                "total_used": total_used,
                "remain": remain,
                "own_used": own_used,
                "subscriptions": sub_result,
            }, ensure_ascii=False))
        else:
            print("=" * 50)
            print("Subscription Status" + (" (all connections)" if is_all_conn else " (current connection)"))
            print("=" * 50)
            print(f"  Used quota: {total_used}  Remaining: {remain}  Current connection used: {own_used}")
            if sub_result:
                for k, codes in sub_result.items():
                    print(f"\n  {k}:")
                    for code in codes:
                        print(f"    - {code}")
            else:
                print("\n  No active subscriptions")
            print("\n" + "=" * 50)

    except Exception as e:
        if output_json:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))
        else:
            print(f"Error: {e}")
        sys.exit(1)
    finally:
        safe_close(ctx)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query subscription status")
    parser.add_argument("--current", action="store_true", help="Query only current connection subscriptions (default: all connections)")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output in JSON format")
    args = parser.parse_args()
    query_subscription(is_all_conn=not args.current, output_json=args.output_json)
