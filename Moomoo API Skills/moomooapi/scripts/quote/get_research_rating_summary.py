#!/usr/bin/env python3
"""
Get Rating Summary

Function: Get institution or analyst rating summary list for a stock, or rating details
          for a specific institution/analyst
Usage: python get_research_rating_summary.py [-h] [--rating-dimension-type RATING_DIMENSION_TYPE] [--uid UID] [--next-key NEXT_KEY] [--num NUM] [--json] code

API Limits:
- Max 30 requests per 30 seconds
- Supports US equities and REITs

Parameter Description:
- code: Stock code, e.g. US.AAPL
- --rating-dimension-type: Rating dimension: 1=Institution (default) 2=Analyst
- --uid: Empty=summary list; non-empty=rating details for specific institution/analyst
         (for analyst uid use with --rating-dimension-type 2)
- --next-key: Pagination key; omit for first page; "-1" means no more data
- --num: Number of results per page, default 10, range 1-20

Return Field Description:
- inst_rating_summary_list:    Institution rating summary list (no uid, rating_dimension_type=1);
                               each item contains institution_info and rating_item_list
                               (each containing rating/target_price/recommendation_date_str/rating_url)
- analyst_rating_summary_list: Analyst rating summary list (no uid, rating_dimension_type=2);
                               each item contains analyst_info and rating_item_list
- inst_rating_detail:          Institution rating detail (uid set, rating_dimension_type=1);
                               contains institution_info/analyst_info_list/rating_item_list
- analyst_rating_detail:       Analyst rating detail (uid set, rating_dimension_type=2);
                               contains analyst_info/rating_item_list
- next_key:                    Pagination key; "-1" means no more data
"""
import argparse
import json
import sys
import os as _os

import pandas as pd

