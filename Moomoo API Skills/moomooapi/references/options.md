<!-- TOC: Options Commands -->
# Options Commands

Option screening, shorthand code resolution, option chain, volatility, exercise probability, strategy combos, P&L analysis, market statistics, unusual activity, 0DTE, earnings options, seller strategies.

> **Hard constraint**: combo option order-book price / order `--price` must come from `get_option_strategy_analysis.py` `bid1`/`ask1`; do NOT call `get_snapshot.py` per leg and manually add/subtract bid/ask.

## Table of Contents

- Option Screener
- Resolve Option Shorthand Code
  - Step 1: You Parse the User Input (the script does not do this step)
  - Step 2: Call the Script to Match from Option Chain
  - Step 3: Display the Result to the User
  - Option Code Format
  - Option Operations Workflow
- Get Option Expiration Dates
- Get Option Chain
- Get Option Volatility
- Get Option Exercise Probability
- Get Option Strategy Combo Legs
- Combo Option Order Book Price (Hard Constraint)
- Get Option Strategy Valid Spreads
- Get Option Snapshot Quote
- Option Strategy P&L Analysis
- Options Data
  - Get Option Volatility (Option Volatility)
  - Get Option Exercise Probability (Option Exercise Probability)
  - Get Option Market Statistics (Volume/OI Time Series)
  - Get Option Underlying Historical Statistics (P/C Ratio)
  - Get Batch Underlying Overview (IV/HV Multi-Period Snapshot)
  - Get Underlying Historical Volatility (IV/HV Time Series)
  - Get Option Underlying Rank (Hot Underlying Rank)
  - Get Option Contract Rank
  - Get Option Unusual Activity
  - Get Option Event Alert Settings
  - Set Option Event Alert Conditions
  - Receive Option Event Push
  - Get 0DTE Underlying Screener
  - Get 0DTE Contract Details
  - Get Earnings Option Screener (IV Crush / Expected Move)
  - Get Option Seller Strategy Screener (Covered Call / Cash Secured Put)
  - Get Option Strategy Combo Legs (Option Strategy)
  - Get Option Strategy Valid Spreads (Option Spread)
  - Get Option Snapshot Quote (Multi-leg Option Quote)
  - Option Strategy P&L Analysis (Combo Bid/Ask + P&L)

---

### Option Screener
Filter options by IV / Greeks / open interest / underlying attributes:
```bash
python skills/moomooapi/scripts/quote/get_option_screen.py --markets US_STOCK HK_STOCK [--config config.json] [--page-count 50] [--json]
```
- Protocol ID 3253; `--markets` required, from `OptMarketCategory`: `US_STOCK`(0) / `US_INDEX`(1) / `US_FUTURE`(2) / `HK_STOCK`(3) / `HK_INDEX`(4) / `JP_STOCK`(5) / `JP_INDEX`(6)
- Returns `(last_page, all_count, DataFrame)` 3-tuple; DataFrame has 47 columns by default (including `underlying` dict)
- US_FUTURE / JP_STOCK / JP_INDEX **return empty results currently** (future support)
- Backend forbids mixing underlying + option in the same group; SDK auto-opens new groups: default AND (new group); same `indicator_type` with `or_with_previous=True` → OR within the current group
- Pass **raw values** uniformly (OpenD handles multipliers): IV / HV / IV_RANK / IV_PERCENTILE take **percent raw values** (30% → **30.0**, not 0.3); DELTA / GAMMA / VEGA / THETA / RHO and probabilities are passed as raw numbers
- `OptUnderlyingIndicator.STOCK_LIST` accepts underlying **stock_id (int)**, not security codes
- `OptUnderlyingIndicator.PLATE(103)` raises an error — **do not use**
- `OptIndicator.PREMIUM(2021)` only supports sort/retrieve; using as filter raises an error
- `BUY_BREAK_EVEN_POINT(3023)` deprecated — use `BUY_TO_BEP(3011)` instead
- If `add_underlying_retrieve` is not called, the returned `underlying` dict fields are `'N/A'`

