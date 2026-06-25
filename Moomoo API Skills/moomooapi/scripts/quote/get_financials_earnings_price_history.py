#!/usr/bin/env python3
"""
Get Earnings Price History

Function: Get stock price history around earnings dates for multiple periods, including
          IV Crush analysis and pre/post earnings performance metrics
Usage: python get_financials_earnings_price_history.py [-h] [--json] code

API Limits:
- Max 30 requests per 30 seconds
- Supports HK and US equities

Parameter Description:
- code: Stock code, e.g. HK.00700

Return Field Description:
- data[]: Flattened list expanded by earnings period + offset trading day; each row contains
  period metadata (fiscal_year/financial_type/period_text/pub_trading_day_str/pub_type/
  is_current/predict_vola_ratio_newest/predict_vola_ratio_highest/predict_vola_val_newest/
  predict_vola_val_highest/option_iv_crush/option_strike_date_iv_crush), publication day
  quotes (trading_day_str/open_price/close_price/highest_price/lowest_price/
  last_close_price/volume), and offset close prices (schedule_delta/schedule_close_price)
"""
import argparse
import json
import math
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
    format_big_number,
)

_SEP = "=" * 64
_DASH = "-" * 64

DISPLAY_COLUMNS = [
    "period_text",
    "is_current",
    "pub_trading_day_str",
    "pub_time_str",
    "pub_type",
    "predict_vola_ratio_newest",
    "predict_vola_ratio_highest",
    "predict_vola_val_newest",
    "predict_vola_val_highest",
    "option_iv_crush",
    "option_strike_date_iv_crush",
    "trading_day_str",
    "close_price",
    "open_price",
    "highest_price",
    "lowest_price",
    "last_close_price",
    "volume",
    "earnings_pre14d",
    "earnings_post14d",
]

DISPLAY_EN = {
    "period_text":                 "Period Text",
    "is_current":                  "Is Current",
    "pub_trading_day_str":         "Pub Trading Day Str",
    "pub_time_str":                "Pub Time Str",
    "pub_type":                    "Pub Type",
    "predict_vola_ratio_newest":   "Predict Vola Ratio Newest",
    "predict_vola_ratio_highest":  "Predict Vola Ratio Highest",
    "predict_vola_val_newest":     "Predict Vola Val Newest",
    "predict_vola_val_highest":    "Predict Vola Val Highest",
    "option_iv_crush":             "Option Iv Crush",
    "option_strike_date_iv_crush": "Option Strike Date Iv Crush",
    "trading_day_str":             "Trading Day Str",
    "close_price":                 "Close Price",
    "open_price":                  "Open Price",
    "highest_price":               "Highest Price",
    "lowest_price":                "Lowest Price",
    "last_close_price":            "Last Close Price",
    "volume":                      "Volume",
    "earnings_pre14d":             "Earnings Pre14d",
    "earnings_post14d":            "Earnings Post14d",
}

_PUB_TYPE_MAP = {0: "-", 1: "Pre-Market", 2: "After-Market", 3: "During-Market"}

_PRICE_COLS = {
    "close_price", "open_price", "highest_price", "lowest_price",
    "last_close_price", "predict_vola_val_newest", "predict_vola_val_highest",
}
_PCT_COLS = {
    "predict_vola_ratio_newest", "predict_vola_ratio_highest",
    "option_iv_crush", "option_strike_date_iv_crush",
    "earnings_pre14d", "earnings_post14d",
}


def _is_numeric_val(x):
    if x is None:
        return False
    if isinstance(x, float) and math.isnan(x):
        return False
    if isinstance(x, (int, float)):
        return True
    s = str(x).strip()
    if not s or s in ("-", "None", "nan", "N/A"):
        return False
    try:
        float(s)
        return True
    except ValueError:
        return False


