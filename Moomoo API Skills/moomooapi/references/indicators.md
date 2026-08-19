<!-- TOC: Technical Indicators -->
# Technical Indicators

Indicator list and calculation (MA/MACD/RSI/KDJ/BOLL etc., 187 indicators).

### Indicators

#### Get Indicator List
When the user asks about "indicator list", "available indicators", "search indicators":
```bash
python skills/moomooapi/scripts/quote/get_indicator_list.py [--search SUB] [--lang 0|1|2] [--mode 0|1] [--json]
```

**Parameters**:
- --search: Filter by short_name substring (case-insensitive)
- --lang: Language filter: 0=no filter (default), 1=MyLang, 2=Python
- --mode: Search mode: 0=Partial (default), 1=Exact match and return script (requires --search)

**Examples**:
```bash
# List all indicators
python skills/moomooapi/scripts/quote/get_indicator_list.py

# Search indicators containing MA
python skills/moomooapi/scripts/quote/get_indicator_list.py --search MA

# Exact match and get script source
python skills/moomooapi/scripts/quote/get_indicator_list.py --search MACD --mode 1 --lang 1
```

#### Get Indicator Calculation Result
When the user asks about "calculate indicator", "indicator result", "MA calc", "MACD result", "RSI", "indicator calc":
```bash
python skills/moomooapi/scripts/quote/get_indicator_calc_result.py --short-name MA --lang 1 --kl-file <Candlestick JSON path> [--param 0=5] [--num 30] [--json]
```

**Prerequisite**: Run `get_kline.py --json` first to produce a cache file with code/ktype/data fields.

**Parameters**:
- --short-name: Indicator short name (IndicatorInfo.shortName, e.g. MA, MACD, RSI) [required]
- --lang: Language: 1=MyLang, 2=Python [required]
- --kl-file: Candlestick JSON path (code/ktype/data from get_kline --json) [required]
- --param: Input override, format idx=value (index from 0); repeatable; omit for cloud defaults
- --num: Use first N Candlesticks (positive int); omit for all bars in file

**Workflow example**:
```bash
# 1. Fetch Candlestick data (JSON to Output/)
python skills/moomooapi/scripts/quote/get_kline.py HK.00700 --ktype 1d --num 100 --json > Output/test_cache_kl_HK_00700_day_100.json

# 2. Calculate MA(5)
python skills/moomooapi/scripts/quote/get_indicator_calc_result.py --short-name MA --lang 1 --kl-file Output/test_cache_kl_HK_00700_day_100.json --param 0=5

# 3. Calculate MACD (default params)
python skills/moomooapi/scripts/quote/get_indicator_calc_result.py --short-name MACD --lang 1 --kl-file Output/test_cache_kl_HK_00700_day_100.json
```

---

---

**Related skills routing:** Related: Candlestick data → quote-commands.md; cloud indicator calculation in-body.
