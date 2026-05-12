#!/usr/bin/env python3
"""
Modify Order

Function: Modify the price and/or quantity of a specified order
Usage: python modify_order.py --order-id 12345678 --price 410 --quantity 200
Note: qty is the expected total quantity after modification (not incremental); A-share Connect market does not support order modification

API Limits:
- Max 20 requests per 30 seconds per account ID
- Min interval of 0.04 seconds between two consecutive requests
- Real accounts require manually unlocking the trade password in the OpenD GUI

Parameter Description:
- price: Securities accounts rounded to 3 decimal places, futures accounts rounded to 9 decimal places, excess is discarded
- qty: Expected total quantity after modification (not incremental), unit is "contracts" for options and futures, rounded to 0 decimal places
- adjust_limit: Positive values adjust upward, negative values adjust downward, e.g. 0.015 means adjustment range not exceeding 1.5% (ignored for futures)
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
    safe_get,
    safe_float,
    format_enum,
    is_empty,
    ModifyOrderOp,
    RET_OK,
)


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


def modify_order(order_id, price=None, quantity=None, adjust_limit=0,
                 acc_id=None, market=None, trd_env=None, security_firm=None, output_json=False):
    acc_id = acc_id or get_default_acc_id()
    trd_env = parse_trd_env(trd_env) if trd_env else get_default_trd_env()

    if price is None and quantity is None:
        msg = "At least one of --price or --quantity must be specified"
        if output_json:
            print(json.dumps({"error": msg}, ensure_ascii=False))
        else:
            print(f"Error: {msg}")
        sys.exit(1)

    if price is not None:
        try:
            price = float(price)
        except (ValueError, TypeError):
            msg = "Price must be a number"
            if output_json:
                print(json.dumps({"error": msg}, ensure_ascii=False))
            else:
                print(f"Error: {msg}")
            sys.exit(1)

    if quantity is not None:
        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError
        except (ValueError, TypeError):
            msg = "Quantity must be a positive integer"
            if output_json:
                print(json.dumps({"error": msg}, ensure_ascii=False))
            else:
                print(f"Error: {msg}")
            sys.exit(1)

    ctx = None
    try:
        ctx = create_trade_context(market, security_firm=parse_security_firm(security_firm))

        # Auto-complete: retrieve missing price or quantity from the original order
        if price is None or quantity is None:
            ret_q, orders = ctx.order_list_query(
                order_id=order_id, trd_env=trd_env, acc_id=acc_id,
            )
            if ret_q == RET_OK and not is_empty(orders):
                orig = orders.iloc[0]
                if price is None:
                    price = float(safe_float(safe_get(orig, "price", default=0)))
                if quantity is None:
                    quantity = int(safe_float(safe_get(orig, "qty", default=0)))

        if price is None or quantity is None:
            msg = "Unable to retrieve price or quantity from the original order, please specify --price and --quantity manually"
            if output_json:
                print(json.dumps({"error": msg}, ensure_ascii=False))
            else:
                print(f"Error: {msg}")
            sys.exit(1)

        ret, data = ctx.modify_order(
            modify_order_op=ModifyOrderOp.NORMAL,
            order_id=order_id,
            qty=quantity,
            price=price,
            adjust_limit=adjust_limit,
            trd_env=trd_env,
            acc_id=acc_id,
        )
        check_ret(ret, data, ctx, "Modify order")

        if hasattr(data, "iloc"):
            row = data.iloc[0]
            result_order_id = safe_get(row, "order_id", default=order_id)
        else:
            result_order_id = order_id

        result = {
            "order_id": str(result_order_id),
            "price": price,
            "quantity": quantity,
            "status": "modified",
        }

        _audit_log({"action": "modify_order", "result": "success", **result})

        if output_json:
            print(json.dumps(result, ensure_ascii=False))
        else:
            print("=" * 50)
            print("Order modified successfully")
            print("=" * 50)
            print(f"  Order ID:     {result_order_id}")
            print(f"  New Price:    {price}")
            print(f"  New Quantity: {quantity}")
            print("=" * 50)

    except Exception as e:
        _audit_log({"action": "modify_order", "result": "error", "order_id": order_id,
                     "price": price, "quantity": quantity, "error": str(e)})
        if output_json:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))
        else:
            print(f"Error: {e}")
        sys.exit(1)
    finally:
        safe_close(ctx)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Modify order (change price and quantity)")
    parser.add_argument("--order-id", required=True, help="Order ID")
    parser.add_argument("--price", type=float, default=None, help="New price (optional, keeps original if not specified)")
    parser.add_argument("--quantity", type=int, default=None, help="New total quantity (optional, keeps original if not specified)")
    parser.add_argument("--adjust-limit", type=float, default=0, help="Price adjustment range (default 0)")
    parser.add_argument("--acc-id", type=int, default=None, help="Account ID")
    parser.add_argument("--market", choices=["US", "HK", "HKCC", "CN", "SG"], default=None, help="Trading market")
    parser.add_argument("--trd-env", choices=["REAL", "SIMULATE"], default=None, help="Trading environment")
    parser.add_argument("--security-firm",
                        choices=["FUTUSECURITIES", "FUTUINC", "FUTUSG", "FUTUAU", "FUTUCA", "FUTUJP", "FUTUMY"],
                        default=None, help="Security firm identifier")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output in JSON format")
    args = parser.parse_args()
    modify_order(order_id=args.order_id, price=args.price, quantity=args.quantity,
                 adjust_limit=args.adjust_limit, acc_id=args.acc_id, market=args.market,
                 trd_env=args.trd_env, security_firm=args.security_firm, output_json=args.output_json)
