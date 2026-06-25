#!/usr/bin/env python3
"""
Get Valuation Detail

Function: Get valuation details for a stock or index, including trend, market distribution,
          sector distribution (stocks only) and profit/revenue growth rate (stocks only);
          PB type has no profit growth module; indices have no ranking/mean/median fields
Usage: python get_valuation_detail.py [-h] [--valuation-type VALUATION_TYPE] [--interval-type INTERVAL_TYPE] [--json] code

API Limits:
- Max 30 requests per 30 seconds
- Supports equities, funds and indices

Parameter Description:
- code: Stock or index code, e.g. HK.00700
- --valuation-type: Valuation type: 1=PE, 2=PB, 3=PS (default: server recommended)
- --interval-type: Time interval (valid 1-10): 1=3Month 2=6Month 3=1Year 4=3Year 5=Since2019
                   6=5Year 7=10Year 8=2Year 9=20Year 10=30Year (default: 3=1Year)

Return Field Description:
- valuation_type:       Actual valuation type returned (PE/PB/PS)
- last_update_time_str: Last update time (YYYY-MM-DD HH:MM:SS)
- trend:                Valuation trend; contains current_value/average_value/
                        valuation_percentile (value before % sign)/forward_value/historical_items
- market_distribution:  Market distribution; contains sections (start/end/number)/total/ranking/
                        average_value
- plate_distribution:   Sector distribution (stocks only); contains sector info and stock items
- profit_growth_rate:   Profit/revenue growth rate (stocks only, no PB); contains growth
                        multiples and period details
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
    safe_float,
    safe_int,
    print_display_df,
    format_big_number,
    pad_disp,
)

_SEP = "=" * 64
_DASH = "-" * 64

_VALUATION_TYPE_MAP = {0: "Recommended", 1: "PE", 2: "PB", 3: "PS"}
_INTERVAL_TYPE_MAP = {
    1: "3Month", 2: "6Month", 3: "1Year", 4: "3Year", 5: "Since2019",
    6: "5Year", 7: "10Year", 8: "2Year", 9: "20Year", 10: "30Year",
}
_DEFAULT_INTERVAL_TYPE = 3


def _fmt(v, digits=2, na="-"):
    if v is None:
        return na
    try:
        return f"{float(v):.{digits}f}"
    except (TypeError, ValueError):
        return na


def _build_trend_summary(trend, interval_type=None):
    it = interval_type if interval_type is not None else _DEFAULT_INTERVAL_TYPE
    interval_str = _INTERVAL_TYPE_MAP.get(safe_int(it), str(it))
    rows = [
        ("Interval",       interval_str),
        ("Current Value",  _fmt(trend.get("current_value"))),
        ("Avg Value",      _fmt(trend.get("average_value"))),
        ("Avg - 1σ",       _fmt(trend.get("avg_minus_1_stddev"))),
        ("Avg + 1σ",       _fmt(trend.get("avg_plus_1_stddev"))),
    ]
    if "forward_value" in trend:
        rows.append(("Forward Value", _fmt(trend.get("forward_value"))))
    if "valuation_percentile" in trend:
        pct = safe_float(trend.get("valuation_percentile"))
        rows.append(("Historical Pct", f"{pct:.2f}%"))
    return rows


def _build_hist_df(hist_items):
    has_plate = any("plate_value" in item for item in hist_items)
    rows = []
    for item in hist_items:
        row = {
            "Date":  item.get("time_str", ""),
            "Value": _fmt(item.get("value")),
        }
        if has_plate:
            row["Sector Avg"] = _fmt(item.get("plate_value"))
        rows.append(row)
    return pd.DataFrame(rows) if rows else pd.DataFrame()


def _fmt_section_range(start, end):
    has_start = start is not None
    has_end = end is not None
    if has_start and has_end:
        return f"{_fmt(start)} ~ {_fmt(end)}"
    if has_start:
        return f"{_fmt(start)}+"
    if has_end:
        return f"<= {_fmt(end)}"
    return "-"


def _build_sections_df(sections, total=None):
    try:
        total_int = int(total) if total is not None else 0
    except (TypeError, ValueError):
        total_int = 0
    rows = []
    for sec in sections:
        num = safe_int(sec.get("number"))
        pct_str = f"{num / total_int * 100:.2f}%" if total_int > 0 else "-"
        rows.append({
            "Range":   _fmt_section_range(sec.get("start"), sec.get("end")),
            "Count":   num,
            "Ratio":   pct_str,
        })
    return pd.DataFrame(rows) if rows else pd.DataFrame()


def _build_stock_items_df(stock_items):
    rows = []
    for item in stock_items:
        rows.append({
            "Symbol":     item.get("symbol", ""),
            "Name":       item.get("name", ""),
            "Value":      _fmt(item.get("value")),
            "Market Cap": format_big_number(item.get("market_cap")),
        })
    return pd.DataFrame(rows) if rows else pd.DataFrame()


def _build_profit_data_df(profit_data):
    rows = []
    for item in profit_data:
        rows.append({
            "Period Str":            item.get("period_str", ""),
            "Report Date Str":       item.get("report_date_str", ""),
            "Market Cap Multiple":   _fmt(item.get("market_cap_multiple")),
            "Finance Data Multiple": _fmt(item.get("finance_data_multiple")),
        })
    return pd.DataFrame(rows) if rows else pd.DataFrame()


def get_valuation_detail(code, valuation_type=None, interval_type=None, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        ret, data = ctx.get_valuation_detail(
            code,
            valuation_type=valuation_type,
            interval_type=interval_type,
        )
        check_ret(ret, data, ctx, "get valuation detail")

        if not data:
            if output_json:
                print(json.dumps({"code": code, "data": {}}, ensure_ascii=False))
            else:
                print(_SEP)
                print(f"Valuation Detail: {code}")
                print(_DASH)
                print("No data")
                print(_SEP)
            return

        vt = safe_int(data.get("valuation_type", 0))
        vt_str = _VALUATION_TYPE_MAP.get(vt, str(vt))

        trend = data.get("trend")
        md = data.get("market_distribution")
        pgr = data.get("profit_growth_rate")

        def _no_data(d, empty_key):
            if not d:
                return True
            return set(d.keys()) <= {empty_key} and not d.get(empty_key)

        trend_has_data = not _no_data(trend, "historical_items")
        md_has_data = not _no_data(md, "sections")
        pgr_has_data = not _no_data(pgr, "profit_data")
        all_no_data = not trend_has_data and not md_has_data and not pgr_has_data

        if output_json:
            out = {"code": code, "data": {} if all_no_data else data}
            print(json.dumps(out, ensure_ascii=False, default=str))
            return

        if all_no_data:
            print("No data")
            return

        upd_str = data.get("last_update_time_str", "")

        print(_SEP)
        print(f"Valuation Detail: {code}")
        print(_DASH)

        if trend:
            print(f"\nValuation Type: {vt_str}  Last Update: {upd_str}")
            if not trend_has_data:
                print("\n[Trend Summary]  No data")
            else:
                print("\n[Trend Summary]")
                for label, val in _build_trend_summary(trend, interval_type=interval_type):
                    print(f"  {pad_disp(label, 16)} {val}")

                hist = trend.get("historical_items", [])
                print(f"\n[Historical Values]  {len(hist)} records")
                if hist:
                    print_display_df(_build_hist_df(hist))
                else:
                    print("  No historical data")

        if md:
            sections = md.get("sections", [])
            total = md.get("total")
            if total is None and not sections:
                print("\n[Market Distribution]  No data")
            else:
                ranking = md.get("ranking")
                avg_v = md.get("average_value")
                med_v = md.get("median_value")
                header = f"\n[Market Distribution]  {len(sections)} ranges  Total={total if total is not None else '-'}"
                if ranking is not None:
                    header += f"  Rank={ranking}/{total if total is not None else '-'}"
                if avg_v is not None:
                    header += f"  Avg={_fmt(avg_v)}  Median={_fmt(med_v)}"
                print(header)
                if sections:
                    print_display_df(_build_sections_df(sections, total))

        plate = data.get("plate_distribution")
        if plate:
            plate_sym = plate.get("plate", "")
            plate_name = plate.get("plate_name", "")
            p_avg = _fmt(plate.get("plate_average_value"))
            p_rank = safe_int(plate.get("plate_ranking"))
            p_cnt = safe_int(plate.get("plate_stock_item_count"))
            print(f"\n[Sector Distribution]  Sector={plate_sym} {plate_name}  Sector Avg={p_avg}  Rank={p_rank}/{p_cnt}")
            stock_items = plate.get("stock_items", [])
            if stock_items:
                print(f"  Sector stocks ({len(stock_items)}):")
                print_display_df(_build_stock_items_df(stock_items))

        if pgr:
            is_ps = (vt == 3)
            section_title = "Revenue Growth Rate" if is_ps else "Profit Growth Rate"
            ttm_label = "Revenue TTM Multiple" if is_ps else "Net Profit TTM Multiple"
            if pgr.get("financial_ttm_multiple") is None:
                print(f"\n[{section_title}]  No data")
            else:
                ttm_m = _fmt(pgr.get("financial_ttm_multiple"))
                cap_m = _fmt(pgr.get("market_cap_multiple"))
                yr_cnt = safe_int(pgr.get("year_count"))
                print(f"\n[{section_title}]  {ttm_label}={ttm_m}  Market Cap Multiple={cap_m}  Years={yr_cnt}")
                conclusion = pgr.get("conclusion_detailed")
                if conclusion:
                    print(f"  Conclusion: {conclusion}")
                profit_data = pgr.get("profit_data", [])
                if profit_data:
                    data_label = "Revenue Data" if is_ps else "Profit Data"
                    print(f"  {data_label} ({len(profit_data)} records):")
                    print_display_df(_build_profit_data_df(profit_data))

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
    parser = argparse.ArgumentParser(description="Get valuation details for a stock or index")
    parser.add_argument("code", help="Stock or index code, e.g. HK.00700")
    parser.add_argument("--valuation-type", type=int, default=None, dest="valuation_type",
                        help="Valuation type: 1=PE, 2=PB, 3=PS (default: server recommended)")
    parser.add_argument("--interval-type", type=int, default=None, dest="interval_type",
                        help="Time interval (1-10): 1=3Month 2=6Month 3=1Year 4=3Year 5=Since2019 "
                             "6=5Year 7=10Year 8=2Year 9=20Year 10=30Year (default: 3=1Year)")
    parser.add_argument("--json", action="store_true", dest="output_json",
                        help="Output in JSON format")
    args = parser.parse_args()

    get_valuation_detail(
        args.code,
        valuation_type=args.valuation_type,
        interval_type=args.interval_type,
        output_json=args.output_json,
    )
