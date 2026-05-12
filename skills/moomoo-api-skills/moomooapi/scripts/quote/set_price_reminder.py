#!/usr/bin/env python3
"""
Set Price Reminder

Function: Set price reminders for a stock
Usage: python set_price_reminder.py HK.00700 --op SET --type PRICE_UP --value 400

API Limits:
- Max 60 requests per 30 seconds
- Max 10 reminders per stock

Parameters:
- op: SET (create/modify), DEL (delete), DEL_ALL (delete all for the stock), ENABLE (enable), DISABLE (disable)
- reminder_type: PRICE_UP (price rises to), PRICE_DOWN (price drops to), CHANGE_RATE_UP (daily gain exceeds),
                 CHANGE_RATE_DOWN (daily loss exceeds), BID_PRICE_UP (bid price rises to), ASK_PRICE_DOWN (ask price drops to),
                 TURNOVER_UP (volume exceeds), TURNOVER_RATE_UP (turnover rate exceeds)
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
    RET_OK,
)


def set_price_reminder(code, op, reminder_type=None, value=None, reminder_id=None, output_json=False):
    ctx = None
    try:
        from moomoo import SetPriceReminderOp, PriceReminderType

        op_map = {
            "SET": SetPriceReminderOp.SET,
            "DEL": SetPriceReminderOp.DEL,
            "DEL_ALL": SetPriceReminderOp.DEL_ALL,
            "ENABLE": SetPriceReminderOp.ENABLE,
            "DISABLE": SetPriceReminderOp.DISABLE,
        }
        op_enum = op_map.get(op.upper())
        if op_enum is None:
            raise ValueError(f"Unsupported operation: {op}, available: {list(op_map.keys())}")

        kwargs = {"code": code, "op": op_enum}
        if reminder_id is not None:
            kwargs["key"] = reminder_id
        if reminder_type:
            type_map = {
                "PRICE_UP": PriceReminderType.PRICE_UP,
                "PRICE_DOWN": PriceReminderType.PRICE_DOWN,
                "CHANGE_RATE_UP": PriceReminderType.CHANGE_RATE_UP,
                "CHANGE_RATE_DOWN": PriceReminderType.CHANGE_RATE_DOWN,
                "BID_PRICE_UP": PriceReminderType.BID_PRICE_UP,
                "ASK_PRICE_DOWN": PriceReminderType.ASK_PRICE_DOWN,
                "TURNOVER_UP": PriceReminderType.TURNOVER_UP,
                "TURNOVER_RATE_UP": PriceReminderType.TURNOVER_RATE_UP,
            }
            t = type_map.get(reminder_type.upper())
            if t is None:
                raise ValueError(f"Unsupported reminder type: {reminder_type}")
            kwargs["reminder_type"] = t
        if value is not None:
            kwargs["reminder_freq"] = 0  # ALWAYS
            kwargs["value"] = value

        ctx = create_quote_context()
        ret, data = ctx.set_price_reminder(**kwargs)
        check_ret(ret, data, ctx, "set price reminder")

        if output_json:
            print(json.dumps({"result": str(data)}, ensure_ascii=False))
        else:
            print(f"Price reminder set successfully: {data}")

    except Exception as e:
        if output_json:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))
        else:
            print(f"Error: {e}")
        sys.exit(1)
    finally:
        safe_close(ctx)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Set price reminder")
    parser.add_argument("code", help="Stock code, e.g. HK.00700")
    parser.add_argument("--op", required=True, choices=["SET", "DEL", "DEL_ALL", "ENABLE", "DISABLE"], help="Operation type")
    parser.add_argument("--type", dest="reminder_type", default=None, help="Reminder type")
    parser.add_argument("--value", type=float, default=None, help="Reminder value")
    parser.add_argument("--reminder-id", type=int, default=None, help="Reminder ID (used for modify/delete)")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output in JSON format")
    args = parser.parse_args()
    set_price_reminder(args.code, args.op, args.reminder_type, args.value, args.reminder_id, args.output_json)
