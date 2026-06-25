#!/usr/bin/env python3
"""
Get Valuation Plate Stock List

Function: Get valuation list for constituents of a sector or index, including valuation,
          forward valuation, historical percentile and market cap; first index request also
          returns the associated sector list
Usage: python get_valuation_plate_stock_list.py [-h] [--valuation-type VALUATION_TYPE] [--next-key NEXT_KEY] [--num NUM] [--sort-type SORT_TYPE] [--sort-id SORT_ID] [--filter-security FILTER_SECURITY] [--json] code

API Limits:
- Max 30 requests per 30 seconds
- Supports sectors and indices; does not support individual stocks
- First request for an index additionally returns the associated sector list (plate_list)

Parameter Description:
- code: Sector or index code, e.g. HK.800000
- --valuation-type: Valuation type: 1=PE (default), 2=PB, 3=PS
- --next-key: Pagination key; omit for first page; "-1" means no more data
- --num: Number of results per page, default 10, range 1-50
- --sort-type: Sort direction: 1=Desc, 2=Asc (default: 2=Asc)
- --sort-id: Sort column: 51=MarketCap (default), 52=Valuation, 53=ForwardValuation,
             54=HistoricalPercentile
- --filter-security: Index only: filter constituents by sector/industry (e.g. HK.LIST23363)

Return Field Description:
- data.count:         Total number of constituent stocks
- data.next_key:      Pagination key; "-1" means no more data
- data.stock_list:    Constituent stock valuation list; each item contains symbol/name/
                      valuation_val/forward_value/valuation_percentile (value before % sign)/
                      market_cap
- data.plate_list:    Sector list for index (first full page only); each item contains symbol/name
"""
import argparse
import json
import sys
import os as _os

import pandas as pd

sys.path.insert(0, _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..")))
from common import (
    create_quote_context,
    check_ret,
    safe_close,
    print_display_df,
    format_big_number,
)

_SEP = "=" * 64
_DASH = "-" * 64

_VALUATION_TYPE_MAP = {1: "PE", 2: "PB", 3: "PS"}


def _fmt_pct(val):
    if val is None:
        return "-"
    try:
        return f"{float(val):.2f}%"
    except Exception:
        return str(val)


def _fmt_float(val, decimals=2):
    if val is None:
        return "-"
    try:
        return f"{float(val):.{decimals}f}"
    except Exception:
        return str(val)


def get_valuation_plate_stock_list(code, valuation_type=None, next_key=None, num=None,
                                   sort_type=None, sort_id=None, filter_security=None,
                                   output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        ret, data = ctx.get_valuation_plate_stock_list(
            code,
            valuation_type=valuation_type,
            next_key=next_key,
            num=num,
            sort_type=sort_type,
            sort_id=sort_id,
            filter_security=filter_security,
        )
        check_ret(ret, data, ctx, "get valuation plate stock list")

        if not data:
            stock_list = []
            total = 0
            nxt = -1
            plate_list = []
        else:
            stock_list = data.get("stock_list", [])
            total = data.get("count", len(stock_list))
            nxt = data.get("next_key", -1)
            plate_list = data.get("plate_list", [])

        nextkey_str = "End(-1)" if nxt in ("-1", -1, None) else str(nxt)

        if not stock_list and not plate_list:
            if output_json:
                print(json.dumps({"code": code, "data": {}}, ensure_ascii=False))
            else:
                print("No data")
            return

        if output_json:
            print(json.dumps({"code": code, "data": {
                "count": total,
                "next_key": nxt,
                "stock_list": stock_list,
                "plate_list": plate_list,
            }}, ensure_ascii=False, default=str))
            return

        print(_SEP)
        print(f"Valuation Plate Stock List: {code}")
        print(_DASH)

        if stock_list:
            rows = []
            for item in stock_list:
                rows.append({
                    "Symbol":               item.get("symbol", "-"),
                    "Name":                 item.get("name", "-") or "-",
                    "Valuation Val":        _fmt_float(item.get("valuation_val")),
                    "Forward Value":        _fmt_float(item.get("forward_value")),
                    "Valuation Percentile": _fmt_pct(item.get("valuation_percentile")),
                    "Market Cap":           format_big_number(item.get("market_cap")),
                })
            print_display_df(pd.DataFrame(rows), max_colwidth=20)

        if plate_list:
            print()
            print(f"Index sector list ({len(plate_list)} sectors):")
            plate_rows = [
                {"No.": i + 1, "Symbol": p.get("symbol", "-"), "Name": p.get("name", "-")}
                for i, p in enumerate(plate_list)
            ]
            print_display_df(pd.DataFrame(plate_rows), max_colwidth=30)

        print(_DASH)
        print(f"Count: {len(stock_list)}   --next-key: {nextkey_str}")
        print(_SEP)

    except SystemExit:
        raise
    except Exception as e:
        if output_json:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))
        else:
            print(f"Error: {e}")
        sys.exit(1)
    finally:
        safe_close(ctx)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Get constituent stock valuation list for a sector or index with pagination support"
    )
    parser.add_argument("code", help="Sector or index code, e.g. HK.800000")
    parser.add_argument("--valuation-type", type=int, default=None, dest="valuation_type",
                        help="Valuation type: 1=PE (default), 2=PB, 3=PS")
    parser.add_argument("--next-key", type=str, default=None, dest="next_key",
                        help='Pagination key; omit for first page; "-1" means no more data')
    parser.add_argument("--num", type=int, default=None, dest="num",
                        help="Number of results per page, default 10, range 1-50")
    parser.add_argument("--sort-type", type=int, default=None, dest="sort_type",
                        help="Sort direction: 1=Desc, 2=Asc (default: 2=Asc)")
    parser.add_argument("--sort-id", type=int, default=None, dest="sort_id",
                        help="Sort column: 51=MarketCap (default), 52=Valuation, "
                             "53=ForwardValuation, 54=HistoricalPercentile")
    parser.add_argument("--filter-security", default=None, dest="filter_security",
                        help="Index only: filter constituents by sector/industry (e.g. HK.LIST23363)")
    parser.add_argument("--json", action="store_true", dest="output_json",
                        help="Output in JSON format")
    args = parser.parse_args()

    get_valuation_plate_stock_list(
        args.code,
        valuation_type=args.valuation_type,
        next_key=args.next_key,
        num=args.num,
        sort_type=args.sort_type,
        sort_id=args.sort_id,
        filter_security=args.filter_security,
        output_json=args.output_json,
    )
