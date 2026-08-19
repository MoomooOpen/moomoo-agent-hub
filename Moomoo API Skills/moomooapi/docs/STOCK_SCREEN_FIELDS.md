# Stock Screener Field Mapping (V2 `get_stock_screen`, proto 3252)

> **Source**: Enums from SDK module `moomoo.quote.stock_screen_const` (source `moomoo/quote/stock_screen_const.py`). The script `scripts/quote/get_stock_screen.py` `_resolve()` accepts **enum-name strings or ints** (e.g. `"PRICE"` ≡ `2201`). **Pass raw values for all `lower`/`upper`; OpenD applies the backend factor** — the "factor" column below only explains **returned values**, do not use it to scale inputs. This doc lists the common high-frequency fields; for the full enum see the SDK source path above.

## Numeric Unit Conventions

| Type | Convention | Example |
|---|---|---|
| Price (PRICE/OPEN_PRICE/HIGH/LOW/BID_PRICE...) | raw currency | `10.0` = 10 HKD/USD |
| Market cap (MARKET_CAP/FLOAT_MARKET_CAP) | raw | `1e10` = 100 亿 (10 billion) |
| Money (NET_PROFIT/REVENUE/EBITDA/TURNOVER...) | raw | `1e8` = 1 亿 (100 million) |
| Percent/ratio (all `_PCT`/`_RATE`/`_RATIO`/growth/turnover/amplitude) | raw percent, **not fraction** | `5.0` = 5%, not `0.05` |
| Shares (TOTAL_SHARE/FLOAT_SHARE/VOLUME) | raw count | `1000` = 1000 shares |
| Timestamp (LISTED_DATE/RELEASED_DATE/SURPRISE_*_DATE) | unix seconds | unix timestamp |

## General Enums

| Enum class | Members |
|---|---|
| `ScrMarket` (values for `simple_field` MARKET) | `HK`=1, `US`=2, `CN`=3, `SG`=4, `CA`=5, `AU`=6, `JP`=7, `MY`=8 |
| `ScrSortDir` (sort direction) | `ASC`=1, `DESC`=2, `ABS_ASC`=3, `ABS_DESC`=4 |
| `Period` (indicator/kline-shape period) | `MINUTE_1`=1, `MINUTE_3`=2, `MINUTE_5`=3, `MINUTE_15`=4, `HOUR_1`=5, `MINUTE_30`=6, `DAY`=11, `WEEK`=21, `MONTH`=31 |
| `Position` (indicator positional relation) | `OVER`=1, `BELOW`=2, `CROSS_UP`=3, `CROSS_DOWN`=4 |
| `OptionHVPeriod` (option HV period) | `HV_30D`=0, `HV_60D`=1, `HV_90D`=2, `HV_120D`=3, `HV_365D`=4 |

## Term (fiscal period — required by `financial_property`)

| Enum | Value | Meaning |
|---|---|---|
| `Q1` | 1 | Q1 report |
| `Q2` | 2 | Q2 report |
| `Q3` | 3 | Q3 report |
| `Q4` | 4 | Q4 report |
| `Q6` | 6 | Interim (cumulative) |
| `Q9` | 9 | Q3 cumulative |
| `LATEST` | 10 | Latest single quarter |
| `ANNUAL` | 100 | Annual FY |
| `SURPRISE_LATEST` | 200 | Latest period |
| `SURPRISE_LATEST_QUARTER` | 201 | Latest quarter |
| `SURPRISE_LATEST_HALF` | 202 | Latest half-year |
| `SURPRISE_LATEST_ANNUAL` | 203 | Latest annual |
| `SURPRISE_LATEST_ALL` | 204 | All |

