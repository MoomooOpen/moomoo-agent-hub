#!/usr/bin/env python3
"""
Receive Candlestick push

Function: Subscribe to stock Candlestick and receive real-time push data via Handler
Usage: python push_kline.py HK.00700 --ktype K_1M --duration 300

API limitations:
- Must first subscribe to the corresponding Candlestick type, subject to subscription quota limits
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
    Session,
    RET_OK,
)

from moomoo import CurKlineHandlerBase, RET_ERROR

# session only supports the following values (OVERNIGHT is not supported for subscribe)
SESSION_MAP = {
    "NONE": Session.NONE,
    "RTH": Session.RTH,
    "ETH": Session.ETH,
    "ALL": Session.ALL,
}

KTYPE_SUB_MAP = {
    "K_1M": SubType.K_1M,
    "K_3M": SubType.K_3M,
    "K_5M": SubType.K_5M,
    "K_15M": SubType.K_15M,
    "K_30M": SubType.K_30M,
    "K_60M": SubType.K_60M,
    "K_DAY": SubType.K_DAY,
    "K_WEEK": SubType.K_WEEK,
    "K_MON": SubType.K_MON,
    "K_QUARTER": SubType.K_QUARTER,
    "K_YEAR": SubType.K_YEAR,
}


class KlineHandler(CurKlineHandlerBase):
    """Candlestick push callback handler class"""
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
                    "time_key": row.get("time_key", ""),
                    "open": safe_float(row.get("open", 0)),
                    "high": safe_float(row.get("high", 0)),
                    "low": safe_float(row.get("low", 0)),
                    "close": safe_float(row.get("close", 0)),
                    "volume": safe_int(row.get("volume", 0)),
                })
            print(json.dumps({"type": "KLINE", "data": records}, ensure_ascii=False), flush=True)
        else:
            print(f"\n[Candlestick Push] {time.strftime('%H:%M:%S')}")
            print(data.to_string(index=False))

        return RET_OK, data


def push_kline(codes, ktype="K_1M", duration=300, session_str="NONE", output_json=False):
    sub_type = KTYPE_SUB_MAP.get(ktype.upper(), SubType.K_1M)
    session = SESSION_MAP.get(session_str.upper(), Session.NONE)

    ctx = None
    try:
        ctx = create_quote_context()
        handler = KlineHandler(output_json=output_json)
        ctx.set_handler(handler)

        ret, msg = ctx.subscribe(codes, [sub_type], subscribe_push=True, session=session)
        check_ret(ret, msg, ctx, "Subscribe to Candlestick push")

        if not output_json:
            print(f"Subscribed to {ktype} Candlestick push: {', '.join(codes)}")
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
    parser = argparse.ArgumentParser(description="Receive Candlestick push")
    parser.add_argument("codes", nargs="+", help="Stock code, e.g. HK.00700")
    parser.add_argument("--ktype", choices=["K_1M", "K_3M", "K_5M", "K_15M", "K_30M", "K_60M", "K_DAY", "K_WEEK", "K_MON", "K_QUARTER", "K_YEAR"],
                        default="K_1M", help="Candlestick type (default: K_1M)")
    parser.add_argument("--duration", type=int, default=300, help="Duration to receive push (seconds, default: 300)")
    parser.add_argument("--session", choices=["NONE", "RTH", "ETH", "ALL"],
                        default="NONE", help="US stock trading session (US only, OVERNIGHT not supported)")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output in JSON format")
    args = parser.parse_args()
    push_kline(args.codes, args.ktype, args.duration, args.session, args.output_json)
