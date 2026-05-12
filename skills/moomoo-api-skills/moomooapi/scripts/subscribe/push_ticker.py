#!/usr/bin/env python3
"""
Receive tick-by-tick push

Function: Subscribe to stock tick-by-tick trades and receive real-time push data via Handler
Usage: python push_ticker.py HK.00700 --duration 60

API limitations:
- Must first subscribe to TICKER type, subject to subscription quota limits
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
    df_to_records,
    SubType,
    Session,
    RET_OK,
)

from moomoo import TickerHandlerBase, RET_ERROR

# session only supports the following values (OVERNIGHT is not supported for subscribe)
SESSION_MAP = {
    "NONE": Session.NONE,
    "RTH": Session.RTH,
    "ETH": Session.ETH,
    "ALL": Session.ALL,
}


class TickerHandler(TickerHandlerBase):
    """Tick-by-tick push callback handler class"""
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
            print(json.dumps({"type": "TICKER", "data": df_to_records(data)}, ensure_ascii=False), flush=True)
        else:
            print(f"\n[Tick-by-tick Push] {time.strftime('%H:%M:%S')}")
            cols = [c for c in ['code', 'time', 'price', 'volume', 'ticker_direction'] if c in data.columns]
            print(data[cols].to_string(index=False))

        return RET_OK, data


def push_ticker(codes, duration=60, session_str="NONE", output_json=False):
    session = SESSION_MAP.get(session_str.upper(), Session.NONE)
    ctx = None
    try:
        ctx = create_quote_context()
        handler = TickerHandler(output_json=output_json)
        ctx.set_handler(handler)

        ret, msg = ctx.subscribe(codes, [SubType.TICKER], subscribe_push=True, session=session)
        check_ret(ret, msg, ctx, "Subscribe to tick-by-tick push")

        if not output_json:
            print(f"Subscribed to tick-by-tick push: {', '.join(codes)}")
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
    parser = argparse.ArgumentParser(description="Receive tick-by-tick push")
    parser.add_argument("codes", nargs="+", help="Stock code, e.g. HK.00700")
    parser.add_argument("--duration", type=int, default=60, help="Duration to receive push (seconds, default: 60)")
    parser.add_argument("--session", choices=["NONE", "RTH", "ETH", "ALL"],
                        default="NONE", help="US stock trading session (US only, OVERNIGHT not supported)")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output in JSON format")
    args = parser.parse_args()
    push_ticker(args.codes, args.duration, args.session, args.output_json)
