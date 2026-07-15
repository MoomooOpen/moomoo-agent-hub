#!/usr/bin/env python3
"""
Fetch Event Contract Historical K-line

Function: Fetch event contract historical K-line; no need to download historical data first, and no subscription to the corresponding K-line type is required; pagination is handled automatically
Usage: python request_history_event_contract_kline.py EC.KXNFLAFCCHAMP-27-CIN --start 2026-07-05 --end 2026-07-09 --pre-side YES --ktype K_DAY [--max-count 10] [--page-req-key KEY] [--json]

API: OpenQuoteContext.request_history_event_contract_kline(code, start=None, end=None,
      pre_side=None, ktype=KLType.K_DAY, kline_source=None, max_count=1000, page_req_key=None)
Return: (ret, DataFrame, page_req_key); columns code / pre_side / name / time_key / open / high / low / close / volume

API Limits:
- ktype only supports K_1M/K_5M/K_60M/K_DAY
- Historical K-line requires no subscription and uses the historical K-line quota; max 1000 bars per packet; when max_count exceeds it, pagination loops automatically (the public method wraps the loop)
- When both start/end are omitted, default end=today, start=end-365 days

start/end combos: str+str / None+str / str+None / None+None
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
    parse_pred_side,
    parse_ec_kline_source,
    EC_KLTYPE_CHOICES,
    KLType,
    ECKlineSource,
    assert_event_contract_support,
)


_KLTYPE_KLTYPE_MAP = {
    "K_1M": KLType.K_1M,
    "K_5M": KLType.K_5M,
    "K_60M": KLType.K_60M,
    "K_DAY": KLType.K_DAY,
}


def request_history_event_contract_kline(code, start=None, end=None, ktype="K_DAY",
                                         pre_side=None, kline_source=None, max_count=1000,
                                         page_req_key=None, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        assert_event_contract_support(ctx, output_json=output_json)

        ktype_key = str(ktype).upper()
        if ktype_key not in _KLTYPE_KLTYPE_MAP:
            raise ValueError(f"ktype only supports {EC_KLTYPE_CHOICES}, got: {ktype}")
        kl_type = _KLTYPE_KLTYPE_MAP[ktype_key]

        pre_side_enum = parse_pred_side(pre_side)
        kline_source_enum = parse_ec_kline_source(kline_source)

        # Historical K-line requires no subscription; fetch directly.
        ret, data, next_page_req_key = ctx.request_history_event_contract_kline(
            code, start=start, end=end, pre_side=pre_side_enum, ktype=kl_type,
            kline_source=kline_source_enum, max_count=max_count, page_req_key=page_req_key)
        check_ret(ret, data, ctx, "Fetch event contract historical K-line")

        records = [] if is_empty(data) else df_to_records(data)

        if output_json:
            print(json.dumps({
                "data": records,
                "page_req_key": next_page_req_key or "",
            }, ensure_ascii=False))
        else:
            print("=" * 70)
            print(f"Event Contract Historical K-line - {code} ({ktype_key})")
            print(f"Range: {start or '(default)'} ~ {end or '(default)'}")
            print("=" * 70)
            if records:
                cols = [c for c in ['code', 'pre_side', 'name', 'time_key', 'open',
                                    'high', 'low', 'close', 'volume']
                        if c in data.columns]
                print_display_df(data[cols], max_colwidth=30)
                print(f"\nTotal {len(data)} bars")
            else:
                print("No data")
            print(f"page_req_key: {next_page_req_key or '(no more)'}")
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
    parser = argparse.ArgumentParser(description="Fetch event contract historical K-line (no subscription needed)")
    parser.add_argument("code", help="Event contract code")
    parser.add_argument("--start", default=None, help="Start time, e.g. 2025-06-20")
    parser.add_argument("--end", default=None, help="End time, e.g. 2025-07-20")
    parser.add_argument("--ktype", choices=EC_KLTYPE_CHOICES, default="K_DAY",
                        help="K-line type (only K_1M/K_5M/K_60M/K_DAY, default K_DAY)")
    parser.add_argument("--pre-side", choices=["YES", "NO"], default=None, help="Contract side")
    parser.add_argument("--kline-source", choices=["ORDER_BOOK_YES"], default=None,
                        help="K-line source ORDER_BOOK_YES; takes precedence over pre-side")
    parser.add_argument("--max-count", type=int, default=1000,
                        help="Max number of data points for this request; None means all")
    parser.add_argument("--page-req-key", default=None, help="Pagination continuation key; omit on first request")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output JSON format")
    args = parser.parse_args()
    request_history_event_contract_kline(
        code=args.code, start=args.start, end=args.end, ktype=args.ktype,
        pre_side=args.pre_side, kline_source=args.kline_source, max_count=args.max_count,
        page_req_key=args.page_req_key,
        output_json=args.output_json)