OptUnderlyingIndicator values: STOCK_LIST=101, INDEX_LIST=106, VOLUME=201, OPEN_INTEREST=202, IV=203, HV=204, IV_RANK=205, IV_PERCENTILE=206, IV_CHANGE=207, IV_CHANGE_RATIO=208, IV_HV_RATIO=209, IV_HV_SPREAD=210, MARKET_CAP=401, STOCK_PRICE=402, CHANGE_RATIO=403.

config.json example (CALL OR PUT in one group, IV>30% in another, sort by open interest desc):
```json
{
  "filters": [
    {"kind": "option", "indicator_type": "OPTION_TYPE", "values": [1]},
    {"kind": "option", "indicator_type": "OPTION_TYPE", "values": [2], "or_with_previous": true},
    {"kind": "underlying", "indicator_type": "IV", "lower": 30.0}
  ],
  "sorts": [{"indicator_type": "OPEN_INTEREST", "desc": true}],
  "option_retrieves": ["OPTION_TYPE", "STRIKE_PRICE", "OPEN_INTEREST", "IMPLIED_VOLATILITY"],
  "underlying_retrieves": ["STOCK_PRICE", "IV", "MARKET_CAP"]
}
```


### Resolve Option Shorthand Code

When the user provides an option description (e.g., `JPM 260320 267.50C`, `腾讯 260320 420.00 购`), **you must first parse out the underlying code, expiry date, strike price, and option type, then call the script to precisely match from the option chain**.

```bash
python skills/moomooapi/scripts/quote/resolve_option_code.py --underlying US.JPM --expiry 2026-03-20 --strike 267.50 --type CALL [--json]
```

#### Step 1: You Parse the User Input (the script does not do this step)

Users may describe options in various formats. You need to extract 4 elements based on context:

| Element | Description | Your Responsibility |
|---------|-------------|---------------------|
| **Underlying Code** | Must include market prefix (e.g., `US.JPM`, `HK.00700`) | Infer the market from context: `JPM` → US stock → `US.JPM`; `腾讯` → HK stock → `HK.00700`; `Apple` → US stock → `US.AAPL` |
| **Expiry Date** | `yyyy-MM-dd` format | Convert from `YYMMDD`: `260320` → `2026-03-20` |
| **Strike Price** | Number | Extract directly: `267.50` |
| **Option Type** | `CALL` or `PUT` | `C`/`Call`/`购`/`认购`/`看涨` → `CALL`; `P`/`Put`/`沽`/`认沽`/`看跌` → `PUT` |

**User Input Format Examples**:

| User Input | Parsed Parameters |
|---------|--------------|
| `JPM 260320 267.50C` | `--underlying US.JPM --expiry 2026-03-20 --strike 267.50 --type CALL` |
| `腾讯 260320 420.00 购` | `--underlying HK.00700 --expiry 2026-03-20 --strike 420.00 --type CALL` |
| `AAPL 261218 200P` | `--underlying US.AAPL --expiry 2026-12-18 --strike 200 --type PUT` |
| `苹果 260117 250 看跌` | `--underlying US.AAPL --expiry 2026-01-17 --strike 250 --type PUT` |
| `买入 BABA 260620 120C` | `--underlying US.BABA --expiry 2026-06-20 --strike 120 --type CALL` |

**Market Inference Rules**:
- User provides a Chinese stock name (腾讯/Tencent, 阿里/Alibaba, 美团/Meituan, etc.) → Use your knowledge to determine the market and code
- User provides English Ticker (JPM, AAPL, TSLA) → Usually US stocks, use `US.` prefix
- User provides prefixed code (US.JPM, HK.00700) → Use directly
- If uncertain → Use AskUserQuestion to ask the user

#### Step 2: Call the Script to Match from Option Chain

```bash
# The script precisely searches via the option chain API and returns the moomoo option code
python skills/moomooapi/scripts/quote/resolve_option_code.py --underlying US.JPM --expiry 2026-03-20 --strike 267.50 --type CALL --json
```

The script will automatically:
1. Call `get_option_chain` to get all options for the underlying at the specified expiry date
2. Precisely match by strike price + option type
3. Return the option code (e.g., `US.JPM260320C267500`)
4. If no match, list the closest contracts for reference

#### Step 3: Display the Result to the User

When displaying the option code, use the format "Moomoo Option Code is `xxx`".

#### Option Code Format

Moomoo option codes are constructed from the following parts:

