#!/usr/bin/env python3
"""
Receive Event Contract Ticker Push

Function: Subscribe to event contract ticker and receive real-time pushes via a Handler
Usage: python push_event_contract_ticker.py EC.KXODIMATCH-26JUL140600INDENG-IND --duration 60 [--json]

API: EventContractTickerHandlerBase push (requires set_handler + subscription to SubType.TICKER)
Return: callback content is a DataFrame; fields code / time / yes_price / no_price / volume / side / sequence

API Limits:
- Requires subscribing to TICKER first, limited by the subscription quota
- The callback runs in a separate thread; mind thread safety
- sequence is the backend tick id, a large integer
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
    SubType,
    RET_OK,
    EventContractTickerHandlerBase,
    assert_event_contract_support,
)

from moomoo import RET_ERROR

# The handler base class is only provided by SDK versions that support Event Contract.
# Fall back to `object` on older SDKs so the module imports cleanly (and -h keeps working);
# the actual availability is enforced in main() via assert_event_contract_support().
_EC_TK_BASE = EventContractTickerHandlerBase if EventContractTickerHandlerBase else object


class EventContractTickerHandler(_EC_TK_BASE):
    """Event contract ticker push callback handler"""
    def __init__(self, output_json=False):
        super().__init__()
        self.output_json = output_json

    def on_recv_rsp(self, rsp_pb):
        ret_code, content = super().on_recv_rsp(rsp_pb)
        if ret_code != RET_OK:
            if self.output_json:
                print(json.dumps({"error": str(content)}, ensure_ascii=False), flush=True)
            else:
                print(f"Push error: {content}", flush=True)
            return RET_ERROR, content

        # content is a DataFrame
        if self.output_json:
            records = []
            for i in range(len(content)):
                row = content.iloc[i] if hasattr(content, "iloc") else content[i]
                records.append({
                    "code": row.get("code", ""),
                    "time": row.get("time", ""),
                    "yes_price": safe_float(row.get("yes_price", 0)),
                    "no_price": safe_float(row.get("no_price", 0)),
                    "volume": safe_float(row.get("volume", 0)),
                    "side": row.get("side", ""),
                    "sequence": str(row.get("sequence", "")),
                })
            print(json.dumps({"type": "EVENT_CONTRACT_TICKER", "data": records}, ensure_ascii=False, default=str), flush=True)
        else:
            print(f"\n[EventContract Ticker Push] {time.strftime('%H:%M:%S')}")
            print(content.to_string(index=False))

        return RET_OK, content


def push_event_contract_ticker(codes, duration=60, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        assert_event_contract_support(ctx, output_json=output_json)

        handler = EventContractTickerHandler(output_json=output_json)
        ctx.set_handler(handler)

        ret, msg = ctx.subscribe_event_contract(codes, [SubType.TICKER], subscribe_push=True)
        check_ret(ret, msg, ctx, "Subscribe event contract ticker push")

        if not output_json:
            print(f"Subscribed event contract ticker push: {', '.join(codes)}")
            print(f"Waiting for pushes for {duration} seconds...")

        time.sleep(duration)

    except KeyboardInterrupt:
        if not output_json:
            print("\nStopped receiving pushes")
    except Exception as e:
        if output_json:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))
        else:
            print(f"Error: {e}")
        sys.exit(1)
    finally:
        safe_close(ctx)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Receive event contract ticker push")
    parser.add_argument("codes", nargs="+", help="Event contract codes, e.g. EC.xxx")
    parser.add_argument("--duration", type=int, default=60, help="Duration to receive (seconds, default: 60)")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output JSON format")
    args = parser.parse_args()
    push_event_contract_ticker(args.codes, args.duration, args.output_json)
