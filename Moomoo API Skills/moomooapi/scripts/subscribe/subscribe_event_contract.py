#!/usr/bin/env python3
"""
Subscribe Event Contract Real-time Info

Function: Subscribe event contract real-time info (order book / ticker / K-line, etc.) by specifying contract codes and data types
Usage: python subscribe_event_contract.py EC.KXODIMATCH-26JUL140600INDENG-IND --types ORDER_BOOK TICKER K_DAY [--kline-source ORDER_BOOK_YES] [--no-first-push] [--json]

API: OpenQuoteContext.subscribe_event_contract(code_list, subtype_list, kline_source_list=None,
      is_first_push=True, subscribe_push=True)
Return: (ret, err_message)

API Limits:
- Subscription count is limited by the OpenD subscription quota
- To receive pushes you must set_handler to register the corresponding handler first (the push scripts push_event_contract_* set it automatically)
- kline_source_list only takes effect when subscribing to K-line types and corresponds one-to-one with K-line types in subtype_list; omit to default to contract-level trade-price K-line
- Event Contract K-line only supports K_1M/K_5M/K_60M/K_DAY

Common SubType: ORDER_BOOK / TICKER / K_1M / K_5M / K_60M / K_DAY
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
    parse_ec_kline_source,
    EC_KLTYPE_CHOICES,
    assert_event_contract_support,
)


_EC_KLINE_SUBTYPES = {"K_1M", "K_5M", "K_60M", "K_DAY"}


def subscribe_event_contract(codes, subtype_names, kline_source_names=None,
                             is_first_push=True, subscribe_push=True, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        assert_event_contract_support(ctx, output_json=output_json)

        subtypes = parse_subtypes(subtype_names)

        # Validate K-line types (Event Contract only supports 4)
        subtype_keys = [str(s).split(".")[-1] for s in subtypes]
        for k in subtype_keys:
            if k.startswith("K_") and k not in _EC_KLINE_SUBTYPES:
                raise ValueError(f"Event Contract K-line only supports {EC_KLTYPE_CHOICES}, got: {k}")

        # kline_source_list only takes effect when subscribing to K-line
        kline_sources = None
        if kline_source_names:
            kline_sources = [parse_ec_kline_source(s) for s in kline_source_names]

        ret, err = ctx.subscribe_event_contract(
            codes, subtypes, kline_source_list=kline_sources,
            is_first_push=is_first_push, subscribe_push=subscribe_push)
        check_ret(ret, err, ctx, "Subscribe event contract")

        result = {
            "codes": codes,
            "subtypes": subtype_keys,
            "kline_sources": kline_source_names or [],
            "is_first_push": is_first_push,
            "subscribe_push": subscribe_push,
            "status": "subscribed",
        }

        if output_json:
            print(json.dumps(result, ensure_ascii=False))
        else:
            print("=" * 50)
            print("Subscribed event contract successfully")
            print("=" * 50)
            print(f"  Contracts: {', '.join(codes)}")
            print(f"  Types: {', '.join(subtype_keys)}")
            if kline_source_names:
                print(f"  K-line sources: {', '.join(kline_source_names)}")
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
    parser = argparse.ArgumentParser(description="Subscribe event contract real-time info")
    parser.add_argument("codes", nargs="+", help="Event contract codes, e.g. EC.xxx")
    parser.add_argument("--types", nargs="+", required=True,
                        help="Subscription types: ORDER_BOOK TICKER K_1M K_5M K_60M K_DAY")
    parser.add_argument("--kline-source", nargs="+", default=None,
                        help="K-line source (only for K-line types): ORDER_BOOK_YES")
    parser.add_argument("--no-first-push", action="store_true", help="Do not push cached data immediately")
    parser.add_argument("--no-push", action="store_true", help="Do not register push callback (pull only)")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output JSON format")
    args = parser.parse_args()
    subscribe_event_contract(
        codes=args.codes, subtype_names=args.types,
        kline_source_names=args.kline_source,
        is_first_push=not args.no_first_push,
        subscribe_push=not args.no_push, output_json=args.output_json)
