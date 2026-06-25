#!/usr/bin/env python3
"""
Get Company Profile

Function: Get company profile tag list for a stock, including text, links and section titles
Usage: python get_company_profile.py [-h] [--json] code

API Limits:
- Max 30 requests per 30 seconds
- Supports equities and funds

Parameter Description:
- code: Stock code, e.g. HK.00700

Return Field Description:
- data[]: Company profile tag list; each item contains name (tag name)/value (content)/
          field_type (Qot_Common.CompanyProfileFieldType: 0=SourceText, 1=LinkType,
          2=IndependentTitle)
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
    disp_width,
)

import pandas as pd

_SEP = "=" * 64
_DASH = "-" * 64

_FIELD_TYPE_MAP = {
    0: "SourceText",
    1: "LinkType",
    2: "IndependentTitle",
}


def _translate_field_type(val):
    try:
        v = int(val)
    except (TypeError, ValueError):
        return str(val)
    return _FIELD_TYPE_MAP.get(v, "-")


def _trunc(s, max_w):
    s = str(s)
    w, out = 0, []
    for c in s:
        cw = 2 if disp_width(c) == 2 else 1
        if w + cw > max_w:
            while out and w + 3 > max_w:
                w -= disp_width(out[-1]) if len(out) > 0 else 1
                out.pop()
            return "".join(out) + "..."
        out.append(c)
        w += cw
    return s


def _pad(s, w, align="left"):
    s = str(s)
    p = max(0, w - disp_width(s))
    return (" " * p + s) if align == "right" else (s + " " * p)


_W_NAME = 24
_W_VAL = 50


def _print_profile_table(df):
    print(_pad("Name", _W_NAME, "right") + "  " + _pad("Value", _W_VAL) + "  Field Type")
    for _, row in df.iterrows():
        name = _trunc(row["name"], _W_NAME)
        val = str(row["value"])
        ftype = str(row["field_type"])
        if ftype == "IndependentTitle":
            print()
            print(row["name"])
            print(val)
        else:
            print(_pad(name, _W_NAME, "right") + "  " + _pad(_trunc(val, _W_VAL), _W_VAL) + "  " + ftype)


def get_company_profile(code, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        ret, data = ctx.get_company_profile(code)
        check_ret(ret, data, ctx, "get company profile")

        row_count = 0 if is_empty(data) else len(data)

        if output_json:
            if is_empty(data):
                print(json.dumps({"code": code, "data": {}}, ensure_ascii=False))
            else:
                print(json.dumps({"code": code, "data": df_to_records(data)}, ensure_ascii=False))
            return

        if is_empty(data):
            print("No data")
        else:
            print(_SEP)
            print(f"Company Profile: {code}")
            print(_DASH)
            disp = data.copy()
            if "field_type" in disp.columns:
                disp["field_type"] = disp["field_type"].apply(_translate_field_type)
            _print_profile_table(disp)
            print(_DASH)
            print(f"Count: {row_count}")
            print(_SEP)

    except Exception as e:
        if output_json:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))
        else:
            print(f"Error: {e}")
        sys.exit(1)
    finally:
        safe_close(ctx)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get company profile information")
    parser.add_argument("code", help="Stock code, e.g. HK.00700")
    parser.add_argument("--json", action="store_true", dest="output_json",
                        help="Output in JSON format")
    args = parser.parse_args()
    get_company_profile(args.code, output_json=args.output_json)
