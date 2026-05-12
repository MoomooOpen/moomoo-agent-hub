#!/usr/bin/env python3
"""
Get Price Reminder List

Function: Retrieve the list of configured price reminders
Usage: python get_price_reminder.py
      python get_price_reminder.py HK.00700

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


def get_price_reminder(code=None, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        kwargs = {}
        if code:
            kwargs["code"] = code

        ret, data = ctx.get_price_reminder(**kwargs)
        check_ret(ret, data, ctx, "get price reminders")

        if is_empty(data):
            if output_json:
                print(json.dumps({"data": []}))
            else:
                print("No price reminders")
            return

        if output_json:
            print(json.dumps({"data": df_to_records(data)}, ensure_ascii=False))
        else:
            print("=" * 70)
            print("Price Reminder List")
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
    parser = argparse.ArgumentParser(description="Get price reminder list")
    parser.add_argument("code", nargs="?", default=None, help="Stock code (optional); omit to return all")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output in JSON format")
    args = parser.parse_args()
    get_price_reminder(args.code, args.output_json)
