#!/usr/bin/env python3
"""
Get Plate List

Function: Retrieve the plate (sector) list for a given market (industry/concept/region), with optional keyword filtering
Usage: python get_plate_list.py --market HK --type CONCEPT --keyword tech

API limits:
- Max 10 requests per 30 seconds

Parameter notes:
- market: No distinction between SH and SZ; entering either returns sub-plates for the entire SH/SZ market
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
    Market,
    Plate,
)

MARKET_MAP = {
    "HK": Market.HK,
    "US": Market.US,
    "SH": Market.SH,
    "SZ": Market.SZ,
}

PLATE_CLASS_MAP = {
    "ALL": Plate.ALL,
    "INDUSTRY": Plate.INDUSTRY,
    "REGION": Plate.REGION,
    "CONCEPT": Plate.CONCEPT,
    "OTHER": Plate.OTHER,
}


def get_plate_list(market="HK", plate_type="ALL", keyword=None, limit=50, output_json=False):
    market_enum = MARKET_MAP.get(market.upper(), Market.HK)
    plate_class = PLATE_CLASS_MAP.get(plate_type.upper(), Plate.ALL)

    ctx = None
    try:
        ctx = create_quote_context()
        ret, data = ctx.get_plate_list(market_enum, plate_class)
        check_ret(ret, data, ctx, "get plate list")

        if is_empty(data):
            if output_json:
                print(json.dumps({"data": []}))
            else:
                print("No data")
            return

        records = []
        for i in range(len(data)):
            row = data.iloc[i] if hasattr(data, "iloc") else data[i]
            plate_name = safe_get(row, "plate_name", "stock_name", default="")
            plate_code = safe_get(row, "code", default="")

            if keyword and keyword.lower() not in str(plate_name).lower():
                continue

            records.append({
                "code": plate_code,
                "name": plate_name,
            })

            if len(records) >= limit:
                break

        if output_json:
            print(json.dumps({"market": market, "type": plate_type, "data": records}, ensure_ascii=False))
        else:
            print("=" * 50)
            print(f"Plate List: {market} - {plate_type}" + (f" (Keyword: {keyword})" if keyword else ""))
            print("=" * 50)
            for r in records:
                print(f"  {r['code']:<20} {r['name']}")
            print(f"\n  Total {len(records)} plates")
            print("=" * 50)

    except Exception as e:
        if output_json:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))
        else:
            print(f"Error: {e}")
        sys.exit(1)
    finally:
        safe_close(ctx)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get plate list")
    parser.add_argument("--market", choices=["HK", "US", "SH", "SZ"], default="HK", help="Market (default: HK)")
    parser.add_argument("--type", dest="plate_type", choices=["ALL", "INDUSTRY", "REGION", "CONCEPT", "OTHER"],
                        default="ALL", help="Plate type (default: ALL)")
    parser.add_argument("--keyword", "-k", default=None, help="Keyword to filter plate names")
    parser.add_argument("--limit", type=int, default=50, help="Limit on number of results (default: 50)")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output in JSON format")
    args = parser.parse_args()
    get_plate_list(args.market, args.plate_type, args.keyword, args.limit, args.output_json)
