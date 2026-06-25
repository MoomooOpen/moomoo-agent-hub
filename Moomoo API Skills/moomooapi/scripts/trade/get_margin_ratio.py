#!/usr/bin/env python3
"""
Get Margin Ratio Data

Function: Query the margin ratio for specified stocks
Usage: python get_margin_ratio.py HK.00700

API Limits:
- Max 10 requests per 30 seconds

Return Field Description:
- im_long_ratio: Initial margin ratio (long)
- im_short_ratio: Initial margin ratio (short)
- mm_long_ratio: Maintenance margin ratio (long)
- mm_short_ratio: Maintenance margin ratio (short)
- is_long_permit: Whether long positions are allowed
- is_short_permit: Whether short positions are allowed
"""
import argparse
import json
import sys
import os as _os
sys.path.insert(0, _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..")))
from common import (
    create_trade_context,
    parse_trd_env,
    TRD_MARKET_CLI_CHOICES,
    parse_security_firm,
    get_default_acc_id,
    get_default_trd_env,
    check_ret,
    safe_close,
    is_empty,
    df_to_records,
)


def get_margin_ratio(codes, acc_id=None, market=None, trd_env=None, security_firm=None, output_json=False):
    acc_id = acc_id or get_default_acc_id()
    trd_env = parse_trd_env(trd_env) if trd_env else get_default_trd_env()

    ctx = None
    try:
        ctx = create_trade_context(market, security_firm=parse_security_firm(security_firm))
        ret, data = ctx.get_margin_ratio(codes)
        check_ret(ret, data, ctx, "Get margin ratio data")

        if is_empty(data):
            if output_json:
                print(json.dumps({"data": []}))
            else:
                print("No margin ratio data")
            return

        if output_json:
            print(json.dumps({"data": df_to_records(data)}, ensure_ascii=False))
        else:
            print("=" * 70)
            print("Margin Ratio Data")
            print("=" * 70)
            print(data.to_string(index=False))
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
    parser = argparse.ArgumentParser(description="Get margin ratio data")
    parser.add_argument("codes", nargs="+", help="Stock codes, e.g. HK.00700")
    parser.add_argument("--acc-id", type=int, default=None, help="Account ID")
    parser.add_argument("--market", choices=TRD_MARKET_CLI_CHOICES, default=None, help="Trading market")
    parser.add_argument("--trd-env", choices=["REAL", "SIMULATE"], default=None, help="Trading environment")
    parser.add_argument("--security-firm",
                        choices=["FUTUSECURITIES", "FUTUINC", "FUTUSG", "FUTUAU", "FUTUCA", "FUTUJP", "FUTUMY"],
                        default=None, help="Security firm identifier")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output in JSON format")
    args = parser.parse_args()
    get_margin_ratio(args.codes, acc_id=args.acc_id, market=args.market,
                     trd_env=args.trd_env, security_firm=args.security_firm, output_json=args.output_json)
