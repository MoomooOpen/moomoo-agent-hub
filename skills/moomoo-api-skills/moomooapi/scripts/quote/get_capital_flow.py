#!/usr/bin/env python3
"""
Get Capital Flow

Function: Get intraday time-series capital flow data for a stock
Usage: python get_capital_flow.py HK.00700

API Limits:
- Max 30 requests per 30 seconds
- Only supports equities, warrants, and funds
- Historical periods only provide data for the most recent 1 year

Parameter Description:
- start/end: Format yyyy-MM-dd, e.g. "2017-06-20"

Return Field Description:
- capital_flow_item_time: Format yyyy-MM-dd HH:mm:ss, accurate to the minute
- main_in_flow: Only valid for historical periods (day, week, month)
- last_valid_time: Only valid for real-time period
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
    safe_get,
    df_to_records,
)


def get_capital_flow(code, period_type=None, start=None, end=None, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        kwargs = {}
        if period_type is not None:
            kwargs["period_type"] = period_type
        if start is not None:
            kwargs["start"] = start
        if end is not None:
            kwargs["end"] = end
        ret, data = ctx.get_capital_flow(code, **kwargs)
        check_ret(ret, data, ctx, "Get capital flow")

        if is_empty(data):
            if output_json:
                print(json.dumps({"code": code, "data": []}))
            else:
                print("No data")
            return

        if output_json:
            records = df_to_records(data, limit=100)
            print(json.dumps({"code": code, "data": records}, ensure_ascii=False))
        else:
            print("=" * 80)
            print(f"Capital Flow: {code}")
            print("=" * 80)
            cols = ["capital_flow_item_time", "last_valid_time", "in_flow",
                    "super_in_flow", "big_in_flow", "mid_in_flow", "sml_in_flow", "main_in_flow"]
            available = [c for c in cols if c in data.columns]
            if available:
                print(data[available].tail(20).to_string(index=False))
            else:
                print(data.tail(20).to_string(index=False))
            print("=" * 80)

    except Exception as e:
        if output_json:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))
        else:
            print(f"Error: {e}")
        sys.exit(1)
    finally:
        safe_close(ctx)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get capital flow")
    parser.add_argument("code", help="Stock code, e.g. HK.00700")
    parser.add_argument("--period-type", type=int, default=None, help="Period type (1=intraday, 2=day, 3=week, 4=month)")
    parser.add_argument("--start", default=None, help="Start date, e.g. 2024-01-01")
    parser.add_argument("--end", default=None, help="End date, e.g. 2024-12-31")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output in JSON format")
    args = parser.parse_args()
    get_capital_flow(args.code, period_type=args.period_type, start=args.start,
                     end=args.end, output_json=args.output_json)
