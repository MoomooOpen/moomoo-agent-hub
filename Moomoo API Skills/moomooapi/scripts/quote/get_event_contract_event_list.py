#!/usr/bin/env python3
"""
Get Prediction Market Event List

Function: Get Event list by Series code, supports status filter and pagination, no subscription required
Usage: python get_event_contract_event_list.py EC.KXUFCVICROUND.SERIES [--count 20] [--status EVENT_ACTIVE] [--next-page KEY] [--json]

API: OpenQuoteContext.get_event_contract_event_list(series_code, status=None, next_page=None, count=None)
Return: (ret, DataFrame, next_page); DataFrame columns event_code / event_name / event_sub_name /
        status / series_code / start_date / end_date / category / tags / mutually_exclusive /
        competition / competition_scope

Pagination: only the first page is returned by default; to continue, pass the previous next_page via --next-page
            (empty string means no more)
Status: --status only accepts event-level status (EVENT_INITIALIZED/EVENT_ACTIVE/EVENT_CLOSED/EVENT_SETTLED/
        EVENT_CANCELED/EVENT_FINALIZED/EVENT_ABNORMAL)
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
    parse_ec_status,
    assert_event_contract_support,
)


_EVENT_STATUS_CHOICES = [
    "EVENT_INITIALIZED", "EVENT_ACTIVE", "EVENT_CLOSED", "EVENT_SETTLED",
    "EVENT_CANCELED", "EVENT_FINALIZED", "EVENT_ABNORMAL",
]


def get_event_contract_event_list(series_code, status=None, next_page=None, count=None, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        assert_event_contract_support(ctx, output_json=output_json)

        status_enum = parse_ec_status(status) if status else None

        ret, data, page = ctx.get_event_contract_event_list(
            series_code, status=status_enum, next_page=next_page, count=count)
        check_ret(ret, data, ctx, "Get prediction market event list")

        records = [] if is_empty(data) else df_to_records(data)

        if output_json:
            print(json.dumps({"data": records, "next_page": page or ""}, ensure_ascii=False))
        else:
            print("=" * 70)
            print(f"Prediction Market Event List - {series_code}")
            print("=" * 70)
            if records:
                cols = [c for c in ['event_code', 'event_name', 'status', 'start_date',
                                    'end_date', 'competition', 'competition_scope']
                        if c in data.columns]
                print_display_df(data[cols], max_colwidth=42)
                print(f"\nTotal {len(data)} events")
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
    parser = argparse.ArgumentParser(description="Get prediction market event list (no subscription required)")
    parser.add_argument("series_code", help="Series code, e.g. EC.KXUFCVICROUND.SERIES")
    parser.add_argument("--status", default=None, choices=_EVENT_STATUS_CHOICES,
                        help="Event status filter, e.g. EVENT_ACTIVE")
    parser.add_argument("--next-page", default=None, help="Pagination token; omit on first page, pass previous next_page to continue")
    parser.add_argument("--count", type=int, default=None, help="Max number returned, default 200")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output JSON format")
    args = parser.parse_args()
    get_event_contract_event_list(
        series_code=args.series_code, status=args.status,
        next_page=args.next_page, count=args.count, output_json=args.output_json)
