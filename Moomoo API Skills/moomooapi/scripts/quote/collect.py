#!/usr/bin/env python3
"""
One-shot panorama data collector for a single ticker (snapshot + capital flow + financials + analyst rating + valuation + option summary)

Purpose: fetch multiple data sources for one ticker in parallel, returning a concise JSON summary (~3-4K tokens) to cut multi-round AI calls. Pairs with references/analysis-frameworks.md earnings-review card.
Usage: python collect.py US.AAPL [--json] [--with-options] [--verbose]

Design notes:
- Reuses common.py: create_quote_context / safe_close / safe_get / safe_float / df_to_records
- A single OpenQuoteContext is reused for all quote calls (the SDK context is the connection; do not create one per thread)
- Parallel fan-out: concurrent.futures.ThreadPoolExecutor (the repo's first parallel collector)
- Graceful degradation: workers do NOT call check_ret (it sys.exits); they check ret != RET_OK locally and return {"error": ...}. A single failing source does not kill the whole collection; failures are aggregated in the errors field.
- Read-only, no trading; safe to run without confirmation.

API limits (all >= 30 req/30s; 6 concurrent calls are well within limits):
- get_market_snapshot: up to 400 codes
- get_capital_flow: 30 req/30s, equities/warrants/funds only
- get_financials_statements: 30 req/30s
- get_research_analyst_consensus: 30 req/30s, equities + REIT
- get_valuation_detail: 30 req/30s, equities/funds/indices
- get_option_expiration_date / get_option_chain: 60 req/30s
"""
import argparse
import json
import sys
import os as _os
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..")))
from common import (
    create_quote_context,
    safe_close,
    safe_get,
    safe_float,
    safe_int,
    df_to_records,
)
from moomoo import RET_OK, PeriodType


# ---------- Per-source workers (each returns a dict) ----------

def _fetch_snapshot(ctx, code):
    try:
        ret, data = ctx.get_market_snapshot([code])
        if ret != RET_OK:
            return {"error": str(data)}
        if data is None or len(data) == 0:
            return {"error": "no snapshot data"}
        row = data.iloc[0] if hasattr(data, "iloc") else data[0]
        return {
            "name": safe_get(row, "name", default=""),
            "price": safe_float(safe_get(row, "last_price", default=0)),
            "prev_close": safe_float(safe_get(row, "prev_close_price", default=0)),
            "open": safe_float(safe_get(row, "open_price", default=0)),
            "high": safe_float(safe_get(row, "high_price", default=0)),
            "low": safe_float(safe_get(row, "low_price", default=0)),
            "volume": safe_int(safe_get(row, "volume", default=0)),
            "turnover": safe_float(safe_get(row, "turnover", default=0)),
            "turnover_rate": safe_float(safe_get(row, "turnover_rate", default=0)),
            "amplitude": safe_float(safe_get(row, "amplitude", default=0)),
            "pe_ttm": safe_float(safe_get(row, "pe_ttm_ratio", default=0)),
            "pe_annual": safe_float(safe_get(row, "pe_ratio", default=0)),
            "pb": safe_float(safe_get(row, "pb_ratio", default=0)),
            "total_market_val": safe_float(safe_get(row, "total_market_val", default=0)),
            "circular_market_val": safe_float(safe_get(row, "circular_market_val", default=0)),
            "update_time": safe_get(row, "update_time", default=""),
        }
    except Exception as e:
        return {"error": str(e)}


def _fetch_capital_flow(ctx, code):
    """Latest trading-day main capital net inflow (PeriodType.DAY, daily)."""
    try:
        ret, data = ctx.get_capital_flow(code, period_type=PeriodType.DAY)
        if ret != RET_OK:
            return {"error": str(data)}
        if data is None or len(data) == 0:
            return {"main_in_flow_latest": None, "note": "no capital flow data"}
        records = df_to_records(data, limit=5)
        latest = records[-1] if records else {}
        return {
            "main_in_flow_latest": safe_float(safe_get(latest, "main_in_flow", default=0)),
            "time": safe_get(latest, "capital_flow_item_time", default=""),
        }
    except Exception as e:
        return {"error": str(e)}


def _fetch_financials(ctx, code):
    """Latest 1-2 income-statement periods (statement_type=1) + key metrics (4)."""
    out = {"income": [], "main_index": [], "period": ""}
    try:
        ret, data = ctx.get_financials_statements(code, statement_type=1, financial_type=10, num=5)
        if ret == RET_OK and isinstance(data, dict):
            report_list = data.get("report_list", [])
            structure = {e["field_id"]: e.get("display_name") or f"field{e['field_id']}"
                         for e in data.get("structure_list", [])}
            if report_list:
                latest = report_list[0]
                out["period"] = latest.get("period_text", "")
                item_map = {item["field_id"]: item for item in latest.get("item_list", [])}
                out["income"] = [
                    {"name": structure.get(fid, str(fid)),
                     "value": safe_float(safe_get(it, "data", default=0)),
                     "yoy": safe_float(safe_get(it, "yoy", default=0))}
                    for fid, it in item_map.items()
                    if structure.get(fid)
                ][:12]  # truncate to control token count
    except Exception as e:
        out["income_error"] = str(e)
    return out


