#!/usr/bin/env python3
"""
Get History Orders

Function: Query the historical order records of an account
Usage: python get_history_orders.py --market HK --start 2026-01-01 --end 2026-03-01

API Limits:
- Max 10 requests per 30 seconds per account ID

Parameter Description:
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


def get_history_orders(acc_id=None, market=None, trd_env=None, code=None,
                       start=None, end=None, status_list=None, limit=200,
                       security_firm=None, output_json=False):
    acc_id = acc_id or get_default_acc_id()
    trd_env = parse_trd_env(trd_env) if trd_env else get_default_trd_env()

    ctx = None
    try:
        ctx = create_trade_context(market, security_firm=parse_security_firm(security_firm))
        kwargs = {"trd_env": trd_env, "acc_id": acc_id}
        if code:
            kwargs["code"] = code
        if start:
            kwargs["start"] = start
        if end:
            kwargs["end"] = end
        if status_list:
            from moomoo import OrderStatus
            status_filter = []
            for s in status_list:
                if hasattr(OrderStatus, s.upper()):
                    status_filter.append(getattr(OrderStatus, s.upper()))
            if status_filter:
                kwargs["status_filter_list"] = status_filter

        ret, data = ctx.history_order_list_query(**kwargs)
        check_ret(ret, data, ctx, "Query history orders")

        if is_empty(data):
            if output_json:
                print(json.dumps({"orders": []}))
            else:
                print("No history orders")
            return

        orders = []
        n = min(len(data), limit)
        for i in range(n):
            row = data.iloc[i] if hasattr(data, "iloc") else data[i]
            orders.append({
                "order_id": str(safe_get(row, "order_id", default="N/A")),
                "code": safe_get(row, "code", default="N/A"),
                "side": format_enum(safe_get(row, "trd_side", default="")),
                "status": format_enum(safe_get(row, "order_status", default="")),
                "qty": safe_float(safe_get(row, "qty", default=0)),
                "price": safe_float(safe_get(row, "price", default=0)),
                "dealt_qty": safe_float(safe_get(row, "dealt_qty", default=0)),
                "create_time": safe_get(row, "create_time", default=""),
                "updated_time": safe_get(row, "updated_time", default=""),
            })

        no_date_filter = not start and not end
        if output_json:
            result = {"count": len(orders), "orders": orders}
            if no_date_filter:
                result["note"] = "Default query returns last 90 days only. Specify --start/--end for older orders."
            print(json.dumps(result, ensure_ascii=False))
        else:
            print("=" * 80)
            print(f"History Orders (Total {len(orders)})")
            if no_date_filter:
                print("Note: Default query returns last 90 days only. Specify --start/--end for older orders.")
            print("=" * 80)
            for o in orders:
                print(f"  [{o['create_time']}] {o['order_id']}  {o['code']}  {o['side']}  "
                      f"{o['qty']} shares@{o['price']}  Dealt:{o['dealt_qty']}  {o['status']}")
            print("=" * 80)

    except Exception as e:
        if output_json:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))
        else:
            print(f"Error: {e}")
        sys.exit(1)
    finally:
        safe_close(ctx)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get history orders")
    parser.add_argument("--acc-id", type=int, default=None, help="Account ID")
    parser.add_argument("--market", choices=["US", "HK", "HKCC", "CN", "SG"], default=None, help="Trading market")
    parser.add_argument("--trd-env", choices=["REAL", "SIMULATE"], default=None, help="Trading environment")
    parser.add_argument("--code", default=None, help="Stock code filter")
    parser.add_argument("--start", default=None, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", default=None, help="End date (YYYY-MM-DD)")
    parser.add_argument("--status", nargs="+", default=None, help="Order status filter (e.g. FILLED_ALL CANCELLED_ALL)")
    parser.add_argument("--limit", type=int, default=200, help="Return count limit")
    parser.add_argument("--security-firm",
                        choices=["FUTUSECURITIES", "FUTUINC", "FUTUSG", "FUTUAU", "FUTUCA", "FUTUJP", "FUTUMY"],
                        default=None, help="Security firm identifier")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output in JSON format")
    args = parser.parse_args()
    get_history_orders(acc_id=args.acc_id, market=args.market, trd_env=args.trd_env,
                       code=args.code, start=args.start, end=args.end,
                       status_list=args.status, limit=args.limit,
                       security_firm=args.security_firm, output_json=args.output_json)
