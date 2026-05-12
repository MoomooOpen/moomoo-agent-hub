#!/usr/bin/env python3
"""
Resolve Option Shorthand Code and Match Moomoo Option Code from Option Chain

Function: Parse user input option description and look up the corresponding Moomoo option code via option chain API
Usage: python resolve_option_code.py --underlying US.JPM --expiry 2026-03-20 --strike 267.50 --type CALL [--json]

Note: The underlying stock code must include the market prefix (e.g. US.JPM, HK.00700), determined by the caller based on context.

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
    safe_float,
    df_to_records,
)


def resolve_option_code(underlying, expiry, strike, option_type, output_json=False):
    """
    Look up matching option contract code via option chain API

    Args:
        underlying: Underlying stock code, must include market prefix (e.g. US.JPM, HK.00700)
        expiry: Expiry date (e.g. 2026-03-20)
        strike: Strike price (e.g. 267.50)
        option_type: CALL or PUT
        output_json: Whether to output JSON
    """
    if '.' not in underlying:
        msg = f"Underlying code '{underlying}' is missing market prefix, please use full format like US.{underlying.upper()} or HK.{underlying}"
        if output_json:
            print(json.dumps({"error": msg}, ensure_ascii=False))
        else:
            print(f"Error: {msg}")
        sys.exit(1)

    ctx = None
    try:
        ctx = create_quote_context()

        # Use expiry date as the time filter range for option chain
        ret, data = ctx.get_option_chain(underlying, start=expiry, end=expiry)
        check_ret(ret, data, ctx, "get option chain")

        if is_empty(data):
            msg = f"No option chain data found for {underlying} on {expiry}"
            if output_json:
                print(json.dumps({"error": msg, "underlying": underlying,
                                  "expiry": expiry, "strike": strike,
                                  "option_type": option_type}, ensure_ascii=False))
            else:
                print(f"Error: {msg}")
            sys.exit(1)

        # Match in option chain: strike price + option type (CALL/PUT)
        matched = []
        for i in range(len(data)):
            row = data.iloc[i] if hasattr(data, "iloc") else data[i]

            row_strike = safe_float(row.get("strike_price", 0))
            row_type = str(row.get("option_type", "")).upper()
            row_code = str(row.get("code", ""))
            row_name = str(row.get("name", ""))
            row_strike_time = str(row.get("strike_time", ""))
            row_last_price = safe_float(row.get("last_price", 0))

            # Match option type
            type_match = False
            if option_type == "CALL" and row_type in ("CALL", "涨", "认购"):
                type_match = True
            elif option_type == "PUT" and row_type in ("PUT", "跌", "认沽"):
                type_match = True

            # Match strike price (float comparison, tolerance 0.001)
            strike_match = abs(row_strike - strike) < 0.001

            if type_match and strike_match:
                matched.append({
                    "code": row_code,
                    "name": row_name,
                    "strike_price": row_strike,
                    "strike_time": row_strike_time,
                    "option_type": row_type,
                    "last_price": row_last_price,
                })

        if not matched:
            msg = (f"No matching contract found in {underlying} option chain\n"
                   f"  Expiry: {expiry}, Strike: {strike}, Type: {option_type}")
            if output_json:
                print(json.dumps({
                    "error": msg,
                    "underlying": underlying,
                    "expiry": expiry,
                    "strike": strike,
                    "option_type": option_type,
                    "available_count": len(data),
                }, ensure_ascii=False))
            else:
                print(f"Error: {msg}")
                # Print the closest contracts to help user verify
                _print_nearby(data, strike, option_type)
            sys.exit(1)

        if output_json:
            print(json.dumps({
                "underlying": underlying,
                "expiry": expiry,
                "strike": strike,
                "option_type": option_type,
                "matched": matched,
            }, ensure_ascii=False))
        else:
            print("=" * 70)
            print(f"Option Code Resolution Result")
            print("=" * 70)
            print(f"  Underlying:  {underlying}")
            print(f"  Expiry:      {expiry}")
            print(f"  Strike:      {strike}")
            print(f"  Type:        {option_type}")
            print("-" * 70)
            for m in matched:
                print(f"  Option Code: {m['code']}")
                print(f"  Name:        {m['name']}")
                print(f"  Last Price:  {m['last_price']}")
                print()
            print("=" * 70)

        return matched

    except SystemExit:
        raise
    except Exception as e:
        if output_json:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))
        else:
            print(f"Error: {e}")
        sys.exit(1)
    finally:
        safe_close(ctx)


def _print_nearby(data, strike, option_type, count=5):
    """When matching fails, print contracts with closest strike prices to help user verify"""
    candidates = []
    for i in range(len(data)):
        row = data.iloc[i] if hasattr(data, "iloc") else data[i]
        row_type = str(row.get("option_type", "")).upper()
        type_match = False
        if option_type == "CALL" and row_type in ("CALL", "涨", "认购"):
            type_match = True
        elif option_type == "PUT" and row_type in ("PUT", "跌", "认沽"):
            type_match = True
        if type_match:
            row_strike = safe_float(row.get("strike_price", 0))
            candidates.append({
                "code": str(row.get("code", "")),
                "strike_price": row_strike,
                "diff": abs(row_strike - strike),
            })

    if candidates:
        candidates.sort(key=lambda x: x["diff"])
        print(f"\nClosest {option_type} contracts:")
        for c in candidates[:count]:
            print(f"  {c['code']}  Strike: {c['strike_price']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Look up Moomoo option code via option chain",
        epilog="Example: python resolve_option_code.py --underlying US.JPM --expiry 2026-03-20 --strike 267.50 --type CALL",
    )
    parser.add_argument("--underlying", required=True,
                        help="Underlying stock code, must include market prefix (e.g. US.JPM, HK.00700)")
    parser.add_argument("--expiry", required=True,
                        help="Expiry date yyyy-MM-dd")
    parser.add_argument("--strike", type=float, required=True,
                        help="Strike price")
    parser.add_argument("--type", dest="option_type", required=True,
                        choices=["CALL", "PUT"],
                        help="Option type")
    parser.add_argument("--json", action="store_true", dest="output_json",
                        help="Output in JSON format")

    args = parser.parse_args()
    resolve_option_code(args.underlying, args.expiry, args.strike, args.option_type, args.output_json)
