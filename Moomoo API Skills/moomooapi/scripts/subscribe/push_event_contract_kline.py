#!/usr/bin/env python3
"""
Receive Prediction Market K-line Push

Function: Subscribe to prediction market K-line and receive real-time pushes via a Handler
Usage: python push_event_contract_kline.py EC.KXODIMATCH-26JUL140600INDENG-IND --ktype K_DAY [--kline-source ORDER_BOOK_YES] [--duration 300] [--json]

API: EventContractKlineHandlerBase push (requires set_handler + subscription to the corresponding K-line type)
Return: callback content is a DataFrame; fields code / pre_side / name / time_key / open / high / low / close / volume

API Limits:
- Requires subscribing to the corresponding K-line type first, limited by the subscription quota
- Prediction Market K-line only supports K_1M/K_5M/K_60M/K_DAY
- Omit kline_source to default to contract-level trade-price K-line
- The callback runs in a separate thread; mind thread safety
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
    parse_ec_kline_source,
    EventContractKlineHandlerBase,
    assert_event_contract_support,
)

from moomoo import RET_ERROR


_KLTYPE_SUBTYPE_MAP = {
    "K_1M": SubType.K_1M,
    "K_5M": SubType.K_5M,
    "K_60M": SubType.K_60M,
    "K_DAY": SubType.K_DAY,
}

# The handler base class is only provided by SDK versions that support prediction market.
# Fall back to `object` on older SDKs so the module imports cleanly (and -h keeps working);
# the actual availability is enforced in main() via assert_event_contract_support().
_EC_KL_BASE = EventContractKlineHandlerBase if EventContractKlineHandlerBase else object


class EventContractKlineHandler(_EC_KL_BASE):
    """Prediction market K-line push callback handler"""
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
                    "pre_side": row.get("pre_side", ""),
                    "name": row.get("name", ""),
                    "time_key": row.get("time_key", ""),
                    "open": safe_float(row.get("open", 0)),
                    "high": safe_float(row.get("high", 0)),
                    "low": safe_float(row.get("low", 0)),
                    "close": safe_float(row.get("close", 0)),
                    "volume": safe_float(row.get("volume", 0)),
                })
            print(json.dumps({"type": "EVENT_CONTRACT_KLINE", "data": records}, ensure_ascii=False, default=str), flush=True)
        else:
            print(f"\n[Prediction Market Kline Push] {time.strftime('%H:%M:%S')}")
            print(content.to_string(index=False))

        return RET_OK, content


def push_event_contract_kline(codes, ktype="K_DAY", kline_source=None, duration=300, output_json=False):
    ktype_key = str(ktype).upper()
    sub_type = _KLTYPE_SUBTYPE_MAP.get(ktype_key, SubType.K_DAY)

    ctx = None
    try:
        ctx = create_quote_context()
        assert_event_contract_support(ctx, output_json=output_json)

        handler = EventContractKlineHandler(output_json=output_json)
        ctx.set_handler(handler)

        kline_sources = None
        if kline_source:
            kline_sources = [parse_ec_kline_source(kline_source)]

        ret, msg = ctx.subscribe_event_contract(
            codes, [sub_type], kline_source_list=kline_sources, subscribe_push=True)
        check_ret(ret, msg, ctx, "Subscribe prediction market K-line push")

        if not output_json:
            print(f"Subscribed prediction market {ktype_key} K-line push: {', '.join(codes)}")
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
    parser = argparse.ArgumentParser(description="Receive prediction market K-line push")
    parser.add_argument("codes", nargs="+", help="Prediction market contract codes, e.g. EC.xxx")
    parser.add_argument("--ktype", choices=["K_1M", "K_5M", "K_60M", "K_DAY"],
                        default="K_DAY", help="K-line type (default: K_DAY)")
    parser.add_argument("--kline-source", choices=["ORDER_BOOK_YES"], default=None,
                        help="K-line source ORDER_BOOK_YES (default contract-level trade-price K-line)")
    parser.add_argument("--duration", type=int, default=300, help="Duration to receive (seconds, default: 300)")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output JSON format")
    args = parser.parse_args()
    push_event_contract_kline(args.codes, args.ktype, args.kline_source, args.duration, args.output_json)
