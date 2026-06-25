#!/usr/bin/env python3
"""
Get Option Exercise Probability

Function: Get historical exercise probability data for an option contract,
          sorted by date descending
Usage: python get_option_exercise_probability.py [-h] [--json] code

API Limits:
- Max 30 requests per 30 seconds
- Supports option contract codes only

Parameter Description:
- code: Option code, e.g. US.AAPL280317C260000

Return Field Description:
- data[]: Exercise probability list sorted by date descending; each item contains
          timestamp/timestamp_str/security_price/strike_probability
          (strike_probability is percent value before % sign, e.g. 12.34 means 12.34%)
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

_SEP = "=" * 64
_DASH = "-" * 64


def get_option_exercise_probability(code, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        ret, df = ctx.get_option_exercise_probability(code)
        check_ret(ret, df, ctx, "get option exercise probability")

        if is_empty(df):
            if output_json:
                print(json.dumps({"code": code, "data": {}}))
            else:
                print("No data")
            return

        row_count = len(df) if df is not None and not df.empty else 0

        if output_json:
            records = df_to_records(df) if df is not None and not df.empty else []
            print(json.dumps({"code": code, "data": records}, ensure_ascii=False, default=str))
            return

        if df is None or df.empty:
            print("No data")
        else:
            print(_SEP)
            print(f"Option Exercise Probability: {code}")
            print(_DASH)
            disp = df.copy()
            disp = disp.drop(columns=["timestamp"], errors="ignore")
            if "security_price" in disp.columns:
                disp["security_price"] = disp["security_price"].apply(
                    lambda x: f"{float(x):.3f}" if x is not None and str(x) != "" else "-"
                )
            if "strike_probability" in disp.columns:
                disp["strike_probability"] = disp["strike_probability"].apply(
                    lambda x: f"{float(x):.2f}%" if x is not None and str(x) != "" else "-"
                )
            disp = disp.rename(columns={
                "timestamp_str":      "Timestamp Str",
                "security_price":     "Security Price",
                "strike_probability": "Strike Probability",
            })
            print_display_df(disp, max_colwidth=24)
            print(_DASH)
            print(f"Count: {row_count}")
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
    parser = argparse.ArgumentParser(description="Get option exercise probability data")
    parser.add_argument("code", help="Option code, e.g. US.AAPL280317C260000")
    parser.add_argument("--json", action="store_true", dest="output_json",
                        help="Output in JSON format")
    args = parser.parse_args()
    get_option_exercise_probability(args.code, output_json=args.output_json)
