#!/usr/bin/env python3
"""
Get Prediction Market (Contract) List

Function: Get contract list by Event code, including contract type, times, status, result and trading attributes, no subscription required
Usage: python get_event_contract.py EC.KXUFCVICROUND-26JUL11SAIPIM.EVENT [--count 20] [--next-page KEY] [--json]

API: OpenQuoteContext.get_event_contract(event_code, next_page=None, count=None)
Return: (ret, data, next_page); data is a dict {'contract_list': DataFrame, 'recommend_contracts': list[dict]}
        contract_list columns: contract_code / event_code / series_code / contract_type / title /
        yes_sub_title / open_time / close_time / determination_time / settled_time /
        latest_expiration_time / status / result / settlement_value / expiration_value /
        volume / can_close_early / tick_size / category / tag

Pagination: only the first page is returned by default; to continue, pass the previous next_page via --next-page
Note: contract_code (i.e. EC.xxx) can be used as the code for snapshot/orderbook/kline/ticker
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


def get_event_contract(event_code, next_page=None, count=None, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        assert_event_contract_support(ctx, output_json=output_json)

        ret, data, page = ctx.get_event_contract(
            event_code, next_page=next_page, count=count)
        check_ret(ret, data, ctx, "Get prediction market contract list")

        contract_df = data.get("contract_list") if isinstance(data, dict) else None
        recommends = data.get("recommend_contracts", []) if isinstance(data, dict) else []
        records = [] if is_empty(contract_df) else df_to_records(contract_df)
        recommend_list = [to_jsonable(r) for r in recommends] if recommends else []

        if output_json:
            print(json.dumps({
                "contract_list": records,
                "recommend_contracts": recommend_list,
                "next_page": page or "",
            }, ensure_ascii=False))
        else:
            print("=" * 70)
            print(f"Prediction Market Contract List - {event_code}")
            print("=" * 70)
            if records:
                cols = [c for c in ['contract_code', 'contract_type', 'title', 'status',
                                    'result', 'volume', 'tick_size']
                        if c in contract_df.columns]
                print_display_df(contract_df[cols], max_colwidth=42)
                print(f"\nTotal {len(contract_df)} contracts")
            else:
                print("No data")
            if recommend_list:
                print(f"\nRecommend contracts: {[r.get('contract_code', r) for r in recommend_list]}")
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
    parser = argparse.ArgumentParser(description="Get prediction market contract list (no subscription required)")
    parser.add_argument("event_code", help="Event code, e.g. EC.KXUFCVICROUND-26JUL11SAIPIM.EVENT")
    parser.add_argument("--next-page", default=None, help="Pagination token; omit on first page, pass previous next_page to continue")
    parser.add_argument("--count", type=int, default=None, help="Max number returned per page, default 100, max 1000")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output JSON format")
    args = parser.parse_args()
    get_event_contract(
        event_code=args.event_code, next_page=args.next_page,
        count=args.count, output_json=args.output_json)
