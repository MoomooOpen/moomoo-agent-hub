#!/usr/bin/env python3
"""
Get Stock's Plates (Sectors)

Function: Query all plates (sectors) a given stock belongs to
Usage: python get_owner_plate.py HK.00700 US.AAPL

API limits:
- Max 10 requests per 30 seconds
- Max 200 stock codes per request
- Only supports stocks and indices

Return field notes:
- plate_type: Industry plate or concept plate
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
    format_enum,
)


def get_owner_plate(codes, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        ret, data = ctx.get_owner_plate(codes)
        check_ret(ret, data, ctx, "get owner plates")

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
                "plate_code": safe_get(row, "plate_code", default=""),
                "plate_name": safe_get(row, "plate_name", default=""),
                "plate_type": format_enum(safe_get(row, "plate_type", default="")),
            })

        if output_json:
            print(json.dumps({"data": records}, ensure_ascii=False))
        else:
            print("=" * 60)
            print("Stock's Plates (Sectors)")
            print("=" * 60)
            current_code = None
            for r in records:
                if r["code"] != current_code:
                    current_code = r["code"]
                    print(f"\n  {current_code}:")
                print(f"    {r['plate_code']:<15} {r['plate_name']:<20} [{r['plate_type']}]")
            print("\n" + "=" * 60)

    except Exception as e:
        if output_json:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))
        else:
            print(f"Error: {e}")
        sys.exit(1)
    finally:
        safe_close(ctx)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get stock's plates (sectors)")
    parser.add_argument("codes", nargs="+", help="Stock codes, e.g. HK.00700 US.AAPL")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output in JSON format")
    args = parser.parse_args()
    get_owner_plate(args.codes, args.output_json)
