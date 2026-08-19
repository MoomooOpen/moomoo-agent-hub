<!-- TOC: Rankings / Calendar / Industrial Chain / Macro / Other -->
# Rankings / Calendar / Industrial Chain / Macro / Other

Hot list, top movers, pre/after/overnight rankings, earnings/economic/dividend calendars, dividend ranking, industrial chain topology, macro indicators, FedWatch, heat map, rise/fall distribution.

## Table of Contents

- Featured Rankings
  - Get Hot List
  - Get Top Movers Rank
  - Get Period Change Rank
  - Get US Pre-Market Rank
  - Get US After-Hours Rank
  - Get US Overnight Rank
  - Get Short Selling Rank
- Earnings & Calendar
  - Get Earnings Calendar
  - Get Earnings Beat Rank
  - Get Economic Calendar
  - Get Dividend Calendar
- Dividend & SOE
  - Get Dividend Rank
  - Get High Dividend SOE Rank
- Industrial Chain
  - Get Industrial Chain List
  - Get Industrial Chain Detail
  - Get Industrial Chain by Plate
  - Get Industrial Plate Info
  - Get Industrial Plate Stock
- Macro Data
  - Get Macro Indicator List
  - Get Macro Indicator History
  - Get FedWatch Target Rate
  - Get FedWatch Dot Plot
- Other Market Data
  - Get Heat Map Data
  - Get Rise/Fall Distribution
  - Get Rating Change

---

### Featured Rankings

#### Get Hot List
When the user asks about "hot list", "hot stocks", "popular stocks ranking":
```bash
python skills/moomooapi/scripts/quote/get_hot_list.py --market US [--sort-field VOLUME_RATIO] [--sort-dir 0] [--count 10] [--offset 0] [--config filters.json] [--json]
```

**Parameters**:
- --market: Market (HK/US), required
- --sort-field: Sort field (VOLUME_RATIO/PRICE_CHANGE/PRICE_CHANGE_RATE/TURNOVER/VOLUME/AMPLITUDE/PRICE), default VOLUME_RATIO
- --sort-dir: Sort direction (0=descending, 1=ascending)
- --count: Return count [1,35], default 10
- --offset: Start offset
- --config: JSON filter config file (HotListFilter)

#### Get Top Movers Rank
When the user asks about "top movers", "gainers", "losers", "top gainers":
```bash
python skills/moomooapi/scripts/quote/get_top_movers_rank.py --market US [--sort-dir 0] [--count 10] [--offset 0] [--config filters.json] [--json]
```

**Parameters**:
- --market: Market (HK/US/MY/SG/JP), required
- --sort-dir: Sort direction (0=descending=gainers, 1=ascending=losers)
- --count: Return count [1,35], default 10
- --config: JSON filter config file (SimpleRankFilter)

#### Get Period Change Rank
When the user asks about "period change rank", "weekly gainers", "monthly performance":
```bash
python skills/moomooapi/scripts/quote/get_period_change_rank.py --market US --period ONE_WEEK [--sort-dir 0] [--count 10] [--offset 0] [--config filters.json] [--json]
```

**Parameters**:
- --market: Market (HK/US/MY/SG/JP), required
- --period: Period (ONE_WEEK/TWO_WEEKS/ONE_MONTH/TWO_MONTHS/THREE_MONTHS/SIX_MONTHS/ONE_YEAR/TWO_YEARS/THREE_YEARS/FIVE_YEARS/TEN_YEARS/YTD), required
- --sort-dir: Sort direction (0=descending, 1=ascending)
- --count: Return count [1,35], default 10
- --config: JSON filter config file (PeriodChangeRankFilter)

#### Get US Pre-Market Rank
When the user asks about "pre-market rank", "pre-market movers":
```bash
python skills/moomooapi/scripts/quote/get_us_pre_market_rank.py [--sort-dir 0] [--count 10] [--offset 0] [--config filters.json] [--json]
```

**Parameters**:
- --sort-dir: Sort direction (0=descending, 1=ascending)
- --count: Return count [1,35], default 10
- --config: JSON filter config file (SimpleRankFilter)

#### Get US After-Hours Rank
When the user asks about "after-hours rank", "after-hours movers":
```bash
python skills/moomooapi/scripts/quote/get_us_after_hours_rank.py [--sort-dir 0] [--count 10] [--offset 0] [--config filters.json] [--json]
```

**Parameters**:
- Same as pre-market rank

#### Get US Overnight Rank
When the user asks about "overnight rank", "overnight movers":
```bash
python skills/moomooapi/scripts/quote/get_us_overnight_rank.py [--sort-dir 0] [--count 10] [--offset 0] [--config filters.json] [--json]
```

**Parameters**:
- Same as pre-market rank

#### Get Short Selling Rank
When the user asks about "short selling rank", "short interest rank", "most shorted":
```bash
python skills/moomooapi/scripts/quote/get_short_selling_rank.py [--market US] [--sort-field SHORT_NUMBER_CHANGE] [--sort-dir 0] [--count 10] [--offset 0] [--plates US.BK2024] [--json]
```

