#!/usr/bin/env python3
"""
Get Valid Combo (Combo-able) Event List

Function: Get combo-able event list, returning the combo-able contracts under each event and the MVC underlying (must be passed to RFQ), no subscription required
Usage: python get_valid_combo_list.py [--category Sports] [--count 20] [--next-page KEY] [--json]

API: OpenQuoteContext.get_valid_combo_list(category=None, competition=None, series=None,
      next_page=None, count=None)
Return: (ret, data, mvc, next_page); data is a DataFrame (event_code / event_name / combo_contracts /
        series_code / category / competition / competition_scope); mvc is the MVC underlying string

Pagination: only the first page is returned by default; to continue, pass --next-page
Note: mvc must be passed through to request_combo_quotes.py for Combo RFQ
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
    to_jsonable,
    assert_event_contract_support,
)


def get_valid_combo_list(category=None, competition=None, series=None,
                         next_page=None, count=None, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        assert_event_contract_support(ctx, output_json=output_json)

        ret, data, mvc, page = ctx.get_valid_combo_list(
            category=category, competition=competition, series=series,
            next_page=next_page, count=count)
        check_ret(ret, data, ctx, "Get valid combo list")

        records = [] if is_empty(data) else df_to_records(data)

        if output_json:
            print(json.dumps({
                "data": records,
                "mvc": to_jsonable(mvc, default=""),
                "next_page": page or "",
            }, ensure_ascii=False))
        else:
            print("=" * 70)
            print("Valid Combo Event List")
            print("=" * 70)
            if records:
                cols = [c for c in ['event_code', 'event_name', 'combo_contracts',
                                    'series_code', 'competition', 'competition_scope']
                        if c in data.columns]
                print_display_df(data[cols], max_colwidth=40)
                print(f"\nTotal {len(data)} combo-able events")
            else:
                print("No data")
            print(f"mvc: {mvc or '(none)'}  <- pass through to request_combo_quotes")
            print(f"next_page: {page or '(no more)'}")
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
    parser = argparse.ArgumentParser(description="Get valid combo event list and mvc (no subscription required)")
    parser.add_argument("--category", default=None, help="Top-level category, e.g. Sports")
    parser.add_argument("--competition", default=None, help="Competition filter")
    parser.add_argument("--series", default=None, help="Series underlying filter, e.g. EC.xxx")
    parser.add_argument("--next-page", default=None, help="Pagination token; omit on first page, pass previous next_page to continue")
    parser.add_argument("--count", type=int, default=None, help="Max number returned per page, default 200")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output JSON format")
    args = parser.parse_args()
    get_valid_combo_list(
        category=args.category, competition=args.competition, series=args.series,
        next_page=args.next_page, count=args.count, output_json=args.output_json)
