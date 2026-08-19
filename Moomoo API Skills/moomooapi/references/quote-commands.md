<!-- TOC: Market Data Commands (Quote) -->
# Market Data Commands (Quote)

Quotes, Candlesticks, order book, capital flow, plates, search, screeners. For options see `options.md`.

> **One-shot panorama**: when you need a ticker's quote + financials + rating + valuation + options together, run `python skills/moomooapi/scripts/quote/collect.py US.AAPL --json [--with-options]` — fetches in parallel and returns a concise JSON (pairs with `references/analysis-frameworks.md` earnings-review card).

## Common Stock Lookup Table

When the user provides a Chinese name, English abbreviation, or Ticker, map it to the full code using the table below. For stocks not in the table, use your knowledge to determine the market and code; if uncertain, use AskUserQuestion to ask the user.

### HK Stocks

| Common Name | Code |
|---------|------|
| Tencent, 腾讯 | `HK.00700` |
| Alibaba, 阿里巴巴, 阿里 | `HK.09988` |
| Meituan, 美团 | `HK.03690` |
| Xiaomi, 小米 | `HK.01810` |
| JD.com, 京东 | `HK.09618` |
| Baidu, 百度 | `HK.09888` |
| NetEase, 网易 | `HK.09999` |
| Kuaishou, 快手 | `HK.01024` |
| BYD, 比亚迪 | `HK.01211` |
| SMIC, 中芯国际 | `HK.00981` |
| Hua Hong Semi, 华虹半导体 | `HK.01347` |
| SenseTime, 商汤 | `HK.00020` |
| Li Auto, 理想汽车, 理想 | `HK.02015` |
| NIO, 蔚来 | `HK.09866` |
| XPeng, 小鹏 | `HK.09868` |
| HSI ETF, 恒生指数 ETF | `HK.02800` |
| Tracker Fund, 盈富基金 | `HK.02800` |

### US Stocks

| Common Name | Code |
|---------|------|
| Apple, 苹果 | `US.AAPL` |
| Tesla, 特斯拉 | `US.TSLA` |
| NVIDIA, 英伟达 | `US.NVDA` |
| Microsoft, 微软 | `US.MSFT` |
| Google, Alphabet, 谷歌 | `US.GOOG` |
| Amazon, 亚马逊 | `US.AMZN` |
| Meta, Facebook, 脸书 | `US.META` |
| Futu, 富途 | `US.FUTU` |
| TSM, 台积电 | `US.TSM` |
| AMD | `US.AMD` |
| Qualcomm, 高通 | `US.QCOM` |
| Netflix, 奈飞 | `US.NFLX` |
| Disney, 迪士尼 | `US.DIS` |
| JPMorgan, JPM, 摩根大通 | `US.JPM` |
| Goldman Sachs, 高盛 | `US.GS` |
| BABA, Alibaba (US), 阿里巴巴 | `US.BABA` |
| JD, JD.com (US), 京东 | `US.JD` |
| PDD, Pinduoduo, 拼多多 | `US.PDD` |
| BIDU, Baidu (US), 百度 | `US.BIDU` |
| NIO (US), 蔚来 | `US.NIO` |
| XPEV, XPeng (US), 小鹏 | `US.XPEV` |
| LI, Li Auto (US), 理想 | `US.LI` |
| SPY, S&P 500 ETF, 标普500 ETF | `US.SPY` |
| QQQ, Nasdaq ETF, 纳指 ETF | `US.QQQ` |

### A-Shares

| Common Name | Code |
|---------|------|
| Kweichow Moutai, 贵州茅台, 茅台 | `SH.600519` |
| Ping An Bank, 平安银行 | `SZ.000001` |
| Ping An Insurance, 中国平安 | `SH.601318` |
| China Merchants Bank, 招商银行 | `SH.600036` |
| CATL, 宁德时代 | `SZ.300750` |
| Wuliangye, 五粮液 | `SZ.000858` |

## Table of Contents

