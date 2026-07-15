#!/usr/bin/env python3
"""
Get Event Contract Series List

Function: Get Series list (a Series is a collection of related Events) by category/tag, no subscription required
Usage: python get_event_contract_series_list.py --category Sports [--tag Football] [--json]

API: OpenQuoteContext.get_event_contract_series_list(category=None, tag=None)
Return: DataFrame with columns series_code / series_name / category / tags / frequency

Note: series_code can be passed to get_event_contract_event_list
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


def get_event_contract_series_list(category=None, tag=None, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        assert_event_contract_support(ctx, output_json=output_json)

        ret, data = ctx.get_event_contract_series_list(category=category, tag=tag)
        check_ret(ret, data, ctx, "Get event contract series list")

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
            print(f"Event Contract Series List - {category or 'All'} {('/' + tag) if tag else ''}")
            print("=" * 70)
            cols = [c for c in ['series_code', 'series_name', 'category', 'tags', 'frequency']
                    if c in data.columns]
            print_display_df(data[cols], max_colwidth=42)
            print(f"\nTotal {len(data)} series")
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
    parser = argparse.ArgumentParser(description="Get event contract series list (no subscription required)")
    parser.add_argument("--category", default=None, help="Top-level category, e.g. Sports")
    parser.add_argument("--tag", default=None, help="Sub-category, e.g. Football")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output JSON format")
    args = parser.parse_args()
    get_event_contract_series_list(category=args.category, tag=args.tag, output_json=args.output_json)
