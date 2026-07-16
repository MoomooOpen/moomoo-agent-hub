#!/usr/bin/env python3
"""
Get Prediction Market Real-time Ticker

Function: Get prediction market real-time trade ticks (YES/NO trade price, volume, trade side, sequence); requires subscribing to TICKER first
Usage: python get_event_contract_ticker.py EC.KXODIMATCH-26JUL140600INDENG-IND [--count 30] [--no-auto-subscribe] [--json]

API: OpenQuoteContext.get_event_contract_ticker(code, count=30)
Return: DataFrame; columns code / time / yes_price / no_price / volume / side / sequence

API Limits:
- Must subscribe to SubType.TICKER before querying, otherwise error "subscribe Ticker data first"
- count default 30, max 1000
- side is the trade direction (YES/NO), distinct from trading buy/sell direction
- sequence is the backend tick id, a large integer
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
    is_empty,
    df_to_records,
    print_display_df,
    SubType,
    assert_event_contract_support,
    ensure_event_contract_subscribed,
)


def get_event_contract_ticker(code, count=30, auto_subscribe=True, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        assert_event_contract_support(ctx, output_json=output_json)

        # Auto-subscribe TICKER before querying (already-subscribed is skipped silently)
        if auto_subscribe:
            ensure_event_contract_subscribed(ctx, code, SubType.TICKER,
                                             output_json=output_json,
                                             action="Subscribe prediction market ticker")

        ret, data = ctx.get_event_contract_ticker(code, count=count)
        check_ret(ret, data, ctx, "Get prediction market ticker")

        if is_empty(data):
            if output_json:
                print(json.dumps({"data": []}))
            else:
                print("No data")
            return

        if output_json:
            print(json.dumps({"data": df_to_records(data)}, ensure_ascii=False))
        else:
            print("=" * 70)
            print(f"Prediction Market Ticker - {code}")
            print("=" * 70)
            cols = [c for c in ['code', 'time', 'yes_price', 'no_price',
                                'volume', 'side', 'sequence']
                    if c in data.columns]
            print_display_df(data[cols], max_colwidth=28)
            print(f"\nTotal {len(data)} ticks")
            print("=" * 70)

    except Exception as e:
        if output_json:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))
        else:
            print(f"Error: {e}")
        sys.exit(1)
    finally:
        safe_close(ctx)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get prediction market real-time ticker (requires TICKER subscription)")
    parser.add_argument("code", help="Prediction market contract code, e.g. EC.KXODIMATCH-26JUL140600INDENG-IND")
    parser.add_argument("--count", type=int, default=30, help="Number of ticks, default 30, max 1000")
    parser.add_argument("--no-auto-subscribe", action="store_true",
                        help="Do not auto-subscribe (use when already subscribed)")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output JSON format")
    args = parser.parse_args()
    get_event_contract_ticker(
        code=args.code, count=args.count,
        auto_subscribe=not args.no_auto_subscribe, output_json=args.output_json)
