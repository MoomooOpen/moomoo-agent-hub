#!/usr/bin/env python3
"""
Get History Order Fill List

Function: Query the historical deal records of an account
Usage: python get_history_order_fill_list.py --start 2024-01-01 --end 2024-01-31

API Limits:
- Max 10 requests per 30 seconds

Parameter Description:
- start/end: Format YYYY-MM-DD HH:MM:SS or YYYY-MM-DD

Return Field Description:
- deal_id: Deal ID
- order_id: Corresponding order ID
- code: Stock code
- trd_side: Trade direction
- price: Deal price
- qty: Deal quantity
- create_time: Deal time
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
    df_to_records,
    format_enum,
)


def get_history_order_fill_list(start=None, end=None, acc_id=None, market=None, trd_env=None,
                                security_firm=None, output_json=False):
    acc_id = acc_id or get_default_acc_id()
    trd_market = parse_market(market) if market else get_default_market()
    trd_env = parse_trd_env(trd_env) if trd_env else get_default_trd_env()

    ctx = None
    try:
        ctx = create_trade_context(trd_market, security_firm=parse_security_firm(security_firm))
        kwargs = {"trd_env": trd_env, "acc_id": acc_id}
        if start:
            kwargs["start"] = start
        if end:
            kwargs["end"] = end

        ret, data = ctx.history_deal_list_query(**kwargs)
        check_ret(ret, data, ctx, "Query history deals")

        if is_empty(data):
            if output_json:
                print(json.dumps({"deals": []}))
            else:
                print("=" * 70)
                print(f"History Deals - Market: {format_enum(trd_market)}")
                print("=" * 70)
                print("\n  No history deal records")
                print("=" * 70)
            return

        no_date_filter = not start and not end
        if output_json:
            result = {"market": format_enum(trd_market), "deals": df_to_records(data)}
            if no_date_filter:
                result["note"] = "Default query returns last 90 days only. Specify --start/--end for older records."
            print(json.dumps(result, ensure_ascii=False))
        else:
            print("=" * 70)
            print(f"History Deals - Market: {format_enum(trd_market)}")
            if no_date_filter:
                print("Note: Default query returns last 90 days only. Specify --start/--end for older records.")
            print("=" * 70)
            print(data.to_string(index=False))
            print(f"\nTotal {len(data)} deals")
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
    parser = argparse.ArgumentParser(description="Get history order fill list")
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
    get_history_order_fill_list(start=args.start, end=args.end, acc_id=args.acc_id, market=args.market,
                                trd_env=args.trd_env, security_firm=args.security_firm, output_json=args.output_json)