- Get Market Snapshot
- Get Candlestick
- Get Order Book
- Get Tick-by-Tick Trades
- Get Time-Sharing Data
- Get Market State
- Get Capital Flow
- Get Capital Distribution
- Get Plate/Sector List
- Get Plate Constituents / Index Constituents
  - Plate Query Workflow
- Get Stock Info
- Search Quote Instruments
- Search News
- Stock Screener
- Stock Screener V2 (recommended for complex factors)
- Warrant Screener V2
- Get Stock's Plates/Sectors

---

### Get Market Snapshot
When the user asks about "quote", "price", or "market data":
```bash
python skills/moomooapi/scripts/quote/get_snapshot.py US.AAPL HK.00700 [--json]
```

### Get Candlestick
When the user asks about "Candlestick", "candlestick", or "historical trend":
```bash
# Real-time Candlestick (latest N bars)
python skills/moomooapi/scripts/quote/get_kline.py HK.00700 --ktype 1d --num 10

# Historical Candlestick (date range)
python skills/moomooapi/scripts/quote/get_kline.py HK.00700 --ktype 1d --start 2025-01-01 --end 2025-12-31
```
- `--ktype`: 1m, 3m, 5m, 15m, 30m, 60m, 1d, 1w, 1M, 1Q, 1Y
- `--rehab`: none (no adjustment), forward (forward adjusted, default), backward (backward adjusted)
- `--num`: Number of real-time Candlestick bars (default 10)
- `--session`: US stock session-based historical Candlestick, options: NONE/RTH/ETH/ALL (US historical only, OVERNIGHT not supported)
- `--json`: JSON format output

### Get Order Book
When the user asks about "order book", "depth", "bid/ask", or "odd lot order book":
```bash
python skills/moomooapi/scripts/quote/get_orderbook.py HK.00700 --num 10 [--json]
# Odd lot order book (only supports MY/SG markets)
python skills/moomooapi/scripts/quote/get_orderbook.py MY.1155 --type ODD [--json]
```
- `--type`: NORMAL=round lot (default), ODD=odd lot
- Odd lot order book only supports MY and SG markets; other markets will return an error
- Response includes `order_book_type` field indicating the current book type

### Get Tick-by-Tick Trades
When the user asks about "tick-by-tick", "trade details", or "ticker":
```bash
python skills/moomooapi/scripts/quote/get_ticker.py HK.00700 --num 20 [--json]
```

### Get Time-Sharing Data
When the user asks about "time-sharing" or "intraday":
```bash
python skills/moomooapi/scripts/quote/get_rt_data.py HK.00700 [--json]
```

### Get Market State
When the user asks about "market state" or "is the market open":
```bash
python skills/moomooapi/scripts/quote/get_market_state.py HK.00700 US.AAPL [--json]
```
- Supported market code prefixes: HK (Hong Kong), US (United States), SH/SZ (China A-shares), SG (Singapore), MY (Malaysia), JP (Japan)

### Get Capital Flow
When the user asks about "capital flow" or "fund inflow/outflow":
```bash
python skills/moomooapi/scripts/quote/get_capital_flow.py HK.00700 [--json]
```

### Get Capital Distribution
When the user asks about "capital distribution", "large/small orders", or "institutional flow":
```bash
python skills/moomooapi/scripts/quote/get_capital_distribution.py HK.00700 [--json]
```

### Get Plate/Sector List
When the user asks about "plate list", "concept plates", or "industry sectors":
```bash
python skills/moomooapi/scripts/quote/get_plate_list.py --market HK --type CONCEPT [--keyword tech] [--limit 50] [--json]
```
- `--market`: HK, US, SH, SZ, SG, MY, JP (SG = Singapore, MY = Malaysia, JP = Japan — all equities only)
- `--type`: ALL, INDUSTRY, REGION, CONCEPT
- `--keyword`/`-k`: Keyword filter

