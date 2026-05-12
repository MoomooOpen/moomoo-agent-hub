#!/usr/bin/env python3
"""
Get Plate Constituents

Function: Retrieve the constituent stock list for a given plate, supporting plate codes or built-in aliases
Usage: python get_plate_stock.py HK.BK1910
      python get_plate_stock.py hsi
      python get_plate_stock.py --list-aliases

API limits:
- Max 10 requests per 30 seconds

Parameter notes:
- plate_code: First obtain the plate code via get_plate_list
- ascend: True for ascending order, False for descending order
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
)

# Built-in plate aliases
PLATE_ALIASES = {
    # HK indices
    "hsi": ("HK.800000", "Hang Seng Index"),
    "hscei": ("HK.800100", "H-shares Index"),
    "hstech": ("HK.800700", "Hang Seng Tech"),
    # HK concepts
    "hk_ai": ("HK.BK1910", "AI Concept"),
    "hk_chip": ("HK.LIST22912", "Chip Concept"),
    "hk_ev": ("HK.LIST22910", "New Energy Vehicles"),
    "hk_bank": ("HK.LIST1239", "Mainland Bank Stocks"),
    "hk_property": ("HK.LIST1234", "Mainland Property Stocks"),
    "hk_biotech": ("HK.LIST22911", "Biotech & Pharma"),
    "hk_internet": ("HK.LIST22886", "Internet Stocks"),
    # US tech
    "us_ai": ("US.LIST2136", "AI Concept"),
    "us_chip": ("US.LIST20077", "Semiconductors"),
    "us_cloud": ("US.LIST2520", "SaaS Concept"),
    "us_cybersecurity": ("US.LIST2570", "Cybersecurity"),
    # US popular
    "us_chinese": ("US.LIST2517", "Chinese ADRs"),
}


def list_aliases():
    """List all available aliases"""
    result = {}
    for alias, (code, desc) in PLATE_ALIASES.items():
        result[alias] = {"code": code, "description": desc}
    return result


def get_plate_stock(plate_code_or_alias, limit=30, output_json=False):
    # Resolve alias
    if plate_code_or_alias in PLATE_ALIASES:
        plate_code, plate_desc = PLATE_ALIASES[plate_code_or_alias]
    else:
        plate_code = plate_code_or_alias
        plate_desc = plate_code

    ctx = None
    try:
        ctx = create_quote_context()
        ret, data = ctx.get_plate_stock(plate_code)
        check_ret(ret, data, ctx, "get plate constituents")

        if is_empty(data):
            if output_json:
                print(json.dumps({"plate": plate_code, "data": []}))
            else:
                print("No data")
            return

        records = []
        n = min(len(data), limit) if limit > 0 else len(data)
        for i in range(n):
            row = data.iloc[i] if hasattr(data, "iloc") else data[i]
            records.append({
                "code": safe_get(row, "code", default=""),
                "name": safe_get(row, "stock_name", default=""),
            })

        if output_json:
            print(json.dumps({"plate": plate_code, "plate_desc": plate_desc, "data": records}, ensure_ascii=False))
        else:
            print("=" * 50)
            print(f"Plate Constituents: {plate_desc} ({plate_code})")
            print("=" * 50)
            for r in records:
                print(f"  {r['code']:<15} {r['name']}")
            print(f"\n  Showing {len(records)} / {len(data)} stocks")
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
    parser = argparse.ArgumentParser(description="Get plate constituents")
    parser.add_argument("plate", nargs="?", default=None, help="Plate code or alias (e.g. HK.BK1910 or hsi)")
    parser.add_argument("--list-aliases", action="store_true", help="List all supported aliases")
    parser.add_argument("--limit", type=int, default=30, help="Limit on number of results (default: 30)")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output in JSON format")
    args = parser.parse_args()

    if args.list_aliases:
        aliases = list_aliases()
        if args.output_json:
            print(json.dumps(aliases, ensure_ascii=False))
        else:
            print("=" * 50)
            print("Supported Plate Aliases")
            print("=" * 50)
            for alias, info in aliases.items():
                print(f"  {alias:<20} {info['code']:<15} {info['description']}")
            print("=" * 50)
    elif args.plate:
        get_plate_stock(args.plate, args.limit, args.output_json)
    else:
        parser.print_help()
