#!/usr/bin/env python3
"""
Receive order book push

Function: Subscribe to stock order book (bid/ask) and receive real-time push data via Handler
Usage: python push_orderbook.py HK.00700 --duration 60

API limitations:
- Must first subscribe to ORDER_BOOK type, subject to subscription quota limits
"""
import argparse
import json
import time
import sys
import os as _os
sys.path.insert(0, _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..")))
from common import (
    create_quote_context,
    check_ret,
    safe_close,
    SubType,
    RET_OK,
    OrderBookType,
)

from moomoo import OrderBookHandlerBase, RET_ERROR


class OrderBookHandler(OrderBookHandlerBase):
    """Order book push callback handler class"""
    def __init__(self, output_json=False):
        super().__init__()
        self.output_json = output_json

    def on_recv_rsp(self, rsp_pb):
        ret_code, data = super().on_recv_rsp(rsp_pb)
        if ret_code != RET_OK:
            if self.output_json:
                print(json.dumps({"error": str(data)}, ensure_ascii=False), flush=True)
            else:
                print(f"Push error: {data}", flush=True)
            return RET_ERROR, data

        if self.output_json:
            print(json.dumps({"type": "ORDER_BOOK", "code": data.get("code", ""), "data": data}, ensure_ascii=False, default=str), flush=True)
        else:
            print(f"\n[Order Book Push] {time.strftime('%H:%M:%S')} - {data.get('code', '')}")
            bid_list = data.get("Bid", [])
            ask_list = data.get("Ask", [])
            print("  Bid:")
            for item in bid_list[:5]:
                print(f"    {item}")
            print("  Ask:")
            for item in ask_list[:5]:
                print(f"    {item}")

        return RET_OK, data


_ODD_LOT_MARKETS = ("MY", "SG")


def push_orderbook(codes, duration=60, output_json=False, order_book_type=None):
    # Odd lot order book only supports MY/SG markets
    if order_book_type == OrderBookType.ODD:
        for code in codes:
            prefix = code.split(".")[0].upper() if "." in code else ""
            if prefix not in _ODD_LOT_MARKETS:
                msg = f"Odd lot order book only supports {'/'.join(_ODD_LOT_MARKETS)} markets, got: {code}"
                if output_json:
                    print(json.dumps({"error": msg}, ensure_ascii=False))
                else:
                    print(f"Error: {msg}")
                sys.exit(1)

    ctx = None
    try:
        ctx = create_quote_context()
        handler = OrderBookHandler(output_json=output_json)
        ctx.set_handler(handler)

        sub_type = SubType.ORDER_BOOK_ODD if order_book_type == OrderBookType.ODD else SubType.ORDER_BOOK
        ret, msg = ctx.subscribe(codes, [sub_type], subscribe_push=True)
        check_ret(ret, msg, ctx, "Subscribe to order book push")

        if not output_json:
            print(f"Subscribed to order book push: {', '.join(codes)}")
            print(f"Waiting for push for {duration} seconds...")

        time.sleep(duration)

    except KeyboardInterrupt:
        if not output_json:
            print("\nStopped receiving push")
    except Exception as e:
        if output_json:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))
        else:
            print(f"Error: {e}")
        sys.exit(1)
    finally:
        safe_close(ctx)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Receive order book push")
    parser.add_argument("codes", nargs="+", help="Stock code, e.g. MY.1155 / SG.S68")
    parser.add_argument("--duration", type=int, default=60, help="Duration to receive push (seconds, default: 60)")
    parser.add_argument("--type", choices=["NORMAL", "ODD"], default=None, help="Order book type: NORMAL=round lot, ODD=odd lot. Odd lot only supports MY/SG markets")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output in JSON format")
    args = parser.parse_args()
    ob_type = getattr(OrderBookType, args.type) if args.type else None
    push_orderbook(args.codes, args.duration, args.output_json, ob_type)
