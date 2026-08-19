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
- price: Still required for market/auction orders (any value accepted). Precision: futures integer 8 digits decimal 9 digits, US options decimal 2 digits, US stocks <=$ 1 allow decimal 4 digits, others decimal 3 digits rounded; prediction market 0.01~0.99 with 2 decimal places
- qty / --quantity: Unit is "contracts" for options and futures. Mutually exclusive with --amount; if both set, amount wins and qty is forced to 0
- amount: Order amount; only for prediction market (EC.). When amount is set, qty is passed as 0
- pred_side: Prediction market side YES/NO; required for prediction market orders
- code: Futures continuous contract codes are automatically converted to actual contract codes; prediction market codes use EC.xxx (no market prefix) via OpenFutureTradeContext
- adjust_limit: Positive values adjust upward, negative values adjust downward, e.g. 0.015 means upward adjustment range not exceeding 1.5%
- remark: Optional remark; defaults to AISKILL when empty, otherwise AISKILL + user input (UTF-8 max 64 bytes total)
- time_in_force: Market orders for HK stocks, A-shares, and global futures only support day validity; use with expire_time when GTD
- expire_time: Order expiry date yyyy-MM-dd; only valid when time_in_force=GTD
- fill_outside_rth: For HK pre-market auction and US pre/post market; market orders not supported during pre/post market sessions
- aux_price: Required for stop-loss/take-profit type orders
- trail_type/trail_value/trail_spread: Required for trailing stop orders
- session: Only for US stocks, supports RTH/ETH/OVERNIGHT/ALL
- jp_acc_type: SubAccType enum, only for FUTUJP accounts. Routes the order to a specific JP
  sub-account (JP_GENERAL / JP_TOKUTEI / JP_NISA_GENERAL / JP_NISA_TSUMITATE / JP_*_SHORT /
  JP_HONPO_* / JP_GAIKOKU_* / JP_DERIVATIVE_*). Defaults to JP_GENERAL server-side.
- position_id: Position ID returned by position_list_query. Required when closing/covering a
  specific JP margin or short position; the API maps the order to that exact position record.
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
    TimeInForce,
    PredSide,
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
    """Append trade audit log to ~/.moomoo_trade_audit.jsonl"""
    import datetime
    try:
        log_path = _os.path.join(_os.path.expanduser("~"), ".moomoo_trade_audit.jsonl")
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


def _resolve_jp_acc_type(jp_acc_type):
    if not jp_acc_type:
        return None
    try:
        from moomoo import SubAccType
    except ImportError:
        return None
    return getattr(SubAccType, str(jp_acc_type).upper(), None)


def _resolve_time_in_force(name):
    if TimeInForce is None:
        raise ValueError("Current SDK does not support TimeInForce")
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


def _parse_trdmarket_auth(row):
    raw = safe_get(row, "trdmarket_auth", default=[])
    if isinstance(raw, str):
        return [s.strip().upper() for s in raw.strip("[]").split(",") if s.strip()]
    if isinstance(raw, list):
        return [format_enum(m).upper() for m in raw]
    return []


def _account_has_prediction(row):
    return "PREDICTION" in _parse_trdmarket_auth(row)


def _build_remark(remark):
    """Use AISKILL when remark is empty; otherwise AISKILL + user input."""
    user_remark = str(remark or "").strip()
    if not user_remark:
        return "AISKILL"
    return f"AISKILL{user_remark}"


