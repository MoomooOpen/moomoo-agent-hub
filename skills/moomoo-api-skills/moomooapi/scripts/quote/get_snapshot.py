#!/usr/bin/env python3
"""
Get Market Snapshot

Function: Get snapshot data for specified stocks (last price, OHLC, volume, etc.), no subscription required
Usage: python get_snapshot.py US.AAPL HK.00700

API Limits:
- Max 60 requests per 30 seconds
- Max 400 stock codes per request
- Under HK stock BMP permission, max 20 HK securities snapshots per request
- Under HK options/futures BMP permission, max 20 snapshots per request

Return Field Notes:
- update_time: Format yyyy-MM-dd HH:mm:ss, Beijing time for HK/A-shares, US Eastern time for US stocks
- turnover_rate/amplitude/bid_ask_ratio: Percentage fields, 20 corresponds to 20%
- pe_ratio/pb_ratio/pe_ttm_ratio/ey_ratio: Ratio fields, % sign not displayed by default
- total_market_val/circular_market_val: Unit: currency unit (e.g. HKD/USD/CNY)
- equity_valid: Underlying stock related fields have valid values only when True
- wrt_valid: Warrant related fields have valid values only when True
- option_valid: Option related fields have valid values only when True
- lot_size: Not available for index options
- price_spread: The price difference between adjacent price levels from ask price
- suspension: True indicates trading halt
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
    safe_get,
    safe_float,
    safe_int,
)


_SNAPSHOT_BATCH_SIZE = 400  # API limit: max 400 codes per request


def _parse_snapshot_row(row):
    """Parse a single snapshot row into a dict."""
    return {
        "code": safe_get(row, "code", default="N/A"),
        "name": safe_get(row, "name", default=""),
        "last_price": safe_float(safe_get(row, "last_price", default=0)),
        "open": safe_float(safe_get(row, "open_price", default=0)),
        "high": safe_float(safe_get(row, "high_price", default=0)),
        "low": safe_float(safe_get(row, "low_price", default=0)),
        "prev_close": safe_float(safe_get(row, "prev_close_price", default=0)),
        "volume": safe_int(safe_get(row, "volume", default=0)),
        "turnover": safe_float(safe_get(row, "turnover", default=0)),
        "bid": safe_float(safe_get(row, "bid_price", default=0)),
        "ask": safe_float(safe_get(row, "ask_price", default=0)),
        "price_spread": safe_float(safe_get(row, "price_spread", default=0)),
    }


def get_snapshot(codes, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()

        # Auto-batch: API limits 400 codes per call
        records = []
        for batch_start in range(0, len(codes), _SNAPSHOT_BATCH_SIZE):
            batch = codes[batch_start:batch_start + _SNAPSHOT_BATCH_SIZE]
            ret, data = ctx.get_market_snapshot(batch)
            check_ret(ret, data, ctx, "get market snapshot")
            if not is_empty(data):
                for i in range(len(data)):
                    row = data.iloc[i] if hasattr(data, "iloc") else data[i]
                    records.append(_parse_snapshot_row(row))

        if not records:
            if output_json:
                print(json.dumps({"data": []}))
            else:
                print("No data")
            return

        if output_json:
            print(json.dumps({"data": records}, ensure_ascii=False))
        else:
            print("=" * 70)
            print("Market Snapshot")
            print("=" * 70)
            for r in records:
                print(f"\n  {r['code']}  {r['name']}")
                print(f"    Last: {r['last_price']}  Open: {r['open']}  High: {r['high']}  Low: {r['low']}  Prev Close: {r['prev_close']}")
                print(f"    Volume: {r['volume']}  Turnover: {r['turnover']}  Bid: {r['bid']}  Ask: {r['ask']}  Spread: {r['price_spread']}")
            print("\n" + "=" * 70)

    except Exception as e:
        if output_json:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))
        else:
            print(f"Error: {e}")
        sys.exit(1)
    finally:
        safe_close(ctx)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get market snapshot (no subscription required)")
    parser.add_argument("codes", nargs="+", help="Stock codes, e.g. US.AAPL HK.00700")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output in JSON format")
    args = parser.parse_args()
    get_snapshot(args.codes, args.output_json)