```
{Market}.{UnderlyingShortName}{YYMMDD}{C/P}{Strike×1000}
```

| Part | Description | Example |
|------|-------------|---------|
| Market | `US` (US stocks), `HK` (HK stocks) | `US` |
| Underlying Short Name | US stocks use Ticker, HK stocks use exchange-assigned abbreviations | `JPM`, `TCH` (Tencent), `MIU` (Xiaomi) |
| YYMMDD | Expiry date (two digits each for year, month, day) | `260320` = 2026-03-20 |
| C/P | `C` = Call, `P` = Put | `C` |
| Strike×1000 | Strike price multiplied by 1000, no decimal point | `267500` = 267.50 |

**Full Examples**:

| Option Description | Option Code |
|---------|---------|
| JPM 2026-03-20 267.50 Call | `US.JPM260320C267500` |
| AAPL 2026-12-18 200 Put | `US.AAPL261218P200000` |
| Tencent (腾讯) 2026-03-27 470 Call | `HK.TCH260327C470000` |
| Xiaomi (小米) 2026-04-29 33 Put | `HK.MIU260429P33000` |
| TIGR 2026-04-10 6.50 Put | `US.TIGR260410P6500` |

> Note: The underlying short name for HK options is not the stock code but an exchange-assigned abbreviation (e.g., Tencent=TCH, Xiaomi=MIU). Therefore, do not manually construct option codes; use `resolve_option_code.py` to look up from the option chain.

#### Option Operations Workflow

When the user mentions options (e.g., "view/buy/sell a certain option"), follow this workflow:

1. **Identify the Option Code**:
   - If the user provides an option description (e.g., `JPM 260320 267.50C` or `腾讯 260320 420 购`), follow the two-step process above: parse → call `resolve_option_code.py` to get the Moomoo Option Code
   - If the user only provides the underlying name and option intent (e.g., "show me JPM Calls expiring next week"), first use `get_option_expiration_date.py` to find expiry dates, then use `get_option_chain.py` to list matching options for the user to choose

2. **Query Option Market Data**:
   - Single-leg options: after obtaining the Moomoo Option Code, use `get_snapshot.py`, `get_kline.py`, etc.
   - **Multi-leg / combo option bid/ask (bid1/ask1)**: **must** use `get_option_strategy_analysis.py` (see "Combo Option Order Book Price" hard constraint below); **do not** call `get_snapshot.py` per leg and manually net bid/ask

3. **Option Trading**:
   - Option orders use the same `place_order.py` script as stock orders
   - Option quantity unit is "contracts"
   - US option prices have 2 decimal places precision

### Get Option Expiration Dates
When the user asks about "option expiry dates" or "what expiration dates are available":
```bash
python skills/moomooapi/scripts/quote/get_option_expiration_date.py US.AAPL [--json]
```

### Get Option Chain
When the user asks about "option chain" or "what options are available":
```bash
python skills/moomooapi/scripts/quote/get_option_chain.py US.AAPL [--start 2026-03-01] [--end 2026-03-31] [--json]
```

### Get Option Volatility
When the user asks about "option volatility", "implied volatility", "historical volatility", "IV", "HV", "volatility premium":
```bash
python skills/moomooapi/scripts/quote/get_option_volatility.py US.AAPL280317C260000 [--query-time-period 2] [--hv-time-period 30] [--json]
```

### Get Option Exercise Probability
When the user asks about "exercise probability", "option exercise probability", "strike probability", "ITM probability":
```bash
python skills/moomooapi/scripts/quote/get_option_exercise_probability.py US.AAPL280317C260000 [--json]
```

### Get Option Strategy Combo Legs
When the user asks about "option strategy", "strategy combo legs", "STRADDLE", "SPREAD", "STRANGLE", "BUTTERFLY", "CONDOR", "option combo":
```bash
python skills/moomooapi/scripts/quote/get_option_strategy.py HK.00700 STRADDLE 2026-05-22 [--spread 10.0] [--far-expire-time 2026-06-26] [--option-type CALL] [--strike-price 300.0] [--json]
```
- Supported strategies: STRADDLE / SPREAD / STRANGLE / BUTTERFLY / CONDOR / IRON_BUTTERFLY / IRON_CONDOR / COLLAR / DIAGONAL_SPREAD
- Returned combo legs can be used as input to `get_option_strategy_analysis.py` (**combo bid/ask & order pricing first**) and `get_option_quote.py` (Greeks / last-price snapshot)

