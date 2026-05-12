#!/usr/bin/env python3
"""
Receive quote push

Function: Subscribe to stock quotes and receive real-time push data via Handler
Usage: python push_quote.py HK.00700 --duration 60

API limitations:
- Must first subscribe to QUOTE type, subject to subscription quota limits
- HK stock BMP permission does not support subscription
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
    safe_float,
    safe_int,
    SubType,
    RET_OK,
)

from moomoo import StockQuoteHandlerBase, RET_ERROR


class QuoteHandler(StockQuoteHandlerBase):
    """Quote push callback handler class"""
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
            records = []
            for i in range(len(data)):
                row = data.iloc[i] if hasattr(data, "iloc") else data[i]
                records.append({
                    "code": row.get("code", ""),
                    "last_price": safe_float(row.get("last_price", 0)),
                    "volume": safe_int(row.get("volume", 0)),
                    "turnover": safe_float(row.get("turnover", 0)),
                    "high_price": safe_float(row.get("high_price", 0)),
                    "low_price": safe_float(row.get("low_price", 0)),
                })
            print(json.dumps({"type": "QUOTE", "data": records}, ensure_ascii=False), flush=True)
        else:
            print(f"\n[Quote Push] {time.strftime('%H:%M:%S')}")
            if hasattr(data, "iloc"):
                print(data[['code', 'last_price', 'volume', 'turnover']].to_string(index=False))
            else:
                for row in data:
                    if hasattr(row, "get"):
                        print(f"  {row.get('code', '')}\t{row.get('last_price', '')}\t{row.get('volume', '')}\t{row.get('turnover', '')}")
                    else:
                        print(f"  {row}")

        return RET_OK, data


def push_quote(codes, duration=60, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        handler = QuoteHandler(output_json=output_json)
        ctx.set_handler(handler)

        ret, msg = ctx.subscribe(codes, [SubType.QUOTE], subscribe_push=True)
        check_ret(ret, msg, ctx, "Subscribe to quote push")

        if not output_json:
            print(f"Subscribed to quote push: {', '.join(codes)}")
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
    parser = argparse.ArgumentParser(description="Receive quote push")
    parser.add_argument("codes", nargs="+", help="Stock code, e.g. HK.00700")
    parser.add_argument("--duration", type=int, default=60, help="Duration to receive push (seconds, default: 60)")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output in JSON format")
    args = parser.parse_args()
    push_quote(args.codes, args.duration, args.output_json)
