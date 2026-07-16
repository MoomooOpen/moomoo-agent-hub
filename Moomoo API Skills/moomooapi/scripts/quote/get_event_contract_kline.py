#!/usr/bin/env python3
"""
Get Prediction Market Real-time K-line

Function: Get prediction market real-time K-line (contract-level trade-price K-line or YES sub-contract order-book K-line); requires subscribing to the corresponding K-line type first
Usage: python get_event_contract_kline.py EC.KXODIMATCH-26JUL140600INDENG-IND --ktype K_DAY --pre-side YES [--kline-source ORDER_BOOK_YES] [--max-count 10] [--no-auto-subscribe] [--json]

API: OpenQuoteContext.get_event_contract_kline(code, pre_side=None, ktype=KLType.K_DAY,
      kline_source=None, max_count=1000)
Return: DataFrame; columns code / pre_side / name / time_key / open / high / low / close / volume

API Limits:
- ktype only supports K_1M/K_5M/K_60M/K_DAY; others raise an error
- Must subscribe to the corresponding K-line type before querying, otherwise error "subscribe KL_Day data first"
- kline_source takes precedence over pre_side; once kline_source is set, pre_side is resolved by the backend
- pre_side is only needed when kline_source=None (contract-level K-line)
- The script auto-subscribes by default; use --no-auto-subscribe to skip when already subscribed
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
    SubType,
    KLType,
    ECKlineSource,
    assert_event_contract_support,
    ensure_event_contract_subscribed,
)


_KLTYPE_SUBTYPE_MAP = {
    "K_1M": SubType.K_1M,
    "K_5M": SubType.K_5M,
    "K_60M": SubType.K_60M,
    "K_DAY": SubType.K_DAY,
}

_KLTYPE_KLTYPE_MAP = {
    "K_1M": KLType.K_1M,
    "K_5M": KLType.K_5M,
    "K_60M": KLType.K_60M,
    "K_DAY": KLType.K_DAY,
}


def get_event_contract_kline(code, ktype="K_DAY", pre_side=None, kline_source=None,
                             max_count=1000, auto_subscribe=True, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        assert_event_contract_support(ctx, output_json=output_json)

        ktype_key = str(ktype).upper()
        if ktype_key not in _KLTYPE_KLTYPE_MAP:
            raise ValueError(f"ktype only supports {EC_KLTYPE_CHOICES}, got: {ktype}")
        kl_type = _KLTYPE_KLTYPE_MAP[ktype_key]
        sub_type = _KLTYPE_SUBTYPE_MAP[ktype_key]

        pre_side_enum = parse_pred_side(pre_side)
        kline_source_enum = parse_ec_kline_source(kline_source)

        # Auto-subscribe the corresponding K-line type before querying
        # (already-subscribed is skipped silently). Pass kline_source_list through to
        # keep it consistent with the query's kline_source, otherwise the subscription
        # is for contract-level K-line and querying YES order-book K-line fails.
        if auto_subscribe:
            src_list = [kline_source_enum] if kline_source_enum is not None else None
            ensure_event_contract_subscribed(ctx, code, sub_type,
                                             output_json=output_json,
                                             kline_source_list=src_list,
                                             action="Subscribe prediction market K-line")

        ret, data = ctx.get_event_contract_kline(
            code, pre_side=pre_side_enum, ktype=kl_type,
            kline_source=kline_source_enum, max_count=max_count)
        check_ret(ret, data, ctx, "Get prediction market K-line")

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
            print(f"Prediction Market K-line - {code} ({ktype_key})")
            print("=" * 70)
            cols = [c for c in ['code', 'pre_side', 'name', 'time_key', 'open',
                                'high', 'low', 'close', 'volume']
                    if c in data.columns]
            print_display_df(data[cols], max_colwidth=30)
            print(f"\nTotal {len(data)} bars")
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
    parser = argparse.ArgumentParser(description="Get prediction market real-time K-line (requires corresponding K-line subscription)")
    parser.add_argument("code", help="Prediction market contract code, e.g. EC.KXODIMATCH-26JUL140600INDENG-IND")
    parser.add_argument("--ktype", choices=EC_KLTYPE_CHOICES, default="K_DAY",
                        help="K-line type (only K_1M/K_5M/K_60M/K_DAY, default K_DAY)")
    parser.add_argument("--pre-side", choices=["YES", "NO"], default=None,
                        help="Contract side (needed for contract-level K-line when kline_source is unset)")
    parser.add_argument("--kline-source", choices=["ORDER_BOOK_YES"], default=None,
                        help="K-line source ORDER_BOOK_YES (YES sub-contract order-book K-line); takes precedence over pre-side")
    parser.add_argument("--max-count", type=int, default=1000, help="Max number of bars, up to 1000")
    parser.add_argument("--no-auto-subscribe", action="store_true",
                        help="Do not auto-subscribe (use when already subscribed)")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output JSON format")
    args = parser.parse_args()
    get_event_contract_kline(
        code=args.code, ktype=args.ktype, pre_side=args.pre_side,
        kline_source=args.kline_source, max_count=args.max_count,
        auto_subscribe=not args.no_auto_subscribe, output_json=args.output_json)
