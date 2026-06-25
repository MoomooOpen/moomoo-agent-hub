#!/usr/bin/env python3
"""
Get Option Volatility

Function: Get option volatility analysis including implied volatility, historical
          volatility and volatility premium for an option contract
Usage: python get_option_volatility.py [-h] [--query-time-period QUERY_TIME_PERIOD] [--hv-time-period HV_TIME_PERIOD] [--json] code

API Limits:
- Max 30 requests per 30 seconds
- Supports option contract codes only

Parameter Description:
- code: Option code, e.g. US.AAPL280317C260000
- --query-time-period: Query time period: 1=Week, 2=Month, 3=Quarter, 4=HalfYear, 5=Year (default 2=Month)
- --hv-time-period: Historical volatility period for underlying (5~250 days, default 30)

Return Field Description:
- data.average_impvol: Average implied volatility (percent value before % sign, e.g. 25.0 means 25%)
- data.impvol_status:  Volatility status (0=Fluctuating, 1=Overvalued, 2=Undervalued)
- data.analysis:       Analysis text
- data.items[]:        Volatility list sorted by date descending; each item contains
                       timestamp/timestamp_str/implied_volatility/history_volatility/volatility_premium
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
    print_display_df,
)

_IMPVOL_STATUS_MAP = {0: "Fluctuating", 1: "Overvalued", 2: "Undervalued"}

_SEP = "=" * 64
_DASH = "-" * 64


def get_option_volatility(code, query_time_period=None, hv_time_period=None, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        kwargs = {}
        if query_time_period is not None:
            kwargs["query_time_period"] = query_time_period
        if hv_time_period is not None:
            kwargs["hv_time_period"] = hv_time_period
        ret, df = ctx.get_option_volatility(code, **kwargs)
        check_ret(ret, df, ctx, "get option volatility")

        if is_empty(df):
            if output_json:
                print(json.dumps({"code": code, "data": {}}))
            else:
                print("No data")
            return

        if output_json:
            avg_impvol_j = df["average_impvol"].iloc[0] if not df.empty and "average_impvol" in df.columns else None
            impvol_status_j = df["impvol_status"].iloc[0] if not df.empty and "impvol_status" in df.columns else None
            analysis_j = df["analysis"].iloc[0] if not df.empty and "analysis" in df.columns else ""
            records = []
            if not df.empty:
                for _, row in df.iterrows():
                    records.append({
                        "timestamp":          row.get("timestamp"),
                        "timestamp_str":      row.get("timestamp_str"),
                        "implied_volatility": row.get("implied_volatility"),
                        "history_volatility": row.get("history_volatility"),
                        "volatility_premium": row.get("volatility_premium"),
                    })
            print(json.dumps({
                "code": code,
                "data": {
                    "average_impvol": avg_impvol_j,
                    "impvol_status": int(impvol_status_j) if impvol_status_j is not None else None,
                    "analysis": analysis_j or "",
                    "items": records,
                },
            }, ensure_ascii=False, default=str))
            return

        avg_impvol = df["average_impvol"].iloc[0] if not df.empty and "average_impvol" in df.columns else None
        status_val = df["impvol_status"].iloc[0] if not df.empty and "impvol_status" in df.columns else None
        status_str = _IMPVOL_STATUS_MAP.get(int(status_val), str(status_val)) if status_val is not None else ""
        analysis = df["analysis"].iloc[0] if not df.empty and "analysis" in df.columns else ""

        print(_SEP)
        print(f"Option Volatility: {code}")
        print(_SEP)
        if avg_impvol is not None:
            print(f"  Average Implied Volatility: {avg_impvol:.2f}%")
        if status_val is not None:
            print(f"  Volatility Status:          {int(status_val)} ({status_str})")
        if analysis:
            print(f"  Analysis:                   {analysis}")
        print()

        if not df.empty:
            cols = [c for c in ["timestamp_str", "implied_volatility", "history_volatility", "volatility_premium"]
                    if c in df.columns]
            disp = df[cols].copy()
            for col in ("implied_volatility", "history_volatility", "volatility_premium"):
                if col in disp.columns:
                    disp[col] = disp[col].apply(lambda x: f"{x:.2f}" if x is not None else "-")
            disp = disp.rename(columns={
                "timestamp_str":      "Timestamp Str",
                "implied_volatility": "Implied Volatility(%)",
                "history_volatility": "History Volatility(%)",
                "volatility_premium": "Volatility Premium(%)",
            })
            print_display_df(disp, max_colwidth=22)
        else:
            print("  No data")

        print(_DASH)
        print(f"Count: {len(df)}")
        print(_SEP)

    except Exception as e:
        if output_json:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))
        else:
            print(f"Error: {e}")
        sys.exit(1)
    finally:
        safe_close(ctx)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get option volatility analysis data")
    parser.add_argument("code", help="Option code, e.g. US.AAPL280317C260000")
    parser.add_argument("--query-time-period", type=int, default=None, dest="query_time_period",
                        help="Query time period: 1=Week, 2=Month, 3=Quarter, 4=HalfYear, 5=Year (default 2=Month)")
    parser.add_argument("--hv-time-period", type=int, default=None, dest="hv_time_period",
                        help="Historical volatility period for underlying (5~250 days, default 30)")
    parser.add_argument("--json", action="store_true", dest="output_json",
                        help="Output in JSON format")
    args = parser.parse_args()
    get_option_volatility(
        args.code,
        query_time_period=args.query_time_period,
        hv_time_period=args.hv_time_period,
        output_json=args.output_json,
    )
