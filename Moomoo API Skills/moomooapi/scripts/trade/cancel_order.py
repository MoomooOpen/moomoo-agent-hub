#!/usr/bin/env python3
"""
Cancel Order

Function: Cancel a specified order
Usage: python cancel_order.py --order-id 12345678

API Limits:
- Max 20 requests per 30 seconds per account ID
- Min interval of 0.04 seconds between two consecutive requests
- Real accounts require manually unlocking the trade password in the OpenD GUI

Parameter Description:
- order_id: The order ID to cancel
- trdmarket: Can specify a market when using cancel_all_order; defaults to cancelling orders in all markets
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
    format_enum,
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


def cancel_order(order_id, acc_id=None, market=None, trd_env=None, security_firm=None, output_json=False):
    acc_id = acc_id or get_default_acc_id()
    trd_env = parse_trd_env(trd_env) if trd_env else get_default_trd_env()

    ctx = None
    try:
        ctx = create_trade_context(market, security_firm=parse_security_firm(security_firm))

        ret, data = ctx.modify_order(
            modify_order_op=ModifyOrderOp.CANCEL,
            order_id=order_id,
            qty=0,
            price=0,
            trd_env=trd_env,
            acc_id=acc_id,
        )
        check_ret(ret, data, ctx, "Cancel order")

        result = {"order_id": order_id, "status": "cancelled"}

        _audit_log({"action": "cancel_order", "result": "success", **result})

        if output_json:
            print(json.dumps(result, ensure_ascii=False))
        else:
            print("=" * 50)
            print("Order cancelled successfully")
            print("=" * 50)
            print(f"  Order ID: {order_id}")
            print("=" * 50)

    except Exception as e:
        _audit_log({"action": "cancel_order", "result": "error", "order_id": order_id, "error": str(e)})
        if output_json:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))
        else:
            print(f"Error: {e}")
        sys.exit(1)
    finally:
        safe_close(ctx)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cancel order")
    parser.add_argument("--order-id", required=True, help="Order ID")
    parser.add_argument("--acc-id", type=int, default=None, help="Account ID")
    parser.add_argument("--market", choices=["US", "HK", "HKCC", "CN", "SG"], default=None, help="Trading market")
    parser.add_argument("--trd-env", choices=["REAL", "SIMULATE"], default=None, help="Trading environment")
    parser.add_argument("--security-firm",
                        choices=["FUTUSECURITIES", "FUTUINC", "FUTUSG", "FUTUAU", "FUTUCA", "FUTUJP", "FUTUMY"],
                        default=None, help="Security firm identifier")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output in JSON format")
    args = parser.parse_args()
    cancel_order(order_id=args.order_id, acc_id=args.acc_id, market=args.market,
                 trd_env=args.trd_env, security_firm=args.security_firm, output_json=args.output_json)