def place_order(code, side, quantity=None, price=None, order_type="NORMAL",
                acc_id=None, trd_env=None, security_firm=None, output_json=False,
                confirmed=False, fill_outside_rth=False, session_str="NONE",
                jp_acc_type=None, position_id=None,
                amount=None, pred_side=None, time_in_force="DAY", expire_time=None,
                remark=""):
    acc_id = acc_id or get_default_acc_id()
    trd_env = parse_trd_env(trd_env) if trd_env else get_default_trd_env()
    trd_side = parse_trd_side(side)
    is_ec = is_event_contract_code(code)
    firm_enum = parse_security_firm(security_firm)

    jp_acc_type_enum = _resolve_jp_acc_type(jp_acc_type)
    if jp_acc_type and jp_acc_type_enum is None:
        _fail(
            f"jp_acc_type={jp_acc_type} is not supported by current moomoo-api SDK. "
            f"Upgrade the SDK or omit --jp-acc-type.",
            output_json,
        )

    if is_ec and format_enum(trd_env) == "SIMULATE":
        _fail("Paper trading does not support prediction markets; use --trd-env REAL", output_json)

    if is_ec and not pred_side:
        _fail("Prediction market orders require --pred-side YES or NO", output_json)

    pred_side_enum = None
    if pred_side:
        try:
            pred_side_enum = _resolve_pred_side(pred_side)
        except ValueError as e:
            _fail(str(e), output_json)

    if amount is not None:
        if not is_ec:
            _fail("--amount is only valid for prediction market (EC.)", output_json)
        qty = 0
    elif quantity is None:
        _fail("Must specify --quantity, or --amount for prediction market", output_json)
    else:
        try:
            if int(quantity) <= 0:
                raise ValueError
            qty = int(quantity)
        except (ValueError, TypeError):
            _fail("Quantity must be a positive integer", output_json)

    if not is_ec:
        market = infer_market_from_code(code)
        if not market:
            _fail(
                f"Unable to infer trading market from code '{code}', please use full format such as "
                f"US.AAPL, HK.00700, SG.D05, MY.1155, JP.7203; prediction market uses EC.xxx",
                output_json,
            )
    else:
        market = None

    if str(order_type).upper() == "MARKET":
        order_type_enum = OrderType.MARKET
        price = 0.0
    else:
        order_type_enum = OrderType.NORMAL
        if price is None:
            _fail("Limit order must specify --price", output_json)

    try:
        tif_enum = _resolve_time_in_force(time_in_force)
    except ValueError as e:
        _fail(str(e), output_json)

    tif_name = str(time_in_force).upper()
    if tif_name == "GTD" and not expire_time:
        _fail("time_in_force=GTD requires --expire-time (yyyy-MM-dd)", output_json)
    if expire_time and tif_name != "GTD":
        _fail("--expire-time is only valid when --time-in-force is GTD", output_json)

    # Real trading hard constraint: must pass --confirmed to actually place the order
    if format_enum(trd_env) == "REAL" and not confirmed:
        summary = {
            "action": "place_order_preview",
            "code": code,
            "side": format_enum(trd_side),
            "quantity": qty,
            "amount": amount,
            "pred_side": str(pred_side).upper() if pred_side else None,
            "price": price,
            "order_type": str(order_type).upper(),
            "time_in_force": tif_name,
            "expire_time": expire_time,
            "trd_env": "REAL",
            "acc_id": acc_id,
            "jp_acc_type": jp_acc_type or None,
            "position_id": position_id or None,
            "is_event_contract": is_ec,
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
            if amount is not None:
                print(f"  Amount:     {amount}")
            else:
                print(f"  Quantity:   {qty}")
            if pred_side:
                print(f"  Prediction Side:  {str(pred_side).upper()}")
            print(f"  Price:      {price}")
            print(f"  Type:       {order_type}")
            print(f"  TIF:        {tif_name}")
            if expire_time:
                print(f"  Expire:     {expire_time}")
            print(f"  Account:    {acc_id}")
            if jp_acc_type:
                print(f"  JP Sub-Account: {jp_acc_type}")
            if position_id:
                print(f"  Position ID: {position_id}")
            print("=" * 60)
            print("Please confirm and re-execute with the --confirmed parameter.")
        sys.exit(2)

    ctx = None
    try:
        if is_ec:
            ctx = create_future_trade_context(security_firm=firm_enum)
        else:
            ctx = create_trade_context(market, security_firm=firm_enum)

        # Validate account role: MASTER accounts are not allowed; prediction market needs PREDICTION
        if acc_id:
            ret, acc_data = ctx.get_acc_list()
            if ret == RET_OK and not is_empty(acc_data):
                matched = False
                has_any_prediction = False
                for i in range(len(acc_data)):
                    row = acc_data.iloc[i] if hasattr(acc_data, "iloc") else acc_data[i]
                    if _account_has_prediction(row):
                        has_any_prediction = True
                    row_acc_id = safe_int(safe_get(row, "acc_id", default=0))
                    if row_acc_id != safe_int(acc_id):
                        continue
                    matched = True
                    acc_role = format_enum(safe_get(row, "acc_role", default=""))
                    if acc_role.upper() == "MASTER":
                        _fail("Master account (MASTER) is not allowed to place orders, please select a non-master account", output_json)
                    if is_ec and not _account_has_prediction(row):
                        if not has_any_prediction:
                            for j in range(len(acc_data)):
                                r2 = acc_data.iloc[j] if hasattr(acc_data, "iloc") else acc_data[j]
                                if _account_has_prediction(r2):
                                    has_any_prediction = True
                                    break
                        if not has_any_prediction:
                            _fail(
                                "Prediction markets are not supported (no futures account with PREDICTION in trdmarket_auth)",
                                output_json,
                            )
                        _fail(
                            f"Account {acc_id} trdmarket_auth does not contain PREDICTION; cannot trade prediction markets",
                            output_json,
                        )
                    break
                if is_ec and not matched:
                    if not has_any_prediction:
                        for i in range(len(acc_data)):
                            row = acc_data.iloc[i] if hasattr(acc_data, "iloc") else acc_data[i]
                            if _account_has_prediction(row):
                                has_any_prediction = True
                                break
                    if not has_any_prediction:
                        _fail(
                            "Prediction markets are not supported (no futures account with PREDICTION in trdmarket_auth)",
                            output_json,
                        )
        elif is_ec:
            ret, acc_data = ctx.get_acc_list()
            if ret == RET_OK and not is_empty(acc_data):
                if not any(
                    _account_has_prediction(
                        acc_data.iloc[i] if hasattr(acc_data, "iloc") else acc_data[i]
                    )
                    for i in range(len(acc_data))
                ):
                    _fail(
                        "Prediction markets are not supported (no futures account with PREDICTION in trdmarket_auth)",
                        output_json,
                    )

        session = ORDER_SESSION_MAP.get(session_str.upper(), Session.NONE)
        order_kwargs = dict(
            price=float(price),
            qty=qty,
            code=code,
            trd_side=trd_side,
            order_type=order_type_enum,
            trd_env=trd_env,
            acc_id=acc_id,
            time_in_force=tif_enum,
            remark=_build_remark(remark),
        )
        if fill_outside_rth:
            order_kwargs["fill_outside_rth"] = True
        if session != Session.NONE:
            order_kwargs["session"] = session
        if expire_time:
            order_kwargs["expire_time"] = expire_time
        if amount is not None:
            order_kwargs["amount"] = float(amount)
        if pred_side_enum is not None:
            order_kwargs["pred_side"] = pred_side_enum
        if jp_acc_type_enum is not None:
            order_kwargs["jp_acc_type"] = jp_acc_type_enum
        if position_id:
            order_kwargs["position_id"] = position_id

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
            "quantity": qty,
            "amount": amount,
            "pred_side": str(pred_side).upper() if pred_side else None,
            "price": price,
            "order_type": str(order_type).upper(),
            "time_in_force": tif_name,
            "expire_time": expire_time,
            "trd_env": format_enum(trd_env),
            "jp_acc_type": jp_acc_type or None,
            "position_id": position_id or None,
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
            if amount is not None:
                print(f"  Amount:      {amount}")
            else:
                print(f"  Quantity:    {qty}")
            if pred_side:
                print(f"  Prediction Side:   {str(pred_side).upper()}")
            print(f"  Price:       {price}")
            print(f"  Type:        {order_type}")
            print(f"  Environment: {format_enum(trd_env)}")
            print("=" * 60)

    except Exception as e:
        _audit_log({"action": "place_order", "result": "error", "code": code,
                     "side": side, "quantity": quantity, "amount": amount,
                     "price": price, "error": str(e)})
        if output_json:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))
        else:
            print(f"Error: {e}")
        sys.exit(1)
    finally:
        safe_close(ctx)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Place order (buy/sell stock / prediction market)")
    parser.add_argument("--code", required=True, help="Instrument code (e.g. US.AAPL; prediction market EC.xxx)")
    parser.add_argument("--side", required=True, choices=["BUY", "SELL"], help="Trade direction")
    parser.add_argument("--quantity", type=int, default=None, help="Quantity (mutually exclusive with --amount; amount wins)")
    parser.add_argument("--amount", type=float, default=None, help="Order amount (prediction market only; preferred over quantity)")
    parser.add_argument("--pred-side", choices=["YES", "NO"], default=None, dest="pred_side",
                        help="Prediction market side (required for prediction market orders)")
    parser.add_argument("--price", type=float, default=None, help="Price (required for limit orders)")
    parser.add_argument("--order-type", default="NORMAL", choices=["NORMAL", "MARKET"], help="Order type")
    parser.add_argument("--time-in-force", default="DAY", dest="time_in_force",
                        help="Time in force (default DAY; GTD requires --expire-time)")
    parser.add_argument("--expire-time", default=None, dest="expire_time",
                        help="Order expiry date yyyy-MM-dd (only when time_in_force=GTD)")
    parser.add_argument("--acc-id", type=int, default=None, help="Account ID")
    parser.add_argument("--trd-env", choices=["REAL", "SIMULATE"], default=None, help="Trading environment")
    parser.add_argument("--security-firm",
                        choices=["FUTUSECURITIES", "FUTUINC", "FUTUSG", "FUTUAU", "FUTUCA", "FUTUJP", "FUTUMY"],
                        default=None, help="Security firm identifier")
    parser.add_argument("--fill-outside-rth", action="store_true",
                        help="Allow order to fill outside regular trading hours (US pre/post market, HK pre-market auction)")
    parser.add_argument("--session", choices=["NONE", "RTH", "ETH", "OVERNIGHT", "ALL"],
                        default="NONE", help="US stock trading session (only for US stocks)")
    parser.add_argument("--jp-acc-type",
                        choices=["JP_GENERAL", "JP_TOKUTEI", "JP_NISA_GENERAL", "JP_NISA_TSUMITATE",
                                 "JP_GENERAL_SHORT", "JP_TOKUTEI_SHORT",
                                 "JP_HONPO_GENERAL", "JP_GAIKOKU_GENERAL",
                                 "JP_HONPO_TOKUTEI", "JP_GAIKOKU_TOKUTEI",
                                 "JP_DERIVATIVE_LONG", "JP_DERIVATIVE_SHORT",
                                 "JP_HONPO_DERIVATIVE_GENERAL", "JP_GAIKOKU_DERIVATIVE_GENERAL",
                                 "JP_HONPO_DERIVATIVE_TOKUTEI", "JP_GAIKOKU_DERIVATIVE_TOKUTEI"],
                        default=None,
                        help="JP sub-account type (only for FUTUJP accounts; default JP_GENERAL server-side)")
    parser.add_argument("--position-id", default=None,
                        help="Position ID (from position_list_query) for closing/covering a specific JP margin or short position")
    parser.add_argument("--remark", default="", help="Remark (default AISKILL when empty; AISKILL+remark when set; UTF-8 max 64 bytes)")
    parser.add_argument("--confirmed", action="store_true", help="Real trading confirmation flag (preview only without this flag)")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output in JSON format")
    args = parser.parse_args()
    place_order(code=args.code, side=args.side, quantity=args.quantity, price=args.price,
                order_type=args.order_type, acc_id=args.acc_id,
                trd_env=args.trd_env, security_firm=args.security_firm,
                output_json=args.output_json, confirmed=args.confirmed,
                fill_outside_rth=args.fill_outside_rth, session_str=args.session,
                jp_acc_type=args.jp_acc_type, position_id=args.position_id,
                amount=args.amount, pred_side=args.pred_side,
                time_in_force=args.time_in_force, expire_time=args.expire_time,
                remark=args.remark)