> **Hard rule**: HK only has `Q1`+`ANNUAL` data; `Q2`/`Q3`/`Q4` are usually missing. `SURPRISE_LATEST` (200-204) currently returns data ≈ `ANNUAL` on HK/US — **use with caution**.
>
> **⚠️ US financial-factor filter coverage is sparse**: using a `financial_property` (e.g. `ROE`/`NET_PROFIT`/`REVENUE`) as a US-market **filter** matches **very few** stocks (in testing, `ROE` term=`ANNUAL` returns only ~3 names US-wide, `LATEST` even fewer) — this is an inherent server-side coverage limit, NOT a wrong term or param. If a PE (`simple_property`) ∩ ROE (`financial_property`) intersection is 0, **do not suspect the enum name/unit**: first run `financial_property` alone for `ROE` and check `all_count` to confirm coverage, then decide whether to widen the threshold or switch to alternative factors like `featured_property` `ANALYST_RATING`/`HIST_PERCENTILE_PE`. HK financial filtering has normal coverage; this mainly affects US.
>
> **⚠️ financial retrieve may return no value**: in testing, a `financial_property` used as a **retrieve** (value field) can return `dval: None` even when the stock passed a filter on the same field (e.g. the 3 US names passing ROE>15 all returned ROE=None on retrieve). This is a server-side limit — the filter works but the retrieve is not always backfilled. To get ROE or other financial values, prefer `get_financials_statements.py` per-ticker.

## Filter Types (filter `type`)

Each filter is a dict; `type` determines the shape. `property_type` (for sort `property_params`) is one of: `simple`/`cumulative`/`financial`/`basic`/`featured`/`broker`/`klineShape` (**camelCase, not `kline_shape`**)/`option`.

| `type` | enum for `name` | key fields | example |
|---|---|---|---|
| `simple_field` | `SimpleField` (uses `field`, not `name`) | `field`, `values` | `{"type":"simple_field","field":"MARKET","values":["HK"]}` |
| `plate` | — | `plate_ids`, `parent_plate_id` | `{"type":"plate","plate_ids":["BK1001"]}` |
| `simple_property` | `SimpleProperty` | `name`, `lower`, `upper`, `*_included`(def true) | `{"type":"simple_property","name":"PRICE","lower":10.0,"upper":100.0}` |
| `cumulative_property` | `CumulativeProperty` | `name`, `days`(def 1), `lower`, `upper` | `{"type":"cumulative_property","name":"PRICE_CHANGE_PCT","days":5,"lower":5.0}` |
| `financial_property` | `FinancialProperty` | `name`, `term`(Term), `lower`, `upper` | `{"type":"financial_property","name":"ROE","term":"ANNUAL","lower":15.0}` |
| `indicator_positional` | `Indicator`(`first_indicator_name`) | `first_indicator_name`, `period_type`(Period), `position`(Position), `second_indicator` | `{"type":"indicator_positional","first_indicator_name":"MA5","period_type":"DAY","position":"CROSS_UP","second_indicator":"MA20"}` |
| `indicator_pattern` | `Pattern`(`name`) | `name`, `period_type`(Period) | `{"type":"indicator_pattern","name":"MACD_GOLD_CROSS","period_type":"DAY"}` |
| `featured_property` | `FeaturedProperty` | `name`, `intervals` | `{"type":"featured_property","name":"CHIPS_PROFIT_RATIO","intervals":[{"filterMin":{"value":50.0,"includes":true}}]}` |
| `broker_holdings` | `BrokerProperty` | `name`, `days`, `param`, `intervals` | `{"type":"broker_holdings","name":"CONCENTRATED_DISTRIBUTION","days":30,"intervals":[...]}` |
| `kline_shape` | `KlineShapeProperty`(`name`) + `KlineShapeType`(`value_set`) | `name`, `period`(Period, **required**), `value_set` | `{"type":"kline_shape","name":"SHAPE_TYPE","period":"DAY","value_set":["DOUBLE_BOTTOMS"]}` |
| `option` | `OptionProperty`(`name`) | `name`, `intervals`, `period`(OptionHVPeriod) | `{"type":"option","name":"STOCK_IV","period":"HV_30D","intervals":[{"filterMin":{"value":20.0,"includes":true}}]}` |

`intervals` shape (featured/broker/option/indicator_positional): `[{"filterMin":{"value":N,"includes":bool}, "filterMax":{"value":N,"includes":bool}}]`.

## Property Enums (common subset)

> Only high-frequency fields are listed per class. **For the full enum see SDK source `moomoo/quote/stock_screen_const.py`** (class name).

### SimpleProperty (quote properties, `simple_property`)