### Combo Option Order Book Price (Hard Constraint)

When the user asks for **combo/strategy bid-ask, order book price, or combo quote**, or when you need `--price` for `place_combo_order` / `comboorder_tradinginfo_query`:

**You must** call `get_option_strategy_analysis.py`. **Do not**:
- Call `get_snapshot.py` on each leg and manually add/subtract bid/ask
- Derive combo prices from single-leg quotes yourself

Recommended flow:
1. `get_option_strategy.py` (optional) → standard strategy legs
2. **`get_option_strategy_analysis.py`** → read **`bid1` (combo bid)** / **`ask1` (combo ask)**
3. To trade: use `bid1`/`ask1` as limit-price reference (buy usually near `ask1`, sell near `bid1`) → `comboorder_tradinginfo_query.py` → `place_combo_order.py`

`legs` input: `[{"code":"...","action":"BUY|SELL","quantity":1.0}, ...]` (same fields as `get_option_strategy` output)

Division of labor vs `get_option_quote.py`:
- **`get_option_strategy_analysis`**: combo-level **bid1/ask1** + max P/L / breakeven / Greeks (**preferred for order book price & combo order pricing**)
- **`get_option_quote`**: last price, change, Greeks snapshot (**not for combo bid/ask** — do not substitute for `get_option_strategy_analysis`)

### Get Option Strategy Valid Spreads
When the user asks about "option spread", "valid spreads", "strategy spread list":
```bash
python skills/moomooapi/scripts/quote/get_option_strategy_spread.py HK.00700 STRANGLE 2026-05-22 [--json]
```
- Supports: SPREAD / STRANGLE / COLLAR / BUTTERFLY / CONDOR / IRON_BUTTERFLY / IRON_CONDOR / DIAGONAL_SPREAD

### Get Option Snapshot Quote
When the user asks about "option snapshot", "option real-time quote", "multi-leg option Greeks" (typically used together with `get_option_strategy.py`):
```bash
python skills/moomooapi/scripts/quote/get_option_quote.py '[{"code":"HK.TCH260522P330000","action":"BUY","quantity":1.0},{"code":"HK.TCH260522C330000","action":"BUY","quantity":1.0}]' [--json]
```
- Input is a JSON array of option legs with fields: code (option code), action (BUY/SELL), quantity (float)
- **Not for combo bid/ask**: use `get_option_strategy_analysis.py` for combo order book price (see hard constraint above)

### Option Strategy P&L Analysis
When the user asks about "P&L analysis", "option profit loss", "max profit", "max loss", "breakeven points", "probability of profit", **"combo bid ask", "combo order book price", "combo quote", "strategy quote"**:
```bash
python skills/moomooapi/scripts/quote/get_option_strategy_analysis.py '[{"code":"HK.TCH260522P330000","action":"BUY","quantity":1.0},{"code":"HK.TCH260522C330000","action":"BUY","quantity":1.0}]' [--json]
```
- Returns **`bid1`/`ask1` (combo order book price)**, max profit/loss, breakeven points, probability of profit, Delta, Theta
- **Combo bid/ask and `place_combo_order` `--price` must come from this script first** — do not compute from single-leg snapshots

---



---

### Options Data

#### Get Option Volatility (Option Volatility)
When user asks about "option volatility", "implied volatility", "historical volatility", "IV", "HV", "volatility premium", "IV vs HV":
```bash
python skills/moomooapi/scripts/quote/get_option_volatility.py [--query-time-period QUERY_TIME_PERIOD] [--hv-time-period HV_TIME_PERIOD] [--json] code
```
- Input is an **option code**; use `resolve_option_code.py` to resolve first if needed

**Market**: Option contract codes only

**Parameters**:
- code: Option code, e.g. US.AAPL280317C260000
- --query-time-period: 1=Week, 2=Month (default), 3=Quarter, 4=HalfYear, 5=Year
- --hv-time-period: Historical volatility period for underlying (5~250 days, default 30)

