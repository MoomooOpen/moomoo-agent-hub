#!/usr/bin/env python3
"""
Get Ticker (Tick-by-Tick) Data

Function: Get recent tick-by-tick trade records for the specified stock
Usage: python get_ticker.py HK.00700 --num 20

API Limits:
- Must subscribe to TICKER type first
- Max 1000 recent ticks
- HK options/futures under LV1 permission do not support tick-by-tick data

Return Field Notes:
- time: Format yyyy-MM-dd HH:mm:ss:xxx, Beijing time for HK/A-shares, US Eastern time for US stocks
- volume: Unit: shares
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


def get_ticker(code, num=20, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        ret, msg = ctx.subscribe([code], [SubType.TICKER])
        if ret != RET_OK:
            print(f"Subscription failed: {msg}")
            sys.exit(1)

        ret, data = ctx.get_rt_ticker(code, num=num)
        check_ret(ret, data, ctx, "get ticker data")

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
                "price": safe_float(safe_get(row, "price", default=0)),
                "volume": safe_int(safe_get(row, "volume", default=0)),
                "turnover": safe_float(safe_get(row, "turnover", default=0)),
                "direction": safe_get(row, "ticker_direction", default=""),
            })

        if output_json:
            print(json.dumps({"code": code, "data": records}, ensure_ascii=False))
        else:
            print("=" * 70)
            print(f"Tick-by-Tick Trades: {code} (Last {num} ticks)")
            print("=" * 70)
            print(f"  {'Time':<20} {'Price':>10} {'Volume':>10} {'Direction':>10}")
            print("  " + "-" * 50)
            for r in records:
                print(f"  {r['time']:<20} {r['price']:>10.3f} {r['volume']:>10} {r['direction']:>10}")
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
    parser = argparse.ArgumentParser(description="Get tick-by-tick trade data")
    parser.add_argument("code", help="Stock code, e.g. HK.00700")
    parser.add_argument("--num", type=int, default=20, help="Number of ticks (default: 20)")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output in JSON format")
    args = parser.parse_args()
    get_ticker(args.code, args.num, args.output_json)
