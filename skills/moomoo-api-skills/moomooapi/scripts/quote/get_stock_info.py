#!/usr/bin/env python3
"""
Get Stock Basic Info

Function: Get basic information for specified stocks (name, lot size, security type, listing date, etc.)
Usage: python get_stock_info.py US.AAPL,HK.00700

API Limits:
- Max 10 requests per 30 seconds
- Max 200 results per request

Parameter Notes:
- code_list: If a stock list is provided, only returns info for specified stocks; otherwise returns all

Return Field Notes:
- listing_date: This field is no longer maintained
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
    format_enum,
    df_to_records,
)


def get_stock_info(codes_str, output_json=False):
    codes = [c.strip() for c in codes_str.split(",") if c.strip()]
    ctx = None
    try:
        ctx = create_quote_context()
        ret, data = ctx.get_market_snapshot(codes)
        check_ret(ret, data, ctx, "get stock info")

        if is_empty(data):
            if output_json:
                print(json.dumps({"data": []}))
            else:
                print("No data")
            return

        records = []
        for i in range(len(data)):
            row = data.iloc[i] if hasattr(data, "iloc") else data[i]
            records.append({
                "code": safe_get(row, "code", default=""),
                "name": safe_get(row, "name", default=""),
                "lot_size": safe_int(safe_get(row, "lot_size", default=0)),
                "stock_type": format_enum(safe_get(row, "stock_type", "sec_type", default="")),
                "listing_date": safe_get(row, "listing_date", default=""),
                "last_price": safe_float(safe_get(row, "last_price", default=0)),
                "market_val": safe_float(safe_get(row, "market_val", default=0)),
            })

        if output_json:
            print(json.dumps({"data": records}, ensure_ascii=False))
        else:
            print("=" * 70)
            print("Stock Basic Info")
            print("=" * 70)
            for r in records:
                print(f"\n  {r['code']}  {r['name']}")
                print(f"    Lot Size: {r['lot_size']}  Type: {r['stock_type']}  Listing Date: {r['listing_date']}")
                print(f"    Last Price: {r['last_price']}  Market Value: {r['market_val']}")
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
    parser = argparse.ArgumentParser(description="Get stock basic info")
    parser.add_argument("codes", help="Stock codes (comma-separated), e.g. US.AAPL,HK.00700")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output in JSON format")
    args = parser.parse_args()
    get_stock_info(args.codes, args.output_json)