#### Get Option Exercise Probability (Option Exercise Probability)
When user asks about "exercise probability", "option exercise probability", "strike probability", "ITM probability":
```bash
python skills/moomooapi/scripts/quote/get_option_exercise_probability.py [--json] code
```
- Input is an **option code**; use `resolve_option_code.py` to resolve first if needed

**Market**: Option contract codes only

**Parameters**:
- code: Option code, e.g. US.AAPL280317C260000

#### Get Option Market Statistics (Volume/OI Time Series)
When user asks about "option market statistics", "option volume trend", "option open interest trend", "market volume/OI":
```bash
python skills/moomooapi/scripts/quote/get_option_market_statistic.py --market US_SECURITY --data-type VOLUME [--begin 2024-01-01] [--end 2024-06-01] [--json]
```

**Parameters**:
- --market: Option market (required): US_SECURITY, US_INDEX, HK_SECURITY, HK_INDEX
- --data-type: Data type (required): VOLUME, OPEN_INTEREST
- --begin: Start date YYYY-MM-DD (defaults to ~1 year ago)
- --end: End date YYYY-MM-DD
- Time span max 1 year; auto-pagination fetches all data

#### Get Option Underlying Historical Statistics (P/C Ratio)
When user asks about "underlying option statistics", "put/call ratio", "PCR", "P/C ratio", "option volume ratio":
```bash
python skills/moomooapi/scripts/quote/get_option_underlying_his_statistic.py US.AAPL [--index-option-type NORMAL] [--begin 2025-01-01] [--end 2025-06-01] [--json]
```

**Parameters**:
- code: Underlying stock code (required), e.g. US.AAPL
- --index-option-type: Index option type: NORMAL, SMALL (only for index underlyings)
- --begin/--end: Date range, max 364 days span
- Open interest data has T-1 delay

#### Get Batch Underlying Overview (IV/HV Multi-Period Snapshot)
When user asks about "underlying overview", "batch underlying data", "underlying IV snapshot", "batch IV HV":
```bash
python skills/moomooapi/scripts/quote/get_option_underlying_overview.py US.AAPL US.TSLA US.NVDA [--index-option-type NORMAL] [--json]
```

**Parameters**:
- codes: Underlying stock codes (required), space-separated, max 500
- --index-option-type: Index option type: NORMAL, SMALL
- Snapshot API returning current latest data; OI has T-1 delay

#### Get Underlying Historical Volatility (IV/HV Time Series)
When user asks about "underlying historical volatility", "IV trend", "HV trend", "IV time series", "IV history":
```bash
python skills/moomooapi/scripts/quote/get_option_underlying_his_volatility.py US.AAPL [--index-option-type NORMAL] [--begin 2025-01-01] [--end 2025-06-01] [--json]
```

**Parameters**:
- code: Underlying stock code (required), e.g. US.AAPL
- --index-option-type: Index option type: NORMAL, SMALL
- --begin/--end: Date range, max 364 days span

#### Get Option Underlying Rank (Hot Underlying Rank)
When user asks about "underlying rank", "option underlying rank", "hot underlying", "IV rank", "HV rank":
```bash
python skills/moomooapi/scripts/quote/get_option_underlying_rank.py --market US_SECURITY --sort-type VOLUME [--sort-direction 0] [--count 20] [--trading-date 2025-06-01] [--config filters.json] [--json]
```

**Parameters**:
- --market: Option market (required): US_SECURITY, US_INDEX, HK_SECURITY, HK_INDEX
- --sort-type: Sort field (required): VOLUME, VOLUME_RATIO, OPEN_INTEREST, OPEN_INTEREST_RATIO, PRICE, PRICE_CHANGE, IV, IV_CHANGE, HV, HV_CHANGE, IV_RANK, IV_PERCENTILE, MARKET_CAP
- --sort-direction: 0=descending (default), 1=ascending
- --count: Page size [1,200]
- --config: JSON filter config file (supports 13 filter types)

#### Get Option Contract Rank
When user asks about "option contract rank", "option rank", "option volume rank", "OI rank", "option IV rank":
```bash
python skills/moomooapi/scripts/quote/get_option_rank.py --market US_SECURITY --sort-type VOLUME [--sort-direction 0] [--count 20] [--trading-date 2025-06-01] [--config filters.json] [--json]
```

