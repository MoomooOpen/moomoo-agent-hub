#!/usr/bin/env python3
"""
Get option strategy valid spreads

Description: Get the list of valid spreads for a given option strategy, underlying, and expiry
Usage: python get_option_strategy_spread.py HK.00700 STRANGLE 2026-05-22

Rate limit:
- Max 30 requests per 30 seconds
- option_strategy only supports: SPREAD / STRANGLE / COLLAR / BUTTERFLY / CONDOR / IRON_BUTTERFLY / IRON_CONDOR / DIAGONAL_SPREAD
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


def get_option_strategy_spread(code, option_strategy, expire_time,
                                far_expire_time=None, index_option_type=None,
                                output_json=False):
    from moomoo import OptionStrategyType, IndexOptionType
    ctx = None
    try:
        ctx = create_quote_context()

        strategy_enum = getattr(OptionStrategyType, option_strategy, None)
        if strategy_enum is None:
            raise ValueError(f"Unknown option strategy type: {option_strategy}")

        kwargs = {}
        if far_expire_time:
            kwargs["far_expire_time"] = far_expire_time
        if index_option_type:
            kwargs["index_option_type"] = getattr(IndexOptionType, index_option_type, IndexOptionType.NORMAL)

        ret, data = ctx.get_option_strategy_spread(code, strategy_enum, expire_time, **kwargs)
        check_ret(ret, data, ctx, "get_option_strategy_spread")

        if is_empty(data):
            if output_json:
                print(json.dumps({"code": code, "data": []}))
            else:
                print("No valid spread data")
            return

        if output_json:
            print(json.dumps({"code": code, "data": df_to_records(data)}, ensure_ascii=False))
        else:
            print("=" * 70)
            print(f"Valid Spreads - {code}  Strategy: {option_strategy}  Expiry: {expire_time}")
            print("=" * 70)
            print(data.to_string(index=False))
            print(f"\n{len(data)} spread(s)")
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
    parser = argparse.ArgumentParser(description="Get valid spread list for an option strategy")
    parser.add_argument("code", help="Underlying stock code, e.g. HK.00700 or US.AAPL")
    parser.add_argument("option_strategy", help="Option strategy type, e.g. STRANGLE / SPREAD / BUTTERFLY")
    parser.add_argument("expire_time", help="Expiry date, format yyyy-MM-dd")
    parser.add_argument("--far-expire-time", default=None, dest="far_expire_time", help="Far expiry date, format yyyy-MM-dd")
    parser.add_argument("--index-option-type", default=None, dest="index_option_type", help="Index option type, e.g. NORMAL")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output JSON format")
    args = parser.parse_args()
    get_option_strategy_spread(
        args.code, args.option_strategy, args.expire_time,
        far_expire_time=args.far_expire_time,
        index_option_type=args.index_option_type,
        output_json=args.output_json,
    )