| Meaning | Enum name | Factor/unit |
|---|---|---|
| Latest price | `PRICE` | 1000 |
| Open / prev close / high / low | `OPEN_PRICE` / `LAST_CLOSE` / `HIGH` / `LOW` | 1000 |
| Change rate | `PRICE_CHANGE_RATE` | 1e5 (5.0=5%) |
| Bid / ask price | `BID_PRICE` / `ASK_PRICE` | 1000 |
| Volume ratio / bid-ask ratio | `VOLUME_RATIO` / `BID_ASK_RATIO` | 1e5 / 1e7 |
| Market cap | `MARKET_CAP` | 1000 (`1e10`=100 亿) |
| PE TTM / PE annual | `PE_TTM` / `PE_ANNUAL` | 1e5 |
| PB | `PB` | 1e5 |
| Dividend yield | `DIVIDEND_RATIO` | 1e5 |
| Listed date / days | `LISTED_DATE` / `LISTED_DAYS` | timestamp / 1 |
| Pre-market price / change | `BEFORE_PRICE` / `BEFORE_CHANGE_PCT` | 1000 / 1e5 |
| After-hours price / change | `AFTER_PRICE` / `AFTER_CHANGE_PCT` | 1000 / 1e5 |
| Overnight price / change | `OVERNIGHT_PRICE` / `OVERNIGHT_CHANGE_PCT` | 1e9 / 1e5 |
| Lot price | `LOT_PRICE` | 1000 |

> Full list includes high-precision `_HP` variants, margin rates, 52-week relative positions — see source `SimpleProperty`.

### CumulativeProperty (range cumulative, takes `days`)

| Meaning | Enum name | Factor/unit |
|---|---|---|
| Price change | `PRICE_CHANGE` | 1000 |
| Price change percent | `PRICE_CHANGE_PCT` | 1e5 (5.0=5%) |
| Amplitude | `AMPLITUDE` | 1e5 |
| Avg volume / avg turnover | `AVG_VOLUME` / `AVG_TURNOVER` | 1 / 1000 |
| Turnover rate | `TURNOVER_RATIO` | 1e5 |

> All 9 members in source `CumulativeProperty` (incl. `HIGH_TO_N_DAY_HIGH` etc.).

### FinancialProperty (financial, `financial_property` requires `term`)

| Meaning | Enum name | Factor/unit |
|---|---|---|
| Net profit / growth | `NET_PROFIT` / `NET_PROFIT_GROWTH` | 1000 / 1e5 |
| Revenue / growth | `REVENUE` / `REVENUE_GROWTH` | 1000 / 1e5 |
| Gross margin / net margin | `GROSS_PROFIT_RATIO` / `NET_PROFIT_RATIO` | 1e5 |
| ROE | `ROE` | 1e5 (15.0=15%) |
| Debt-to-assets | `DEBT_TO_ASSETS` | 1e5 |
| EBITDA / margin | `EBITDA` / `EBITDA_MARGIN` | 1000 / 1e5 |
| ROIC | `ROIC` | 1e5 |
| Basic / diluted EPS | `BASIC_EPS` / `DILUTED_EPS` | 1000 |
| Total / float shares | `TOTAL_SHARE` / `FLOAT_SHARE` | 1 |
| Float market cap | `FLOAT_MARKET_CAP` | 1000 |
| PS TTM / PCF TTM | `PS_TTM` / `PCF_TTM` | 1e5 |
| Operating cash flow TTM | `OPERATING_CASH_FLOW_TTM` | 1000 |
| Free cash flow | `FREE_CASH_FLOW` | 1e3 |
| Major CAGRs (3/5/10y) | `REVENUE_CAGR` / `NET_PROFIT_CAGR` / `ROE_CAGR` / `EBITDA_CAGR` | 1e5 |

> Full ~130 members include solvency (current/quick ratio, financial leverage), operating (turnover), growth, earnings-surprise (SURPRISE_*) — see source `FinancialProperty`.

### FeaturedProperty (featured)

