#!/usr/bin/env python3
"""
Modify Watchlist Securities

Function: Add or remove securities from watchlist
Usage: python modify_user_security.py "My Watchlist" ADD HK.00700 US.AAPL
      python modify_user_security.py "My Watchlist" DEL HK.00700

API Limits:
- Max 60 requests per 30 seconds

Parameters:
- op: ADD (add), DEL (delete)
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


def modify_user_security(group_name, op, codes, output_json=False):
    ctx = None
    try:
        from moomoo import ModifyUserSecurityOp
        op_map = {
            "ADD": ModifyUserSecurityOp.ADD,
            "DEL": ModifyUserSecurityOp.DEL,
        }
        op_enum = op_map.get(op.upper())
        if op_enum is None:
            raise ValueError(f"Unsupported operation: {op}, available: ADD, DEL")

        ctx = create_quote_context()
        ret, data = ctx.modify_user_security(group_name, op_enum, codes)
        check_ret(ret, data, ctx, "modify watchlist securities")

        if output_json:
            print(json.dumps({"result": "ok", "group_name": group_name, "op": op, "codes": codes}, ensure_ascii=False))
        else:
            action = "added" if op.upper() == "ADD" else "removed"
            print(f"Successfully {action} watchlist securities: {', '.join(codes)} -> group \"{group_name}\"")

    except Exception as e:
        if output_json:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))
        else:
            print(f"Error: {e}")
        sys.exit(1)
    finally:
        safe_close(ctx)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Modify watchlist securities")
    parser.add_argument("group_name", help="Watchlist group name")
    parser.add_argument("op", choices=["ADD", "DEL"], help="Operation type")
    parser.add_argument("codes", nargs="+", help="Stock code list")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output in JSON format")
    args = parser.parse_args()
    modify_user_security(args.group_name, args.op, args.codes, args.output_json)
