#!/usr/bin/env python3
"""
Get Order Fee

Function: Query the fee details of specified orders
Usage: python get_order_fee.py 12345678 87654321

API Limits:
- Max 10 requests per 30 seconds
- Max 20 orders per query

Return Field Description:
- order_id: Order ID
- total_fee: Total fee
- fee_list: Fee detail list
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


def get_order_fee(order_ids, acc_id=None, market=None, trd_env=None, security_firm=None, output_json=False):
    acc_id = acc_id or get_default_acc_id()
    trd_env = parse_trd_env(trd_env) if trd_env else get_default_trd_env()

    ctx = None
    try:
        ctx = create_trade_context(market, security_firm=parse_security_firm(security_firm))
        ret, data = ctx.order_fee_query(
            order_id_list=order_ids,
            trd_env=trd_env,
            acc_id=acc_id,
        )
        check_ret(ret, data, ctx, "Get order fee")

        if is_empty(data):
            if output_json:
                print(json.dumps({"data": []}))
            else:
                print("No order fee data")
            return

        if output_json:
            print(json.dumps({"data": df_to_records(data)}, ensure_ascii=False))
        else:
            print("=" * 70)
            print("Order Fee Details")
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
    parser = argparse.ArgumentParser(description="Get order fee")
    parser.add_argument("order_ids", nargs="+", help="Order ID list")
    parser.add_argument("--acc-id", type=int, default=None, help="Account ID")
    parser.add_argument("--market", choices=TRD_MARKET_CLI_CHOICES, default=None, help="Trading market")
    parser.add_argument("--trd-env", choices=["REAL", "SIMULATE"], default=None, help="Trading environment")
    parser.add_argument("--security-firm",
                        choices=["FUTUSECURITIES", "FUTUINC", "FUTUSG", "FUTUAU", "FUTUCA", "FUTUJP", "FUTUMY"],
                        default=None, help="Security firm identifier")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output in JSON format")
    args = parser.parse_args()
    get_order_fee(args.order_ids, acc_id=args.acc_id, market=args.market,
                  trd_env=args.trd_env, security_firm=args.security_firm, output_json=args.output_json)
