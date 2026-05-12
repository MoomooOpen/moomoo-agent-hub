#!/usr/bin/env python3
"""
Get Order List

Function: Query today's orders for the current account
Usage: python get_orders.py --market HK --trd-env SIMULATE

API Limits:
- Max 10 requests per 30 seconds per account ID (only when refreshing cache)

Parameter Description:
- refresh_cache: True to request from server immediately (subject to rate limit), False to use OpenD cache
- start/end: Format YYYY-MM-DD HH:MM:SS or YYYY-MM-DD HH:MM:SS.MS

Return Field Description:
- qty/dealt_qty: Unit is "contracts" for options and futures
- price: Rounded to 3 decimal places
- dealt_avg_price: No precision limit
- create_time/updated_time: Format yyyy-MM-dd HH:mm:ss
"""
import argparse
import json
import sys
import os as _os
sys.path.insert(0, _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..")))
from common import (
    create_trade_context,
    parse_trd_env,
    parse_market,
    parse_security_firm,
    get_default_acc_id,
    get_default_trd_env,
    get_default_market,
    check_ret,
    safe_close,
    is_empty,
    format_enum,
    safe_get,
    safe_float,
)


def get_orders(acc_id=None, market=None, trd_env=None, security_firm=None, output_json=False):
    acc_id = acc_id or get_default_acc_id()
    trd_market = parse_market(market) if market else get_default_market()
    trd_env = parse_trd_env(trd_env) if trd_env else get_default_trd_env()

    ctx = None
    try:
        ctx = create_trade_context(trd_market, security_firm=parse_security_firm(security_firm))
        ret, data = ctx.order_list_query(trd_env=trd_env, acc_id=acc_id, refresh_cache=True)
        check_ret(ret, data, ctx, "Query orders")

        if is_empty(data):
            if output_json:
                print(json.dumps({"orders": []}))
            else:
                print("=" * 70)
                print(f"Order List - Market: {format_enum(trd_market)}")
                print("=" * 70)
                print("\n  No orders")
                print("=" * 70)
            return

        orders = []
        for i in range(len(data)):
            row = data.iloc[i] if hasattr(data, "iloc") else data[i]
            orders.append({
                "order_id": str(safe_get(row, "order_id", "orderID", default="N/A")),
                "code": safe_get(row, "code", default="N/A"),
                "side": format_enum(safe_get(row, "trd_side", "side", default="N/A")),
                "status": format_enum(safe_get(row, "order_status", "status", default="N/A")),
                "qty": safe_float(safe_get(row, "qty", "quantity", default=0)),
                "price": safe_float(safe_get(row, "price", default=0)),
                "dealt_qty": safe_float(safe_get(row, "dealt_qty", default=0)),
                "dealt_avg_price": safe_float(safe_get(row, "dealt_avg_price", default=0)),
            })

        if output_json:
            print(json.dumps({"market": format_enum(trd_market), "orders": orders}, ensure_ascii=False))
        else:
            print("=" * 70)
            print(f"Order List - Market: {format_enum(trd_market)}")
            print("=" * 70)
            for o in orders:
                print(f"\n  Order ID: {o['order_id']}")
                print(f"    Code: {o['code']}  Side: {o['side']}  Status: {o['status']}")
                print(f"    Ordered: {o['qty']} shares @ {o['price']}  Dealt: {o['dealt_qty']} shares @ {o['dealt_avg_price']}")
                print("  " + "-" * 66)
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
    parser = argparse.ArgumentParser(description="Get today's order list")
    parser.add_argument("--acc-id", type=int, default=None, help="Account ID")
    parser.add_argument("--market", choices=["US", "HK", "HKCC", "CN", "SG"], default=None, help="Trading market")
    parser.add_argument("--trd-env", choices=["REAL", "SIMULATE"], default=None, help="Trading environment")
    parser.add_argument("--security-firm",
                        choices=["FUTUSECURITIES", "FUTUINC", "FUTUSG", "FUTUAU", "FUTUCA", "FUTUJP", "FUTUMY"],
                        default=None, help="Security firm identifier")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output in JSON format")
    args = parser.parse_args()
    get_orders(acc_id=args.acc_id, market=args.market, trd_env=args.trd_env,
               security_firm=args.security_firm, output_json=args.output_json)
