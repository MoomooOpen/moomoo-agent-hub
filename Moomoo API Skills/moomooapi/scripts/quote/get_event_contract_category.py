#!/usr/bin/env python3
"""
Get Event Contract Category List

Function: Get Event Contract top-level categories and their sub-categories (tags), no subscription required
Usage: python get_event_contract_category.py [--category Sports] [--json]

API: OpenQuoteContext.get_event_contract_category(category=None)
Return: DataFrame with columns category / category_name / tags (tags is a list of sub-category id strings)

Call chain: category(get_event_contract_category) -> filter_competition
            -> Series(get_event_contract_series_list) -> Event -> Contract -> snapshot/orderbook/kline/ticker
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
    is_empty,
    df_to_records,
    print_display_df,
    assert_event_contract_support,
)


def get_event_contract_category(category=None, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        assert_event_contract_support(ctx, output_json=output_json)

        ret, data = ctx.get_event_contract_category(category=category)
        check_ret(ret, data, ctx, "Get event contract category")

        if is_empty(data):
            if output_json:
                print(json.dumps({"data": []}))
            else:
                print("No data")
            return

        if output_json:
            print(json.dumps({"data": df_to_records(data)}, ensure_ascii=False))
        else:
            print("=" * 70)
            print("Event Contract Categories")
            print("=" * 70)
            print_display_df(data, max_colwidth=60)
            print(f"\nTotal {len(data)} categories")
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
    parser = argparse.ArgumentParser(description="Get event contract category list (no subscription required)")
    parser.add_argument("--category", default=None, help="Top-level category id, e.g. Sports; omit to return all")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output JSON format")
    args = parser.parse_args()
    get_event_contract_category(category=args.category, output_json=args.output_json)
