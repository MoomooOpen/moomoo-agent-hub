#!/usr/bin/env python3
"""
Get Shareholders Holder Detail

Function: Get detailed holder list for a specific holding type of a stock, with support for
          type filter, sort column and report period selection
Usage: python get_shareholders_holder_detail.py [-h] [--request-type REQUEST_TYPE] [--next-key NEXT_KEY] [--num NUM] [--sort-column SORT_COLUMN] [--sort-type SORT_TYPE] [--period-id PERIOD_ID] [--holder-id HOLDER_ID] [--json] code

API Limits:
- Max 30 requests per 30 seconds
- Supports HK and US equities and funds
- Pagination supported, default 10 per page; pagination key is string type

Parameter Description:
- code: Stock code, e.g. US.AAPL
- --request-type: Request type: 0=Default, 1000=All, 1=Other Institutions,
                  2=Traditional Investment Managers, 3=Hedge Funds, 4=Venture Capital/PE,
                  5=Corporate Pension, 6=Foundation Funds, 7=Insurance Companies,
                  8=Banks/Investment Banks, 9=Family Offices/Trusts, 10=Sovereign Wealth Funds,
                  11=REITs, 12=Structured Finance Managers, 13=Union Pension,
                  14=Government Pension, 15=Endowment Funds, 100=Individuals, 200=ADS,
                  300=Listed Companies, 400=Unlisted Companies, 500=State-Owned Shares
- --next-key: Pagination key; omit for first page; "-1" means no more data
- --num: Number of results per page, default 10, range 1-50
- --sort-column: Sort column: 61=Holder Quantity (default), 62=Share Change Num
- --sort-type: Sort direction: 1=Desc (default), 2=Asc
- --period-id: Report period ID, 0=latest
- --holder-id: Holder object ID, 0=no filter; can be obtained from GetShareholdersOverview(3237)/
               GetShareholdersHoldingChanges(3238)/this API(3239)/GetInsiderHolderList(3241)/
               GetInsiderTradeList(3242)

Return Field Description:
- data.update_time_str: Data update time (YYYY-MM-DD HH:MM:SS)
- data.next_key:        Pagination key; "-1" means no more data
- data.items[]:         Holder detail list; each item contains period_text/holder_id/name/
                        holder_quantity/holder_quantity_change/holder_pct/holder_pct_change/
                        holding_date_str/close_price/price_change_pct/source_group_name
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

import pandas as pd

_SEP = "=" * 64
_DASH = "-" * 64


def _build_display_df(data: pd.DataFrame) -> pd.DataFrame:
    rows = []
    any_large_quantity = any(
        abs(float(r.get("holder_quantity") or 0)) >= 10000
        for _, r in data.iterrows()
    )
    any_large_change = any(
        abs(float(r.get("holder_quantity_change") or 0)) >= 10000
        for _, r in data.iterrows()
    )

    def _isnull(v):
        return v is None or (isinstance(v, float) and pd.isna(v))

    for _, row in data.iterrows():
        holder_id = row.get("holder_id")
        holder_quantity = row.get("holder_quantity")
        holder_quantity_change = row.get("holder_quantity_change")
        holder_pct = row.get("holder_pct")
        holder_pct_change = row.get("holder_pct_change")
        close_price = row.get("close_price")
        price_change_pct = row.get("price_change_pct")
        rows.append({
            "Period Text":          str(row.get("period_text") or "") or "-",
            "Holding Date Str":     str(row.get("holding_date_str") or "") or "-",
            "Holder Id":            int(holder_id) if not _isnull(holder_id) else 0,
            "Name":                 str(row.get("name") or "") or "-",
            "Holder Quantity": (
                format_big_number(holder_quantity)
                if any_large_quantity and not _isnull(holder_quantity)
                else (str(int(holder_quantity)) if not _isnull(holder_quantity) else "-")
            ),
            "Holder Quantity Change": (
                format_big_number(holder_quantity_change)
                if any_large_change and not _isnull(holder_quantity_change)
                else (str(int(holder_quantity_change)) if not _isnull(holder_quantity_change) else "-")
            ),
            "Holder Pct":           f"{float(holder_pct):.2f}%" if holder_pct is not None else "-",
            "Holder Pct Change":    f"{float(holder_pct_change):.2f}%" if holder_pct_change is not None else "-",
            "Close Price":          f"{float(close_price):.3f}" if close_price is not None else "-",
            "Price Change Pct":     f"{float(price_change_pct):.2f}%" if price_change_pct is not None else "-",
            "Source Group Name":    str(row.get("source_group_name") or "") or "-",
        })
    return pd.DataFrame(rows)


def get_shareholders_holder_detail(code, request_type=None, next_key=None, num=None,
                                   sort_column=None, sort_type=None, period_id=None,
                                   holder_id=None, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        ret, data = ctx.get_shareholders_holder_detail(
            code, request_type=request_type, next_key=next_key, num=num,
            sort_column=sort_column, sort_type=sort_type,
            period_id=period_id, holder_id=holder_id,
        )
        check_ret(ret, data, ctx, "get shareholders holder detail")

        page_next_key = data.attrs.get("next_key", "-1") if hasattr(data, "attrs") else "-1"
        if is_empty(data):
            page_next_key = "-1"
        row_count = len(data) if not is_empty(data) else 0
        next_key_display = "End(-1)" if page_next_key == "-1" else str(page_next_key)

        if output_json:
            if is_empty(data):
                records = []
                update_time_str = ""
            else:
                update_time_str = str(data.iloc[0].get("update_time_str", "") or "")
                records = df_to_records(data)
                for r in records:
                    r.pop("update_time", None)
                    r.pop("update_time_str", None)
            inner = {
                "update_time_str": update_time_str,
                "next_key": page_next_key,
                "items": records,
            }
            print(json.dumps({"code": code, "data": inner}, ensure_ascii=False))
        else:
            if is_empty(data):
                print("No data")
            else:
                update_time_str = str(data.iloc[0].get("update_time_str", "") or "")
                print(_SEP)
                print(f"Shareholders Holder Detail: {code}"
                      + (f"  Updated: {update_time_str}" if update_time_str else ""))
                print(_DASH)
                print_display_df(_build_display_df(data), max_colwidth=28)
                print(_DASH)
                print(f"Count: {row_count}   --next-key: {next_key_display}")
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
        description="Get detailed holder list by type with pagination support"
    )
    parser.add_argument("code", help="Stock code, e.g. US.AAPL")
    parser.add_argument("--request-type", type=int, default=None, dest="request_type",
                        help="Request type: 0=Default, 1000=All, 1=Other Institutions, "
                             "2=Traditional Investment Managers, 3=Hedge Funds, "
                             "4=Venture Capital/PE, 5=Corporate Pension, 6=Foundation Funds, "
                             "7=Insurance Companies, 8=Banks/Investment Banks, "
                             "9=Family Offices/Trusts, 10=Sovereign Wealth Funds, 11=REITs, "
                             "12=Structured Finance Managers, 13=Union Pension, "
                             "14=Government Pension, 15=Endowment Funds, 100=Individuals, "
                             "200=ADS, 300=Listed Companies, 400=Unlisted Companies, "
                             "500=State-Owned Shares")
    parser.add_argument("--next-key", default=None, dest="next_key",
                        help='Pagination key; omit for first page; "-1" means no more data')
    parser.add_argument("--num", type=int, default=None,
                        help="Number of results per page, default 10, range 1-50")
    parser.add_argument("--sort-column", type=int, default=None, dest="sort_column",
                        help="Sort column: 61=Holder Quantity (default), 62=Share Change Num")
    parser.add_argument("--sort-type", type=int, default=None, dest="sort_type",
                        help="Sort direction: 1=Desc (default), 2=Asc")
    parser.add_argument("--period-id", type=int, default=None, dest="period_id",
                        help="Report period ID, 0=latest")
    parser.add_argument("--holder-id", type=int, default=None, dest="holder_id",
                        help="Holder object ID, 0=no filter; can be obtained from 3237/3238/3239/3241/3242")
    parser.add_argument("--json", action="store_true", dest="output_json",
                        help="Output in JSON format")
    args = parser.parse_args()
    get_shareholders_holder_detail(
        args.code,
        request_type=args.request_type,
        next_key=args.next_key,
        num=args.num,
        sort_column=args.sort_column,
        sort_type=args.sort_type,
        period_id=args.period_id,
        holder_id=args.holder_id,
        output_json=args.output_json,
    )