**Parameters**:
- --market: Market (HK/US), default US
- --sort-field: Sort field (SHORT_NUMBER_CHANGE/SHORT_RATIO_CHANGE/SHORT_NUMBER/SHORT_RATIO/VOLUME/POSITION_VOLUME/POSITION_RATIO/DAYS_TO_COVER/WEEK_AVG_VOLUME/WEEK_AVG_SHORT_NUMBER/WEEK_AVG_SHORT_RATIO/MONTH_AVG_VOLUME/MONTH_AVG_SHORT_NUMBER/MONTH_AVG_SHORT_RATIO)
- --count: Return count [1,35], default 10
- --plates: Industry plate codes, comma-separated

### Earnings & Calendar

#### Get Earnings Calendar
When the user asks about "earnings calendar", "earnings dates", "reporting schedule":
```bash
python skills/moomooapi/scripts/quote/get_earnings_calendar.py --market US [--sort-type MARKET_CAP] [--begin-date 2026-06-23] [--end-date 2026-06-30] [--config filters.json] [--json]
```

**Parameters**:
- --market: Market (HK/US), required
- --sort-type: Sort type (MARKET_CAP/EARNINGS_TIME/NAME/CODE)
- --begin-date/--end-date: Date range
- --config: JSON filter config file (EarningsCalendarFilter)

#### Get Earnings Beat Rank
When the user asks about "earnings beat", "earnings surprise", "EPS beat":
```bash
python skills/moomooapi/scripts/quote/get_earnings_beat_rank.py --market US [--beat-type REVENUE] [--count 10] [--term Q] [--sort-field SURPRISE_PCT] [--config filters.json] [--json]
```

**Parameters**:
- --market: Market (HK/US), required
- --beat-type: Beat type (REVENUE/EPS)
- --count: Return count [1,35], default 10
- --term: Reporting period (Q=quarterly/H=semi-annual/A=annual)
- --sort-field: Sort field (SURPRISE_PCT/ACTUAL/CONSENSUS/MARKET_CAP)
- --config: JSON filter config file (EarningsBeatRankFilter)

#### Get Economic Calendar
When the user asks about "economic calendar", "economic events", "macro events":
```bash
python skills/moomooapi/scripts/quote/get_economic_calendar.py --begin-date 2026-06-23 [--end-date 2026-06-30] [--markets US,HK] [--importance HIGH] [--count 50] [--json]
```

**Parameters**:
- --begin-date: Start date yyyy-MM-dd, required
- --end-date: End date
- --markets: Market list (HK/US/SH/SG/JP/AU/MY/CA), comma-separated
- --importance: Importance (ALL/LOW/MEDIUM/HIGH)
- --count: Page size, default 50

#### Get Dividend Calendar
When the user asks about "dividend calendar", "ex-dividend dates", "dividend schedule":
```bash
python skills/moomooapi/scripts/quote/get_dividend_calendar.py --market US [--date 2026-06-23] [--offset 0] [--count 10] [--json]
```

**Parameters**:
- --market: Market (HK/US), required
- --date: Date yyyy-MM-dd
- --offset: Start offset
- --count: Return count

### Dividend & SOE

#### Get Dividend Rank
When the user asks about "dividend rank", "high dividend", "dividend yield ranking":
```bash
python skills/moomooapi/scripts/quote/get_dividend_rank.py --market US --rank-type HIGH_YIELD [--count 50] [--sort-field DIVIDEND_YIELD_TTM] [--config filters.json] [--json]
```

**Parameters**:
- --market: Market (HK/US/MY/SG/JP), required
- --rank-type: Rank type (HIGH_YIELD/DIVIDEND_GROWTH), required
- --count: Return count [1,300]
- --sort-field: Sort field (DIVIDEND_YIELD_TTM/AVG_DIVIDEND_YIELD_5Y/DISTRIBUTION_FREQUENCY/DIVIDEND_GROW_YEAR/DIVIDENDS_TTM/PAYOUT_RATIO_LFY/PRICE/MARKET_CAP/CHANGE_RATE/CHANGE_AMOUNT)
- --config: JSON filter config file (DividendRankFilter)

#### Get High Dividend SOE Rank
When the user asks about "high dividend SOE", "state-owned enterprise dividend":
```bash
python skills/moomooapi/scripts/quote/get_high_dividend_soe_rank.py [--sort-field DIVIDEND_YIELD_TTM] [--sort-dir 0] [--count 20] [--offset 0] [--config filters.json] [--json]
```

**Parameters**:
- --sort-field: Sort field (MARKET_CAP/DIVIDEND_YIELD_TTM/PB/PE_TTM/PRICE/CHANGE_RATIO)
- --sort-dir: Sort direction (0=descending, 1=ascending)
- --count: Return count
- --config: JSON filter config file (HighDividendSOERankFilter)
- HK market only



