#!/usr/bin/env python3
"""
Get Watchlist Groups

Function: Get the user's watchlist group list
Usage: python get_user_security_group.py

API Limits:
- Max 60 requests per 30 seconds

Return Fields:
- group_id: Group ID
- group_name: Group name
- group_type: Group type
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


def get_user_security_group(group_type=None, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        kwargs = {}
        if group_type is not None:
            from moomoo import UserSecurityGroupType
            type_map = {
                "ALL": UserSecurityGroupType.ALL,
                "CUSTOM": UserSecurityGroupType.CUSTOM,
                "SYSTEM": UserSecurityGroupType.SYSTEM,
            }
            t = type_map.get(group_type.upper())
            if t is not None:
                kwargs["group_type"] = t

        ret, data = ctx.get_user_security_group(**kwargs)
        check_ret(ret, data, ctx, "get watchlist groups")

        if is_empty(data):
            if output_json:
                print(json.dumps({"data": []}))
            else:
                print("No watchlist groups")
            return

        if output_json:
            print(json.dumps({"data": df_to_records(data)}, ensure_ascii=False))
        else:
            print("=" * 70)
            print("Watchlist Groups")
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
    parser = argparse.ArgumentParser(description="Get watchlist groups")
    parser.add_argument("--group-type", choices=["ALL", "CUSTOM", "SYSTEM"], default=None, help="Group type")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output in JSON format")
    args = parser.parse_args()
    get_user_security_group(args.group_type, args.output_json)