def _fetch_analyst(ctx, code):
    try:
        ret, data = ctx.get_research_analyst_consensus(code)
        if ret != RET_OK:
            return {"error": str(data)}
        if not isinstance(data, dict):
            return {"error": "no consensus data"}
        return {
            "avg_target": safe_float(data.get("average", 0)),
            "highest_target": safe_float(data.get("highest", 0)),
            "lowest_target": safe_float(data.get("lowest", 0)),
            "rating": safe_get(data, "rating", default=""),
            "total_analysts": safe_int(data.get("total", 0)),
            "buy_pct": safe_float(data.get("buy", 0)),
            "hold_pct": safe_float(data.get("hold", 0)),
            "sell_pct": safe_float(data.get("sell", 0)),
            "update_time": safe_get(data, "update_time_str", default=""),
        }
    except Exception as e:
        return {"error": str(e)}


def _fetch_valuation(ctx, code):
    """PE/PB historical percentile (server-recommended type, 1-year interval)."""
    try:
        ret, data = ctx.get_valuation_detail(code, interval_type=3)
        if ret != RET_OK:
            return {"error": str(data)}
        if not isinstance(data, dict):
            return {"error": "no valuation data"}
        trend = data.get("trend") or {}
        return {
            "valuation_type": safe_get(data, "valuation_type", default=""),
            "pe_or_pb_current": safe_float(trend.get("current_value", 0)),
            "pe_or_pb_avg": safe_float(trend.get("average_value", 0)),
            "percentile": safe_float(trend.get("valuation_percentile", 0)),
        }
    except Exception as e:
        return {"error": str(e)}


def _fetch_options(ctx, code):
    """Nearest-expiry option chain summary (HK/US equities/ETFs only)."""
    try:
        ret, data = ctx.get_option_expiration_date(code)
        if ret != RET_OK:
            return {"error": str(data)}
        if data is None or len(data) == 0:
            return {"error": "no option expiry (only HK/US equities/ETFs supported)"}
        records = df_to_records(data, limit=60)
        if not records:
            return {"error": "no expiration dates"}
        nearest = records[0]
        nearest_expiry = safe_get(nearest, "strike_time", default="") or safe_get(nearest, "datetime", default="")
        return {
            "nearest_expiry": nearest_expiry,
            "total_expiries": len(records),
        }
    except Exception as e:
        return {"error": str(e)}


def collect(code, output_json=False, with_options=False, verbose=False):
    ctx = None
    try:
        ctx = create_quote_context()

        # Submit parallel tasks (single ctx reused)
        tasks = {
            "snapshot": lambda: _fetch_snapshot(ctx, code),
            "flows": lambda: _fetch_capital_flow(ctx, code),
            "finances": lambda: _fetch_financials(ctx, code),
            "rating": lambda: _fetch_analyst(ctx, code),
            "valuation": lambda: _fetch_valuation(ctx, code),
        }
        if with_options:
            tasks["options"] = lambda: _fetch_options(ctx, code)

        result = {"code": code}
        errors = []
        with ThreadPoolExecutor(max_workers=6) as pool:
            future_to_name = {pool.submit(fn): name for name, fn in tasks.items()}
            for fut in as_completed(future_to_name):
                name = future_to_name[fut]
                try:
                    data = fut.result()
                except Exception as e:
                    data = {"error": str(e)}
                # Single-source failure: record in errors, do not abort the whole collection
                if isinstance(data, dict) and "error" in data and len(data) == 1:
                    errors.append({"source": name, "error": data["error"]})
                    result[name] = data
                else:
                    result[name] = data
        result["errors"] = errors

        # Truncate to control token count (non-verbose mode)
        if not verbose:
            result.setdefault("snapshot", {}).pop("update_time", None)

        if output_json:
            print(json.dumps(result, ensure_ascii=False))
        else:
            print("=" * 70)
            print(f"Panorama summary: {code}")
            print("=" * 70)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            print("=" * 70)
            print("Tip: use --json for machine parsing; pairs with analysis-frameworks.md earnings-review card")
        return result

    except Exception as e:
        if output_json:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))
        else:
            print(f"Error: {e}")
        sys.exit(1)
    finally:
        safe_close(ctx)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="One-shot panorama collector (quote+financials+rating+valuation+options)")
    parser.add_argument("code", help="Stock code, e.g. US.AAPL / HK.00700")
    parser.add_argument("--json", action="store_true", dest="output_json", help="JSON-formatted output")
    parser.add_argument("--with-options", action="store_true", help="Also fetch option summary (HK/US equities/ETFs only)")
    parser.add_argument("--verbose", action="store_true", help="Keep all fields (no truncation)")
    args = parser.parse_args()
    collect(args.code, output_json=args.output_json, with_options=args.with_options, verbose=args.verbose)
