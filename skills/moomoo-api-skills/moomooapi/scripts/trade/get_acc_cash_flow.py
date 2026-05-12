#!/usr/bin/env python3
"""
Get Account Cash Flow

Function: Query the cash inflow/outflow records of an account
Usage: python get_acc_cash_flow.py --start 2024-01-01 --end 2024-01-31

API Limits:
- Max 10 requests per 30 seconds

Return Field Description:
- flow_type: Cash flow type
- amount: Amount
- currency: Currency
- create_time: Creation time
"""
import argparse
import json
import sys
import os as _os
sys.path.insert(0, _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..")))
from common import (
    create_trade_context,
    parse_trd_env,
    parse_security_firm,
    get_default_acc_id,
    get_default_trd_env,
    check_ret,
    safe_close,
    is_empty,
    df_to_records,
)


def get_acc_cash_flow(start=None, end=None, acc_id=None, market=None, trd_env=None, security_firm=None, output_json=False):
    acc_id = acc_id or get_default_acc_id()
    trd_env = parse_trd_env(trd_env) if trd_env else get_default_trd_env()

    ctx = None
    try:
        ctx = create_trade_context(market, security_firm=parse_security_firm(security_firm))
        kwargs = {"trd_env": trd_env, "acc_id": acc_id}
        if start:
            kwargs["start"] = start
        if end:
            kwargs["end"] = end

        ret, data = ctx.get_acc_cash_flow(**kwargs)
        check_ret(ret, data, ctx, "Get cash flow")

        if is_empty(data):
            if output_json:
                print(json.dumps({"data": []}))
            else:
                print("No cash flow records")
            return

        if output_json:
            print(json.dumps({"data": df_to_records(data)}, ensure_ascii=False))
        else:
            print("=" * 70)
            print("Account Cash Flow")
            print("=" * 70)
            print(data.to_string(index=False))
            print(f"\nTotal {len(data)} records")
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
    parser = argparse.ArgumentParser(description="Get account cash flow")
    parser.add_argument("--start", default=None, help="Start date yyyy-MM-dd")
    parser.add_argument("--end", default=None, help="End date yyyy-MM-dd")
    parser.add_argument("--acc-id", type=int, default=None, help="Account ID")
    parser.add_argument("--market", choices=["US", "HK", "HKCC", "CN", "SG"], default=None, help="Trading market")
    parser.add_argument("--trd-env", choices=["REAL", "SIMULATE"], default=None, help="Trading environment")
    parser.add_argument("--security-firm",
                        choices=["FUTUSECURITIES", "FUTUINC", "FUTUSG", "FUTUAU", "FUTUCA", "FUTUJP", "FUTUMY"],
                        default=None, help="Security firm identifier")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output in JSON format")
    args = parser.parse_args()
    get_acc_cash_flow(start=args.start, end=args.end, acc_id=args.acc_id, market=args.market,
                      trd_env=args.trd_env, security_firm=args.security_firm, output_json=args.output_json)
