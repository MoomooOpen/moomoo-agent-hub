#!/usr/bin/env python3
"""
Receive Prediction Market Order Book Push

Function: Subscribe to prediction market order book (YES/NO bid/ask) and receive real-time pushes via a Handler
Usage: python push_event_contract_orderbook.py EC.KXODIMATCH-26JUL140600INDENG-IND --duration 60 [--json]

API: EventContractOrderBookHandlerBase push (requires set_handler + subscription to SubType.ORDER_BOOK first)
Return: callback content is a list[dict] (one dict per contract); fields code / yes_bids / yes_asks / no_bids / no_asks

API Limits:
- Requires subscribing to ORDER_BOOK first, limited by the subscription quota
- The first push only returns the first level; subsequent pushes return per actual order book changes
- The callback runs in a separate thread; mind thread safety
- Note: unlike get_event_contract_order_book, the push returns a list of dicts (one per contract)
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
    EventContractOrderBookHandlerBase,
    assert_event_contract_support,
)

from moomoo import RET_ERROR

# The handler base class is only provided by SDK versions that support prediction market.
# Fall back to `object` on older SDKs so the module imports cleanly (and -h keeps working);
# the actual availability is enforced in main() via assert_event_contract_support().
_EC_OB_BASE = EventContractOrderBookHandlerBase if EventContractOrderBookHandlerBase else object


class EventContractOrderBookHandler(_EC_OB_BASE):
    """Prediction market order book push callback handler"""
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

        # content is a list[dict] (one dict per contract)
        for ob in content:
            if self.output_json:
                print(json.dumps({
                    "type": "EVENT_CONTRACT_ORDER_BOOK",
                    "code": ob.get("code", ""),
                    "yes_bids": ob.get("yes_bids", []),
                    "yes_asks": ob.get("yes_asks", []),
                    "no_bids": ob.get("no_bids", []),
                    "no_asks": ob.get("no_asks", []),
                }, ensure_ascii=False, default=str), flush=True)
            else:
                print(f"\n[Prediction Market OrderBook Push] {time.strftime('%H:%M:%S')} - {ob.get('code', '')}")
                for label, key in [("YES bid", "yes_bids"), ("YES ask", "yes_asks"),
                                   ("NO bid", "no_bids"), ("NO ask", "no_asks")]:
                    levels = ob.get(key, [])
                    print(f"  {label}: {levels[:5]}")

        return RET_OK, content


def push_event_contract_orderbook(codes, duration=60, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        assert_event_contract_support(ctx, output_json=output_json)

        handler = EventContractOrderBookHandler(output_json=output_json)
        ctx.set_handler(handler)

        ret, msg = ctx.subscribe_event_contract(codes, [SubType.ORDER_BOOK], subscribe_push=True)
        check_ret(ret, msg, ctx, "Subscribe prediction market order book push")

        if not output_json:
            print(f"Subscribed prediction market order book push: {', '.join(codes)}")
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
    parser = argparse.ArgumentParser(description="Receive prediction market order book push")
    parser.add_argument("codes", nargs="+", help="Prediction market contract codes, e.g. EC.xxx")
    parser.add_argument("--duration", type=int, default=60, help="Duration to receive (seconds, default: 60)")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output JSON format")
    args = parser.parse_args()
    push_event_contract_orderbook(args.codes, args.duration, args.output_json)
