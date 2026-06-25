#!/usr/bin/env python3
"""
Get Stock Splits

Function: Get stock split/consolidation history (HK stocks have additional fields),
          with pagination support
Usage: python get_corporate_actions_stock_splits.py [-h] [--next-key KEY] [--num N] [--json] code

API Limits:
- Max 30 requests per 30 seconds
- Supports HK and US equities and funds

Parameter Description:
- code: Stock code, e.g. HK.00700
- --next-key: Pagination key; omit for first page; "-1" means no more data
- --num: Number of results per page, default 10, range 1-50

Return Field Description:
- data.next_key:   Pagination key; "-1" means no more data
- data.items[]:    Split/consolidation list; each item contains dir_deci_pub_date_str/
                   reform_type/rate; HK equities and trusts additionally contain
                   ex_date_str/sm_deci_date_str/temp_trade_begin_date_str/
                   simul_trade_begin_date_str/simul_trade_end_date_str/event_status/
                   new_par_value/temp_share_code/temp_share_abbr_name/new_trade_unit/
                   shares_after_effect
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
    format_big_number,
    disp_width,
    pad_disp,
)

def _reform_type_str(v):
    return str(v) if v else "-"


def _par_value_str(v):
    if v is None:
        return "-"
    try:
        f = float(v)
    except (TypeError, ValueError):
        return "-"
    if f == 0:
        return "-"
    return f"{f:.6f}"


def _print_header(code):
    print("=" * 64)
    print(f"Stock Splits: {code}")
    print("-" * 64)


def _print_footer(count, nk):
    print("-" * 64)
    nk_disp = "End(-1)" if nk == "-1" else nk
    print(f"Count: {count}   --next-key: {nk_disp}")
    print("=" * 64)


def _col_widths(rows, headers):
    widths = [disp_width(h) for h in headers]
    for row in rows:
        for i, h in enumerate(headers):
            widths[i] = max(widths[i], disp_width(str(row.get(h, "-"))))
    return widths


def _print_table(rows, is_hk):
    if not rows:
        print("  No data")
        return

    common_cols = ["Date", "Reform Type", "Rate"]
    hk_cols = ["Ex Date", "Resolution Date", "Temp Trade Begin", "Parallel Trade Period",
               "Event Status", "New Par Value", "Temp Share Code", "Temp Share Abbr",
               "New Trade Unit", "Shares After Effect"]
    candidate_cols = common_cols + (hk_cols if is_hk else [])

    disp_rows = []
    for item in rows:
        begin = item.get("simul_trade_begin_date_str") or ""
        end = item.get("simul_trade_end_date_str") or ""
        simul = f"{begin}~{end}" if (begin or end) else "-"
        row = {
            "Date":        item.get("dir_deci_pub_date_str") or "-",
            "Reform Type": _reform_type_str(item.get("reform_type")),
            "Rate":        item.get("rate") or "-",
        }
        if is_hk:
            row.update({
                "Ex Date":              item.get("ex_date_str") or "-",
                "Resolution Date":      item.get("sm_deci_date_str") or "-",
                "Temp Trade Begin":     item.get("temp_trade_begin_date_str") or "-",
                "Parallel Trade Period": simul,
                "Event Status":         item.get("event_status") or "-",
                "New Par Value":        _par_value_str(item.get("new_par_value")),
                "Temp Share Code":      item.get("temp_share_code") or "-",
                "Temp Share Abbr":      item.get("temp_share_abbr_name") or "-",
                "New Trade Unit":       str(item.get("new_trade_unit") or "-"),
                "Shares After Effect":  format_big_number(item.get("shares_after_effect")),
            })
        disp_rows.append(row)

    cols = [c for c in candidate_cols if any(str(r.get(c, "-")) != "-" for r in disp_rows)]

    widths = _col_widths(disp_rows, cols)
    sep = "  "
    header_line = sep.join(pad_disp(h, w) for h, w in zip(cols, widths))
    print(header_line)
    print("-" * min(sum(widths) + len(sep) * (len(cols) - 1), 120))
    for row in disp_rows:
        line = sep.join(pad_disp(str(row.get(c, "-")), w) for c, w in zip(cols, widths))
        print(line)


def display_non_json(code, next_key, num):
    ctx = None
    try:
        ctx = create_quote_context()
        ret, data = ctx.get_corporate_actions_stock_splits(code, next_key=next_key, num=num)
        check_ret(ret, data, ctx, "get stock splits")
        items = [] if is_empty(data) else data.get("split_list", [])
        if not items:
            print("No data")
            return
        nk = data.get("next_key", "-1")
        is_hk = code.upper().startswith("HK.")
        _print_header(code)
        _print_table(items, is_hk)
        _print_footer(len(items), nk)
    finally:
        safe_close(ctx)


def display_json(code, next_key, num):
    ctx = None
    try:
        ctx = create_quote_context()
        ret, data = ctx.get_corporate_actions_stock_splits(code, next_key=next_key, num=num)
        check_ret(ret, data, ctx, "get stock splits")
        items = [] if is_empty(data) else data.get("split_list", [])
        if not items:
            print(json.dumps({"code": code, "data": {}}, ensure_ascii=False))
            return
        nk = data.get("next_key", "-1")
        print(json.dumps({"code": code, "data": {"next_key": nk, "items": items}}, ensure_ascii=False))
    finally:
        safe_close(ctx)


def main():
    parser = argparse.ArgumentParser(
        description="Get stock split/consolidation history with pagination support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("code", help="Stock code, e.g. HK.00700")
    parser.add_argument("--next-key", default=None, dest="next_key", metavar="KEY",
                        help='Pagination key; omit for first page; "-1" means no more data')
    parser.add_argument("--num", type=int, default=None, metavar="N",
                        help="Number of results per page, default 10, range 1-50")
    parser.add_argument("--json", action="store_true", dest="output_json",
                        help="Output in JSON format")
    args = parser.parse_args()

    if args.output_json:
        display_json(args.code, args.next_key, args.num)
    else:
        display_non_json(args.code, args.next_key, args.num)


if __name__ == "__main__":
    main()