| Meaning | Enum name | Factor/unit |
|---|---|---|
| Chips profit ratio | `CHIPS_PROFIT_RATIO` | 1e5 |
| Short position / cover days | `SHORT_POSITION` / `COVER_DAYS` | 1 / 1e3 |
| Trade / search / average index | `TRADE_INDEX` / `SEARCH_INDEX` / `AVERAGE_INDEX` | 1e5 |
| Institutional holding ratio | `INST_RATIO` | 1e5 |
| Analyst rating / target price | `ANALYST_RATING` / `ANALYST_TARGET_PRICE` | 1000 / 1e9 |
| Morningstar fair value / star / moat | `MORNINGSTAR_FAIR_VALUE` / `MORNINGSTAR_STAR` / `MORNINGSTAR_MOAT` | 1e9 / 1 / 1 |
| PE / PB historical percentile | `HIST_PERCENTILE_PE` / `HIST_PERCENTILE_PB` | 1e5 |
| Average dividend yield (3/5y) | `AVERAGE_DIVIDEND_YIELD` | 1e5 |
| Main net inflow (param CashFlowPeriod) | `CASH_FLOW_MAIN_NET_IN` | 1e3 |

> Full ~100 members include employee count, shareholder perks, AU franking — see source `FeaturedProperty`.

### BrokerProperty (broker holdings, HK only, all 7)

| Meaning | Enum name | Factor/unit |
|---|---|---|
| Concentrated distribution | `CONCENTRATED_DISTRIBUTION` | 1e5 |
| Holdings change | `HOLDINGS_CHANGE` | 1e5 |
| Broker count / rank | `BROKER_NUM` / `BROKER_RANK` | 1 |
| Holdings ratio | `HOLDINGS_RATIO` | 1e5 |
| CCASS ratio / change | `CENTRAL_HOLDINGS_RATIO` / `CENTRAL_HOLDINGS_CHANGE` | 1e5 |

### KlineShapeProperty + KlineShapeType (candlestick pattern)

`KlineShapeProperty` (all 6): `SHAPE_TYPE`(pattern itself) / `RISE_PROB`(rise probability,1e5) / `AFTER_SELECTED_CHG`(post-selection change,1e5) / `SELECTED_TIME` / `SUPPORT_LEVEL`(1e9) / `PRESSURE_LEVEL`(1e9).

`KlineShapeType` (`value_set` for `SHAPE_TYPE`, all 22 valid values):
- Bullish: `DOUBLE_BOTTOMS` / `TRIPLE_BOTTOMS` / `HEAD_SHOULDERS_BOTTOM` / `CUP_BOTTOM` / `TRUMPET_BOTTOM` / `FLAG` / `SYMMETRY_TRIANGLE` / `SUSTAINABLE_RHOMBUS` / `WEDGE` / `SUSTAINABLE_TRIANGLE`
- Bearish: `DOUBLE_PEAKS` / `TRIPLE_PEAKS` / `HEAD_SHOULDERS_PEAK` / `CUP_PEAK` / `TRUMPET_PEAK` / `FLAG_DOWN` / `SYMMETRY_TRIANGLE_DOWN` / `SUSTAINABLE_RHOMBUS_DOWN` / `WEDGE_DOWN` / `SUSTAINABLE_TRIANGLE_DOWN`
- Categories: `BULLISH_TYPE` / `BEARISH_TYPE`

### OptionProperty (underlying option properties, all 11)

| Meaning | Enum name | Factor/unit |
|---|---|---|
| Stock IV / rank / percentile | `STOCK_IV` / `STOCK_IV_RANK` / `STOCK_IV_PERCENTILE` | 1e6 |
| Earnings IV crush (takes earnings-period param) | `STOCK_EARNINGS_IV_CRUSH` | 1e6 |
| Stock IV change / change ratio | `STOCK_IV_CHG` / `STOCK_IV_CHG_RATIO` | 1e6 |
| Stock HV (takes `period` OptionHVPeriod) | `STOCK_HV` | 1e6 |
| IV-HV / IV/HV (default 30d) | `STOCK_IV_MINUS_HV` / `STOCK_IV_DIV_HV` | 1e6 |
| Option volume / open interest | `STOCK_OPTION_VOL` / `STOCK_OPTION_OPEN_IN` | 1 |

### Indicator (technical indicators, for `indicator_positional`)