**Parameters**:
- --market: Option market (required): US_SECURITY, US_INDEX, HK_SECURITY, HK_INDEX
- --sort-type: Sort type (required): VOLUME, TURNOVER, OI, OI_INCREMENT, OI_DECREMENT, OI_MARKET_CAP, OI_MARKET_CAP_INCREMENT, OI_MARKET_CAP_DECREMENT, CHANGE_RATE, IV
- --sort-direction: 0=descending (default), 1=ascending
- --count: Page size [1,200]
- --config: JSON filter config file (supports 18 filter types)

#### Get Option Unusual Activity
When user asks about "option unusual activity", "option flow", "unusual options", "option sweep", "large option orders":
```bash
python skills/moomooapi/scripts/quote/get_option_event.py --market US_SECURITY [--count 50] [--config filters.json] [--json]
```

**Parameters**:
- --market: Option market (required): US_SECURITY, US_INDEX, HK_SECURITY, HK_INDEX
- --count: Page size [1,300]
- --config: JSON filter/sort config file (supports 25+ filter types + sort)

**Config example**:
```json
{
  "filters": [
    {"indicator_type": "OPTION_TYPE", "value_list": [1]},
    {"indicator_type": "TURNOVER", "interval_min": 100000.0},
    {"indicator_type": "OWNER_LIST", "security_list": ["US.TSLA", "US.AAPL"]}
  ],
  "sort": {"indicator_type": "TURNOVER", "direction": "DESCEND"}
}
```

#### Get Option Event Alert Settings
When user asks about "option event alerts", "alert list", "my option alerts", "view alert settings":
```bash
python skills/moomooapi/scripts/quote/get_option_event_alert.py [--count 50] [--json]
```

**Parameters**:
- --count: Page size [1,500], default 200
- Auto-pagination fetches all alert settings

**Response fields** (--json output):
- key: Alert unique identifier
- enable: Alert switch
- option_market: Market category (OptionMarket)
- watchlist_group_name: Watchlist group name
- underlying: Specified underlying code
- option_type: Option type CALL/PUT
- side_type_list: Trade direction list
- order_type_list: Order type list
- market_cap_range_min/max: Underlying market cap range
- market_cap_min_inclusive/max_inclusive: Market cap closed interval flag
- expiry_days_range_min/max: Days to expiry range
- expiry_days_min_inclusive/max_inclusive: Days to expiry closed interval flag
- price_range_min/max: Event trade price range
- price_min_inclusive/max_inclusive: Price closed interval flag
- size_range_min/max: Event trade size range (contracts)
- size_min_inclusive/max_inclusive: Size closed interval flag
- premium_range_min/max: Event premium range
- premium_min_inclusive/max_inclusive: Premium closed interval flag
- iv_range_min/max: Implied volatility range (%)
- iv_min_inclusive/max_inclusive: IV closed interval flag
- earnings_date_begin/end: Earnings date filter (yyyy-MM-dd)
- note: Note

#### Set Option Event Alert Conditions
When user asks about "set option alert", "add alert", "delete alert", "modify alert", "enable alert":
```bash
python skills/moomooapi/scripts/quote/set_option_event_alert.py --op ADD --config alert.json [--json]
python skills/moomooapi/scripts/quote/set_option_event_alert.py --op DELETE --key 14694 [--json]
python skills/moomooapi/scripts/quote/set_option_event_alert.py --op ENABLE --key 14694 [--json]
python skills/moomooapi/scripts/quote/set_option_event_alert.py --op DISABLE --key 14694 [--json]
python skills/moomooapi/scripts/quote/set_option_event_alert.py --op DELETE_ALL [--json]
```

**Parameters**:
- --op: Operation type (required): ADD, DELETE, MODIFY, ENABLE, DISABLE, DELETE_ALL
- --key: Alert unique identifier (for DELETE/MODIFY/ENABLE/DISABLE)
- --config: JSON config file (for ADD/MODIFY)

