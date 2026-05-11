#!/usr/bin/env python3
"""
Get Candlestick Data

Function: Get Candlestick (candlestick) data for a stock, supports both real-time and historical data
- Real-time Candlestick: Get the most recent N Candlesticks (requires subscription)
- Historical Candlestick: Get historical data for a specified date range (no subscription needed)

API Limits:
- Real-time Candlestick: Max 1000 most recent bars, requires subscription first
- Historical Candlestick: Max 60 requests per 30 seconds; minute K up to 8 years, daily K up to 20 years
- Historical Candlestick quota: Each stock requested within 30 days uses 1 quota; same stock does not count again
- PE ratio and turnover rate are only available for daily K and above periods for equities
- Options only provide daily K, 1-min K, 5-min K, 15-min K, 60-min K
- US pre-market, after-hours, and overnight sessions only for 60-min and below periods

Parameter Description:
- num: Max 1000 bars per page (historical Candlestick auto-paginates to fetch all)
- max-page: Limit max pagination count; if not set, fetches all

Return Field Description:
- time_key: Format yyyy-MM-dd HH:mm:ss; HK/A-share in Beijing time, US in Eastern time
- turnover_rate: Percentage field, returns decimal by default, e.g. 0.01 corresponds to 1%
- last_close: Previous period's close price; first bar's last_close may be 0
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
    safe_float,
    safe_int,
    KLType,
    SubType,
    AuType,
    Session,
    RET_OK,
)

# session only for US historical Candlestick, OVERNIGHT not supported
HISTORY_SESSION_MAP = {
    "NONE": Session.NONE,
    "RTH": Session.RTH,
    "ETH": Session.ETH,
    "ALL": Session.ALL,
}

KTYPE_MAP = {
    "1m": KLType.K_1M,
    "3m": KLType.K_3M,
    "5m": KLType.K_5M,
    "15m": KLType.K_15M,
    "30m": KLType.K_30M,
    "60m": KLType.K_60M,
    "1d": KLType.K_DAY,
    "1w": KLType.K_WEEK,
    "1M": KLType.K_MON,
    "1Q": KLType.K_QUARTER,
    "1Y": KLType.K_YEAR,
}

REHAB_MAP = {
    "none": AuType.NONE,
    "forward": AuType.QFQ,
    "backward": AuType.HFQ,
}

KTYPE_TO_SUBTYPE = {
    KLType.K_1M: SubType.K_1M,
    KLType.K_3M: SubType.K_3M,
    KLType.K_5M: SubType.K_5M,
    KLType.K_15M: SubType.K_15M,
    KLType.K_30M: SubType.K_30M,
    KLType.K_60M: SubType.K_60M,
    KLType.K_DAY: SubType.K_DAY,
    KLType.K_WEEK: SubType.K_WEEK,
    KLType.K_MON: SubType.K_MON,
    KLType.K_QUARTER: SubType.K_QUARTER,
    KLType.K_YEAR: SubType.K_YEAR,
}


def get_kline(code, ktype="1d", num=10, start=None, end=None, rehab="forward",
              max_page=None, session_str="NONE", output_json=False):
    kl_type = KTYPE_MAP.get(ktype, KLType.K_DAY)
    au_type = REHAB_MAP.get(rehab, AuType.QFQ)
    session = HISTORY_SESSION_MAP.get(session_str.upper(), Session.NONE)

    ctx = None
    try:
        ctx = create_quote_context()
        if start or end:
            # Historical Candlestick: supports pagination to fetch all data
            import pandas as pd
            page_size = min(num, 1000)
            ret, data, page_req_key = ctx.request_history_kline(
                code, start=start, end=end,
                ktype=kl_type, autype=au_type,
                max_count=page_size,
                session=session,
            )
            check_ret(ret, data, ctx, "Get Candlestick")
            all_data = data
            page_count = 1
            while page_req_key is not None:
                if max_page and page_count >= max_page:
                    break
                ret, data, page_req_key = ctx.request_history_kline(
                    code, start=start, end=end,
                    ktype=kl_type, autype=au_type,
                    max_count=page_size,
                    page_req_key=page_req_key,
                    session=session,
                )
                check_ret(ret, data, ctx, "Get Candlestick (pagination)")
                if not is_empty(data):
                    all_data = pd.concat([all_data, data], ignore_index=True)
                page_count += 1
            data = all_data
            source = "history"
        else:
            sub_type = KTYPE_TO_SUBTYPE.get(kl_type, SubType.K_DAY)
            ret, msg = ctx.subscribe([code], [sub_type])
            if ret != RET_OK:
                print(f"Subscription failed: {msg}")
                sys.exit(1)
            ret, data = ctx.get_cur_kline(code, num, kl_type, au_type)
            source = "realtime"
            check_ret(ret, data, ctx, "Get Candlestick")

        if is_empty(data):
            if output_json:
                print(json.dumps({"code": code, "ktype": ktype, "data": []}))
            else:
                print("No data")
            return

        records = []
        for i in range(len(data)):
            row = data.iloc[i] if hasattr(data, "iloc") else data[i]
            records.append({
                "time": safe_get(row, "time_key", default=""),
                "open": safe_float(safe_get(row, "open", default=0)),
                "high": safe_float(safe_get(row, "high", default=0)),
                "low": safe_float(safe_get(row, "low", default=0)),
                "close": safe_float(safe_get(row, "close", default=0)),
                "volume": safe_int(safe_get(row, "volume", default=0)),
                "turnover": safe_float(safe_get(row, "turnover", default=0)),
            })

        if output_json:
            print(json.dumps({"code": code, "ktype": ktype, "source": source, "data": records}, ensure_ascii=False))
        else:
            title = f"Candlestick: {code} ({ktype}"
            if start or end:
                title += f", {start or 'start'} to {end or 'now'}"
            else:
                title += f", last {num} bars"
            title += ")"

            print("=" * 80)
            print(title)
            print("=" * 80)
            print(f"  {'Time':<20} {'Open':>10} {'High':>10} {'Low':>10} {'Close':>10} {'Volume':>12}")
            print("  " + "-" * 76)
            for r in records:
                print(f"  {r['time']:<20} {r['open']:>10.2f} {r['high']:>10.2f} {r['low']:>10.2f} {r['close']:>10.2f} {r['volume']:>12}")
            print("=" * 80)

    except Exception as e:
        if output_json:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))
        else:
            print(f"Error: {e}")
        sys.exit(1)
    finally:
        safe_close(ctx)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get Candlestick data (real-time or historical)")
    parser.add_argument("code", help="Stock code, e.g. US.AAPL, HK.00700")
    parser.add_argument("--ktype", choices=["1m", "3m", "5m", "15m", "30m", "60m", "1d", "1w", "1M", "1Q", "1Y"],
                        default="1d", help="Candlestick type (default: 1d)")
    parser.add_argument("--num", type=int, default=10, help="Number of Candlesticks, page size for historical mode (default: 10)")
    parser.add_argument("--start", type=str, default=None, help="Historical data start date (YYYY-MM-DD)")
    parser.add_argument("--end", type=str, default=None, help="Historical data end date (YYYY-MM-DD)")
    parser.add_argument("--max-page", type=int, default=None, help="Max pagination count for historical Candlestick; if not set, fetches all")
    parser.add_argument("--rehab", choices=["none", "forward", "backward"], default="forward",
                        help="Adjustment type: none (no adjustment), forward (forward adjustment), backward (backward adjustment)")
    parser.add_argument("--session", choices=["NONE", "RTH", "ETH", "ALL"],
                        default="NONE", help="US stock session-based historical Candlestick (US only, OVERNIGHT not supported)")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output in JSON format")
    args = parser.parse_args()
    get_kline(args.code, args.ktype, args.num, start=args.start, end=args.end,
              rehab=args.rehab, max_page=args.max_page, session_str=args.session,
              output_json=args.output_json)