---

### Industrial Chain

#### Get Industrial Chain List
When the user asks about "industrial chain", "supply chain", "industry chain list":
```bash
python skills/moomooapi/scripts/quote/get_industrial_chain_list.py --market HK [--keyword chip] [--count 20] [--json]
```

**Parameters**:
- --market: Market (HK/US/CN/JP/SG/MY), required
- --keyword: Search keyword
- --count: Page size [1,50]
- Auto-pagination

#### Get Industrial Chain Detail
When the user asks about "industrial chain detail", "supply chain upstream downstream":
```bash
python skills/moomooapi/scripts/quote/get_industrial_chain_detail.py --chain-id 123 [--json]
```

**Parameters**:
- --chain-id: Industrial chain ID (required, from get_industrial_chain_list)

#### Get Industrial Chain by Plate
When the user asks about "plate industrial chain", "sector chain":
```bash
python skills/moomooapi/scripts/quote/get_industrial_chain_by_plate.py --plate-id 123 [--json]
```

**Parameters**:
- --plate-id: Industrial plate ID (required)

#### Get Industrial Plate Info
When the user asks about "industrial plate info", "sector info":
```bash
python skills/moomooapi/scripts/quote/get_industrial_plate_info.py --plate-id 123 [--json]
```

**Parameters**:
- --plate-id: Industrial plate ID (required)

#### Get Industrial Plate Stock
When the user asks about "industrial plate stocks", "sector constituents":
```bash
python skills/moomooapi/scripts/quote/get_industrial_plate_stock.py --plate-id 123 [--chain-id 456] [--markets HK,US] [--sort-field MARKET_VAL] [--ascend] [--count 50] [--json]
```

**Parameters**:
- --chain-id/--plate-id: One required, plate-id takes priority
- --markets: Market filter (HK/US/CN/JP/SG/MY), comma-separated
- --sort-field: Sort field (CODE/CHANGE_RATE/TURNOVER/VOLUME/MARKET_VAL)
- --ascend: Ascending order
- Auto-pagination



---

### Macro Data

#### Get Macro Indicator List
When the user asks about "macro indicators", "economic indicators list":
```bash
python skills/moomooapi/scripts/quote/get_macro_indicator_list.py --region US [--json]
```

**Parameters**:
- --region: Country/Region (HK/US/JP/SG/AU/CA/MY/CN), required

#### Get Macro Indicator History
When the user asks about "macro history", "indicator history", "CPI history", "GDP history":
```bash
python skills/moomooapi/scripts/quote/get_macro_indicator_history.py --indicator-id 123 [--time 2026-06-01] [--max-count 100] [--json]
```

**Parameters**:
- --indicator-id: Macro indicator ID (required, from get_macro_indicator_list)
- --time: Time point yyyy-MM-dd (fetch backwards)
- --max-count: Max records, default 100, limit 1000

#### Get FedWatch Target Rate
When the user asks about "FedWatch", "fed rate probability", "CME FedWatch":
```bash
python skills/moomooapi/scripts/quote/get_fed_watch_target_rate.py [--json]
```

**Parameters**:
- No parameters required

#### Get FedWatch Dot Plot
When the user asks about "dot plot", "fed dot plot", "FOMC projections":
```bash
python skills/moomooapi/scripts/quote/get_fed_watch_dot_plot.py [--json]
```

**Parameters**:
- No parameters required

### Other Market Data

#### Get Heat Map Data
When the user asks about "heat map", "sector heat map", "market heat map":
```bash
python skills/moomooapi/scripts/quote/get_heat_map_data.py --market US [--sort-field CHANGE_RATE] [--ascend] [--count 30] [--plate-type INDUSTRY] [--json]
```

**Parameters**:
- --market: Market (HK/US/CN), required
- --sort-field: Sort field (CHANGE_RATE/MARKET_VAL/TURNOVER/HOT)
- --plate-type: Plate type (INDUSTRY/CONCEPT/THEME)
- Auto-pagination

#### Get Rise/Fall Distribution
When the user asks about "rise fall distribution", "advance decline":
```bash
python skills/moomooapi/scripts/quote/get_rise_fall_distribution.py [--security HK.BK1001] [--market HK] [--json]
```

**Parameters**:
- --security: Plate code (priority)
- --market: Market (HK/US/CN), used when security not provided
- One of the two required

#### Get Rating Change
When the user asks about "rating change", "analyst upgrades", "downgrades":
```bash
python skills/moomooapi/scripts/quote/get_rating_change.py --market US [--change-type UPGRADE] [--count 10] [--json]
```

**Parameters**:
- --market: Market (US only), required
- --change-type: Rating change type (UPGRADE/DOWNGRADE/NEW_RATING)
- --count: Page size [1,20]
- Auto-pagination

---

---

**Related skills routing:** Related: plates/constituents → quote-commands.md; macro indicator history in-body; industrial chain upstream/downstream linkage.