def _apply_display_scale(df):
    df = df.copy()
    for col in _PRICE_COLS:
        if col in df.columns:
            df[col] = df[col].apply(
                lambda x: f"{float(x):.3f}" if _is_numeric_val(x) else "-"
            )
    for col in _PCT_COLS:
        if col in df.columns:
            df[col] = df[col].apply(
                lambda x: f"{float(x):.2f}" if _is_numeric_val(x) else "-"
            )
    if "volume" in df.columns:
        df["volume"] = df["volume"].apply(
            lambda x: format_big_number(x) if _is_numeric_val(x) else "-"
        )
    if "pub_time_str" in df.columns:
        df["pub_time_str"] = df["pub_time_str"].apply(
            lambda x: str(x).strip() if (x is not None and str(x).strip() not in ("", "-", "None", "nan")) else "-"
        )
    if "pub_type" in df.columns:
        df["pub_type"] = df["pub_type"].apply(
            lambda x: _PUB_TYPE_MAP.get(int(float(x)), "-") if _is_numeric_val(x) else "-"
        )
    if "is_current" in df.columns:
        df["is_current"] = df["is_current"].map(
            lambda x: "-" if (x is None or str(x) in ("nan", "None", ""))
            else ("Yes" if x is True or x == "True" or x == 1
                  else ("No" if x is False or x == "False" or x == 0 else str(x)))
        )
    df = df.fillna("-")
    df = df.replace("", "-")
    return df


def _compute_schedule_metrics(df):
    period_col = "period_text"
    if period_col not in df.columns or "schedule_delta" not in df.columns:
        return df

    period_deltas = {}
    for _, row in df.iterrows():
        pt = row.get(period_col)
        key = str(pt) if pt is not None else ""
        if key not in period_deltas:
            period_deltas[key] = {}
        d = row.get("schedule_delta")
        c = row.get("schedule_close_price")
        try:
            di = int(float(d))
            cv = float(c)
            if not math.isnan(cv):
                period_deltas[key][di] = cv
        except (TypeError, ValueError):
            pass

    def _pct_change(dm, d_num, d_base):
        p_num = dm.get(d_num)
        p_base = dm.get(d_base)
        if p_num is None or p_base is None or p_base == 0:
            return None
        return (p_num - p_base) / p_base * 100

    base = df.drop_duplicates(subset=[period_col], keep="first").reset_index(drop=True).copy()
    pre14, post14 = [], []
    for pt in base[period_col]:
        dm = period_deltas.get(str(pt) if pt is not None else "", {})
        pre14.append(_pct_change(dm, -1, -15))
        post14.append(_pct_change(dm, 14, 0))
    base["earnings_pre14d"] = pre14
    base["earnings_post14d"] = post14
    return base


def get_financials_earnings_price_history(code, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        api = getattr(ctx, "get_financials_earnings_price_history", None)
        if not callable(api):
            raise AttributeError(
                "Current moomoo-api does not support get_financials_earnings_price_history. "
                "Please upgrade the SDK."
            )
        ret, data = api(code)
        check_ret(ret, data, ctx, "get earnings price history")

        if output_json:
            if is_empty(data):
                print(json.dumps({"code": code, "data": {}}, ensure_ascii=False))
            else:
                print(json.dumps({"code": code, "data": df_to_records(data)},
                                 ensure_ascii=False, default=str))
        else:
            if is_empty(data):
                print("No data")
            else:
                agg = _compute_schedule_metrics(data)
                disp = _apply_display_scale(agg)
                avail = [c for c in DISPLAY_COLUMNS if c in disp.columns]
                out = disp[avail].rename(columns={k: DISPLAY_EN[k] for k in avail if k in DISPLAY_EN})
                print(_SEP)
                print(f"Earnings Price History: {code}")
                print(_DASH)
                print_display_df(out, max_colwidth=25)
                print(_DASH)
                print(f"Total {len(agg)} periods")
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
        description="Get stock price history around earnings dates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("code", help="Stock code, e.g. HK.00700")
    parser.add_argument("--json", action="store_true", dest="output_json",
                        help="Output in JSON format")
    args = parser.parse_args()
    get_financials_earnings_price_history(args.code, output_json=args.output_json)