### Get Plate Constituents / Index Constituents
When the user asks about "plate stocks", "constituents", "HSI constituents", or "index constituents":
```bash
python skills/moomooapi/scripts/quote/get_plate_stock.py hsi [--limit 30] [--json]
python skills/moomooapi/scripts/quote/get_plate_stock.py HK.BK1910 [--json]
python skills/moomooapi/scripts/quote/get_plate_stock.py --list-aliases  # List all aliases
```
- Supports querying plate constituents and **index constituents** (e.g., Hang Seng Index, Hang Seng Tech Index, etc.)
- Built-in aliases: `hsi` (Hang Seng Index), `hstech` (Hang Seng Tech), `hk_ai` (AI), `hk_chip` (Chips), `hk_ev` (NEV), `us_ai` (US AI), `us_chip` (Semiconductors), `us_chinese` (Chinese ADRs), etc.

#### Plate Query Workflow
1. On first query, run `--list-aliases` to get the alias list and cache it
2. Match the user's request against cached aliases
3. If no match, search with `get_plate_list.py --keyword`
4. Use the found plate code to call `get_plate_stock.py`

### Get Stock Info
When the user asks about "stock info" or "basic info":
```bash
python skills/moomooapi/scripts/quote/get_stock_info.py US.AAPL,HK.00700 [--json]
```
- Uses `get_market_snapshot` under the hood, returns snapshot data with real-time quotes (including price, market cap, P/E ratio, etc.)
- Maximum 400 stocks per request

### Search Quote Instruments
When the user asks to "search stocks", "find symbol", or "search quote":
```bash
python skills/moomooapi/scripts/quote/get_search_quote.py keyword [--max-count 10] [--json]
```
- Search stocks, ETFs, plates, and other quote instruments by keyword
- `max_count` defaults to 10, max 100
- Returns `market`/`code`/`name`/`sec_type`/`is_watched`
- Rate limit: max 10 requests per 30 seconds

Examples:
```bash
python skills/moomooapi/scripts/quote/get_search_quote.py aapl
python skills/moomooapi/scripts/quote/get_search_quote.py tencent --max-count 20 --json
```

### Search News
When the user asks to "search news", "search notices", or "search information":
```bash
python skills/moomooapi/scripts/quote/get_search_news.py keyword [--max-count 10] [--news-sub-type ALL] [--json]
```
- Search news, notices, ratings, and other information by keyword
- `--news-sub-type`: `ALL` / `NEWS` / `NOTICE` / `RATING`
- Returns `title`/`news_sub_type`/`source`/`publish_time`/`view_count`/`related_securities`/`url`
- Rate limit: max 10 requests per 30 seconds

Examples:
```bash
python skills/moomooapi/scripts/quote/get_search_news.py space
python skills/moomooapi/scripts/quote/get_search_news.py apple --news-sub-type NEWS --json
```

### Stock Screener
When the user asks about "stock screener", "filter", or "stock filter":
```bash
python skills/moomooapi/scripts/quote/get_stock_filter.py --market HK [filters] [--sort field] [--limit 20] [--json]
```
Filter parameters:
- Price: `--min-price`, `--max-price`
- Market cap (100M): `--min-market-cap`, `--max-market-cap`
- PE: `--min-pe`, `--max-pe`
- PB: `--min-pb`, `--max-pb`
- Change rate (%): `--min-change-rate`, `--max-change-rate`
- Volume: `--min-volume`
- Turnover rate (%): `--min-turnover-rate`, `--max-turnover-rate`
- Sort: `--sort` (market_val/price/volume/turnover/turnover_rate/change_rate/pe/pb)
- `--asc`: Ascending order

Examples:
```bash
# Top 20 HK stocks by market cap
python skills/moomooapi/scripts/quote/get_stock_filter.py --market HK --sort market_val --limit 20
# PE between 10-30
python skills/moomooapi/scripts/quote/get_stock_filter.py --market US --min-pe 10 --max-pe 30
# Top 10 gainers
python skills/moomooapi/scripts/quote/get_stock_filter.py --market HK --sort change_rate --limit 10
```

