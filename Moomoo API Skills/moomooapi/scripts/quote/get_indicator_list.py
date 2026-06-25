#!/usr/bin/env python3
"""
Get All Available Indicators

Function: List all loaded indicator entries. Each entry may include both MyLang and
          Python versions, showing short_name/full_name, each input value, and outputs.
          Use --search for case-insensitive substring filter (short_name only).
          --lang  Filter language: 0=Unknown (no filter), 1=MyLang, 2=Python
          --mode  Search mode: 0=Partial (default), 1=Exact match and return script
                  (Exact requires --search; matched entries include script field)
Usage: python get_indicator_list.py [--search SUB] [--lang 0|1|2] [--mode 0|1] [--json]
"""
import argparse
import json
import sys
import os as _os
sys.path.insert(0, _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..")))
from common import create_quote_context, check_ret, safe_close

ENTRY_SEP = "-" * 80
INFO_SEP = "-" * 40


def _fmt_value(v):
    """Render {'type': str, 'value': ...} as a string."""
    if v is None:
        return "<none>"
    t = v.get("type", "?")
    val = v.get("value")
    if t == "COLOR" and isinstance(val, dict):
        return "COLOR(a={alpha},r={red},g={green},b={blue})".format(**val)
    return f"{t}:{val}"


def _print_info(label, info):
    """Print one language version of an info dict."""
    print(f"  [{label}] short_name={info['short_name']}  full_name={info['full_name']}")
    inputs = info.get("inputs") or []
    if inputs:
        print(f"    inputs ({len(inputs)}):")
        for ipt in inputs:
            v = ipt.get("value")
            var_name = ipt.get("var_name")
            suffix = f"  [{var_name}]" if var_name else ""
            print(f"      #{ipt['index']:>2} {ipt['name']}{suffix}: {_fmt_value(v)}")
    outputs = info.get("outputs") or []
    if outputs:
        print(f"    outputs ({len(outputs)}):")
        for o in outputs:
            print(f"      #{o['index']:>2} {o['name']}")
    script = info.get("script") or ""
    if script:
        fence_lang = "python" if label.lower() == "python" else "mylang"
        print(f"    script ({len(script)} chars):")
        print(f"```{fence_lang}")
        print(script)
        print("```")


def get_indicator_list(output_json=False, search_key=None, lang_type=0, search_mode=0):
    ctx = None
    try:
        ctx = create_quote_context()
        ret, data = ctx.get_indicator_list(
            search_key=search_key,
            lang_type=lang_type,
            search_mode=search_mode,
        )
        check_ret(ret, data, ctx, "Get indicator list")

        if output_json:
            print(json.dumps({"data": data}, ensure_ascii=False))
            return

        print("=" * 80)
        lang_label = {0: "All", 1: "MyLang", 2: "Python"}.get(lang_type, str(lang_type))
        mode_label = {0: "Partial", 1: "Exact"}.get(search_mode, str(search_mode))
        print(f"Indicator list  lang={lang_label}  mode={mode_label}  search={search_key or '<none>'}")
        print("=" * 80)

        count_my = 0
        count_py = 0
        for idx, entry in enumerate(data):
            my = entry.get("my_lang")
            py = entry.get("python")
            if my:
                count_my += 1
            if py:
                count_py += 1

            ident_parts = []
            if my:
                ident_parts.append(f"MyLang:{my['short_name']}")
            if py:
                ident_parts.append(f"Python:{py['short_name']}")
            ident = " | ".join(ident_parts) if ident_parts else "<empty>"

            print(ENTRY_SEP)
            print(f"[{idx}] {ident}")

            if my:
                _print_info("MyLang", my)
            if my and py:
                print(INFO_SEP)
            if py:
                _print_info("Python", py)

        print("=" * 80)
        print(f"Total entries: {len(data)} (MyLang={count_my}, Python={count_py})")
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
        description=(
            "Get all available indicators (each entry may include MyLang/Python). "
            "Supports short_name substring filter, language filter, and Exact mode for script."
        )
    )
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output JSON (raw dict list)")
    parser.add_argument("--search", dest="search", default=None, metavar="SUB",
                        help="Search substring (case-insensitive); omit to return all")
    parser.add_argument("--lang", dest="lang", type=int, default=0, choices=[0, 1, 2],
                        help="Language filter: 0=no filter (default), 1=MyLang, 2=Python")
    parser.add_argument("--mode", dest="mode", type=int, default=0, choices=[0, 1],
                        help="Search mode: 0=Partial (default), 1=Exact match and return script")
    args = parser.parse_args()
    get_indicator_list(
        output_json=args.output_json,
        search_key=args.search,
        lang_type=args.lang,
        search_mode=args.mode,
    )
