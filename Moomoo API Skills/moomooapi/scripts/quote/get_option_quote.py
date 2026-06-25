#!/usr/bin/env python3
"""
Get option quote

Description: Get real-time option snapshot for combo legs (last price, Greeks, etc.; no combo-level bid1/ask1)
Usage: python get_option_quote.py '[{"code":"HK.TCH260522P330000","action":"BUY","quantity":1.0},{"code":"HK.TCH260522C330000","action":"BUY","quantity":1.0}]'

Note: For combo order book price (bid1/ask1), use get_option_strategy_analysis.py instead

Rate limit:
- Max 30 requests per 30 seconds
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
)


def parse_legs(legs_json):
    from moomoo import OptionStrategyLeg, StrategyLegAction
    items = json.loads(legs_json)
    legs = []
    for item in items:
        leg = OptionStrategyLeg()
        leg.code = item["code"]
        leg.action = item.get("action", "BUY")
        leg.quantity = float(item.get("quantity", 1.0))
        legs.append(leg)
    return legs


def get_option_quote(legs_json, output_json=False):
    ctx = None
    try:
        legs = parse_legs(legs_json)
        ctx = create_quote_context()
        ret, data = ctx.get_option_quote(legs)
        check_ret(ret, data, ctx, "get_option_quote")

        if is_empty(data):
            if output_json:
                print(json.dumps({"data": []}))
            else:
                print("No option quote data")
            return

        if output_json:
            print(json.dumps({"data": df_to_records(data)}, ensure_ascii=False))
        else:
            print("=" * 70)
            print("Option Quote")
            print("=" * 70)
            cols = [c for c in [
                "price", "change_val", "change_rate", "volume", "turnover",
                "high_price", "low_price", "option_type", "strike_price",
                "expire_time", "delta", "gamma", "vega", "theta", "rho",
                "implied_volatility", "open_interest", "prob_of_profit",
                "max_profit", "max_loss",
            ] if c in data.columns]
            print(data[cols].to_string(index=False))
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
    parser = argparse.ArgumentParser(description="Get real-time option snapshot")
    parser.add_argument(
        "legs",
        help='Combo legs JSON, e.g. \'[{"code":"HK.TCH260522P330000","action":"BUY","quantity":1.0}]\''
    )
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output JSON format")
    args = parser.parse_args()
    get_option_quote(args.legs, output_json=args.output_json)
