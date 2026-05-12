#!/usr/bin/env python3
"""
Get Positions and Funds

Function: Query account fund status and position list
Usage: python get_portfolio.py --market HK --trd-env SIMULATE

API Limits:
- Max 10 requests per 30 seconds per account ID (only when refreshing cache)

Parameter Description:
- currency: Only applicable to futures accounts and consolidated securities accounts; other account types ignore this parameter; returned fund fields will be converted to this currency
- refresh_cache: True to request from server immediately (subject to rate limit), False to use OpenD cache

Return Field Description:
- power (buying power): Approximate value calculated at 50% initial margin ratio; use get_max_trd_qtys for precise values
- total_assets: Total net asset value = securities net value + fund net value + bond net value
- market_val: Only applicable to securities accounts
- avl_withdrawal_cash: Only applicable to securities accounts
- currency: Only applicable to consolidated securities accounts and futures accounts
- pl_ratio_avg_cost (P/L ratio by average cost): Percentage field, 20 means 20%, not applicable to futures
- average_cost: Average cost price (consistent with APP); do not use cost_price (diluted cost)
- unrealized_pl: Unrealized P/L (average cost basis); do not use pl_val (diluted cost basis)
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
    format_enum,
)


def get_portfolio(acc_id=None, market=None, trd_env=None, currency=None, security_firm=None, output_json=False):
    acc_id = acc_id or get_default_acc_id()
    trd_env = parse_trd_env(trd_env) if trd_env else get_default_trd_env()

    ctx = None
    try:
        ctx = create_trade_context(market, security_firm=parse_security_firm(security_firm))
        # Query funds (refresh_cache=True to avoid stale data, especially for paper trading)
        query_kwargs = dict(trd_env=trd_env, acc_id=acc_id, refresh_cache=True)
        if currency:
            query_kwargs["currency"] = currency
        ret, acc_data = ctx.accinfo_query(**query_kwargs)
        check_ret(ret, acc_data, ctx, "Query account funds")

        funds = {}
        if not is_empty(acc_data):
            row = acc_data.iloc[0] if hasattr(acc_data, "iloc") else acc_data
            total_assets = safe_float(safe_get(row, "total_assets", default=0))
            initial_margin = safe_float(safe_get(row, "initial_margin", default=0))
            available_funds_raw = safe_get(row, "available_funds", default="N/A")
            available_funds = safe_float(available_funds_raw)
            # available_funds returns N/A for some account types, fallback to total_assets - initial_margin
            # Only fall back when the raw value is 'N/A' or missing, to avoid misidentifying a real 0 as missing
            if str(available_funds_raw) == "N/A" or available_funds_raw in (None, ""):
                available_funds = total_assets - initial_margin if initial_margin > 0 else total_assets
            funds = {
                "currency": safe_get(row, "currency", default="N/A"),
                "total_assets": total_assets,
                "cash": safe_float(safe_get(row, "cash", default=0)),
                "market_val": safe_float(safe_get(row, "market_val", default=0)),
                "long_mv": safe_float(safe_get(row, "long_mv", default=0)),
                "short_mv": safe_float(safe_get(row, "short_mv", default=0)),
                "frozen_cash": safe_float(safe_get(row, "frozen_cash", default=0)),
                "avl_withdrawal_cash": safe_float(safe_get(row, "avl_withdrawal_cash", default=0)),
                "power": safe_float(safe_get(row, "power", "buying_power", default=0)),
                "available_funds": available_funds,
                "initial_margin": initial_margin,
                "maintenance_margin": safe_float(safe_get(row, "maintenance_margin", default=0)),
                "risk_status": safe_get(row, "risk_status", default="N/A"),
                "us_cash": safe_float(safe_get(row, "us_cash", default=0)),
                "ca_cash": safe_float(safe_get(row, "ca_cash", default=0)),
            }

        # Query positions (refresh_cache=True to avoid stale data)
        ret, pos_data = ctx.position_list_query(trd_env=trd_env, acc_id=acc_id, refresh_cache=True)
        check_ret(ret, pos_data, ctx, "Query positions")

        positions = []
        if not is_empty(pos_data):
            for i in range(len(pos_data)):
                row = pos_data.iloc[i] if hasattr(pos_data, "iloc") else pos_data[i]
                positions.append({
                    "code": safe_get(row, "code", default=""),
                    "name": safe_get(row, "stock_name", default=""),
                    "qty": safe_float(safe_get(row, "qty", default=0)),
                    "can_sell_qty": safe_float(safe_get(row, "can_sell_qty", default=0)),
                    "average_cost": safe_float(safe_get(row, "average_cost", default=0)),
                    "nominal_price": safe_float(safe_get(row, "nominal_price", default=0)),
                    "market_val": safe_float(safe_get(row, "market_val", default=0)),
                    "unrealized_pl": safe_float(safe_get(row, "unrealized_pl", default=0)),
                    "pl_ratio_avg_cost": safe_float(safe_get(row, "pl_ratio_avg_cost", default=0)),
                    "realized_pl": safe_float(safe_get(row, "realized_pl", default=0)),
                    "today_pl_val": safe_float(safe_get(row, "today_pl_val", default=0)),
                })

        if output_json:
            print(json.dumps({"funds": funds, "positions": positions}, ensure_ascii=False))
        else:
            print("=" * 70)
            ccy_label = f"  Currency: {funds.get('currency', 'N/A')}" if funds else ""
            print(f"Account Overview (Environment: {format_enum(trd_env)}){ccy_label}")
            print("=" * 70)
            if funds:
                print(f"\n  Total Assets: {funds['total_assets']:.2f}  Cash: {funds['cash']:.2f}  Buying Power: {funds['power']:.2f}")
                print(f"  Position Value: {funds['market_val']:.2f}  Available Funds: {funds['available_funds']:.2f}  Frozen: {funds['frozen_cash']:.2f}")
            print(f"\n  {'Position List':=^66}")
            if positions:
                print(f"  {'Code':<12} {'Name':<10} {'Qty':>8} {'Avg Cost':>10} {'Value':>12} {'P/L%':>8}")
                print("  " + "-" * 66)
                for p in positions:
                    print(f"  {p['code']:<12} {p['name']:<10} {p['qty']:>8.0f} {p['average_cost']:>10.2f} {p['market_val']:>12.2f} {p['pl_ratio_avg_cost']:>8.2f}%")
            else:
                print("  No positions")
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
    parser = argparse.ArgumentParser(description="Get positions and funds")
    parser.add_argument("--acc-id", type=int, default=None, help="Account ID")
    parser.add_argument("--market", choices=["US", "HK", "HKCC", "CN", "SG"], default=None, help="Trading market")
    parser.add_argument("--trd-env", choices=["REAL", "SIMULATE"], default=None, help="Trading environment")
    parser.add_argument("--currency", choices=["HKD", "USD", "CNH", "JPY", "AUD", "CAD", "MYR", "SGD"], default=None,
                        help="Currency type (default determined by server)")
    parser.add_argument("--security-firm",
                        choices=["FUTUSECURITIES", "FUTUINC", "FUTUSG", "FUTUAU", "FUTUCA", "FUTUJP", "FUTUMY"],
                        default=None, help="Security firm identifier")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output in JSON format")
    args = parser.parse_args()
    get_portfolio(acc_id=args.acc_id, market=args.market, trd_env=args.trd_env,
                  currency=args.currency, security_firm=args.security_firm, output_json=args.output_json)
