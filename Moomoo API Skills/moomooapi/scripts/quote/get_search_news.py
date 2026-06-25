#!/usr/bin/env python3
"""
Search News

Function: Search news, notices, ratings, and other information by keyword
Usage: python get_search_news.py space [--max-count 10] [--news-sub-type ALL] [--json]

API Limits:
- Max 10 requests per 30 seconds

Parameters:
- keyword: Search term (required)
- --max-count: Max results (default 10, max 100)
- --news-sub-type: News sub-type (ALL/NEWS/NOTICE/RATING, default ALL)

Return fields:
- title: Title
- news_sub_type: News sub-type
- source: Source
- publish_time: Publish time
- view_count: View count
- related_securities: Related securities
- url: Detail page URL
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

NEWS_SUB_TYPE_MAP = {}


def _load_news_sub_type_map():
    global NEWS_SUB_TYPE_MAP
    if NEWS_SUB_TYPE_MAP:
        return NEWS_SUB_TYPE_MAP
    try:
        from moomoo import NewsSubType
    except ImportError as e:
        raise RuntimeError(f"Current moomoo-api does not provide NewsSubType ({e}); please upgrade SDK") from e
    NEWS_SUB_TYPE_MAP.update({
        "ALL": NewsSubType.ALL,
        "NEWS": NewsSubType.NEWS,
        "NOTICE": NewsSubType.NOTICE,
        "RATING": NewsSubType.RATING,
    })
    return NEWS_SUB_TYPE_MAP


def get_search_news(keyword, max_count=10, news_sub_type="ALL", output_json=False):
    if not keyword or not str(keyword).strip():
        raise ValueError("Search keyword cannot be empty")
    max_count = max(1, min(int(max_count), 100))
    sub_type_map = _load_news_sub_type_map()
    sub_type = sub_type_map.get(str(news_sub_type).upper())
    if sub_type is None:
        raise ValueError(f"Unsupported news_sub_type: {news_sub_type}, available: {list(sub_type_map.keys())}")

    ctx = None
    try:
        ctx = create_quote_context()
        if not hasattr(ctx, "get_search_news"):
            raise RuntimeError("Current OpenD/SDK does not provide get_search_news; please upgrade")

        ret, data = ctx.get_search_news(keyword.strip(), max_count, news_sub_type=sub_type)
        check_ret(ret, data, ctx, "Search news")

        if is_empty(data):
            if output_json:
                print(json.dumps({
                    "keyword": keyword,
                    "news_sub_type": news_sub_type.upper(),
                    "data": [],
                }, ensure_ascii=False))
            else:
                print("No matching results")
            return

        records = df_to_records(data)
        if output_json:
            print(json.dumps({
                "keyword": keyword,
                "news_sub_type": news_sub_type.upper(),
                "count": len(records),
                "data": records,
            }, ensure_ascii=False))
        else:
            print("=" * 100)
            print(f"Search news: {keyword} (type={news_sub_type.upper()}, {len(records)} results)")
            print("=" * 100)
            print_display_df(data, max_colwidth=40)
            print("=" * 100)

    except Exception as e:
        if output_json:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))
        else:
            print(f"Error: {e}")
        sys.exit(1)
    finally:
        safe_close(ctx)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search news")
    parser.add_argument("keyword", help="Search term")
    parser.add_argument("--max-count", type=int, default=10, help="Max results (default 10, max 100)")
    parser.add_argument("--news-sub-type", default="ALL",
                        choices=["ALL", "NEWS", "NOTICE", "RATING"],
                        help="News sub-type (default ALL)")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output in JSON format")
    args = parser.parse_args()
    get_search_news(args.keyword, args.max_count, args.news_sub_type, args.output_json)
