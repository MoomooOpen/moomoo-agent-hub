#!/usr/bin/env python3
"""
Subscribe to real-time market data

Function: Subscribe to specified data types for stocks (QUOTE/ORDER_BOOK/TICKER/RT_DATA/BROKER/Candlestick, etc.)
Usage: python subscribe.py HK.00700 --types QUOTE ORDER_BOOK

API limitations:
- Each stock subscription of one type uses 1 subscription quota (quota depends on user level, 100~2000)
- Must subscribe for at least one minute before unsubscribing
- HK stock BMP permission does not support subscription; US stock after-hours requires LV1 or above
- SF permission users are limited to subscribing to order book for 50 securities simultaneously
- HK options/futures LV1 permission does not support tick-by-tick subscription types

Parameter notes:
- is_first_push: True pushes the last cached data before disconnection, False waits for the latest server push
- subscribe_push: True enables real-time callback push (required), False only retrieves data via active request (saves performance)
- is_detailed_orderbook: Only used when subscribing to ORDER_BOOK under HK SF permission; US LV2 does not provide detailed breakdown
- extended_time: Only used for subscribing to US stock real-time Candlestick, intraday, and tick-by-tick data
- session: Only used for subscribing to US stock real-time Candlestick, intraday, and tick-by-tick data; OVERNIGHT is not supported
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
    parse_subtypes,
    Session,
)

# session only supports the following values (OVERNIGHT is not supported for subscribe)
SESSION_MAP = {
    "NONE": Session.NONE,
    "RTH": Session.RTH,
    "ETH": Session.ETH,
    "ALL": Session.ALL,
}


def subscribe(codes, subtype_names, is_first_push=True, subscribe_push=False,
              extended_time=False, session_str="NONE", output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        subtypes = parse_subtypes(subtype_names)
        session = SESSION_MAP.get(session_str.upper(), Session.NONE)

        ret, msg = ctx.subscribe(
            codes, subtypes,
            is_first_push=is_first_push,
            subscribe_push=subscribe_push,
            extended_time=extended_time,
            session=session,
        )
        check_ret(ret, msg, ctx, "Subscribe")

        result = {
            "codes": codes,
            "subtypes": [str(s).split(".")[-1] for s in subtypes],
            "is_first_push": is_first_push,
            "subscribe_push": subscribe_push,
            "extended_time": extended_time,
            "session": session_str.upper(),
            "status": "subscribed",
        }

        if output_json:
            print(json.dumps(result, ensure_ascii=False))
        else:
            print("=" * 50)
            print("Subscription successful")
            print("=" * 50)
            print(f"  Stocks: {', '.join(codes)}")
            print(f"  Types: {', '.join(result['subtypes'])}")
            print("=" * 50)

    except Exception as e:
        if output_json:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))
        else:
            print(f"Error: {e}")
        sys.exit(1)
    finally:
        safe_close(ctx)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Subscribe to real-time market data")
    parser.add_argument("codes", nargs="+", help="Stock code, e.g. HK.00700 US.AAPL")
    parser.add_argument("--types", nargs="+", required=True,
                        help="Subscription types: QUOTE ORDER_BOOK TICKER RT_DATA BROKER K_DAY K_1M K_5M K_15M K_30M K_60M K_WEEK K_MON")
    parser.add_argument("--no-first-push", action="store_true", help="Do not immediately push cached data")
    parser.add_argument("--push", action="store_true", help="Enable push callback")
    parser.add_argument("--extended-time", action="store_true", help="US stock pre-market and after-hours data")
    parser.add_argument("--session", choices=["NONE", "RTH", "ETH", "ALL"],
                        default="NONE", help="US stock trading session (only for US Candlestick/intraday/tick-by-tick, OVERNIGHT not supported)")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output in JSON format")
    args = parser.parse_args()
    subscribe(codes=args.codes, subtype_names=args.types,
              is_first_push=not args.no_first_push, subscribe_push=args.push,
              extended_time=args.extended_time, session_str=args.session,
              output_json=args.output_json)
