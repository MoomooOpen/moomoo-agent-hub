#!/usr/bin/env python3
"""
Get Company Executive Background

Function: Get background introduction for an executive of a stock
Usage: python get_company_executive_background.py [-h] [--json] code leader_name

API Limits:
- Max 30 requests per 30 seconds
- Supports equities and funds

Parameter Description:
- code: Stock code, e.g. HK.00700
- --leader-name: Executive name; use the leader_name field value from get_company_executives.py;
                 supports direct text or Unicode escape sequences (e.g. "\\u9a6c\\u5316\\u817e"),
                 both forms are equivalent

Return Field Description:
- data.leader_name:      Executive name (matches request parameter)
- data.brief_background: Executive background summary (text)
"""
import argparse
import json
import sys
import os as _os
import textwrap

sys.path.insert(0, _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..")))
from common import (
    create_quote_context,
    check_ret,
    safe_close,
    is_empty,
)

_SEP = "=" * 64
_DASH = "-" * 64


def get_company_executive_background(code, leader_name, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        ret, data = ctx.get_company_executive_background(code, leader_name=leader_name)
        check_ret(ret, data, ctx, "get company executive background")

        if is_empty(data):
            if output_json:
                print(json.dumps({"code": code, "data": {}}))
            else:
                print("No data")
            return

        bg = data.get("brief_background", "") if isinstance(data, dict) else ""

        if not bg:
            if output_json:
                print(json.dumps({"code": code, "data": {}}))
            else:
                print("No data")
            return

        if output_json:
            print(json.dumps({
                "code": code,
                "data": {"leader_name": leader_name, "brief_background": bg},
            }, ensure_ascii=False))
        else:
            print(_SEP)
            print(f"Company Executive Background: {code}")
            print(_DASH)
            wrapped = textwrap.fill(bg, width=70)
            print(f"Brief Background:\n{wrapped}")
            print(_DASH)
            print(_SEP)

    except SystemExit:
        raise
    except Exception as e:
        if output_json:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))
        else:
            print(f"Error: {e}")
        sys.exit(1)
    finally:
        safe_close(ctx)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get executive background introduction")
    parser.add_argument("code", help="Stock code, e.g. HK.00700")
    parser.add_argument("leader_name",
                        help="Executive name from get_company_executives.py leader_name field")
    parser.add_argument("--json", action="store_true", dest="output_json",
                        help="Output in JSON format")
    args = parser.parse_args()
    if args.leader_name:
        try:
            args.leader_name = args.leader_name.encode('raw_unicode_escape').decode('unicode_escape')
        except (UnicodeDecodeError, UnicodeEncodeError):
            pass
    get_company_executive_background(args.code, leader_name=args.leader_name, output_json=args.output_json)