sys.path.insert(0, _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..")))
from common import create_quote_context, check_ret, safe_close, is_empty, print_display_df

_SEP = "=" * 64
_DASH = "-" * 64

_RATING_LABEL = {
    1: "Sell",
    2: "Underperform",
    3: "Hold",
    4: "Buy",
    5: "Strong Buy",
}

_CHANGE_TYPE_LABEL = {0: "Unchanged", 1: "Upgraded", 2: "Downgraded", 3: "Initiated"}


def _rating_str(rating):
    if rating is None:
        return "-"
    return _RATING_LABEL.get(rating, str(rating))


def _parse_change_type(items):
    n = len(items)
    if n == 0:
        return 0
    if n == 1:
        return 3
    curr = items[0]
    prev = items[1]
    curr_r = curr.get("rating") or 0
    prev_r = prev.get("rating") or 0
    if curr_r != prev_r:
        return 1 if curr_r > prev_r else 2
    curr_p = curr.get("target_price") or 0
    prev_p = prev.get("target_price") or 0
    _EPS = 1e-9
    if curr_p and prev_p:
        diff = curr_p - prev_p
        if diff > _EPS:
            return 1
        if diff < -_EPS:
            return 2
    return 0


def _fmt_price(raw):
    if raw is None or raw == 0:
        return "-"
    return f"{raw:.3f}"


def _format_target_price(items):
    if not items:
        return "-"
    curr_p = items[0].get("target_price") or 0
    prev_p = None
    for it in items[1:]:
        p = it.get("target_price")
        if p:
            prev_p = p
            break
    if prev_p is not None:
        display_curr = curr_p if curr_p else prev_p
        return f"{_fmt_price(prev_p)}->{_fmt_price(display_curr)}"
    return _fmt_price(curr_p) if curr_p else "-"


def _print_inst_info(info, prefix="  "):
    if not info:
        return
    print(f"{prefix}Institution Name:    {info.get('institution_name', '-')}")
    print(f"{prefix}Institution En Name: {info.get('institution_en_name', '-')}")
    print(f"{prefix}Institution UID:     {info.get('institution_uid', '-')}")
    print(f"{prefix}Source:              {info.get('institution_source_name', '-')}")
    print(f"{prefix}Update Date:         {info.get('update_time_str', '-')}")


def _print_analyst_info(info, prefix="  "):
    if not info:
        return
    print(f"{prefix}Analyst Name:        {info.get('analyst_name', '-')}")
    print(f"{prefix}Analyst UID:         {info.get('analyst_uid', '-')}")
    stars = info.get("num_of_stars")
    if stars is not None:
        print(f"{prefix}Stars:               {stars}")
    success = info.get("success_rate")
    if success is not None:
        print(f"{prefix}Success Rate:        {float(success):.2f}%")
    excess = info.get("excess_return")
    if excess is not None:
        print(f"{prefix}Excess Return:       {float(excess):.2f}%")
    stock_success = info.get("stock_success_rate")
    if stock_success is not None:
        print(f"{prefix}Stock Success Rate:  {float(stock_success):.2f}%")
    stock_avg = info.get("stock_avg_return")
    if stock_avg is not None:
        print(f"{prefix}Stock Avg Return:    {float(stock_avg):.2f}%")
    update_str = info.get("update_time_str")
    if update_str:
        print(f"{prefix}Update Date:         {update_str}")
    inst = info.get("institution_info")
    if inst:
        print(f"{prefix}Institution:         {inst.get('institution_name', '-')} ({inst.get('institution_uid', '-')})")


def _inst_detail_items_df(items, analyst_info_list):
    stars_map = {an.get("analyst_uid", ""): an.get("num_of_stars", "-")
                 for an in analyst_info_list if an.get("analyst_uid")}
    rows = []
    for it in items:
        uid_val = it.get("analyst_uid", "-")
        rows.append({
            "Analyst Uid":        uid_val,
            "Stars":              stars_map.get(uid_val, "-"),
            "Rating":             _rating_str(it.get("rating")),
            "Target Price":       _fmt_price(it.get("target_price")),
            "Date":               it.get("recommendation_date_str", "-"),
            "Rating Url":         it.get("rating_url", "-"),
        })
    return pd.DataFrame(rows)


def _analyst_detail_items_df(items, num_of_stars):
    rows = []
    for it in items:
        rows.append({
            "Stars":        num_of_stars,
            "Rating":       _rating_str(it.get("rating")),
            "Target Price": _fmt_price(it.get("target_price")),
            "Date":         it.get("recommendation_date_str", "-"),
            "Rating Url":   it.get("rating_url", "-"),
        })
    return pd.DataFrame(rows)


def get_research_rating_summary(code, rating_dimension_type=None, uid=None, num=None,
                                next_key=None, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        ret, data = ctx.get_research_rating_summary(
            code,
            rating_dimension_type=rating_dimension_type,
            uid=uid,
            num=num,
            next_key=next_key,
        )
        check_ret(ret, data, ctx, "get rating summary")

        if is_empty(data):
            if output_json:
                print(json.dumps({"code": code, "data": []}))
            else:
                print("No data")
            return

        nk = data.get("next_key", "-1")

        def _count_items(d):
            n = 0
            n += len(d.get("inst_rating_summary_list", []))
            n += len(d.get("analyst_rating_summary_list", []))
            if d.get("inst_rating_detail"):
                n += 1
            if d.get("analyst_rating_detail"):
                n += 1
            return n

        total_items = _count_items(data)
        nk_display = "End(-1)" if nk == "-1" else (nk if nk else "End(-1)")

        if output_json:
            print(json.dumps({"code": code, "data": data}, ensure_ascii=False))
            return

        summary_list = data.get("inst_rating_summary_list", [])
        analyst_summary_list = data.get("analyst_rating_summary_list", [])
        inst_detail = data.get("inst_rating_detail")
        analyst_detail = data.get("analyst_rating_detail")

        if not any([summary_list, analyst_summary_list, inst_detail, analyst_detail]):
            print("No data")
            return

        print(_SEP)
        print(f"Rating Summary: {code}")
        print(_DASH)

        if summary_list:
            print(f"[Institution Rating Summary]  {len(summary_list)} institutions")
            rows = []
            for row in summary_list:
                inst_info = row.get("institution_info", {})
                items = row.get("rating_item_list", [])
                change_type = _parse_change_type(items)
                curr_rating = items[0].get("rating") if items else None
                rows.append({
                    "Institution Name":  inst_info.get("institution_name", "-"),
                    "Institution Uid":   inst_info.get("institution_uid", "-"),
                    "Rating":            _rating_str(curr_rating),
                    "Target Price":      _format_target_price(items),
                    "Change (1yr)":      f"{_CHANGE_TYPE_LABEL.get(change_type, change_type)}({len(items)})",
                    "Date":              items[0].get("recommendation_date_str", "-") if items else "-",
                })
            if rows:
                print_display_df(pd.DataFrame(rows), max_colwidth=60)
            else:
                print("  No rating entries")

        if analyst_summary_list:
            print(f"[Analyst Rating Summary]  {len(analyst_summary_list)} analysts")
            rows = []
            for row in analyst_summary_list:
                an_info = row.get("analyst_info", {})
                items = row.get("rating_item_list", [])
                change_type = _parse_change_type(items)
                curr_rating = items[0].get("rating") if items else None
                curr_item = items[0] if items else {}
                rows.append({
                    "Analyst Name":  an_info.get("analyst_name", "-"),
                    "Stars":         an_info.get("num_of_stars", "-"),
                    "Analyst Uid":   an_info.get("analyst_uid", "-"),
                    "Rating":        _rating_str(curr_rating),
                    "Target Price":  _format_target_price(items),
                    "Change (1yr)":  f"{_CHANGE_TYPE_LABEL.get(change_type, change_type)}({len(items)})",
                    "Date":          curr_item.get("recommendation_date_str", "-") if items else "-",
                    "Rating Url":    curr_item.get("rating_url", "-"),
                })
            if rows:
                print_display_df(pd.DataFrame(rows), max_colwidth=60)
            else:
                print("  No rating entries")

        if inst_detail:
            print("[Institution Rating Detail]")
            _print_inst_info(inst_detail.get("institution_info", {}))
            print()
            analyst_list = inst_detail.get("analyst_info_list", [])
            if analyst_list:
                print(f"  Analysts ({len(analyst_list)}):")
                for an in analyst_list:
                    stars = an.get("num_of_stars")
                    success = an.get("success_rate")
                    print(f"    - {an.get('analyst_name', '-')}  uid={an.get('analyst_uid', '-')}"
                          + (f"  stars={stars}" if stars is not None else "")
                          + (f"  success_rate={success}%" if success is not None else "")
                          + f"  updated={an.get('update_time_str', '-')}")
            items = inst_detail.get("rating_item_list", [])
            if items:
                print(f"\n  Rating Records ({len(items)}):")
                print_display_df(_inst_detail_items_df(items, analyst_list), max_colwidth=60)

        if analyst_detail:
            print("[Analyst Rating Detail]")
            an_info = analyst_detail.get("analyst_info", {})
            _print_analyst_info(an_info)
            items = analyst_detail.get("rating_item_list", [])
            if items:
                print(f"\n  Rating Records ({len(items)}):")
                print_display_df(_analyst_detail_items_df(items, an_info.get("num_of_stars", "-")), max_colwidth=60)

        print(_DASH)
        print(f"Count: {total_items}   --next-key: {nk_display}")
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
    parser = argparse.ArgumentParser(description="Get research rating summary with pagination support")
    parser.add_argument("code", help="Stock code, e.g. US.AAPL")
    parser.add_argument("--rating-dimension-type", type=int, default=None,
                        help="Rating dimension: 1=Institution (default) 2=Analyst")
    parser.add_argument("--uid", default=None,
                        help="Empty=summary list; non-empty=details for specific institution/analyst "
                             "(for analyst uid use with --rating-dimension-type 2)")
    parser.add_argument("--next-key", default=None, dest="next_key",
                        help='Pagination key; omit for first page; "-1" means no more data')
    parser.add_argument("--num", type=int, default=None,
                        help="Number of results per page, default 10, range 1-20")
    parser.add_argument("--json", action="store_true", dest="output_json",
                        help="Output in JSON format")
    args = parser.parse_args()
    get_research_rating_summary(
        args.code,
        rating_dimension_type=args.rating_dimension_type,
        uid=args.uid,
        num=args.num,
        next_key=args.next_key,
        output_json=args.output_json,
    )
