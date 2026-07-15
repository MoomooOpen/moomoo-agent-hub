#!/usr/bin/env python3
"""
Combo RFQ (Request Combo Quotes)

Function: Submit the user's combined contract legs (ComboLeg list) and MVC underlying to obtain the combo quote (bid/ask) and quote id (used for placing orders), no subscription required
Usage: python request_combo_quotes.py '[{"code":"EC.xxx-FRA","trd_side":"BUY","qty_ratio":1,"pred_side":"YES"},{"code":"EC.xxx-ENG","trd_side":"BUY","qty_ratio":1,"pred_side":"YES"}]' --mvc KALSHI.KXMVECROSSCATEGORY-R [--json]

API: OpenQuoteContext.request_combo_quotes(combo_leg_list, mvc)
Return: (ret, dict); dict contains combo_leg_list(echoed legs) / bid_price / ask_price / quote_id / should_retry

Leg JSON fields:
- code: str, required, contract code EC.xxx
- trd_side: BUY/SELL/SELL_SHORT/BUY_BACK, required
- qty_ratio: quantity ratio, required
- pred_side: YES/NO, required (missing raises "event contract combo missing required pred direction")
- position_id: optional, position id (only used for moomoo JP close)

Notes:
- mvc must be passed through from get_valid_combo_list.py; do not construct it yourself
- At least 2 legs are required; legs can come from different events (cross-competition combo)
- bid_price/should_retry are N/A when no corresponding quote, not an error
- quote_id has a time limit; if it expires, placing an order will fail and you must re-request; Combo order uses place_combo_order.py with quote_id
"""
import argparse
import json
import sys
import os as _os
sys.path.insert(0, _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..")))
from common import (
    create_quote_context,
    check_ret,
    safe_close,
    parse_pred_side,
    format_enum,
    to_jsonable,
    ComboLeg,
    TrdSide,
    assert_event_contract_support,
)


def _parse_combo_trd_side(side_str):
    """Parse combo-leg trading side -> TrdSide (combo legs support BUY/SELL/SELL_SHORT/BUY_BACK)"""
    if not side_str:
        raise ValueError("trd_side cannot be empty")
    key = str(side_str).strip().upper()
    if not hasattr(TrdSide, key):
        raise ValueError(f"Invalid trading side: {side_str}, must be BUY/SELL/SELL_SHORT/BUY_BACK")
    return getattr(TrdSide, key)


def _parse_combo_legs(legs_json):
    """Parse legs JSON list -> ComboLeg object list"""
    assert_event_contract_support()
    try:
        items = json.loads(legs_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Combo legs JSON parse failed: {e}")
    if not isinstance(items, list) or len(items) == 0:
        raise ValueError("Combo legs must be a non-empty JSON array")
    if len(items) < 2:
        raise ValueError("Event contract combo requires at least two legs")

    legs = []
    for idx, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Leg {idx} must be an object")
        code = str(item.get("code", "")).strip()
        if not code:
            raise ValueError(f"Leg {idx} is missing code")
        trd_side = item.get("trd_side")
        if trd_side is None:
            raise ValueError(f"Leg {idx} is missing trd_side")
        qty_ratio = item.get("qty_ratio")
        if qty_ratio is None:
            raise ValueError(f"Leg {idx} is missing qty_ratio")
        pred_side = item.get("pred_side")
        if pred_side is None or str(pred_side).strip() == "":
            raise ValueError(f"Leg {idx} is missing pred_side (YES/NO required)")

        leg = ComboLeg()
        leg.code = code
        leg.trd_side = _parse_combo_trd_side(str(trd_side))
        leg.qty_ratio = float(qty_ratio)
        leg.pred_side = parse_pred_side(str(pred_side))
        if "position_id" in item and item["position_id"] not in (None, ""):
            leg.position_id = int(item["position_id"])
        legs.append(leg)
    return legs


def _leg_to_dict(leg):
    """ComboLeg object -> JSON-serializable dict"""
    d = {
        "code": getattr(leg, "code", None),
        "trd_side": format_enum(getattr(leg, "trd_side", None)),
        "qty_ratio": to_jsonable(getattr(leg, "qty_ratio", None)),
        "pred_side": format_enum(getattr(leg, "pred_side", None)),
    }
    pos_id = getattr(leg, "position_id", None)
    if pos_id is not None:
        d["position_id"] = pos_id
    return d


def request_combo_quotes(legs_json, mvc, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        assert_event_contract_support(ctx, output_json=output_json)

        if not mvc or not isinstance(mvc, str):
            raise ValueError("mvc is required and must be passed through from get_valid_combo_list.py")

        legs = _parse_combo_legs(legs_json)

        ret, data = ctx.request_combo_quotes(legs, mvc)
        check_ret(ret, data, ctx, "Combo RFQ")

        leg_list = data.get("combo_leg_list", []) if isinstance(data, dict) else []
        result = {
            "combo_leg_list": [_leg_to_dict(l) for l in leg_list],
            "bid_price": to_jsonable(data.get("bid_price")),
            "ask_price": to_jsonable(data.get("ask_price")),
            "quote_id": to_jsonable(data.get("quote_id")),
            "should_retry": to_jsonable(data.get("should_retry")),
        }

        if output_json:
            print(json.dumps(result, ensure_ascii=False))
        else:
            print("=" * 70)
            print("Combo RFQ Result")
            print("=" * 70)
            print(f"  YES bid: {result['bid_price']}")
            print(f"  YES ask: {result['ask_price']}")
            print(f"  quote_id: {result['quote_id']}")
            print(f"  should_retry: {result['should_retry']}")
            print(f"\n  Combo legs ({len(result['combo_leg_list'])}):")
            for leg in result["combo_leg_list"]:
                print(f"    {leg['code']}  {leg['trd_side']}  ratio={leg['qty_ratio']}  pred={leg['pred_side']}")
            print("\n  Note: quote_id has a time limit; place the order soon via place_combo_order.py")
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
    parser = argparse.ArgumentParser(description="Combo RFQ (no subscription required)")
    parser.add_argument("legs", help='Combo legs JSON array, e.g. [{"code":"EC.xxx-FRA","trd_side":"BUY","qty_ratio":1,"pred_side":"YES"},...]')
    parser.add_argument("--mvc", required=True, help="MVC underlying, passed through from get_valid_combo_list.py")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output JSON format")
    args = parser.parse_args()
    request_combo_quotes(legs_json=args.legs, mvc=args.mvc, output_json=args.output_json)
