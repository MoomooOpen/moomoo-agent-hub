#!/usr/bin/env python3
"""
Get Financial Statements

Function: Get financial statements for a stock (Income/BalanceSheet/CashFlow/MainIndex)
Usage: python get_financials_statements.py [-h] [--statement-type STATEMENT_TYPE] [--financial-type FINANCIAL_TYPE] [--currency-code CURRENCY_CODE] [--next-key KEY] [--num N] [--json] code

API Limits:
- Max 30 requests per 30 seconds
- Supports equities and funds

Parameter Description:
- code: Stock code, e.g. HK.00700
- --statement-type: Statement type: 1=Income 2=BalanceSheet 3=CashFlow 4=MainIndex (default: 1)
- --financial-type: Financial period type: 1=Q1 2=Q2 3=Q3 4=Q4 5=Q6(Q1+Q2) 6=Q9(Q1+Q2+Q3)
                    7=Annual 9=QuarterlyCombo(Q1/Q2/Q3/Q4) 10=Quarterly+Annual 11=CumulativeQuarterly
                    (default: 10)
- --currency-code: Currency code (ISO 4217), e.g. CNY, USD, HKD; empty = original currency
- --next-key: Pagination key; omit for first page; "-1" means no more data
- --num: Number of results per page, default 10, range 1-50

Return Field Description:
- structure_list: Field structure list; each item contains field_id and display_name
- report_list:    Report data list; each item contains period_text/date_time_str/fiscal_year/
                  financial_type/currency_code/currency_info/accounting_standards/auditor_report
                  and item_list (each containing field_id/data/yoy/qoq)
- next_key:       Pagination key; "-1" means no more data
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
)

_SEP = "=" * 64
_DASH = "-" * 64

def _fmt_value(v):
    if v is None:
        return "--"
    try:
        f = float(v)
        return format_big_number(f)
    except (TypeError, ValueError):
        return str(v)


def _fmt_pct(v):
    if v is None:
        return "--"
    try:
        return f"{float(v):.2f}%"
    except (TypeError, ValueError):
        return "--"


def _build_display_output(code, result):
    lines = []
    lines.append(_SEP)
    lines.append(f"Financial Statements: {code}")
    lines.append(_DASH)

    structure_list = result.get("structure_list", [])
    report_list = result.get("report_list", [])

    if not report_list:
        lines.append("No data")
    else:
        id_to_name = {e["field_id"]: e["display_name"] or f"Field{e['field_id']}" for e in structure_list}

        for rpt in report_list:
            period = rpt.get("period_text") or "--"
            date_s = rpt.get("date_time_str") or "--"
            cur_info = rpt.get("currency_info") or ""
            acc_std = rpt.get("accounting_standards") or ""
            aud_report = rpt.get("auditor_report") or ""
            cur_code = rpt.get("currency_code") or ""

            meta_parts = [f"Period End: {date_s}"]
            if cur_info:
                meta_parts.append(f"Currency: {cur_info}")
            if cur_code and cur_code != cur_info:
                meta_parts.append(f"Currency Code: {cur_code}")
            if acc_std:
                meta_parts.append(f"Accounting Standards: {acc_std}")
            if aud_report:
                meta_parts.append(f"Auditor Report: {aud_report}")

            lines.append(f"[{period}]  " + "  ".join(meta_parts))

            item_map = {item["field_id"]: item for item in rpt.get("item_list", [])}
            for fid, fname in sorted(id_to_name.items()):
                item = item_map.get(fid)
                if item is None:
                    continue
                d = item.get("data")
                yoy = item.get("yoy")
                qoq = item.get("qoq")
                val_str = _fmt_value(d)
                extras = []
                if yoy is not None:
                    extras.append(f"YoY: {_fmt_pct(yoy)}")
                if qoq is not None:
                    extras.append(f"QoQ: {_fmt_pct(qoq)}")
                extra_str = "  " + "  ".join(extras) if extras else ""
                lines.append(f"  {fname}: {val_str}{extra_str}")

    lines.append(_DASH)
    nk = result.get("next_key", "-1")
    nk_disp = "End(-1)" if nk == "-1" else nk
    lines.append(f"Count: {len(report_list)}  --next-key: {nk_disp}")
    lines.append(_SEP)
    return "\n".join(lines)


def get_financials_statements(code, statement_type=None, financial_type=None, currency_code=None, next_key=None, num=None, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        ret, data = ctx.get_financials_statements(
            code,
            statement_type=statement_type,
            financial_type=financial_type,
            currency_code=currency_code,
            next_key=next_key,
            num=num,
        )
        check_ret(ret, data, ctx, "get financial statements")

        report_list = data.get("report_list", []) if isinstance(data, dict) else None
        no_data = is_empty(data) or (isinstance(data, dict) and not report_list)
        if no_data:
            if output_json:
                print(json.dumps({"code": code, "data": {}}))
            else:
                print("No data")
            return

        if output_json:
            print(json.dumps({"code": code, "data": data}, ensure_ascii=False, default=str))
        else:
            print(_build_display_output(code, data))

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
    parser = argparse.ArgumentParser(description="Get financial statements with pagination support")
    parser.add_argument("code", help="Stock code, e.g. HK.00700")
    parser.add_argument(
        "--statement-type", type=int, default=None,
        help="Statement type: 1=Income 2=BalanceSheet 3=CashFlow 4=MainIndex (default: 1)",
    )
    parser.add_argument(
        "--financial-type", type=int, default=None, dest="financial_type",
        help=(
            "Financial period type: 1=Q1 2=Q2 3=Q3 4=Q4 5=Q6(Q1+Q2) 6=Q9(Q1+Q2+Q3) "
            "7=Annual 9=QuarterlyCombo 10=Quarterly+Annual 11=CumulativeQuarterly (default: 10)"
        ),
    )
    parser.add_argument(
        "--currency-code", type=str, default=None,
        help="Currency code (ISO 4217), e.g. CNY, USD, HKD; empty = original currency",
    )
    parser.add_argument(
        "--next-key", type=str, default=None, metavar="KEY",
        help='Pagination key; omit for first page; "-1" means no more data',
    )
    parser.add_argument(
        "--num", type=int, default=None, metavar="N",
        help="Number of results per page, default 10, range 1-50",
    )
    parser.add_argument("--json", action="store_true", dest="output_json",
                        help="Output in JSON format")

    args = parser.parse_args()
    get_financials_statements(args.code, statement_type=args.statement_type,
                              financial_type=args.financial_type, currency_code=args.currency_code,
                              next_key=args.next_key, num=args.num, output_json=args.output_json)
