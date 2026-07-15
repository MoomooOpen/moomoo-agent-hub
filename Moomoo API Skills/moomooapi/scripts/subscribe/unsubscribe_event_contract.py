#!/usr/bin/env python3
"""
Unsubscribe Event Contract

Function: Precisely unsubscribe event contract by contract code, data type, and K-line source
Usage: python unsubscribe_event_contract.py EC.xxx --types TICKER [--kline-source ORDER_BOOK_YES] [--json]

API: OpenQuoteContext.unsubscribe_event_contract(code_list, subtype_list, kline_source_list=None)
Return: (ret, err_message)

API Limits:
- At least 1 minute must pass after subscribing before unsubscribing
- The three dimensions (contract/type/source) must match the subscription exactly to match precisely
- To cancel all subscriptions on the current connection, use unsubscribe_all_event_contract.py
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
    assert_event_contract_support,
)


def unsubscribe_event_contract(codes, subtype_names, kline_source_names=None, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        assert_event_contract_support(ctx, output_json=output_json)

        subtypes = parse_subtypes(subtype_names)
        kline_sources = None
        if kline_source_names:
            kline_sources = [parse_ec_kline_source(s) for s in kline_source_names]

        ret, err = ctx.unsubscribe_event_contract(
            codes, subtypes, kline_source_list=kline_sources)
        check_ret(ret, err, ctx, "Unsubscribe event contract")

        result = {
            "codes": codes,
            "subtypes": [str(s).split(".")[-1] for s in subtypes],
            "kline_sources": kline_source_names or [],
            "status": "unsubscribed",
        }

        if output_json:
            print(json.dumps(result, ensure_ascii=False))
        else:
            print("=" * 50)
            print("Unsubscribed event contract successfully")
            print("=" * 50)
            print(f"  Contracts: {', '.join(codes)}")
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
    parser = argparse.ArgumentParser(description="Unsubscribe event contract")
    parser.add_argument("codes", nargs="+", help="Event contract codes, e.g. EC.xxx")
    parser.add_argument("--types", nargs="+", required=True,
                        help="Unsubscribe types: ORDER_BOOK TICKER K_1M K_5M K_60M K_DAY")
    parser.add_argument("--kline-source", nargs="+", default=None,
                        help="K-line source (precisely unsubscribe a specific K-line source): ORDER_BOOK_YES")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output JSON format")
    args = parser.parse_args()
    unsubscribe_event_contract(
        codes=args.codes, subtype_names=args.types,
        kline_source_names=args.kline_source, output_json=args.output_json)
