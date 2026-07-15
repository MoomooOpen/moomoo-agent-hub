#!/usr/bin/env python3
"""
Place combo order

Description: Submit option combo/strategy or event-contract combo order
Usage:
  # Option combo
  python place_combo_order.py '[{"code":"US.AAPL260529C302500","trd_side":"BUY","qty_ratio":1},{"code":"US.AAPL","trd_side":"SELL","qty_ratio":100}]' --price 9.9 --quantity 1
  # Event-contract combo (all legs EC.; quote_id + per-leg pred_side required)
  python place_combo_order.py '[{"code":"EC.xxx","trd_side":"BUY","qty_ratio":1,"pred_side":"YES"},{"code":"EC.yyy","trd_side":"BUY","qty_ratio":1,"pred_side":"YES"}]' --price 0.55 --quantity 1 --quote-id {id} --trd-env REAL --confirmed

Rate limit:
- Max 15 requests per 30 seconds per account ID
- Minimum interval between two orders is 0.02 seconds
- Shares the same rate limit bucket with place_order

Parameter notes:
- combo_leg_list: Option legs: code/trd_side/qty_ratio/position_id(optional); event-contract legs also need pred_side
- trd_side: Supports BUY/SELL/SELLSHORT/BUYBACK (aliases SELL_SHORT/BUY_BACK also accepted) for option combos
- quote_id: Required for event-contract combos (from request_combo_quotes); ignored for option combos
- price: For event-contract combos must come from request_combo_quotes ask/bid
- FUTUJP rules apply to option combos only
"""
import argparse
import json
import sys
import os as _os

