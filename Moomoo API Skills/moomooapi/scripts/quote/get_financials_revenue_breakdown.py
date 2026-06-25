#!/usr/bin/env python3
"""
Get Revenue Breakdown

Function: Get revenue breakdown for a stock, returning product/industry/region/business dimension data
Usage: python get_financials_revenue_breakdown.py [-h] [--date DATE] [--financial-type FINANCIAL_TYPE] [--currency-code CURRENCY_CODE] [--json] code

API Limits:
- Max 30 requests per 30 seconds
- Supports equities and funds

Parameter Description:
- code: Stock code, e.g. HK.00700
- --date: Filter timestamp; pass a date value from screen_date_list to query history; omit for latest
- --financial-type: Financial period type:
                    1=Q1 2=Q2 3=Q3 4=Q4 5=SemiAnnual 6=Q9 7=Annual 9=QuarterlyCombo
- --currency-code: Currency code (ISO 4217), e.g. CNY, USD, HKD; empty = original currency

Return Field Description:
- period:           Financial period, e.g. "2024/Q3"
- breakdown_list:   List of dimension groups; each group has type and item_list
  - type:           Dimension type (1=Product 2=Industry 4=Region 8=Business)
  - item_list:      Each item contains name/main_oper_income/ratio
                    (ratio is percentage value before % sign, e.g. 12.34 means 12.34%)
- currency_code:    Currency code (ISO 4217)
- screen_date_list: Available historical dates (only returned when date and financial_type are both omitted);
                    each item contains date/period_text/financial_type
"""
import argparse
import json
import math
import sys
import os as _os

sys.path.insert(0, _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..")))
from common import (
    create_quote_context,
    check_ret,
    safe_close,
    is_empty,
    print_display_df,
    format_big_number,
)

import pandas as pd

_SEP = "=" * 64
_DASH = "-" * 64

_TYPE_NAMES = {1: "Product", 2: "Industry", 4: "Region", 8: "Business"}
_FINANCIAL_TYPE_NAMES = {
    1: "Q1",
    2: "Q2",
    3: "Q3",
    4: "Q4",
    5: "SemiAnnual",
    6: "Q9",
    7: "Annual",
    9: "QuarterlyCombo",
}


def get_financials_revenue_breakdown(code, date=None, financial_type=None,
                                     currency_code=None, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        ret, data = ctx.get_financials_revenue_breakdown(
            code,
            date=date,
            financial_type=financial_type,
            currency_code=currency_code,
        )
        check_ret(ret, data, ctx, "get revenue breakdown")

        breakdown_list = data.get("breakdown_list", []) if isinstance(data, dict) else []
        no_data = is_empty(data) or not breakdown_list
        if no_data:
            if output_json:
                print(json.dumps({"code": code, "data": {}}))
            else:
                print("No data")
            return

        period = data.get("period", "")
        currency = data.get("currency_code", "")
        screen_dates = data.get("screen_date_list", [])

        if output_json:
            print(json.dumps({"code": code, "data": data}, ensure_ascii=False, default=str))
        else:
            print(_SEP)
            print(f"Revenue Breakdown  Code: {code}  Period: {period}  Currency: {currency}")

            for group in breakdown_list:
                group_type = group.get("type", 0)
                type_name = _TYPE_NAMES.get(group_type, str(group_type))
                item_list = group.get("item_list", [])
                if not item_list:
                    continue
                print(_DASH)
                print(f"[{type_name}]")
                rows = []
                for item in item_list:
                    income_val = item.get("main_oper_income")
                    ratio_val = item.get("ratio")
                    try:
                        ratio_str = (
                            f"{float(ratio_val):.2f}%"
                            if (ratio_val is not None and not math.isnan(float(ratio_val)))
                            else "-"
                        )
                    except (TypeError, ValueError):
                        ratio_str = "-"
                    rows.append({
                        "Name": item.get("name", ""),
                        "Main Oper Income": format_big_number(income_val),
                        "Ratio": ratio_str,
                    })
                print_display_df(pd.DataFrame(rows), max_colwidth=32)

            if screen_dates:
                sd_rows = []
                for sd in screen_dates:
                    ft = sd.get("financial_type", 0)
                    ft_name = _FINANCIAL_TYPE_NAMES.get(ft, str(ft))
                    sd_rows.append({
                        "Period Text": sd.get("period_text", ""),
                        "Date": sd.get("date", 0),
                        "Financial Type": f"{ft}({ft_name})",
                    })
                print(f"\nAvailable dates ({len(screen_dates)} total):")
                print_display_df(pd.DataFrame(sd_rows), max_colwidth=24)

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
    parser = argparse.ArgumentParser(description="Get company revenue breakdown by dimension")
    parser.add_argument("code", help="Stock code, e.g. HK.00700")
    parser.add_argument(
        "--date", type=int, default=None,
        help="Filter timestamp; pass a date value from screen_date_list to query history; omit for latest",
    )
    parser.add_argument(
        "--financial-type", type=int, default=None,
        help=(
            "Financial period type: "
            "1=Q1 2=Q2 3=Q3 4=Q4 5=SemiAnnual 6=Q9 7=Annual 9=QuarterlyCombo"
        ),
    )
    parser.add_argument(
        "--currency-code", type=str, default=None,
        help="Currency code (ISO 4217), e.g. CNY, USD, HKD; empty = original currency",
    )
    parser.add_argument("--json", action="store_true", dest="output_json",
                        help="Output in JSON format")
    args = parser.parse_args()

    get_financials_revenue_breakdown(
        args.code,
        date=args.date,
        financial_type=args.financial_type,
        currency_code=args.currency_code,
        output_json=args.output_json,
    )
