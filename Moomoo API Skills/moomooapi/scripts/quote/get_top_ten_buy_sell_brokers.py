#!/usr/bin/env python3
"""
Get Top Ten Buy Sell Brokers

Function: Get top ten net buy and net sell broker lists for a HK stock (real-time or historical);
          real-time data includes avg price/total volume/total turnover; historical data includes
          net volume and broker name only
Usage: python get_top_ten_buy_sell_brokers.py [-h] [--days-before DAYS_BEFORE] [--json] code

API Limits:
- Max 30 requests per 30 seconds
- Supports HK equities and funds
- days_before=0 returns real-time data (includes avg_price/total_vol/total_turnover);
  days_before>0 returns net volume and broker name only

Parameter Description:
- code: Stock code, e.g. HK.00700
- --days: Trading days before current date; 0=real-time, >0=Nth historical trading day
          (default: real-time)

Return Field Description:
- data[]: Broker list sorted by net buy/sell volume descending; each item contains
          is_real_time/data_time/data_time_str/broker_name/buy_sell_type/net_vol/
          avg_price/total_vol/total_turnover
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
    format_big_number,
)

_SEP = "=" * 64
_DASH = "-" * 64

_COLS_REALTIME = ["broker_name", "net_vol", "avg_price", "total_vol", "total_turnover"]
_COLS_HIST = ["broker_name", "net_vol"]

_COLS_EN = {
    "broker_name":    "Broker Name",
    "net_vol":        "Net Vol",
    "avg_price":      "Avg Price",
    "total_vol":      "Total Vol",
    "total_turnover": "Total Turnover",
}


def get_top_ten_buy_sell_brokers(code, days_before=None, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        kwargs = {}
        if days_before is not None:
            kwargs["days_before"] = days_before
        ret, data = ctx.get_top_ten_buy_sell_brokers(code, **kwargs)
        check_ret(ret, data, ctx, "get top ten buy sell brokers")

        total_rows = len(data) if data is not None and not is_empty(data) else 0

        if output_json:
            records = df_to_records(data) if not is_empty(data) else []
            print(json.dumps({"code": code, "data": records}, ensure_ascii=False))
            return

        if is_empty(data):
            print("No data")
        else:
            update_time = ""
            if "data_time_str" in data.columns:
                _ts = data["data_time_str"].dropna()
                _ts = _ts[_ts.astype(str).str.len() > 0]
                if not _ts.empty:
                    update_time = str(_ts.iloc[0])

            print(_SEP)
            header = f"Top Ten Buy Sell Brokers: {code}"
            if days_before is not None:
                header += f"  days-before={days_before}"
            print(header)
            if update_time:
                print(f"Update Time: {update_time}")
            print(_DASH)

            is_realtime = data.iloc[0].get("is_real_time", True)
            cols = _COLS_REALTIME if is_realtime else _COLS_HIST
            buy_data = data[data["buy_sell_type"] == 1].copy() if "buy_sell_type" in data.columns else data
            sell_data = data[data["buy_sell_type"] == 2].copy() if "buy_sell_type" in data.columns else data

            def _print_section(label, df):
                avail = [c for c in cols if c in df.columns]
                print(f"\n{label}  ({len(df)} brokers)")
                print(_DASH)
                if is_empty(df):
                    print("No data")
                else:
                    sub = df[avail].copy()
                    for col in ("net_vol", "total_vol", "total_turnover"):
                        if col in sub.columns:
                            sub[col] = sub[col].apply(lambda x: format_big_number(x) if x else "-")
                    if "avg_price" in sub.columns:
                        sub["avg_price"] = sub["avg_price"].apply(lambda x: f"{x:.3f}" if x else "-")
                    sub = sub.rename(columns={k: _COLS_EN[k] for k in avail if k in _COLS_EN})
                    print_display_df(sub, max_colwidth=28)

            _print_section("Top Net Buy Brokers", buy_data)
            _print_section("Top Net Sell Brokers", sell_data)
            print(_DASH)
            print(f"Count: {total_rows}")
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
    parser = argparse.ArgumentParser(description="Get top ten net buy/sell brokers for HK stocks")
    parser.add_argument("code", help="Stock code, e.g. HK.00700")
    parser.add_argument("--days-before", type=int, default=None, dest="days_before",
                        help="Trading days before current date; 0=real-time, >0=historical (default: real-time)")
    parser.add_argument("--json", action="store_true", dest="output_json",
                        help="Output in JSON format")
    args = parser.parse_args()
    get_top_ten_buy_sell_brokers(args.code, days_before=args.days_before, output_json=args.output_json)
