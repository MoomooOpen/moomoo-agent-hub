#!/usr/bin/env python3
"""
Option strategy P&L analysis

Description: Analyze profit/loss for a custom or multi-leg option combo; returns combo-level bid1/ask1 (order book price), max profit/loss, breakeven points, etc.
Usage: python get_option_strategy_analysis.py '[{"code":"HK.TCH260522P330000","action":"BUY","quantity":1.0},{"code":"HK.TCH260522C330000","action":"BUY","quantity":1.0}]'

Agent guidance:
- Use this script first for combo bid/ask (bid1/ask1) and for pricing place_combo_order / comboorder_tradinginfo_query
- Do NOT call get_snapshot per leg and manually net bid/ask

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
    from moomoo import OptionStrategyLeg
    items = json.loads(legs_json)
    legs = []
    for item in items:
        leg = OptionStrategyLeg()
        leg.code = item["code"]
        leg.action = item.get("action", "BUY")
        leg.quantity = float(item.get("quantity", 1.0))
        legs.append(leg)
    return legs


def get_option_strategy_analysis(legs_json, output_json=False):
    ctx = None
    try:
        legs = parse_legs(legs_json)
        ctx = create_quote_context()
        ret, data = ctx.get_option_strategy_analysis(legs)
        check_ret(ret, data, ctx, "get_option_strategy_analysis")

        if is_empty(data):
            if output_json:
                print(json.dumps({"data": []}))
            else:
                print("No P&L analysis data")
            return

        if output_json:
            print(json.dumps({"data": df_to_records(data)}, ensure_ascii=False))
        else:
            print("=" * 70)
            print("Option Strategy P&L Analysis")
            print("=" * 70)
            cols = [c for c in [
                "code", "name", "option_strategy",
                "bid1", "ask1", "max_profit", "max_loss",
                "breakeven_points", "prob_of_profit", "delta", "theta",
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
    parser = argparse.ArgumentParser(description="Option strategy P&L analysis")
    parser.add_argument(
        "legs",
        help='Combo legs JSON, e.g. \'[{"code":"HK.TCH260522P330000","action":"BUY","quantity":1.0}]\''
    )
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output JSON format")
    args = parser.parse_args()
    get_option_strategy_analysis(args.legs, output_json=args.output_json)
