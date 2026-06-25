#!/usr/bin/env python3
"""
Place combo order

Description: Submit option combo/strategy order
Usage: python place_combo_order.py '[{"code":"US.AAPL260529C302500","trd_side":"BUY","qty_ratio":1},{"code":"US.AAPL","trd_side":"SELL","qty_ratio":100}]' --price 9.9 --quantity 1

Rate limit:
- Max 15 requests per 30 seconds per account ID
- Minimum interval between two orders is 0.02 seconds
- Shares the same rate limit bucket with place_order

Parameter notes:
- combo_leg_list: Combo legs JSON list; item fields: code/trd_side/qty_ratio/position_id(optional)
- trd_side: Supports BUY/SELL/SELLSHORT/BUYBACK (aliases SELL_SHORT/BUY_BACK also accepted)
- FUTUJP rules: use BUY/SELLSHORT for opening legs and SELL/BUYBACK for closing legs. Closing legs must
  provide position_id from position_list_query(show_option_strategy_view=True)
- price: Order price (still required for market/auction style order types)
- qty: Combo quantity; leg actual qty = qty * qty_ratio
- order_type: Order type, default NORMAL
- time_in_force: Validity type, default DAY; use with expire_time when GTD
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
    infer_market_from_code,
    check_ret,
    safe_close,
    format_enum,
    safe_get,
    safe_float,
    is_empty,
)


def _audit_log(entry):
    import datetime
    try:
        log_path = _os.path.join(_os.path.expanduser("~"), ".futu_trade_audit.jsonl")
        entry["timestamp"] = datetime.datetime.now().isoformat()
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass


def _resolve_order_type(name):
    from moomoo import OrderType
    key = str(name).upper()
    val = getattr(OrderType, key, None)
    if val is None:
        raise ValueError(f"Unsupported order_type: {name}")
    return val


def _resolve_time_in_force(name):
    from moomoo import TimeInForce
    key = str(name).upper()
    val = getattr(TimeInForce, key, None)
    if val is None:
        raise ValueError(f"Unsupported time_in_force: {name}")
    return val


def _resolve_combo_leg_side(side_raw):
    """Resolve combo leg side aliases to TrdSide enum and canonical name."""
    from moomoo import TrdSide

    raw = str(side_raw).strip().upper()
    alias_map = {
        "BUY": "BUY",
        "SELL": "SELL",
        "SELLSHORT": "SELL_SHORT",
        "SELL_SHORT": "SELL_SHORT",
        "BUYBACK": "BUY_BACK",
        "BUY_BACK": "BUY_BACK",
        # Tolerate common typo from user inputs.
        "BACKBACK": "BUY_BACK",
    }
    target = alias_map.get(raw)
    if not target:
        raise ValueError(
            f"Invalid combo leg trd_side: {side_raw}. "
            f"Supported: BUY, SELL, SELLSHORT, BUYBACK"
        )
    val = getattr(TrdSide, target, None)
    if val is None:
        raise ValueError(
            f"Current moomoo-api SDK does not support TrdSide.{target}. "
            f"Please upgrade SDK and retry."
        )
    return val, target


def _parse_combo_legs(legs_json, enforce_jp_close_rules=False):
    from moomoo import ComboLeg

    try:
        items = json.loads(legs_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse combo legs JSON: {e}")
    if not isinstance(items, list) or len(items) == 0:
        raise ValueError("Combo legs must be a non-empty JSON array")

    combo_legs = []
    for idx, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Combo leg #{idx} must be an object")
        code = str(item.get("code", "")).strip()
        if not code:
            raise ValueError(f"Combo leg #{idx} missing code")
        qty_ratio = item.get("qty_ratio", None)
        if qty_ratio is None:
            raise ValueError(f"Combo leg #{idx} missing qty_ratio")
        trd_side = item.get("trd_side", None)
        if trd_side is None:
            raise ValueError(f"Combo leg #{idx} missing trd_side")

        side_enum, side_name = _resolve_combo_leg_side(trd_side)

        leg = ComboLeg()
        leg.code = code
        leg.trd_side = side_enum
        leg.qty_ratio = float(qty_ratio)
        has_position_id = "position_id" in item and item["position_id"] not in (None, "")
        if has_position_id:
            leg.position_id = int(item["position_id"])

        if enforce_jp_close_rules:
            is_close_leg = side_name in ("SELL", "BUY_BACK")
            is_open_leg = side_name in ("BUY", "SELL_SHORT")
            if is_close_leg and not has_position_id:
                raise ValueError(
                    f"FUTUJP close leg #{idx} ({code}, side={side_name}) requires position_id. "
                    f"Use position_list_query with show_option_strategy_view=True to get position_id."
                )
            if is_open_leg and has_position_id:
                raise ValueError(
                    f"FUTUJP open leg #{idx} ({code}, side={side_name}) should not include position_id. "
                    f"Use BUY/SELLSHORT for open legs and SELL/BUYBACK for close legs."
                )
        combo_legs.append(leg)
    return combo_legs


def place_combo_order(legs_json, price, quantity, order_type="NORMAL",
                      acc_id=None, trd_env=None, security_firm=None, remark="",
                      time_in_force="DAY", expire_time=None, confirmed=False,
                      output_json=False):
    acc_id = acc_id or get_default_acc_id()
    trd_env = parse_trd_env(trd_env) if trd_env else get_default_trd_env()

    firm_enum = parse_security_firm(security_firm)
    enforce_jp_close_rules = format_enum(firm_enum) == "FUTUJP"

    combo_legs = _parse_combo_legs(legs_json, enforce_jp_close_rules=enforce_jp_close_rules)
    first_code = safe_get(combo_legs[0], "code", default="")
    market = infer_market_from_code(first_code)
    if not market:
        msg = f"Unable to infer trading market from first combo leg code '{first_code}'"
        if output_json:
            print(json.dumps({"error": msg}, ensure_ascii=False))
        else:
            print(f"Error: {msg}")
        sys.exit(1)

    order_type_enum = _resolve_order_type(order_type)
    tif_enum = _resolve_time_in_force(time_in_force)

    try:
        if float(quantity) <= 0:
            raise ValueError
    except (ValueError, TypeError):
        msg = "quantity must be a positive number"
        if output_json:
            print(json.dumps({"error": msg}, ensure_ascii=False))
        else:
            print(f"Error: {msg}")
        sys.exit(1)

    if format_enum(trd_env) == "REAL" and not confirmed:
        preview = {
            "action": "place_combo_order_preview",
            "legs": json.loads(legs_json),
            "price": float(price),
            "quantity": float(quantity),
            "order_type": str(order_type).upper(),
            "time_in_force": str(time_in_force).upper(),
            "expire_time": expire_time,
            "trd_env": "REAL",
            "acc_id": acc_id,
            "message": "Real trading combo order needs confirmation. Re-run with --confirmed after checking details.",
        }
        if output_json:
            print(json.dumps(preview, ensure_ascii=False))
        else:
            print("=" * 60)
            print("Real Combo Order Preview (Not Executed)")
            print("=" * 60)
            print(f"  Price:         {price}")
            print(f"  Quantity:      {quantity}")
            print(f"  Order Type:    {order_type}")
            print(f"  Time In Force: {time_in_force}")
            if expire_time:
                print(f"  Expire Time:   {expire_time}")
            print(f"  Account:       {acc_id}")
            print(f"  Legs:          {len(combo_legs)}")
            print("=" * 60)
            print("Please re-run with --confirmed to submit.")
        sys.exit(2)

    ctx = None
    try:
        ctx = create_trade_context(market, security_firm=firm_enum)
        ret, data = ctx.place_combo_order(
            combo_leg_list=combo_legs,
            price=float(price),
            qty=float(quantity),
            order_type=order_type_enum,
            trd_env=trd_env,
            acc_id=acc_id,
            remark=remark,
            time_in_force=tif_enum,
            expire_time=expire_time,
        )
        check_ret(ret, data, ctx, "Place combo order")

        if is_empty(data):
            result = {
                "status": "submitted",
                "message": "Order submitted, but no order details were returned",
            }
        else:
            row = data.iloc[0] if hasattr(data, "iloc") else data[0]
            result = {
                "order_id": str(safe_get(row, "order_id", default="")),
                "code": str(safe_get(row, "code", default="")),
                "strategy_type": str(safe_get(row, "strategy_type", default="")),
                "trd_side": str(safe_get(row, "trd_side", default="")),
                "order_type": str(safe_get(row, "order_type", default="")),
                "order_status": str(safe_get(row, "order_status", default="")),
                "qty": safe_float(safe_get(row, "qty", default=0.0)),
                "price": safe_float(safe_get(row, "price", default=0.0)),
                "amount": safe_float(safe_get(row, "amount", default=0.0)),
                "time_in_force": str(safe_get(row, "time_in_force", default="")),
                "expire_time": str(safe_get(row, "expire_time", default="")),
                "dealt_qty": safe_float(safe_get(row, "dealt_qty", default=0.0)),
                "dealt_avg_price": safe_float(safe_get(row, "dealt_avg_price", default=0.0)),
                "create_time": str(safe_get(row, "create_time", default="")),
                "updated_time": str(safe_get(row, "updated_time", default="")),
                "last_err_msg": str(safe_get(row, "last_err_msg", default="")),
                "remark": str(safe_get(row, "remark", default="")),
            }

        _audit_log({"action": "place_combo_order", "result": "success", **result})

        if output_json:
            print(json.dumps(result, ensure_ascii=False))
        else:
            print("=" * 70)
            print("Combo order placed successfully")
            print("=" * 70)
            print(f"  Order ID:       {result.get('order_id', '')}")
            print(f"  Combo Code:     {result.get('code', '')}")
            print(f"  Strategy Type:  {result.get('strategy_type', '')}")
            print(f"  Side:           {result.get('trd_side', '')}")
            print(f"  Quantity:       {result.get('qty', '')}")
            print(f"  Price:          {result.get('price', '')}")
            print(f"  Status:         {result.get('order_status', '')}")
            print("=" * 70)

    except Exception as e:
        _audit_log({
            "action": "place_combo_order",
            "result": "error",
            "legs": json.loads(legs_json) if legs_json else [],
            "price": price,
            "quantity": quantity,
            "error": str(e),
        })
        if output_json:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))
        else:
            print(f"Error: {e}")
        sys.exit(1)
    finally:
        safe_close(ctx)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Place combo order (option combo/strategy)")
    parser.add_argument(
        "legs",
        help='Combo legs JSON, e.g. \'[{"code":"US.AAPL260529C302500","trd_side":"BUY","qty_ratio":1},{"code":"US.AAPL","trd_side":"SELL","qty_ratio":100}]\' (trd_side supports BUY/SELL/SELLSHORT/BUYBACK)',
    )
    parser.add_argument("--price", type=float, required=True, help="Order price")
    parser.add_argument("--quantity", type=float, required=True, help="Combo quantity")
    parser.add_argument("--order-type", default="NORMAL", help="Order type (default NORMAL)")
    parser.add_argument("--acc-id", type=int, default=None, help="Account ID")
    parser.add_argument("--trd-env", choices=["REAL", "SIMULATE"], default=None, help="Trading environment")
    parser.add_argument(
        "--security-firm",
        choices=["FUTUSECURITIES", "FUTUINC", "FUTUSG", "FUTUAU", "FUTUCA", "FUTUJP", "FUTUMY"],
        default=None,
        help="Security firm identifier",
    )
    parser.add_argument("--remark", default="", help="Remark (UTF-8 max length 64 bytes)")
    parser.add_argument("--time-in-force", default="DAY", help="Time in force (default DAY)")
    parser.add_argument("--expire-time", default=None, help="Expire time (yyyy-MM-dd, valid when GTD)")
    parser.add_argument("--confirmed", action="store_true", help="Real trading confirmation flag (preview only without this)")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output JSON format")
    args = parser.parse_args()

    place_combo_order(
        legs_json=args.legs,
        price=args.price,
        quantity=args.quantity,
        order_type=args.order_type,
        acc_id=args.acc_id,
        trd_env=args.trd_env,
        security_firm=args.security_firm,
        remark=args.remark,
        time_in_force=args.time_in_force,
        expire_time=args.expire_time,
        confirmed=args.confirmed,
        output_json=args.output_json,
    )
