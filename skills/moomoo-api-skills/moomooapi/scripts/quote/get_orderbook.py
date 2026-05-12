#!/usr/bin/env python3
"""
Get Order Book Data

Function: Retrieve the order book (bid/ask depth) data for a given stock
Usage: python get_orderbook.py HK.00700 --num 10

API limits:
- Requires prior subscription to ORDER_BOOK type
- US stocks return real-time order book data for the current trading session; no need to set session

Return field notes:
- svr_recv_time_bid/svr_recv_time_ask: Some data receive times may be zero (e.g. after server restart or first push of cached data)
- Bid/Ask order details: Up to 1000 entries under HK SF permission; other permissions do not support this
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
    SubType,
    RET_OK,
)


def get_orderbook(code, num=10, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        # Must subscribe to ORDER_BOOK first
        ret, msg = ctx.subscribe([code], [SubType.ORDER_BOOK])
        if ret != RET_OK:
            print(f"Subscription failed: {msg}")
            sys.exit(1)

        ret, data = ctx.get_order_book(code, num=num)
        check_ret(ret, data, ctx, "get order book")

        if is_empty(data):
            if output_json:
                print(json.dumps({"code": code, "Bid": [], "Ask": []}))
            else:
                print("No data")
            return

        # data is a dict containing Bid and Ask lists
        bids = data.get("Bid", [])
        asks = data.get("Ask", [])

        if output_json:
            print(json.dumps({"code": code, "Bid": bids, "Ask": asks}, ensure_ascii=False))
        else:
            print("=" * 60)
            print(f"Order Book: {code}")
            print("=" * 60)
            print(f"  {'Ask':^28}  |  {'Bid':^28}")
            print("  " + "-" * 58)
            max_rows = max(len(bids), len(asks))
            for i in range(max_rows):
                ask_str = ""
                bid_str = ""
                if i < len(asks):
                    a = asks[len(asks) - 1 - i]
                    ask_str = f"  Ask{len(asks)-i}: {a[0]:>10.3f} x {int(a[1]):>8}"
                if i < len(bids):
                    b = bids[i]
                    bid_str = f"  Bid{i+1}: {b[0]:>10.3f} x {int(b[1]):>8}"
                print(f"  {ask_str:<28}  |  {bid_str:<28}")
            print("=" * 60)

    except Exception as e:
        if output_json:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))
        else:
            print(f"Error: {e}")
        sys.exit(1)
    finally:
        safe_close(ctx)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get order book data")
    parser.add_argument("code", help="Stock code, e.g. HK.00700")
    parser.add_argument("--num", type=int, default=10, help="Number of price levels (default: 10)")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output in JSON format")
    args = parser.parse_args()
    get_orderbook(args.code, args.num, args.output_json)
