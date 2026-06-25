#!/usr/bin/env python3
"""
Query Crypto Order Fee

Function: Query fee details for specified crypto orders (real trading only)
Usage: python get_crypto_order_fee.py 12345678 87654321 --security-firm FUTUINC --acc-id 12345

API Limits:
- Max 10 requests per 30 seconds
- Max 20 orders per query

Parameter Description:
- order_ids: order ID list (positional, 1-20 entries)
- Crypto fee query is built on OpenCryptoTradeContext; real trading only (TrdEnv.REAL)
- security_firm only supports FUTUSECURITIES / FUTUINC / FUTUSG

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
    create_crypto_trade_context,
    parse_security_firm,
    get_default_acc_id,
    check_ret,
    safe_close,
    is_empty,
    df_to_records,
    TrdEnv,
)


def get_crypto_order_fee(order_ids, acc_id=None, security_firm=None, output_json=False):
    acc_id = acc_id or get_default_acc_id()
    firm_enum = parse_security_firm(security_firm)

    if len(order_ids) > 20:
        msg = f"At most 20 orders per query; received {len(order_ids)}"
        if output_json:
            print(json.dumps({"error": msg}, ensure_ascii=False))
        else:
            print(f"Error: {msg}")
        sys.exit(1)

    ctx = None
    try:
        ctx = create_crypto_trade_context(security_firm=firm_enum)
        ret, data = ctx.order_fee_query(
            order_id_list=list(order_ids),
            trd_env=TrdEnv.REAL,
            acc_id=acc_id,
        )
        check_ret(ret, data, ctx, "Query crypto order fee")

        if is_empty(data):
            if output_json:
                print(json.dumps({"data": []}, ensure_ascii=False))
            else:
                print("No order fee data")
            return

        if output_json:
            print(json.dumps({"data": df_to_records(data)}, ensure_ascii=False))
        else:
            print("=" * 70)
            print("Crypto Order Fee Details")
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
    parser = argparse.ArgumentParser(description="Query crypto order fee (real trading only)")
    parser.add_argument("order_ids", nargs="+", help="Order ID list (max 20)")
    parser.add_argument("--acc-id", type=int, default=None, help="Crypto account ID")
    parser.add_argument("--security-firm",
                        choices=["FUTUSECURITIES", "FUTUINC", "FUTUSG"],
                        default=None, help="Security firm (only FUTUSECURITIES/FUTUINC/FUTUSG)")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output in JSON format")
    args = parser.parse_args()
    get_crypto_order_fee(args.order_ids, acc_id=args.acc_id,
                         security_firm=args.security_firm, output_json=args.output_json)
