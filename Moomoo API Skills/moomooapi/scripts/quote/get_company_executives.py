#!/usr/bin/env python3
"""
Get Company Executives

Function: Get directors and executives list for a stock, including display name, position,
          tenure start date, publication date, gender, age, education and annual salary
Usage: python get_company_executives.py [-h] [--json] code

API Limits:
- Max 30 requests per 30 seconds
- Supports equities and funds

Parameter Description:
- code: Stock code, e.g. HK.00700

Return Field Description:
- data[]: Director and executive list; each item contains display_leader_name (display name)/
          leader_name (for querying executive background)/position_name/begin_date_str/
          issue_date_str/leader_gender/leader_age/highest_education/annual_salary
"""
import argparse
import json
import sys
import os as _os

import pandas as pd

sys.path.insert(0, _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..")))
from common import (
    create_quote_context,
    check_ret,
    safe_close,
    is_empty,
    df_to_records,
    print_display_df,
    format_big_number,
)

_SEP = "=" * 64
_DASH = "-" * 64


def _build_display_df(data):
    def _has_large(col):
        if col not in data.columns:
            return False
        return any(
            v is not None and not (isinstance(v, float) and pd.isna(v))
            and abs(float(v)) >= 10000
            for v in data[col]
        )

    salary_large = _has_large("annual_salary")

    rows = []
    for _, row in data.iterrows():
        def _v(col):
            v = row.get(col)
            if v is None or (isinstance(v, float) and pd.isna(v)):
                return "-"
            if str(v) == "":
                return "-"
            return v

        sal_raw = row.get("annual_salary")
        if sal_raw is None or (isinstance(sal_raw, float) and pd.isna(sal_raw)):
            salary_disp = "-"
        elif salary_large:
            salary_disp = format_big_number(sal_raw)
        else:
            salary_disp = str(int(sal_raw))

        rows.append({
            "Display Leader Name": _v("display_leader_name"),
            "Position Name":       _v("position_name"),
            "Annual Salary":       salary_disp,
            "Begin Date Str":      _v("begin_date_str"),
            "Highest Education":   _v("highest_education"),
            "Leader Age":          _v("leader_age"),
            "Leader Gender":       _v("leader_gender"),
            "Issue Date Str":      _v("issue_date_str"),
            "Leader Name":         _v("leader_name"),
        })

    return pd.DataFrame(rows)


def get_company_executives(code, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        ret, data = ctx.get_company_executives(code)
        check_ret(ret, data, ctx, "get company executives")

        row_count = len(data) if not is_empty(data) else 0

        if output_json:
            if is_empty(data):
                records = []
            else:
                records = df_to_records(data)
                for r in records:
                    r.pop("begin_date", None)
                    r.pop("issue_date", None)
                    for int_field in ("annual_salary",):
                        v = r.get(int_field)
                        if v is not None and isinstance(v, float) and not (v != v):
                            r[int_field] = int(v)
            print(json.dumps({"code": code, "data": records}, ensure_ascii=False))
        else:
            if is_empty(data):
                print("No data")
            else:
                print(_SEP)
                print(f"Company Executives: {code}")
                print(_DASH)
                print_display_df(_build_display_df(data), max_colwidth=30)
                print(_DASH)
                print(f"Count: {row_count}")
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
    parser = argparse.ArgumentParser(description="Get company directors and executives information")
    parser.add_argument("code", help="Stock code, e.g. HK.00700")
    parser.add_argument("--json", action="store_true", dest="output_json",
                        help="Output in JSON format")
    args = parser.parse_args()
    get_company_executives(args.code, output_json=args.output_json)
