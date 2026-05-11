#!/usr/bin/env python3
"""
Get Real-Time Data (Time-Sharing)

Function: Get intraday time-sharing data for the specified stock
Usage: python get_rt_data.py HK.00700

API Limits:
- Must subscribe to RT_DATA type first

Return Field Notes:
- time: Format yyyy-MM-dd HH:mm:ss, Beijing time for HK/A-shares, US Eastern time for US stocks
- is_blank: False for normal data, True for synthetic data (padded during non-trading hours)
- avg_price: This field is N/A for options
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
    safe_float,
    safe_int,
    SubType,
    RET_OK,
)


def get_rt_data(code, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        ret, msg = ctx.subscribe([code], [SubType.RT_DATA])
        if ret != RET_OK:
            print(f"Subscription failed: {msg}")
            sys.exit(1)

        ret, data = ctx.get_rt_data(code)
        check_ret(ret, data, ctx, "get real-time data")

        if is_empty(data):
            if output_json:
                print(json.dumps({"code": code, "data": []}))
            else:
                print("No data")
            return

        records = []
        for i in range(len(data)):
            row = data.iloc[i] if hasattr(data, "iloc") else data[i]
            records.append({
                "time": safe_get(row, "time", default=""),
                "price": safe_float(safe_get(row, "cur_price", default=0)),
                "avg_price": safe_float(safe_get(row, "avg_price", default=0)),
                "volume": safe_int(safe_get(row, "volume", default=0)),
                "turnover": safe_float(safe_get(row, "turnover", default=0)),
            })

        if output_json:
            print(json.dumps({"code": code, "data": records}, ensure_ascii=False))
        else:
            print("=" * 70)
            print(f"Real-Time Data: {code}")
            print("=" * 70)
            print(f"  {'Time':<20} {'Price':>10} {'Avg Price':>10} {'Volume':>12}")
            print("  " + "-" * 54)
            for r in records:
                print(f"  {r['time']:<20} {r['price']:>10.3f} {r['avg_price']:>10.3f} {r['volume']:>12}")
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
    parser = argparse.ArgumentParser(description="Get real-time (time-sharing) data")
    parser.add_argument("code", help="Stock code, e.g. HK.00700")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output in JSON format")
    args = parser.parse_args()
    get_rt_data(args.code, args.output_json)
