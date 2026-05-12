#!/usr/bin/env python3
"""
Query Maximum Tradable Quantity

Function: Query the maximum buy/sell quantity for a specified stock
Usage: python get_max_trd_qtys.py HK.00700 --price 400

API Limits:
- Max 10 requests per 30 seconds

Parameter Description:
- price: Target price (required), used to calculate tradable quantity
- order_type: Order type, default NORMAL (limit order)
- session: Only for US stocks, supports RTH/ETH/OVERNIGHT/ALL
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
    safe_get,
    safe_float,
    safe_int,
    format_enum,
    OrderType,
    Session,
)

# Order session only for US stocks
ORDER_SESSION_MAP = {
    "NONE": Session.NONE,
    "RTH": Session.RTH,
    "ETH": Session.ETH,
    "OVERNIGHT": Session.OVERNIGHT,
    "ALL": Session.ALL,
}


def get_max_trd_qtys(code, price, acc_id=None, market=None, trd_env=None,
                     security_firm=None, session_str="NONE", output_json=False):
    acc_id = acc_id or get_default_acc_id()
    trd_env = parse_trd_env(trd_env) if trd_env else get_default_trd_env()
    session = ORDER_SESSION_MAP.get(session_str.upper(), Session.NONE)

    ctx = None
    try:
        ctx = create_trade_context(market, security_firm=parse_security_firm(security_firm))
        query_kwargs = dict(
            order_type=OrderType.NORMAL,
            code=code,
            price=price,
            trd_env=trd_env,
            acc_id=acc_id,
        )
        if session != Session.NONE:
            query_kwargs["session"] = session
        ret, data = ctx.acctradinginfo_query(**query_kwargs)
        check_ret(ret, data, ctx, "Query maximum tradable quantity")

        if is_empty(data):
            if output_json:
                print(json.dumps({"data": {}}))
            else:
                print("No data")
            return

        row = data.iloc[0] if hasattr(data, "iloc") else data[0]
        result = {
            "code": code,
            "price": price,
            "max_cash_buy": safe_int(safe_get(row, "max_cash_buy", default=0)),
            "max_cash_and_margin_buy": safe_int(safe_get(row, "max_cash_and_margin_buy", default=0)),
            "max_position_sell": safe_int(safe_get(row, "max_position_sell", default=0)),
        }

        if output_json:
            print(json.dumps({"data": result}, ensure_ascii=False))
        else:
            print("=" * 70)
            print(f"Maximum Tradable Quantity - {code} @ {price}")
            print("=" * 70)
            print(f"  Max Cash Buy: {result['max_cash_buy']}")
            print(f"  Max Margin Buy: {result['max_cash_and_margin_buy']}")
            print(f"  Max Sell: {result['max_position_sell']}")
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
    parser = argparse.ArgumentParser(description="Query maximum tradable quantity")
    parser.add_argument("code", help="Stock code, e.g. HK.00700")
    parser.add_argument("--price", type=float, required=True, help="Target price")
    parser.add_argument("--acc-id", type=int, default=None, help="Account ID")
    parser.add_argument("--market", choices=["US", "HK", "HKCC", "CN", "SG"], default=None, help="Trading market")
    parser.add_argument("--trd-env", choices=["REAL", "SIMULATE"], default=None, help="Trading environment")
    parser.add_argument("--security-firm",
                        choices=["FUTUSECURITIES", "FUTUINC", "FUTUSG", "FUTUAU", "FUTUCA", "FUTUJP", "FUTUMY"],
                        default=None, help="Security firm identifier")
    parser.add_argument("--session", choices=["NONE", "RTH", "ETH", "OVERNIGHT", "ALL"],
                        default="NONE", help="US stock trading session (only for US stocks)")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output in JSON format")
    args = parser.parse_args()
    get_max_trd_qtys(args.code, args.price, acc_id=args.acc_id, market=args.market,
                     trd_env=args.trd_env, security_firm=args.security_firm,
                     session_str=args.session, output_json=args.output_json)
