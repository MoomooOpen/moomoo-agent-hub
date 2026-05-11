#!/usr/bin/env python3
"""
Get Trading Calendar

Function: Get the list of trading days for a specified market
Usage: python get_trading_days.py US --start 2024-01-01 --end 2024-01-31

API Limits:
- Max 60 requests per 30 seconds
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
    TradeDateMarket,
    Market,
)


def get_trading_days(market_str, start=None, end=None, output_json=False):
    ctx = None
    try:
        # TradeDateMarket enum: NONE, HK, US, CN, NT, ST, JP_FUTURE, SG_FUTURE
        # Note: No SH/SZ, A-shares use CN uniformly
        if TradeDateMarket is not None:
            market_map = {
                "HK": TradeDateMarket.HK,
                "US": TradeDateMarket.US,
                "CN": TradeDateMarket.CN,
                "NT": TradeDateMarket.NT,
                "ST": TradeDateMarket.ST,
            }
            for name in ["JP_FUTURE", "SG_FUTURE"]:
                if hasattr(TradeDateMarket, name):
                    market_map[name] = getattr(TradeDateMarket, name)
        else:
            market_map = {
                "HK": Market.HK,
                "US": Market.US,
            }
        market = market_map.get(market_str.upper())
        if market is None:
            raise ValueError(f"Unsupported market: {market_str}, available: {list(market_map.keys())}")

        ctx = create_quote_context()
        kwargs = {"market": market}
        if start:
            kwargs["start"] = start
        if end:
            kwargs["end"] = end

        ret, data = ctx.request_trading_days(**kwargs)
        check_ret(ret, data, ctx, "get trading calendar")

        if is_empty(data):
            if output_json:
                print(json.dumps({"market": market_str, "data": []}))
            else:
                print("No trading day data")
            return

        if output_json:
            # data may be a list or DataFrame
            if hasattr(data, 'iloc'):
                records = df_to_records(data)
            else:
                records = [str(d) for d in data]
            print(json.dumps({"market": market_str, "data": records}, ensure_ascii=False))
        else:
            print("=" * 70)
            print(f"Trading Calendar - {market_str}")
            print("=" * 70)
            if hasattr(data, 'to_string'):
                print(data.to_string(index=False))
            else:
                for d in data:
                    print(f"  {d}")
            print(f"\nTotal {len(data)} trading days")
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
    parser = argparse.ArgumentParser(description="Get trading calendar")
    parser.add_argument("market", choices=["HK", "US", "CN", "NT", "ST", "JP_FUTURE", "SG_FUTURE"], help="Market (HK/US/CN/NT Shenzhen-HK Stock Connect/ST Shanghai-HK Stock Connect)")
    parser.add_argument("--start", default=None, help="Start date yyyy-MM-dd")
    parser.add_argument("--end", default=None, help="End date yyyy-MM-dd")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output in JSON format")
    args = parser.parse_args()
    get_trading_days(args.market, start=args.start, end=args.end, output_json=args.output_json)
