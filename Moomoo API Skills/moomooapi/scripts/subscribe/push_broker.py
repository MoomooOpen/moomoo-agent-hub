#!/usr/bin/env python3
"""
Receive broker queue push

Function: Subscribe to stock broker queue and receive real-time push data via Handler
Usage: python push_broker.py HK.00700 --duration 60

API limitations:
- Must first subscribe to BROKER type, subject to subscription quota limits
- Only HK stocks support broker queue
- Requires LV2 market data permission
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
)

from moomoo import BrokerHandlerBase, RET_ERROR


class BrokerHandler(BrokerHandlerBase):
    """Broker queue push callback handler class"""
    def __init__(self, output_json=False):
        super().__init__()
        self.output_json = output_json

    def on_recv_rsp(self, rsp_pb):
        ret_code, stock_code, data = super().on_recv_rsp(rsp_pb)
        if ret_code != RET_OK:
            if self.output_json:
                print(json.dumps({"error": str(data)}, ensure_ascii=False), flush=True)
            else:
                print(f"Push error: {data}", flush=True)
            return RET_ERROR, stock_code, data

        if self.output_json:
            print(json.dumps({"type": "BROKER", "code": stock_code, "data": data}, ensure_ascii=False, default=str), flush=True)
        else:
            print(f"\n[Broker Push] {time.strftime('%H:%M:%S')} - {stock_code}")
            if isinstance(data, dict):
                bid_list = data.get("bid_broker_list", [])
                ask_list = data.get("ask_broker_list", [])
                print("  Bid brokers:")
                for item in bid_list[:5]:
                    print(f"    {item}")
                print("  Ask brokers:")
                for item in ask_list[:5]:
                    print(f"    {item}")
            else:
                print(f"  {data}")

        return RET_OK, stock_code, data


def push_broker(codes, duration=60, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        handler = BrokerHandler(output_json=output_json)
        ctx.set_handler(handler)

        ret, msg = ctx.subscribe(codes, [SubType.BROKER], subscribe_push=True)
        check_ret(ret, msg, ctx, "Subscribe to broker push")

        if not output_json:
            print(f"Subscribed to broker push: {', '.join(codes)}")
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
    parser = argparse.ArgumentParser(description="Receive broker queue push (requires LV2 permission)")
    parser.add_argument("codes", nargs="+", help="Stock code, e.g. HK.00700")
    parser.add_argument("--duration", type=int, default=60, help="Duration to receive push (seconds, default: 60)")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output in JSON format")
    args = parser.parse_args()
    push_broker(args.codes, args.duration, args.output_json)
