#!/usr/bin/env python3
"""
Get Event Contract Real-time Order Book

Function: Get event contract YES/NO two-sided multi-level bid/ask; requires subscribing to ORDER_BOOK first
Usage: python get_event_contract_order_book.py EC.KXODIMATCH-26JUL140600INDENG-IND [--num 5] [--no-auto-subscribe] [--json]

API: OpenQuoteContext.get_event_contract_order_book(code, num=10)
Return: dict {'code', 'yes_bids': [(price,size),...], 'yes_asks', 'no_bids', 'no_asks'}

API Limits:
- Must subscribe to SubType.ORDER_BOOK before querying, otherwise error "subscribe OrderBook data first"
- num must be > 0, default 10; actual returned levels are converged by the backend
- The script auto-subscribes by default; use --no-auto-subscribe to skip when already subscribed
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
    SubType,
    assert_event_contract_support,
    ensure_event_contract_subscribed,
)


def _format_book_side(levels, n_show=None):
    """Format one side of the order book -> [[price, size], ...] (JSON-serializable)"""
    out = []
    for lv in levels:
        if isinstance(lv, (list, tuple)) and len(lv) >= 2:
            out.append([float(lv[0]), float(lv[1])])
        else:
            out.append(lv)
    if n_show:
        out = out[:n_show]
    return out


def get_event_contract_order_book(code, num=10, auto_subscribe=True, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        assert_event_contract_support(ctx, output_json=output_json)

        # Auto-subscribe ORDER_BOOK before querying (already-subscribed is skipped silently)
        if auto_subscribe:
            ensure_event_contract_subscribed(ctx, code, SubType.ORDER_BOOK,
                                             output_json=output_json,
                                             action="Subscribe event contract order book")

        ret, data = ctx.get_event_contract_order_book(code, num=num)
        check_ret(ret, data, ctx, "Get event contract order book")

        result = {
            "code": data.get("code", code),
            "yes_bids": _format_book_side(data.get("yes_bids", [])),
            "yes_asks": _format_book_side(data.get("yes_asks", [])),
            "no_bids": _format_book_side(data.get("no_bids", [])),
            "no_asks": _format_book_side(data.get("no_asks", [])),
        }

        if output_json:
            print(json.dumps(result, ensure_ascii=False))
        else:
            print("=" * 64)
            print(f"Event Contract Order Book - {result['code']}")
            print("=" * 64)
            for label, side in [("YES bid", "yes_bids"), ("YES ask", "yes_asks")]:
                levels = result[side]
                print(f"  {label}:")
                for i, lv in enumerate(levels, 1):
                    if isinstance(lv, list) and len(lv) >= 2:
                        print(f"    {i}: {lv[0]:>8.3f} x {lv[1]:>10.2f}")
                    else:
                        print(f"    {i}: {lv}")
            for label, side in [("NO bid", "no_bids"), ("NO ask", "no_asks")]:
                levels = result[side]
                print(f"  {label}:")
                for i, lv in enumerate(levels, 1):
                    if isinstance(lv, list) and len(lv) >= 2:
                        print(f"    {i}: {lv[0]:>8.3f} x {lv[1]:>10.2f}")
                    else:
                        print(f"    {i}: {lv}")
            print("=" * 64)

    except Exception as e:
        if output_json:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))
        else:
            print(f"Error: {e}")
        sys.exit(1)
    finally:
        safe_close(ctx)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get event contract real-time order book (requires ORDER_BOOK subscription)")
    parser.add_argument("code", help="Event contract code, e.g. EC.KXODIMATCH-26JUL140600INDENG-IND")
    parser.add_argument("--num", type=int, default=10, help="Number of order book levels, default 10, must be > 0")
    parser.add_argument("--no-auto-subscribe", action="store_true",
                        help="Do not auto-subscribe (use when already subscribed)")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output JSON format")
    args = parser.parse_args()
    get_event_contract_order_book(
        code=args.code, num=args.num,
        auto_subscribe=not args.no_auto_subscribe, output_json=args.output_json)