### Stock Screener V2 (recommended for complex factors)
For multi-class factor screening (fundamentals / technical patterns / chips / heat / analyst ratings / capital flow / option IV/HV / broker holdings), prefer the V2 API `get_stock_screen`:
```bash
python skills/moomooapi/scripts/quote/get_stock_screen.py --config config.json [--page-from 0] [--page-count 200] [--json]
```
- Protocol ID 3252; broader factor coverage (11 categories, 244+ indicators)
- Pass **raw values** uniformly (OpenD handles multipliers): PRICE 10.0, MARKET_CAP 1e10; percent change 5% → **5.0** (not 0.05)
- **Enum names / units / Term / filter-type mapping in `docs/STOCK_SCREEN_FIELDS.md`** (consult on demand; do not guess enum names)
- Returns `(last_page, all_count, items)` 3-tuple where `items` is `list[dict]`; field names come from enum names (e.g. `PRICE`, `MARKET_CAP`)
- Each `retrieves` entry is **one** name (one entry per field); not a `fields` array
- Sorting uses `set_sort` (single) or `sorts` (multi): `direction` + `property_type` + `property_params={"name": ...}`; direction enum `ScrSortDir.ASC/DESC/ABS_ASC/ABS_DESC`
- You must explicitly declare `retrieves`; otherwise only `stock_id` is returned
- HK BMP entitlement not supported; HK only ships Q1/ANNUAL — Q2/Q3/Q4 financials usually missing
- `Term.SURPRISE_LATEST`(200~204) on HK/US currently equals `ANNUAL` data — use with caution
- `add_kline_shape` / `add_retrieve_kline_shape` require `period` (only 1d=11 / 1h=21)

config.json example:
```json
{
  "filters": [
    {"type": "simple_field", "field": "MARKET", "values": ["HK"]},
    {"type": "simple_property", "name": "PRICE", "lower": 10.0},
    {"type": "simple_property", "name": "MARKET_CAP", "lower": 1e10},
    {"type": "cumulative_property", "name": "PRICE_CHANGE_PCT", "days": 5, "lower": 5.0}
  ],
  "retrieves": [
    {"type": "basic",  "name": "CODE"},
    {"type": "basic",  "name": "NAME"},
    {"type": "simple", "name": "PRICE"},
    {"type": "simple", "name": "MARKET_CAP"}
  ],
  "sort": {"direction": "DESC", "property_type": "simple",
           "property_params": {"name": "MARKET_CAP"}}
}
```

### Warrant Screener V2
Filter warrants / CBBCs / inline warrants by issuer, IV, leverage, etc:
```bash
python skills/moomooapi/scripts/quote/get_warrant_screen.py --market HK [--stock-owner HK.00700] [--warrant-type CALL] [--min-price 0.01 --max-price 5] [--config config.json] [--only-count] [--json]
```
- Protocol ID 3254; `--market` required: HK / SG / MY (others not supported)
- Returns `(last_page, all_count, DataFrame)` 3-tuple; DataFrame has 43 columns
- `add_interval_filter` `min_val`/`max_val` are both optional; **passing none disables that condition** (no error)
- Pass **raw values** uniformly (OpenD handles multipliers)
- `WarrantType` (int): CALL=1, PUT=2, BULL=3, BEAR=4, IW=5 (inline warrant — SDK name is `IW`, not `INLINE`)
- `STOCK_OWNER` (5) accepts either stock_id (int) or security code (str, e.g. `"HK.00700"`)
- For complex conditions use `--config` JSON: `interval_filters` / `choice_filters` / `sorts`; `field_id` accepts enum names (e.g. `"CURRENT_PRICE"`) or numbers
- With `--only-count`, the returned DataFrame is empty; only `all_count` is meaningful

Common WarrantField IDs: 4=ISSUER_ID, 5=STOCK_OWNER, 6=WARRANT_TYPE, 8=CURRENT_PRICE, 9=STREET_RATIO, 10=VOLUME, 16=LEVERAGE_RATIO, 19=STATUS, 23=EFFECTIVE_LEVERAGE.


### Get Stock's Plates/Sectors
When the user asks about "which plates/sectors" a stock belongs to:
```bash
python skills/moomooapi/scripts/quote/get_owner_plate.py HK.00700 US.AAPL [--json]
```

---

**Related skills routing:** Related: options → options.md; fundamentals/F10 → fundamentals.md; screener result ranking in-body.
