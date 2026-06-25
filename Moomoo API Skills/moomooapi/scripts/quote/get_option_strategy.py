#!/usr/bin/env python3
"""
Get option strategy

Description: Query combo legs for an option strategy type
Usage: python get_option_strategy.py HK.00700 STRADDLE 2026-05-22
       python get_option_strategy.py HK.00700 SPREAD 2026-05-22 --spread 10.0

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


def get_option_strategy(code, option_strategy, expire_time, spread=None,
                        far_expire_time=None, index_option_type=None,
                        option_type=None, strike_price=None, output_json=False):
    from moomoo import OptionStrategyType, IndexOptionType, OptionType
    ctx = None
    try:
        ctx = create_quote_context()

        strategy_enum = getattr(OptionStrategyType, option_strategy, None)
        if strategy_enum is None:
            raise ValueError(f"Unknown option strategy type: {option_strategy}")

        kwargs = {}
        if spread is not None:
            kwargs["spread"] = spread
        if far_expire_time:
            kwargs["far_expire_time"] = far_expire_time
        if index_option_type:
            kwargs["index_option_type"] = getattr(IndexOptionType, index_option_type, IndexOptionType.NORMAL)
        if option_type:
            kwargs["option_type"] = getattr(OptionType, option_type, OptionType.ALL)
        if strike_price is not None:
            kwargs["strike_price"] = strike_price

        ret, data = ctx.get_option_strategy(code, strategy_enum, expire_time, **kwargs)
        check_ret(ret, data, ctx, "get_option_strategy")

        if is_empty(data):
            if output_json:
                print(json.dumps({"code": code, "data": []}))
            else:
                print("No option strategy data")
            return

        if output_json:
            records = df_to_records(data)
            for r in records:
                if "legs" in r:
                    r["legs"] = [str(leg) for leg in r["legs"]]
            print(json.dumps({"code": code, "data": records}, ensure_ascii=False))
        else:
            print("=" * 70)
            print(f"Option Strategy - {code}  Strategy: {option_strategy}  Expiry: {expire_time}")
            print("=" * 70)
            cols = [c for c in ["code", "name", "option_strategy", "stock_owner", "legs"] if c in data.columns]
            print(data[cols].to_string(index=False))
            print(f"\n{len(data)} record(s)")
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
    parser = argparse.ArgumentParser(description="Get option strategy combo legs")
    parser.add_argument("code", help="Underlying stock code, e.g. HK.00700 or US.AAPL")
    parser.add_argument("option_strategy", help="Option strategy type, e.g. STRADDLE / SPREAD / STRANGLE")
    parser.add_argument("expire_time", help="Expiry date, format yyyy-MM-dd")
    parser.add_argument("--spread", type=float, default=None, help="Spread value (required for vertical/strangle strategies)")
    parser.add_argument("--far-expire-time", default=None, dest="far_expire_time", help="Far expiry date, format yyyy-MM-dd")
    parser.add_argument("--index-option-type", default=None, dest="index_option_type", help="Index option type, e.g. NORMAL")
    parser.add_argument("--option-type", default=None, dest="option_type", help="Call/put filter, e.g. CALL / PUT / ALL")
    parser.add_argument("--strike-price", type=float, default=None, dest="strike_price", help="Strike price")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output JSON format")
    args = parser.parse_args()
    get_option_strategy(
        args.code, args.option_strategy, args.expire_time,
        spread=args.spread, far_expire_time=args.far_expire_time,
        index_option_type=args.index_option_type, option_type=args.option_type,
        strike_price=args.strike_price, output_json=args.output_json,
    )
