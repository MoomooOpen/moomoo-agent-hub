#!/usr/bin/env python3
"""
Get Indicator Calculation Result (calcId + push mode)

Function: Submit indicator calc request (Qot_RequestIndicatorCalc, 3260) using local
          cached Candlestick data; req returns calcId immediately, OpenD pushes result
          via Qot_PushIndicatorCalc (3261); this script registers IndicatorCalcHandlerBase
          and waits synchronously for the push matching calcId.

Code and Candlestick period are read from code/ktype at the top level of --kl-file JSON
(written by get_kline).

Usage:
    python get_indicator_calc_result.py --short-name MA --lang 1 \
        --kl-file E:/OpenD/Output/test_cache_kl_HK_00700_day_100.json --param 0=5
    python get_indicator_calc_result.py --short-name MA --lang 1 \
        --kl-file E:/OpenD/Output/test_cache_kl_HK_00700_day_100.json --param 0=5 --num 30

Parameters:
    --short-name  Indicator short name (IndicatorInfo.shortName)              [required]
    --lang        Language: 1=MyLang, 2=Python (IndicatorLangType)          [required]
    --kl-file     Candlestick JSON path (code/ktype/data from get_kline)      [required]
    --param       Input override idx=value (IndicatorInputItem, index from 0); repeatable
    --num         Use first N Candlesticks for calc (positive int); omit for all in file
    --json        Output JSON
"""
import argparse
import json
import sys
import threading
import os as _os
import pandas as pd
sys.path.insert(0, _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..")))
from common import create_quote_context, check_ret, safe_close
from moomoo import IndicatorCalcHandlerBase, RET_OK


# JSON top-level ktype string → Qot_Common.KLType wire value
KTYPE_WIRE_MAP = {
    "1m": 1,  "3m": 10, "5m": 6,  "15m": 7, "30m": 8, "60m": 9,
    "1d": 2,  "1w": 3,  "1M": 4,  "1Q": 11, "1Y": 5,
}


def _load_kl_payload(kl_file):
    with open(kl_file, "r", encoding="utf-8") as f:
        raw = json.load(f)
    if not isinstance(raw, dict):
        raise ValueError("Candlestick JSON must be an object with code/ktype/data fields")
    code = raw.get("code")
    ktype = raw.get("ktype")
    records = raw.get("data", [])
    if not code:
        raise ValueError("Missing stock code: no code field in JSON")
    return code, ktype, records


def _resolve_kl_type(json_ktype):
    if json_ktype is None:
        raise ValueError("Missing Candlestick period: no ktype field in JSON")
    if isinstance(json_ktype, int):
        return json_ktype
    s = str(json_ktype)
    if s in KTYPE_WIRE_MAP:
        return KTYPE_WIRE_MAP[s]
    raise ValueError(f"Unrecognized ktype: {json_ktype!r} (supported: {list(KTYPE_WIRE_MAP)} or int wire value)")


def _parse_params(items):
    result = []
    for it in items or []:
        if "=" not in it:
            raise ValueError(f"--param format must be idx=value, got: {it}")
        idx_str, val = it.split("=", 1)
        result.append({"index": int(idx_str), "value": val})
    return result


def _normalize_klines_for_sdk(records):
    """get_kline --json outputs time; SDK request_indicator_calc_async expects time_key."""
    out = []
    for row in records:
        r = dict(row)
        if "time_key" not in r and "time" in r:
            r["time_key"] = r.pop("time")
        out.append(r)
    return out


class _CalcCollector(IndicatorCalcHandlerBase):
    """Route push by calcId and wait for the target calcId result."""
    def __init__(self):
        super().__init__()
        self._lock = threading.Lock()
        self._results = {}
        self._cond = threading.Condition(self._lock)

    def on_recv_rsp(self, rsp_pb):
        ret_code, content = super().on_recv_rsp(rsp_pb)
        if isinstance(content, dict) and content.get("calc_id"):
            with self._cond:
                self._results[content["calc_id"]] = (ret_code, content)
                self._cond.notify_all()
        elif ret_code != RET_OK:
            print(f"push parse error: {content}", file=sys.stderr)
        return ret_code, content

    def wait_for(self, calc_id, timeout=60):
        with self._cond:
            while calc_id not in self._results:
                if not self._cond.wait(timeout):
                    raise TimeoutError(
                        f"Push wait timed out ({timeout}s), calc_id={calc_id!r}"
                    )
            return self._results[calc_id]


def get_indicator_calc_result(short_name, lang, kl_file, param_items, output_json, num=None):
    ctx = None
    try:
        code, kl_type, records = _load_kl_payload(kl_file)
        kl_type = _resolve_kl_type(kl_type)
        klines = _normalize_klines_for_sdk(records)
        input_params = _parse_params(param_items)
        ctx = create_quote_context()
        collector = _CalcCollector()
        ctx.set_handler(collector)

        ret, calc_id = ctx.request_indicator_calc_async(
            short_name=short_name,
            lang_type=lang,
            code=code,
            kl_type=kl_type,
            klines=klines,
            num=num,
            input_params=input_params,
        )
        check_ret(ret, calc_id, ctx, "Get indicator calc result")

        if not output_json:
            print(f"Calc request sent calc_id={calc_id}, waiting for push (up to 60s)...")

        ret_code, result = collector.wait_for(calc_id)

        if output_json:
            print(json.dumps({
                "calc_id":     calc_id,
                "success":     ret_code == RET_OK,
                "err_msg":     result.get("err_msg", ""),
                "outputs":     result.get("outputs", []),
                "output_rows": result.get("output_rows", []),
            }, ensure_ascii=False))
            return

        if ret_code != RET_OK:
            print(f"calc_id={calc_id}  calc failed: {result.get('err_msg', '')}")
            sys.exit(1)

        outputs = result["outputs"]
        rows = result["output_rows"]
        lang_label = {1: "MyLang", 2: "Python"}.get(lang, str(lang))
        print(f"calc_id={calc_id}")
        print(f"Indicator: {short_name}  lang={lang_label}  {code}  bars={len(klines)}  lines={len(outputs)}  (last 10 rows)")

        col_names = [o.get("name", f"line{i}") for i, o in enumerate(outputs)]
        records = []
        for row in rows:
            vals = row.get("values") or []
            rec = {"time": row.get("time", "")}
            for i, name in enumerate(col_names):
                rec[name] = vals[i] if i < len(vals) else None
            records.append(rec)

        df = pd.DataFrame(records, columns=["time", *col_names])
        with pd.option_context("display.max_columns", None,
                               "display.width", None,
                               "display.float_format", lambda v: f"{v:.3f}"):
            print(df.tail(10).to_string(index=False))
    except Exception as e:
        if output_json:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))
        else:
            print(f"Error: {e}")
        sys.exit(1)
    finally:
        safe_close(ctx)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get indicator calc result: submit request and wait for push")
    parser.add_argument("--short-name", required=True)
    parser.add_argument("--lang", type=int, required=True, choices=[1, 2])
    parser.add_argument("--kl-file", required=True, help="Candlestick JSON (code/ktype/data)")
    parser.add_argument("--param", action="append", default=[], dest="params", metavar="IDX=VAL")
    parser.add_argument("--num", type=int, default=None,
                        help="Use first N Candlesticks for calc; omit for all in --kl-file")
    parser.add_argument("--json", action="store_true", dest="output_json")
    args = parser.parse_args()
    get_indicator_calc_result(
        short_name=args.short_name,
        lang=args.lang,
        kl_file=args.kl_file,
        param_items=args.params,
        output_json=args.output_json,
        num=args.num,
    )
