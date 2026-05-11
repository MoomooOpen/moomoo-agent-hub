#!/usr/bin/env python3
"""
Get Global State

Function: Get OpenD global state info, including market states, server version, login status, etc.
Usage: python get_global_state.py

Return Field Description (dict):
- market_hk/market_us/market_sh/market_sz: Market states
- market_hkfuture/market_usfuture: Futures market states
- server_ver: Server version
- qot_logined: Whether quote is logged in
- trd_logined: Whether trade is logged in
"""
import argparse
import json
import sys
import os as _os
sys.path.insert(0, _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..")))
from common import (
    create_quote_context,
    safe_close,
    to_jsonable,
    RET_OK,
)


def get_global_state(output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        ret, data = ctx.get_global_state()
        if ret != RET_OK:
            if output_json:
                print(json.dumps({"error": str(data)}, ensure_ascii=False))
            else:
                print(f"Failed to get global state: {data}")
            sys.exit(1)

        # data is a dict, not a DataFrame
        if output_json:
            result = {k: to_jsonable(v) for k, v in data.items()}
            print(json.dumps({"data": result}, ensure_ascii=False))
        else:
            print("=" * 70)
            print("OpenD Global State")
            print("=" * 70)
            for key, val in data.items():
                print(f"  {key}: {val}")
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
    parser = argparse.ArgumentParser(description="Get OpenD global state")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output in JSON format")
    args = parser.parse_args()
    get_global_state(args.output_json)
