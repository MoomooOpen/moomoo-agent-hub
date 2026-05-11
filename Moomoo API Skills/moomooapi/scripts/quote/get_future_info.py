#!/usr/bin/env python3
"""
Get Future Contract Info

Function: Get detailed information for futures contracts
Usage: python get_future_info.py HK.MCHmain HK.MCH2501

API Limits:
- Max 60 requests per 30 seconds
- Max 200 codes per request

Return Field Description:
- last_trade_time: Last trading time
- owner_code: Underlying code (main continuous contract maps to current month contract code)
- exchange: Exchange
- contract_size/contract_size_unit: Contract size and unit
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
)


def get_future_info(codes, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        ret, data = ctx.get_future_info(codes)
        check_ret(ret, data, ctx, "Get future info")

        if is_empty(data):
            if output_json:
                print(json.dumps({"data": []}))
            else:
                print("No future info data")
            return

        if output_json:
            print(json.dumps({"data": df_to_records(data)}, ensure_ascii=False))
        else:
            print("=" * 70)
            print("Future Contract Info")
            print("=" * 70)
            print(data.to_string(index=False))
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
    parser = argparse.ArgumentParser(description="Get future contract info")
    parser.add_argument("codes", nargs="+", help="Future codes, e.g. HK.MCHmain HK.MCH2501")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output in JSON format")
    args = parser.parse_args()
    get_future_info(args.codes, args.output_json)
