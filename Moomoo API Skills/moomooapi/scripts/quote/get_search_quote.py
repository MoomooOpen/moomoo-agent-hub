#!/usr/bin/env python3
"""
Search Quote Instruments

Function: Search stocks, ETFs, plates, and other quote instruments by keyword
Usage: python get_search_quote.py aapl [--max-count 10] [--json]

API Limits:
- Max 10 requests per 30 seconds

Parameters:
- keyword: Search term (required)
- --max-count: Max results (default 10, max 100)

Return fields:
- market: Market type
- code: Stock code
- name: Stock name
- sec_type: Security type (STOCK/ETF/PLATE, etc.)
- is_watched: Whether already in watchlist
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
)


def get_search_quote(keyword, max_count=10, output_json=False):
    if not keyword or not str(keyword).strip():
        raise ValueError("Search keyword cannot be empty")
    max_count = max(1, min(int(max_count), 100))

    ctx = None
    try:
        ctx = create_quote_context()
        if not hasattr(ctx, "get_search_quote"):
            raise RuntimeError("Current OpenD/SDK does not provide get_search_quote; please upgrade")

        ret, data = ctx.get_search_quote(keyword.strip(), max_count)
        check_ret(ret, data, ctx, "Search quote instruments")

        if is_empty(data):
            if output_json:
                print(json.dumps({"keyword": keyword, "data": []}, ensure_ascii=False))
            else:
                print("No matching results")
            return

        records = df_to_records(data)
        if output_json:
            print(json.dumps({"keyword": keyword, "count": len(records), "data": records}, ensure_ascii=False))
        else:
            print("=" * 90)
            print(f"Search quote: {keyword} ({len(records)} results)")
            print("=" * 90)
            print_display_df(data)
            print("=" * 90)

    except Exception as e:
        if output_json:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))
        else:
            print(f"Error: {e}")
        sys.exit(1)
    finally:
        safe_close(ctx)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search quote instruments")
    parser.add_argument("keyword", help="Search term")
    parser.add_argument("--max-count", type=int, default=10, help="Max results (default 10, max 100)")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output in JSON format")
    args = parser.parse_args()
    get_search_quote(args.keyword, args.max_count, args.output_json)
