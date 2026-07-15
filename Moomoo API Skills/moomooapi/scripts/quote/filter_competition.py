#!/usr/bin/env python3
"""
Filter Competition

Function: Get available competition names and the full set of play types (scopes) by top-level category and tag, no subscription required
Usage: python filter_competition.py --category Sports [--tag Baseball] [--json]

API: OpenQuoteContext.filter_competition(category=None, tag=None)
Return: DataFrame with columns category / tag / competition (list of competition names) / scope (full play-type set)

Note: competition names can be passed as the competition param to get_event_contract_milestone_list
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
    assert_event_contract_support,
)


def filter_competition(category=None, tag=None, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        assert_event_contract_support(ctx, output_json=output_json)

        ret, data = ctx.filter_competition(category=category, tag=tag)
        check_ret(ret, data, ctx, "Filter competition")

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
            print(f"Filter Competition - {category or 'All'} {('/' + tag) if tag else ''}")
            print("=" * 70)
            for i in range(len(data)):
                row = data.iloc[i]
                comp = row.get("competition")
                scope = row.get("scope")
                print(f"\n  [{row.get('tag', '')}]")
                print(f"    Competitions: {comp}")
                print(f"    Scopes: {scope}")
            print(f"\nTotal {len(data)} tags")
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
    parser = argparse.ArgumentParser(description="Filter competition (get competitions and scopes, no subscription required)")
    parser.add_argument("--category", default=None, help="Top-level category, e.g. Sports")
    parser.add_argument("--tag", default=None, help="Sub-category, e.g. Baseball")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output JSON format")
    args = parser.parse_args()
    filter_competition(category=args.category, tag=args.tag, output_json=args.output_json)
