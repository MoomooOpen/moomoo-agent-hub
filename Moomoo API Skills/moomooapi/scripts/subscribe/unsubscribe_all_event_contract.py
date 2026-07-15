#!/usr/bin/env python3
"""
Unsubscribe All Event Contract Subscriptions on the Current Connection

Function: One-click cancel all event contract subscriptions on the current connection
Usage: python unsubscribe_all_event_contract.py [--json]

API: OpenQuoteContext.unsubscribe_all_event_contract()
Return: (ret, err_message)

API Limits:
- At least 1 minute must pass after subscribing before unsubscribing
- To cancel specific subscriptions, use unsubscribe_event_contract.py
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
    assert_event_contract_support,
)


def unsubscribe_all_event_contract(output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        assert_event_contract_support(ctx, output_json=output_json)

        ret, err = ctx.unsubscribe_all_event_contract()
        check_ret(ret, err, ctx, "Unsubscribe all event contracts")

        if output_json:
            print(json.dumps({"result": "ok"}, ensure_ascii=False))
        else:
            print("Unsubscribed all event contracts on the current connection")

    except Exception as e:
        if output_json:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))
        else:
            print(f"Error: {e}")
        sys.exit(1)
    finally:
        safe_close(ctx)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Unsubscribe all event contracts on the current connection")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output JSON format")
    args = parser.parse_args()
    unsubscribe_all_event_contract(args.output_json)
