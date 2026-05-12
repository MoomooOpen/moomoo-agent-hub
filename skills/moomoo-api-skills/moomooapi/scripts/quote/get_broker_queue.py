#!/usr/bin/env python3
"""
Get Broker Queue

Function: Get the broker bid/ask queue data for a stock
Usage: python get_broker_queue.py HK.00700

API Limits:
- Must subscribe to BROKER type first
- Only HK stocks support broker queue
- Requires LV2 market data permission
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
    SubType,
)


def get_broker_queue(code, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        ret, msg = ctx.subscribe([code], [SubType.BROKER])
        check_ret(ret, msg, ctx, "Subscribe broker queue")

        ret, bid_data, ask_data = ctx.get_broker_queue(code)
        check_ret(ret, bid_data, ctx, "Get broker queue")

        if output_json:
            print(json.dumps({
                "code": code,
                "bid_broker": df_to_records(bid_data),
                "ask_broker": df_to_records(ask_data),
            }, ensure_ascii=False))
        else:
            print("=" * 70)
            print(f"Broker Queue - {code}")
            print("=" * 70)
            print("\nBid Brokers:")
            if is_empty(bid_data):
                print("  No data")
            else:
                print(bid_data.to_string(index=False))
            print("\nAsk Brokers:")
            if is_empty(ask_data):
                print("  No data")
            else:
                print(ask_data.to_string(index=False))
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
    parser = argparse.ArgumentParser(description="Get broker queue (requires LV2 permission)")
    parser.add_argument("code", help="Stock code, e.g. HK.00700")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output in JSON format")
    args = parser.parse_args()
    get_broker_queue(args.code, args.output_json)
