#!/usr/bin/env python3
"""
Get Prediction Market Snapshot

Function: Batch get prediction market real-time snapshot (last price, cumulative volume, YES/NO bid/ask, open interest, etc.), no subscription required
Usage: python get_event_contract_snapshot.py EC.KXODIMATCH-26JUL140600INDENG-IND --json
       python get_event_contract_snapshot.py EC.xxx1 EC.xxx2 [--json]

API: OpenQuoteContext.get_event_contract_snapshot(code_list)
Return: DataFrame; columns code / name / event_code / yes_sub_title / no_sub_title / status /
        price / cumulative_volume / yes_bid / yes_bid_size / yes_ask / yes_ask_size /
        no_bid / no_bid_size / no_ask / no_ask_size / last_trade_time / volume_24h / open_interest

Note: snapshot only returns the first bid/ask level; for multi-level depth use get_event_contract_order_book.py
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


def get_event_contract_snapshot(code_list, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        assert_event_contract_support(ctx, output_json=output_json)

        if isinstance(code_list, str):
            code_list = [code_list]

        ret, data = ctx.get_event_contract_snapshot(code_list)
        check_ret(ret, data, ctx, "Get prediction market snapshot")

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
            print("Prediction Market Snapshot")
            print("=" * 70)
            cols = [c for c in ['code', 'name', 'status', 'price', 'cumulative_volume',
                                'yes_bid', 'yes_ask', 'no_bid', 'no_ask',
                                'last_trade_time', 'volume_24h', 'open_interest']
                    if c in data.columns]
            print_display_df(data[cols], max_colwidth=30)
            print(f"\nTotal {len(data)} contracts")
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
    parser = argparse.ArgumentParser(description="Get prediction market snapshot (no subscription required)")
    parser.add_argument("codes", nargs="+", help="Prediction market contract codes, e.g. EC.KXODIMATCH-26JUL140600INDENG-IND")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output JSON format")
    args = parser.parse_args()
    get_event_contract_snapshot(args.codes, args.output_json)
