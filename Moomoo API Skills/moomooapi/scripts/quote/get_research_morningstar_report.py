#!/usr/bin/env python3
"""
Get Morningstar Report

Function: Get Morningstar research report for a stock, including star rating, fair value,
          economic moat, financial health, capital allocation and analyst notes
Usage: python get_research_morningstar_report.py [-h] [--json] code

API Limits:
- Max 30 requests per 30 seconds
- Supports equities and REITs

Parameter Description:
- code: Stock code, e.g. US.AAPL

Return Field Description:
- rating_type:                         Rating type (Qot_Common.MorningstarRatingType: 1=Quantitative 2=Qualitative)
- star_rating / star_update_time / star_update_time_str: Morningstar star rating (1-5) and update time
- fair_value:                          Fair value
- economic_moat_label / uncertainty_label / capital_allocation_label: Rating labels per dimension
- [xxx]_content (multiple):           Analysis text per dimension; covers fair_value/economic_moat/
                                       uncertainty/financial_health/capital_allocation/analyst_note/
                                       investment_thesis/fundamentals/valuation
- analyst_note_title:                 Analyst note title
- bull_say / bear_say:                 Bull/bear argument lists; each item contains context/update_time_str
- analyst_report_by_line:             Analyst by-line list
- analyst_report_update_time / analyst_report_update_time_str: Analyst report update time
- pdf_url:                             PDF report URL
"""
import argparse
import json
import sys
import os as _os

sys.path.insert(0, _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..")))
from common import create_quote_context, check_ret, safe_close, is_empty

_SEP = "=" * 64
_DASH = "-" * 64

_RATING_TYPE_LABEL = {
    1: "Quantitative",
    2: "Qualitative",
}

_STAR_LABEL = {
    1: "*",
    2: "**",
    3: "***",
    4: "****",
    5: "*****",
}


def _swut_text(d):
    if not d:
        return ""
    return d.get("context") or ""


def _swut_time(d):
    if not d:
        return ""
    return d.get("update_time_str") or ""


def get_research_morningstar_report(code, output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        ret, data = ctx.get_research_morningstar_report(code)
        check_ret(ret, data, ctx, "get Morningstar report")

        if is_empty(data) or not any(data.values()):
            if output_json:
                print(json.dumps({"code": code, "data": {}}))
            else:
                print("No data")
            return

        if output_json:
            print(json.dumps({"code": code, "data": data}, ensure_ascii=False))
            return

        print(_SEP)
        print(f"Morningstar Report: {code}")
        print(_DASH)

        rt = data.get("rating_type")
        if rt is not None:
            print(f"Rating Type:        {_RATING_TYPE_LABEL.get(rt, str(rt))}")
        sr = data.get("star_rating")
        if sr is not None:
            print(f"Star Rating:        {_STAR_LABEL.get(sr, str(sr))}")
        star_time = data.get("star_update_time_str")
        if star_time:
            print(f"Star Update Date:   {star_time}")
        fv = data.get("fair_value")
        if fv is not None:
            print(f"Fair Value:         {fv:.3f}")
        fvc = data.get("fair_value_content")
        fv_time = _swut_time(fvc)
        if fv_time:
            print(f"Fair Value Date:    {fv_time}")
        if any([rt, sr, star_time, fv]):
            print()

        fvc_text = _swut_text(fvc)
        if fvc_text:
            print("[Fair Value Analysis]")
            if fv_time:
                print(f"  Update Date: {fv_time}")
            for line in fvc_text.splitlines():
                print(f"  {line}")
            print()

        def _print_rating_section(title, label, content_d):
            text = _swut_text(content_d)
            time_str = _swut_time(content_d)
            if not label and not text:
                return
            print(f"[{title}]")
            if label:
                print(f"  Rating: {label}")
            if time_str:
                print(f"  Update Date: {time_str}")
            if text:
                for line in text.splitlines():
                    print(f"  {line}")
            print()

        _print_rating_section("Economic Moat",
                              data.get("economic_moat_label"),
                              data.get("economic_moat_content"))
        _print_rating_section("Uncertainty",
                              data.get("uncertainty_label"),
                              data.get("uncertainty_content"))
        _print_rating_section("Financial Health",
                              data.get("financial_health_label"),
                              data.get("financial_health_content"))
        _print_rating_section("Capital Allocation",
                              data.get("capital_allocation_label"),
                              data.get("capital_allocation_content"))

        by_lines = data.get("analyst_report_by_line") or []
        ar_time = data.get("analyst_report_update_time_str")
        if by_lines or ar_time:
            print("[Analyst By-Line]")
            for name in by_lines:
                print(f"  {name}")
            if ar_time:
                print(f"  Report Update Date: {ar_time}")
            print()

        bull = data.get("bull_say") or []
        if bull:
            print("[Bull Case]")
            bull_time = _swut_time(bull[0])
            if bull_time:
                print(f"  Update Date: {bull_time}")
            for item in bull:
                print(f"  - {_swut_text(item)}")
            print()

        bear = data.get("bear_say") or []
        if bear:
            print("[Bear Case]")
            bear_time = _swut_time(bear[0])
            if bear_time:
                print(f"  Update Date: {bear_time}")
            for item in bear:
                print(f"  - {_swut_text(item)}")
            print()

        note_title_d = data.get("analyst_note_title")
        note_content_d = data.get("analyst_note_content")
        note_title = _swut_text(note_title_d)
        note_content = _swut_text(note_content_d)
        note_time = _swut_time(note_title_d) or _swut_time(note_content_d)
        if note_title or note_content:
            print("[Analyst Note]")
            if note_title:
                print(f"  Title: {note_title}")
            if note_time:
                print(f"  Update Date: {note_time}")
            if note_content:
                for line in note_content.splitlines():
                    print(f"  {line}")
            print()

        thesis_d = data.get("investment_thesis_content")
        thesis_text = _swut_text(thesis_d)
        thesis_time = _swut_time(thesis_d)
        if thesis_text:
            print("[Investment Thesis]")
            if thesis_time:
                print(f"  Update Date: {thesis_time}")
            for line in thesis_text.splitlines():
                print(f"  {line}")
            print()

        fund_text = _swut_text(data.get("fundamentals_content"))
        if fund_text:
            print("[Fundamentals]")
            for line in fund_text.splitlines():
                print(f"  {line}")
            print()

        val_text = _swut_text(data.get("valuation_content"))
        if val_text:
            print("[Valuation]")
            for line in val_text.splitlines():
                print(f"  {line}")
            print()

        pdf_url = data.get("pdf_url")
        if pdf_url:
            print(f"PDF Report URL: {pdf_url}")

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
    parser = argparse.ArgumentParser(description="Get Morningstar research report")
    parser.add_argument("code", help="Stock code, e.g. US.AAPL")
    parser.add_argument("--json", action="store_true", dest="output_json",
                        help="Output in JSON format")
    args = parser.parse_args()
    get_research_morningstar_report(args.code, output_json=args.output_json)