**JSON config fields**:
- Monitor scope (choose one): option_market / watchlist_group_name / underlying
- option_type: Option type CALL/PUT
- side_type_list: Trade direction list (BUY/SELL/NEUTRAL)
- order_type_list: Order type list (SWEEP/BLOCK/NORMAL/CROSS/FLOOR)
- market_cap_range_min/max: Underlying market cap range
- expiry_days_range_min/max: Days to expiry range
- price_range_min/max: Event trade price range
- size_range_min/max: Event trade size range (contracts)
- premium_range_min/max: Event premium range
- iv_range_min/max: Implied volatility range (%)
- Each range supports independent open/closed interval (e.g., size_min_inclusive: false for open), default true (closed)
- earnings_date_begin/end: Earnings date filter (yyyy-MM-dd)
- note: Note (max 20 chars)

#### Receive Option Event Push
When user asks about "option event push", "realtime option activity", "subscribe option events", "option event notifications":
```bash
python skills/moomooapi/scripts/subscribe/push_option_event.py [--duration 300] [--json]
```

**Parameters**:
- --duration: Listen duration in seconds (default 300)
- Requires alert conditions set via set_option_event_alert first
- Ctrl+C to interrupt

#### Get 0DTE Underlying Screener
When user asks about "0DTE", "zero dte", "same-day expiration options", "0DTE screener", "0DTE underlying":
```bash
python skills/moomooapi/scripts/quote/get_option_zero_dte_screener.py --market US_SECURITY [--sort-type VOLUME] [--asc] [--count 20] [--config filters.json] [--json]
```

**Parameters**:
- --market: Option market (required): US_SECURITY, US_INDEX, HK_SECURITY, HK_INDEX
- --sort-type: Sort type: VOLUME, IV, CHANGE_RATIO, OPEN_INTEREST, MARKET_CAP
- --asc: Sort ascending
- --count: Page size [1,500], default 50
- --config: JSON filter config file (supports 10 filter types)
- Output chain_info can be used as input for get_option_zero_dte_contract

#### Get 0DTE Contract Details
When user asks about "0DTE contracts", "zero dte contract", "0DTE option chain", "0DTE contract details":
```bash
python skills/moomooapi/scripts/quote/get_option_zero_dte_contract.py --owner US.TSLA --chain-info chain.json [--sort-type VOLUME] [--asc] [--config filters.json] [--json]
```

**Parameters**:
- --owner: Underlying stock code (required), e.g. US.TSLA
- --chain-info: chain_info JSON file path (required, from get_option_zero_dte_screener output)
- --sort-type: Sort type: VOLUME, OPEN_INTEREST, IV, DELTA
- --config: JSON filter config file (supports 15 filter types)
- No pagination, returns all results at once

#### Get Earnings Option Screener (IV Crush / Expected Move)
When user asks about "earnings options", "IV crush", "earnings volatility", "earnings screener", "earnings option play":
```bash
python skills/moomooapi/scripts/quote/get_option_earnings_screener.py --market US_SECURITY [--sort-type EARNINGS_DATE] [--asc] [--count 50] [--config filters.json] [--json]
```

**Parameters**:
- --market: Option market (required): US_SECURITY, HK_SECURITY (only these two supported)
- --sort-type: Sort type: EARNINGS_DATE, VOLUME, IV, MARKET_CAP, CHANGE_RATIO, PRICE, IV_RANK, IV_PERCENTILE, HV, OPEN_INTEREST, LAST_REPORT_IV_CRUSH, HISTORY_REPORT_IV_CRUSH, LAST_REPORT_CHG_RATIO, HISTORY_REPORT_CHG_RATIO, ESTIMATE_EPS_YOY, ESTIMATE_REVENUE_YOY, EXPECTED_MOVE_RATIO
- --count: Page size [1,500], default 50
- --config: JSON filter config file (supports 20 filter types)

#### Get Option Seller Strategy Screener (Covered Call / Cash Secured Put)
When user asks about "option seller strategy", "covered call", "cash secured put", "CC strategy", "CSP strategy", "seller screener", "income strategy":
```bash
python skills/moomooapi/scripts/quote/get_option_seller_screener.py --market US_SECURITY --seller-type COVERED_CALL [--sort-type ANNUALIZED_RETURN] [--asc] [--config filters.json] [--json]
```

**Parameters**:
- --market: Option market (required): US_SECURITY, US_INDEX, HK_SECURITY, HK_INDEX
- --seller-type: Seller strategy (required): COVERED_CALL, CASH_SECURED_PUT
- --sort-type: Sort type: ANNUALIZED_RETURN, INTERVAL_RETURN, ITM_PROBABILITY, PREMIUM
- --config: JSON filter config file (supports 26 filter types: 13 underlying + 13 option level)
- No pagination, returns all results at once

