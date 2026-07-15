#!/usr/bin/env python3
"""
Get Event Contract Milestone List

Function: Get milestone time points (e.g. a match) for sport-type event contracts, supports category/competition/related-event filters and pagination, no subscription required
Usage: python get_event_contract_milestone_list.py [--category Sports] [--competition "FIFA World Cup"] [--related-event EC.xxx] [--count 20] [--next-page KEY] [--json]

API: OpenQuoteContext.get_event_contract_milestone_list(category=None, competition=None,
      related_event=None, next_page=None, count=None)
Return: (ret, DataFrame, next_page); columns milestone_code / title / category / type / start_date /
        end_date / primary_event_code / related_events / notification_message

Pagination: only the first page is returned by default; to continue, pass --next-page
Note: competition values must be obtained first via filter_competition.py
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


def get_event_contract_milestone_list(category=None, competition=None, related_event=None,
                                      next_page=None, count=None, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        assert_event_contract_support(ctx, output_json=output_json)

        ret, data, page = ctx.get_event_contract_milestone_list(
            category=category, competition=competition, related_event=related_event,
            next_page=next_page, count=count)
        check_ret(ret, data, ctx, "Get event contract milestone list")

        records = [] if is_empty(data) else df_to_records(data)

        if output_json:
            print(json.dumps({"data": records, "next_page": page or ""}, ensure_ascii=False))
        else:
            print("=" * 70)
            print("Event Contract Milestone List")
            print("=" * 70)
            if records:
                cols = [c for c in ['milestone_code', 'title', 'type', 'start_date',
                                    'end_date', 'primary_event_code', 'notification_message']
                        if c in data.columns]
                print_display_df(data[cols], max_colwidth=38)
                print(f"\nTotal {len(data)} milestones")
            else:
                print("No data")
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
    parser = argparse.ArgumentParser(description="Get event contract milestone list (no subscription required)")
    parser.add_argument("--category", default=None, help="Top-level category, e.g. Sports")
    parser.add_argument("--competition", default=None, help="Competition name (from filter_competition), e.g. FIFA World Cup")
    parser.add_argument("--related-event", default=None, help="Related event code, e.g. EC.xxx")
    parser.add_argument("--next-page", default=None, help="Pagination token; omit on first page, pass previous next_page to continue")
    parser.add_argument("--count", type=int, default=None, help="Max number returned, default 200")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output JSON format")
    args = parser.parse_args()
    get_event_contract_milestone_list(
        category=args.category, competition=args.competition,
        related_event=args.related_event, next_page=args.next_page,
        count=args.count, output_json=args.output_json)
