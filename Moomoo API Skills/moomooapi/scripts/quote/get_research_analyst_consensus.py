#!/usr/bin/env python3
"""
Get Analyst Consensus

Function: Get analyst consensus rating, target price range and rating distribution
          for a stock (past 3 months)
Usage: python get_research_analyst_consensus.py [-h] [--json] code

API Limits:
- Max 30 requests per 30 seconds
- Supports equities and REITs

Parameter Description:
- code: Stock code, e.g. US.AAPL

Return Field Description:
- highest / average / lowest: Target price range
- rating:           Consensus rating (Qot_Common.ResearchRatingType)
- total:            Total number of analysts rated (past 3 months)
- update_time_str:  Rating data update date (YYYY-MM-DD)
- buy / hold / sell: Rating distribution percentage values (before % sign, e.g. 12.34 = 12.34%)
- strong_buy / underperform: Non-US markets only
"""
import argparse
import json
import sys
import os as _os

sys.path.insert(0, _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..")))
from common import create_quote_context, check_ret, safe_close, is_empty

_RATING_LABEL = {
    1: "Sell",
    2: "Underperform",
    3: "Hold",
    4: "Buy",
    5: "Strong Buy",
}

_DIST_ROWS_ALL = [
    ("strong_buy",   "Strong Buy"),
    ("buy",          "Buy"),
    ("hold",         "Hold"),
    ("underperform", "Underperform"),
    ("sell",         "Sell"),
]
_DIST_ROWS_US = [
    ("buy",  "Buy"),
    ("hold", "Hold"),
    ("sell", "Sell"),
]

_SEP = "=" * 64
_DASH = "-" * 64


def get_research_analyst_consensus(code, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        ret, data = ctx.get_research_analyst_consensus(code)
        check_ret(ret, data, ctx, "get analyst consensus")

        if is_empty(data) or not any(data.values()):
            if output_json:
                print(json.dumps({"code": code, "data": {}}))
            else:
                print("No data")
            return

        if output_json:
            print(json.dumps({"code": code, "data": data}, ensure_ascii=False))
            return

        print(_SEP)
        print(f"Analyst Consensus: {code}")
        print(_DASH)

        highest = data.get("highest")
        average = data.get("average")
        lowest = data.get("lowest")
        if highest is not None:
            print(f"Highest Target Price: {highest:.3f}")
        if average is not None:
            print(f"Average Target Price: {average:.3f}")
        else:
            print("Average Target Price: -")
        if lowest is not None:
            print(f"Lowest Target Price:  {lowest:.3f}")

        rating = data.get("rating")
        if rating is not None:
            print(f"Consensus Rating:     {_RATING_LABEL.get(rating, str(rating))} ({rating})")
        else:
            print("Consensus Rating:     -")
        total = data.get("total")
        if total is not None:
            print(f"Total Analysts:       {total}")
        update_time_str = data.get("update_time_str")
        if update_time_str:
            print(f"Update Date:          {update_time_str}")

        print()
        print("Rating Distribution:")
        is_us = code.upper().startswith("US.")
        dist_rows = _DIST_ROWS_US if is_us else _DIST_ROWS_ALL
        max_lw = max(len(lbl) for _, lbl in dist_rows)
        for key, label in dist_rows:
            pct = data.get(key)
            padded = label.ljust(max_lw)
            if pct is not None:
                print(f"  {padded}: {pct:.2f}%")
            else:
                print(f"  {padded}: -")

        print(_DASH)
        print(f"Field count: {len(data)}")
        print(_SEP)

    except SystemExit:
        raise
    except Exception as e:
        if output_json:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))
        else:
            print(f"Error: {e}")
        sys.exit(1)
    finally:
        safe_close(ctx)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get analyst consensus rating and target price")
    parser.add_argument("code", help="Stock code, e.g. US.AAPL")
    parser.add_argument("--json", action="store_true", dest="output_json",
                        help="Output in JSON format")
    args = parser.parse_args()
    get_research_analyst_consensus(args.code, output_json=args.output_json)