---

#### Get Option Strategy Combo Legs (Option Strategy)
When user asks about "option strategy", "strategy combo legs", "STRADDLE", "SPREAD", "STRANGLE", "BUTTERFLY", "CONDOR", "option combo":
```bash
python skills/moomooapi/scripts/quote/get_option_strategy.py [--spread 10.0] [--far-expire-time 2026-06-26] [--index-option-type NORMAL] [--option-type CALL] [--strike-price 300.0] [--json] code option_strategy expire_time
```
- Input: code (underlying), option_strategy (strategy type), expire_time (expiry date yyyy-MM-dd)

**Rate limit**: Max 30 requests per 30 seconds

**Parameters**:
- code: Underlying code, e.g. HK.00700 / US.AAPL
- option_strategy: Strategy type — STRADDLE / SPREAD / STRANGLE / BUTTERFLY / CONDOR / IRON_BUTTERFLY / IRON_CONDOR / COLLAR / DIAGONAL_SPREAD
- expire_time: Expiry date, format yyyy-MM-dd
- --spread: Spread value (required for some strategies)
- --far-expire-time: Far expiry date (for DIAGONAL_SPREAD)
- --option-type: CALL / PUT / ALL
- --strike-price: Strike price
---

#### Get Option Strategy Valid Spreads (Option Spread)
When user asks about "option spread", "valid spreads", "strategy spread list":
```bash
python skills/moomooapi/scripts/quote/get_option_strategy_spread.py [--far-expire-time 2026-06-26] [--index-option-type NORMAL] [--json] code option_strategy expire_time
```
- Input: code (underlying), option_strategy (strategy type), expire_time (expiry date)

**Rate limit**: Max 30 requests per 30 seconds; only supports SPREAD / STRANGLE / COLLAR / BUTTERFLY / CONDOR / IRON_BUTTERFLY / IRON_CONDOR / DIAGONAL_SPREAD

**Parameters**:
- code: Underlying code, e.g. HK.00700
- option_strategy: Strategy type (see supported list above)
- expire_time: Expiry date, format yyyy-MM-dd
---

#### Get Option Snapshot Quote (Multi-leg Option Quote)
When user asks about "option snapshot", "option real-time quote", "multi-leg option Greeks" (typically used together with `get_option_strategy.py`):
```bash
python skills/moomooapi/scripts/quote/get_option_quote.py [--json] legs
```
- Input is a JSON array string of option legs
- **Not for combo bid/ask**: combo order book price must use `get_option_strategy_analysis.py`

**Rate limit**: Max 30 requests per 30 seconds

**Parameters**:
- legs: JSON array, e.g. `'[{"code":"HK.TCH260522P330000","action":"BUY","quantity":1.0}]'`
  - code: Option code
  - action: BUY / SELL
  - quantity: Quantity (float)
---

#### Option Strategy P&L Analysis (Combo Bid/Ask + P&L)
When user asks about "P&L analysis", "option profit loss", "max profit", "max loss", "breakeven points", "probability of profit", **"combo bid ask", "combo order book price", "combo quote", "strategy quote"**:
```bash
python skills/moomooapi/scripts/quote/get_option_strategy_analysis.py [--json] legs
```
- Input is a JSON array string of option legs; returns **`bid1`/`ask1` (combo order book price)**, max profit/loss, breakeven points, probability of profit, Delta, Theta
- **Hard constraint**: combo bid/ask and `--price` for `place_combo_order` / `comboorder_tradinginfo_query` **must come from this script** — do not net single-leg `get_snapshot.py` quotes manually

**Rate limit**: Max 30 requests per 30 seconds

**Parameters**:
- legs: JSON array, e.g. `'[{"code":"HK.TCH260522P330000","action":"BUY","quantity":1.0},{"code":"HK.TCH260522C330000","action":"BUY","quantity":1.0}]'`
---

---

**Related skills routing:** Related: combo order → trade-commands.md; option seller/0DTE screening in-body; IV from get_option_strategy_analysis (hard constraint).
