#!/usr/bin/env python3
"""
Query Maximum Tradable Quantity for Crypto

Function: Query the maximum buy/sell quantity for a specified crypto pair
         (cash account only, real trading only)
Usage: python get_crypto_max_trd_qtys.py --code CC.BTCUSD --price 72873.22

Notes:
- Crypto only supports cash accounts; no margin buying power (no max_cash_and_margin_buy)
- Real trading only (TrdEnv.REAL); simulation is not supported
- code must be a trading pair (CC.BTCUSD / CC.ETHUSD / CC.BTCHKD), not CC.BTC
- Security firm only supports FUTUSECURITIES / FUTUINC / FUTUSG
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
    is_crypto_code,
    check_ret,
    safe_close,
    is_empty,
    safe_get,
    safe_float,
    OrderType,
    TrdEnv,
)


def get_crypto_max_trd_qtys(code, price, acc_id=None, security_firm=None, output_json=False):
    acc_id = acc_id or get_default_acc_id()

    if not is_crypto_code(code):
        msg = f"Crypto max tradable quantity code must start with CC. (e.g. CC.BTCUSD), got: {code}"
        if output_json:
            print(json.dumps({"error": msg}, ensure_ascii=False))
        else:
            print(f"Error: {msg}")
        sys.exit(1)

    base = code.split(".", 1)[1] if "." in code else ""
    if len(base) < 6:
        msg = f"Crypto max tradable quantity requires a trading pair code (e.g. CC.BTCUSD), got base currency: {code}"
        if output_json:
            print(json.dumps({"error": msg}, ensure_ascii=False))
        else:
            print(f"Error: {msg}")
        sys.exit(1)

    firm_enum = parse_security_firm(security_firm)

    ctx = None
    try:
        ctx = create_crypto_trade_context(security_firm=firm_enum)
        ret, data = ctx.acctradinginfo_query(
            order_type=OrderType.NORMAL,
            code=code,
            price=price,
            trd_env=TrdEnv.REAL,
            acc_id=acc_id,
        )
        check_ret(ret, data, ctx, "Query crypto max tradable quantity")

        if is_empty(data):
            if output_json:
                print(json.dumps({"data": {}}, ensure_ascii=False))
            else:
                print("No data")
            return

        row = data.iloc[0] if hasattr(data, "iloc") else data[0]
        result = {
            "code": code,
            "price": price,
            "acc_id": acc_id,
            "max_cash_buy": safe_float(safe_get(row, "max_cash_buy", default=0)),
            "max_position_sell": safe_float(safe_get(row, "max_position_sell", default=0)),
        }

        if output_json:
            print(json.dumps({"data": result}, ensure_ascii=False))
        else:
            print("=" * 70)
            print(f"Crypto Max Tradable Quantity - {code} @ {price}")
            print("=" * 70)
            print(f"  Account:        {acc_id}")
            print(f"  Max Cash Buy:   {result['max_cash_buy']}")
            print(f"  Max Sell:       {result['max_position_sell']}")
            print("  Note: Crypto only supports cash accounts; no margin buying power")
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
    parser = argparse.ArgumentParser(description="Query crypto maximum tradable quantity (cash account only)")
    parser.add_argument("--code", required=True, help="Crypto trading pair code (e.g. CC.BTCUSD)")
    parser.add_argument("--price", type=float, required=True, help="Target price")
    parser.add_argument("--acc-id", type=int, default=None, help="Crypto account ID")
    parser.add_argument("--security-firm",
                        choices=["FUTUSECURITIES", "FUTUINC", "FUTUSG"],
                        default=None, help="Security firm (only FUTUSECURITIES/FUTUINC/FUTUSG)")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output in JSON format")
    args = parser.parse_args()
    get_crypto_max_trd_qtys(code=args.code, price=args.price, acc_id=args.acc_id,
                            security_firm=args.security_firm, output_json=args.output_json)
