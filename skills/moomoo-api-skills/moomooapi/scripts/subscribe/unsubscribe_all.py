#!/usr/bin/env python3
"""
Unsubscribe all

Function: Cancel all subscriptions for the current connection
Usage: python unsubscribe_all.py

API limitations:
- Must subscribe for at least 1 minute before unsubscribing
- Quota is only released after all connections have unsubscribed from the same security
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
    RET_OK,
)


def unsubscribe_all(output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        ret, data = ctx.unsubscribe_all()
        check_ret(ret, data, ctx, "Unsubscribe all")

        if output_json:
            print(json.dumps({"result": "ok"}, ensure_ascii=False))
        else:
            print("All subscriptions cancelled")

    except Exception as e:
        if output_json:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))
        else:
            print(f"Error: {e}")
        sys.exit(1)
    finally:
        safe_close(ctx)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Unsubscribe all")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output in JSON format")
    args = parser.parse_args()
    unsubscribe_all(args.output_json)
