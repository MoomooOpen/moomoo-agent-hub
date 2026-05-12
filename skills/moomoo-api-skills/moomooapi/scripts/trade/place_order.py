#!/usr/bin/env python3
"""
Place Order

Function: Place a buy or sell order for a stock on a specified account
Note: Uses simulated account by default; real trading requires specifying --trd-env REAL

API Limits:
- Max 15 requests per 30 seconds per account ID
- Min interval of 0.02 seconds between two consecutive orders
- Real accounts require manually unlocking the trade password in the OpenD GUI

Parameter Description:
- price: Still required for market/auction orders (any value accepted). Precision: futures integer 8 digits decimal 9 digits, US options decimal 2 digits, US stocks <=$ 1 allow decimal 4 digits, others decimal 3 digits rounded
- qty: Unit is "contracts" for options and futures
- code: Futures continuous contract codes are automatically converted to actual contract codes
- adjust_limit: Positive values adjust upward, negative values adjust downward, e.g. 0.015 means upward adjustment range not exceeding 1.5%
- remark: UTF-8 length limit 64 bytes
- time_in_force: Market orders for HK stocks, A-shares, and global futures only support day validity
- fill_outside_rth: For HK pre-market auction and US pre/post market; market orders not supported during pre/post market sessions
- aux_price: Required for stop-loss/take-profit type orders
- trail_type/trail_value/trail_spread: Required for trailing stop orders
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
    parse_trd_side,
    parse_security_firm,
    get_default_acc_id,
    get_default_trd_env,
    infer_market_from_code,
    check_ret,
    safe_close,
    format_enum,
    safe_get,
    safe_int,
    OrderType,
    Session,
    RET_OK,
    is_empty,
)

# Order session only for US stocks
ORDER_SESSION_MAP = {
    "NONE": Session.NONE,
    "RTH": Session.RTH,
    "ETH": Session.ETH,
    "OVERNIGHT": Session.OVERNIGHT,
    "ALL": Session.ALL,
}


def _audit_log(entry):
    """Append trade audit log to ~/.futu_trade_audit.jsonl"""
    import datetime
    try:
        log_path = _os.path.join(_os.path.expanduser("~"), ".futu_trade_audit.jsonl")
        entry["timestamp"] = datetime.datetime.now().isoformat()
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass


def place_order(code, side, quantity, price=None, order_type="NORMAL",
                acc_id=None, trd_env=None, security_firm=None, output_json=False,
                confirmed=False, fill_outside_rth=False, session_str="NONE"):
    acc_id = acc_id or get_default_acc_id()
    trd_env = parse_trd_env(trd_env) if trd_env else get_default_trd_env()
    trd_side = parse_trd_side(side)

    # Automatically infer trading market from --code prefix
    market = infer_market_from_code(code)
    if not market:
        msg = f"Unable to infer trading market from code '{code}', please use full format such as US.AAPL, HK.00700"
        if output_json:
            print(json.dumps({"error": msg}, ensure_ascii=False))
        else:
            print(f"Error: {msg}")
        sys.exit(1)

    if str(order_type).upper() == "MARKET":
        order_type_enum = OrderType.MARKET
        price = 0.0
    else:
        order_type_enum = OrderType.NORMAL
        if price is None:
            print("Error: Limit order must specify --price")
            sys.exit(1)

    try:
        if quantity is None or int(quantity) <= 0:
            raise ValueError
    except (ValueError, TypeError):
        if output_json:
            print(json.dumps({"error": "Quantity must be a positive integer"}, ensure_ascii=False))
        else:
            print("Error: Quantity must be a positive integer")
        sys.exit(1)

    # Real trading hard constraint: must pass --confirmed to actually place the order
    if format_enum(trd_env) == "REAL" and not confirmed:
        summary = {
            "action": "place_order_preview",
            "code": code,
            "side": format_enum(trd_side),
            "quantity": quantity,
            "price": price,
            "order_type": str(order_type).upper(),
            "trd_env": "REAL",
            "acc_id": acc_id,
            "message": "Real trading requires confirmation. Please verify order details and re-execute with the --confirmed parameter.",
        }
        if output_json:
            print(json.dumps(summary, ensure_ascii=False))
        else:
            print("=" * 60)
            print("Real Trading Preview (Not Executed)")
            print("=" * 60)
            print(f"  Code:       {code}")
            print(f"  Side:       {format_enum(trd_side)}")
            print(f"  Quantity:   {quantity}")
            print(f"  Price:      {price}")
            print(f"  Type:       {order_type}")
            print(f"  Account:    {acc_id}")
            print("=" * 60)
            print("Please confirm and re-execute with the --confirmed parameter.")
        sys.exit(2)

    ctx = None
    try:
        ctx = create_trade_context(market, security_firm=parse_security_firm(security_firm))
        # Validate account role: MASTER accounts are not allowed to place orders
        if acc_id:
            ret, acc_data = ctx.get_acc_list()
            if ret == RET_OK and not is_empty(acc_data):
                for i in range(len(acc_data)):
                    row = acc_data.iloc[i] if hasattr(acc_data, "iloc") else acc_data[i]
                    row_acc_id = safe_int(safe_get(row, "acc_id", default=0))
                    if row_acc_id == safe_int(acc_id):
                        acc_role = format_enum(safe_get(row, "acc_role", default=""))
                        if acc_role.upper() == "MASTER":
                            msg = "Master account (MASTER) is not allowed to place orders, please select a non-master account"
                            if output_json:
                                print(json.dumps({"error": msg}, ensure_ascii=False))
                            else:
                                print(f"Error: {msg}")
                            sys.exit(1)
                        break

        session = ORDER_SESSION_MAP.get(session_str.upper(), Session.NONE)
        order_kwargs = dict(
            price=float(price),
            qty=int(quantity),
            code=code,
            trd_side=trd_side,
            order_type=order_type_enum,
            trd_env=trd_env,
            acc_id=acc_id,
        )
        if fill_outside_rth:
            order_kwargs["fill_outside_rth"] = True
        if session != Session.NONE:
            order_kwargs["session"] = session
        ret, data = ctx.place_order(**order_kwargs)
        check_ret(ret, data, ctx, "Place order")

        if hasattr(data, "iloc"):
            row = data.iloc[0]
            order_id = safe_get(row, "order_id", "orderID", default=str(data))
        else:
            order_id = str(data)

        result = {
            "order_id": str(order_id),
            "code": code,
            "side": format_enum(trd_side),
            "quantity": quantity,
            "price": price,
            "order_type": str(order_type).upper(),
            "trd_env": format_enum(trd_env),
            "status": "submitted",
        }

        _audit_log({"action": "place_order", "result": "success", **result})

        if output_json:
            print(json.dumps(result, ensure_ascii=False))
        else:
            print("=" * 60)
            print("Order placed successfully")
            print("=" * 60)
            print(f"  Order ID:    {order_id}")
            print(f"  Code:        {code}")
            print(f"  Side:        {format_enum(trd_side)}")
            print(f"  Quantity:    {quantity}")
            print(f"  Price:       {price}")
            print(f"  Type:        {order_type}")
            print(f"  Environment: {format_enum(trd_env)}")
            print("=" * 60)

    except Exception as e:
        _audit_log({"action": "place_order", "result": "error", "code": code,
                     "side": side, "quantity": quantity, "price": price, "error": str(e)})
        if output_json:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))
        else:
            print(f"Error: {e}")
        sys.exit(1)
    finally:
        safe_close(ctx)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Place order (buy/sell stock)")
    parser.add_argument("--code", required=True, help="Stock code (e.g. US.AAPL)")
    parser.add_argument("--side", required=True, choices=["BUY", "SELL"], help="Trade direction")
    parser.add_argument("--quantity", type=int, required=True, help="Quantity")
    parser.add_argument("--price", type=float, default=None, help="Price (required for limit orders)")
    parser.add_argument("--order-type", default="NORMAL", choices=["NORMAL", "MARKET"], help="Order type")
    parser.add_argument("--acc-id", type=int, default=None, help="Account ID")
    parser.add_argument("--trd-env", choices=["REAL", "SIMULATE"], default=None, help="Trading environment")
    parser.add_argument("--security-firm",
                        choices=["FUTUSECURITIES", "FUTUINC", "FUTUSG", "FUTUAU", "FUTUCA", "FUTUJP", "FUTUMY"],
                        default=None, help="Security firm identifier")
    parser.add_argument("--fill-outside-rth", action="store_true",
                        help="Allow order to fill outside regular trading hours (US pre/post market, HK pre-market auction)")
    parser.add_argument("--session", choices=["NONE", "RTH", "ETH", "OVERNIGHT", "ALL"],
                        default="NONE", help="US stock trading session (only for US stocks)")
    parser.add_argument("--confirmed", action="store_true", help="Real trading confirmation flag (preview only without this flag)")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output in JSON format")
    args = parser.parse_args()
    place_order(code=args.code, side=args.side, quantity=args.quantity, price=args.price,
                order_type=args.order_type, acc_id=args.acc_id,
                trd_env=args.trd_env, security_firm=args.security_firm,
                output_json=args.output_json, confirmed=args.confirmed,
                fill_outside_rth=args.fill_outside_rth, session_str=args.session)
