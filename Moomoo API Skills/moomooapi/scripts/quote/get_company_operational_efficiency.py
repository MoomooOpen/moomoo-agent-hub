#!/usr/bin/env python3
"""
Get Company Operational Efficiency

Function: Get operational efficiency metrics for a stock, including employee count,
          revenue per capita, operating profit per capita and net profit per capita
Usage: python get_company_operational_efficiency.py [-h] [--next-key NEXT_KEY] [--num NUM] [--currency-code CURRENCY_CODE] [--json] code

API Limits:
- Max 30 requests per 30 seconds
- Supports equities and funds

Parameter Description:
- code: Stock code, e.g. HK.00700
- --next-key: Pagination key; omit for first page; "-1" means no more data
- --num: Number of results per page, default 10, range 1-50
- --currency-code: Currency code (ISO 4217), e.g. CNY, USD, HKD; omit for default currency

Return Field Description:
- item_list:     Operational efficiency list; each item contains period_text/end_date_str/
                 employee_num/employee_num_yoy/income_per_capita/income_per_capita_yoy/
                 profit_per_capita/profit_per_capita_yoy/net_profit_per_capita/
                 net_profit_per_capita_yoy (yoy values are percentage values before % sign)
- next_key:      Pagination key; "-1" means no more data
- currency_code: Currency code (ISO 4217)
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
    print_display_df,
    format_big_number,
)

import pandas as pd

_SEP = "=" * 64
_DASH = "-" * 64


def get_company_operational_efficiency(code, num=None, next_key=None, currency_code=None,
                                       output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        kwargs = {}
        if num is not None:
            kwargs["num"] = num
        if next_key is not None:
            kwargs["next_key"] = next_key
        if currency_code is not None:
            kwargs["currency_code"] = currency_code
        ret, data = ctx.get_company_operational_efficiency(code, **kwargs)
        check_ret(ret, data, ctx, "get company operational efficiency")

        item_list = data.get("item_list", []) if isinstance(data, dict) else None
        no_data = is_empty(data) or not item_list
        if no_data:
            if output_json:
                print(json.dumps({"code": code, "data": {}}))
            else:
                print("No data")
            return

        currency = data.get("currency_code", "")
        nk = data.get("next_key", "")

        if output_json:
            print(json.dumps({"code": code, "data": data}, ensure_ascii=False, default=str))
            return

        print(_SEP)
        print(f"Company Operational Efficiency: {code}")
        print(_DASH)
        currency_label = f"({currency})" if currency else ""
        rows = []
        for item in item_list:
            period = item.get("period_text") or str(item.get("fiscal_year", ""))
            end_date = item.get("end_date_str", "")
            emp = item.get("employee_num")
            emp_yoy = item.get("employee_num_yoy")
            inc = item.get("income_per_capita")
            inc_yoy = item.get("income_per_capita_yoy")
            profit = item.get("profit_per_capita")
            profit_yoy = item.get("profit_per_capita_yoy")
            net = item.get("net_profit_per_capita")
            net_yoy = item.get("net_profit_per_capita_yoy")

            def _fmt_yoy(v):
                return f"{v:.2f}%" if v is not None else "-"

            rows.append({
                "Period Text":              period,
                "End Date Str":             end_date,
                "Employee Num":             str(emp) if emp is not None else "-",
                "Employee Num Yoy":         _fmt_yoy(emp_yoy),
                f"Income Per Capita{currency_label}": format_big_number(inc) if inc is not None else "-",
                "Income Yoy":               _fmt_yoy(inc_yoy),
                f"Profit Per Capita{currency_label}": format_big_number(profit) if profit is not None else "-",
                "Profit Yoy":               _fmt_yoy(profit_yoy),
                f"Net Profit Per Capita{currency_label}": format_big_number(net) if net is not None else "-",
                "Net Profit Yoy":           _fmt_yoy(net_yoy),
            })

        print_display_df(pd.DataFrame(rows), max_colwidth=18)
        print(_DASH)
        nk_display = nk if nk else "-"
        print(f"Count: {len(item_list)}   --next-key: {nk_display}")
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
    parser = argparse.ArgumentParser(
        description="Get company operational efficiency data with pagination support"
    )
    parser.add_argument("code", help="Stock code, e.g. HK.00700")
    parser.add_argument("--next-key", default=None,
                        help='Pagination key; omit for first page; "-1" means no more data')
    parser.add_argument("--num", "-n", type=int, default=None,
                        help="Number of results per page, default 10, range 1-50")
    parser.add_argument("--currency-code", default=None,
                        help="Currency code (ISO 4217), e.g. CNY, USD, HKD; omit for default currency")
    parser.add_argument("--json", action="store_true", dest="output_json",
                        help="Output in JSON format")
    args = parser.parse_args()
    get_company_operational_efficiency(
        args.code,
        num=args.num,
        next_key=args.next_key,
        currency_code=args.currency_code,
        output_json=args.output_json,
    )
