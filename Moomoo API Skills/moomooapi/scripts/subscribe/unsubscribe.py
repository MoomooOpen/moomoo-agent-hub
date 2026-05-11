#!/usr/bin/env python3
"""
Unsubscribe

Function: Unsubscribe specified data types for specified stocks
Usage: python unsubscribe.py HK.00700 --types QUOTE ORDER_BOOK
      python unsubscribe.py --all  (unsubscribe all)

API limitations:
- Must subscribe for at least one minute before unsubscribing
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
    parse_subtypes,
)


def unsubscribe(codes=None, subtype_names=None, unsubscribe_all=False, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        if unsubscribe_all:
            ret, msg = ctx.unsubscribe_all()
            check_ret(ret, msg, ctx, "Unsubscribe all")
            result = {"status": "all_unsubscribed"}
        else:
            if not codes or not subtype_names:
                print("Error: Must specify stock codes and subscription types, or use --all to unsubscribe all")
                sys.exit(1)
            subtypes = parse_subtypes(subtype_names)
            ret, msg = ctx.unsubscribe(codes, subtypes)
            check_ret(ret, msg, ctx, "Unsubscribe")
            result = {
                "codes": codes,
                "subtypes": [str(s).split(".")[-1] for s in subtypes],
                "status": "unsubscribed",
            }

        if output_json:
            print(json.dumps(result, ensure_ascii=False))
        else:
            print("=" * 50)
            if unsubscribe_all:
                print("All subscriptions cancelled")
            else:
                print("Unsubscription successful")
                print(f"  Stocks: {', '.join(codes)}")
                print(f"  Types: {', '.join(result['subtypes'])}")
            print("=" * 50)

    except Exception as e:
        if output_json:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))
        else:
            print(f"Error: {e}")
        sys.exit(1)
    finally:
        safe_close(ctx)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Unsubscribe")
    parser.add_argument("codes", nargs="*", help="Stock codes")
    parser.add_argument("--types", nargs="+", default=None, help="Subscription type list")
    parser.add_argument("--all", action="store_true", dest="unsub_all", help="Unsubscribe all")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output in JSON format")
    args = parser.parse_args()
    unsubscribe(codes=args.codes if args.codes else None,
                subtype_names=args.types,
                unsubscribe_all=args.unsub_all,
                output_json=args.output_json)