sys.path.insert(0, _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..")))
from common import (
    create_trade_context,
    create_future_trade_context,
    is_event_contract_code,
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
    safe_int,
    is_empty,
    PredSide,
    RET_OK,
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


def _fail(msg, output_json=False, code=1):
    if output_json:
        print(json.dumps({"error": msg}, ensure_ascii=False))
    else:
        print(f"Error: {msg}")
    sys.exit(code)


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


def _resolve_pred_side(name):
    if PredSide is None:
        raise ValueError("Current SDK does not support PredSide; please upgrade moomoo-api")
    key = str(name).upper()
    val = getattr(PredSide, key, None)
    if val is None or key == "UNKNOWN":
        raise ValueError(f"Unsupported pred_side: {name}; use YES or NO")
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


def _parse_trdmarket_auth(row):
    raw = safe_get(row, "trdmarket_auth", default=[])
    if isinstance(raw, str):
        return [s.strip().upper() for s in raw.strip("[]").split(",") if s.strip()]
    if isinstance(raw, list):
        return [format_enum(m).upper() for m in raw]
    return []


def _account_has_prediction(row):
    return "PREDICTION" in _parse_trdmarket_auth(row)


def _classify_combo_legs(items):
    flags = [is_event_contract_code(str(it.get("code", "")).strip()) for it in items]
    if all(flags):
        return True
    if not any(flags):
        return False
    raise ValueError(
        "Invalid combo: cannot mix event-contract legs (EC.) with non-EC legs; "
        "all legs must be EC. or none"
    )


def _parse_combo_legs(legs_json, enforce_jp_close_rules=False):
    from moomoo import ComboLeg

    try:
        items = json.loads(legs_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse combo legs JSON: {e}")
    if not isinstance(items, list) or len(items) == 0:
        raise ValueError("Combo legs must be a non-empty JSON array")

    is_ec = _classify_combo_legs(items)
    combo_legs = []
    side_names = []
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
        side_names.append(side_name)

        leg = ComboLeg()
        leg.code = code
        leg.trd_side = side_enum
        leg.qty_ratio = float(qty_ratio)
        has_position_id = "position_id" in item and item["position_id"] not in (None, "")
        if has_position_id:
            leg.position_id = int(item["position_id"])

        if is_ec:
            pred = item.get("pred_side")
            if pred in (None, ""):
                raise ValueError(f"Event-contract combo leg #{idx} missing pred_side (YES/NO)")
            leg.pred_side = _resolve_pred_side(pred)
        elif enforce_jp_close_rules:
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

    if is_ec and len(set(side_names)) > 1:
        raise ValueError(
            f"Event-contract combo requires identical trd_side on all legs, got: {side_names}"
        )

    return combo_legs, is_ec


def _validate_prediction_account(ctx, acc_id, output_json):
    ret, acc_data = ctx.get_acc_list()
    if ret != RET_OK or is_empty(acc_data):
        return
    has_any = False
    for i in range(len(acc_data)):
        row = acc_data.iloc[i] if hasattr(acc_data, "iloc") else acc_data[i]
        if _account_has_prediction(row):
            has_any = True
        if acc_id and safe_int(safe_get(row, "acc_id", default=0)) == safe_int(acc_id):
            if format_enum(safe_get(row, "acc_role", default="")).upper() == "MASTER":
                _fail("Master account (MASTER) is not allowed to place orders", output_json)
            if not _account_has_prediction(row):
                # scan rest for any PREDICTION
                if not has_any:
                    for j in range(len(acc_data)):
                        r2 = acc_data.iloc[j] if hasattr(acc_data, "iloc") else acc_data[j]
                        if _account_has_prediction(r2):
                            has_any = True
                            break
                if not has_any:
                    _fail(
                        "Event contracts are not supported (no futures account with PREDICTION in trdmarket_auth)",
                        output_json,
                    )
                _fail(
                    f"Account {acc_id} trdmarket_auth does not contain PREDICTION; cannot place event-contract combo",
                    output_json,
                )
    if not has_any:
        _fail(
            "Event contracts are not supported (no futures account with PREDICTION in trdmarket_auth)",
            output_json,
        )


def place_combo_order(legs_json, price, quantity, order_type="NORMAL",
                      acc_id=None, trd_env=None, security_firm=None, remark="",
                      time_in_force="DAY", expire_time=None, confirmed=False,
                      quote_id=None, output_json=False):
    acc_id = acc_id or get_default_acc_id()
    trd_env = parse_trd_env(trd_env) if trd_env else get_default_trd_env()

    firm_enum = parse_security_firm(security_firm)
    enforce_jp_close_rules = format_enum(firm_enum) == "FUTUJP"

    try:
        raw_items = json.loads(legs_json)
        if not isinstance(raw_items, list) or len(raw_items) == 0:
            raise ValueError("Combo legs must be a non-empty JSON array")
        is_ec = _classify_combo_legs(raw_items)
        combo_legs, is_ec = _parse_combo_legs(
            legs_json,
            enforce_jp_close_rules=(enforce_jp_close_rules and not is_ec),
        )
    except ValueError as e:
        _fail(str(e), output_json)
    except json.JSONDecodeError as e:
        _fail(f"Failed to parse combo legs JSON: {e}", output_json)

    if is_ec:
        if not quote_id:
            _fail(
                "Event-contract combo requires --quote-id (from request_combo_quotes)",
                output_json,
            )
        if format_enum(trd_env) == "SIMULATE":
            _fail("Paper trading does not support event-contract combos; use --trd-env REAL", output_json)
        market = None
    else:
        quote_id = None  # silently ignore for option combos
        first_code = safe_get(combo_legs[0], "code", default="")
        market = infer_market_from_code(first_code)
        if not market:
            _fail(f"Unable to infer trading market from first combo leg code '{first_code}'", output_json)

    try:
        order_type_enum = _resolve_order_type(order_type)
        tif_enum = _resolve_time_in_force(time_in_force)
    except ValueError as e:
        _fail(str(e), output_json)

    try:
        if float(quantity) <= 0:
            raise ValueError
    except (ValueError, TypeError):
        _fail("quantity must be a positive number", output_json)

    tif_name = str(time_in_force).upper()
    if tif_name == "GTD" and not expire_time:
        _fail("time_in_force=GTD requires --expire-time (yyyy-MM-dd)", output_json)
    if expire_time and tif_name != "GTD":
        _fail("--expire-time is only valid when --time-in-force is GTD", output_json)

    if format_enum(trd_env) == "REAL" and not confirmed:
        preview = {
            "action": "place_combo_order_preview",
            "legs": json.loads(legs_json),
            "price": float(price),
            "quantity": float(quantity),
            "order_type": str(order_type).upper(),
            "time_in_force": tif_name,
            "expire_time": expire_time,
            "quote_id": quote_id,
            "is_event_contract": is_ec,
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
            if quote_id:
                print(f"  quote_id:      {quote_id}")
            print(f"  Account:       {acc_id}")
            print(f"  Legs:          {len(combo_legs)}")
            print("=" * 60)
            print("Please re-run with --confirmed to submit.")
        sys.exit(2)

    ctx = None
    try:
        if is_ec:
            ctx = create_future_trade_context(security_firm=firm_enum)
            _validate_prediction_account(ctx, acc_id, output_json)
        else:
            ctx = create_trade_context(market, security_firm=firm_enum)

        order_kwargs = dict(
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
        if quote_id:
            order_kwargs["quote_id"] = quote_id

        ret, data = ctx.place_combo_order(**order_kwargs)
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
                "quote_id": quote_id,
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
            "quote_id": quote_id,
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
    parser = argparse.ArgumentParser(description="Place combo order (option combo/strategy / event-contract combo)")
    parser.add_argument(
        "legs",
        help='Combo legs JSON. Option example with BUY/SELL/SELLSHORT/BUYBACK; '
             'event-contract: all EC. codes and each leg must include pred_side',
    )
    parser.add_argument("--price", type=float, required=True,
                        help="Order price (event-contract: from request_combo_quotes ask/bid)")
    parser.add_argument("--quantity", type=float, required=True, help="Combo quantity")
    parser.add_argument("--quote-id", default=None, dest="quote_id",
                        help="Quote ID (required for event-contract combo; ignored for option combo)")
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
        quote_id=args.quote_id,
        output_json=args.output_json,
    )