Common: `PRICE`(latest) / `MA5`/`MA10`/`MA20`/`MA60`/`MA120`/`MA250`(simple MA) / `MA`(dynamic) / `EMA5`..`EMA250` / `KDJ_K`/`KDJ_D`/`KDJ_J` / `MACD_DIF`/`MACD_DEA`/`MACD_MACD` / `RSI_12` / `BOLL_UPPER`/`BOLL_MIDDLE`/`BOLL_LOWER`. Full ~39 members in source `Indicator`.

### Pattern (technical patterns, for `indicator_pattern`, all 22 valid values)

MA alignment: `MA_LONG`/`MA_SHORT`/`EMA_LONG`/`EMA_SHORT`; crosses: `KDJ_GOLD_CROSS`/`KDJ_DEATH_CROSS`/`MACD_GOLD_CROSS`/`MACD_DEATH_CROSS`/`RSI_GOLD_CROSS`/`RSI_DEATH_CROSS`; divergence: `KDJ_TOP_DIVERGE`/`KDJ_BOTTOM_DIVERGE`/`MACD_TOP_DIVERGE`/`MACD_BOTTOM_DIVERGE`/`RSI_TOP_DIVERGE`/`RSI_BOTTOM_DIVERGE`; BOLL: `BOLL_BREAK_UPPER`/`BOLL_BREAK_LOWER`/`BOLL_CROSS_MID_UP`/`BOLL_CROSS_MID_DOWN`; summary: `BULLISH`/`BEARISH`.

## retrieves & sort

- **retrieves**: each entry is a **single `name`** (not a `fields` array), e.g. `{"type":"simple","name":"PRICE"}`. **Without `retrieves`, only `stock_id` is returned.** retrieve `type`: `basic`/`simple`/`cumulative`/`financial`/`indicator`/`featured`/`broker`/`option`/`kline_shape`.
- **sort** (single, `set_sort`) or **sorts** (array, `add_sort`): `{"direction":"DESC","property_type":"simple","property_params":{"name":"MARKET_CAP"}}`. `direction` uses `ScrSortDir`; `property_type` per the filter-types note above.

## Caveats / Disabled & Use-with-caution

1. **Enum names are case-sensitive, exact match**: `price`/`Price` do not resolve (`_resolve` uses strict `hasattr`) and pass through to OpenD as a literal string, causing an error.
2. **`property_type` uses camelCase `klineShape`** (not `kline_shape`) — mixed with snake_case `type` values, easy to get wrong.
3. **`kline_shape` `period` is required**, only `DAY`(=11) and `HOUR_1`(=5) supported (note `WEEK`=21, not 1-hour).
4. **HK BMP permission is unsupported** by V2 screener.
5. HK financials: only `Q1`+`ANNUAL`; `SURPRISE_LATEST` (200-204) ≈ ANNUAL on HK/US, use with caution.
6. **US financial-factor filter coverage is sparse** (`ROE`/`NET_PROFIT` etc. as US filters match very few; in testing ROE ANNUAL returns only ~3 US names); when an intersection is 0, first run the single factor and check `all_count` — do not suspect the enum name/unit. See the Term section above.
7. `Term.SURPRISE_*` financial properties (4906-4944) must pair with `SURPRISE_*` terms.
6. `Term.SURPRISE_*` financial properties (4906-4944) must pair with `SURPRISE_*` terms.

> **Option screener (`get_option_screen`, proto 3253, a separate endpoint) caveats** (not part of this table, cross-reference only): `OptUnderlyingIndicator.PLATE`=103 disabled (backend unimplemented, errors); `OptIndicator.PREMIUM`=2021 supports sort/retrieve only, errors as a filter; `OptIndicator.BUY_BREAK_EVEN_POINT`=3023 deprecated, use `BUY_TO_BEP`=3011.

## V1 (`get_stock_filter`) comparison

V1 is the legacy endpoint (`StockField` enum + CLI flags + manual `*1e8` factor, market cap in 亿), with only 8 sortable fields (market_val/price/volume/turnover/turnover_rate/change_rate/pe/pb). **Prefer V2** (244+ factors, declarative JSON, OpenD auto-scaling). Use V1 only for ultra-simple filtering.
