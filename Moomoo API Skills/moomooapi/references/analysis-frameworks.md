<!-- TOC: Analysis Frameworks & Output Templates -->
# Analysis Frameworks & Output Templates

This doc teaches the AI **what to do with the data and how to structure the output** — not how to call APIs (see `references/*.md` for that), but templates for the analyze→output step. Each framework has: data source → output structure → key checks. When filling a template, organize strictly by the output structure; do not dump raw data.

## Table of Contents

- Earnings Review Card
- Position Diagnostic Checklist
- Screener Result Ranking

---

## 1. Earnings Review Card

**Trigger**: when the user says "analyze XX's latest earnings", "review XX's results", "how were XX's earnings".

**Data source** (prefer `collect.py` for one-shot; or call individually):
- `python skills/moomooapi/scripts/quote/collect.py US.AAPL --json` (positional `code` arg; snapshot + finances + rating + valuation — recommended; add `--with-options` for option summary)
- Or manually: `get_financials_statements.py` (income + key metrics) + `get_research_analyst_consensus.py` (rating/target) + `get_valuation_detail.py` (PE/PB percentile) + `get_financials_earnings_price_move.py` (earnings-day price reaction)

**Output structure** (organize by this; 1-3 lines per block):

```
[XX (CODE) Latest Earnings Review] Period: YYYY-Qx

1. Core metrics (YoY)
   - Revenue: X 亿, YoY ±x%
   - Net profit (attributable): X 亿, YoY ±x%
   - Gross margin: x% (±xpct YoY)
   - Net margin: x% (±xpct YoY)

2. Earnings quality
   - ROE: x% (trend: up/down/flat)
   - Operating cash flow vs net profit: X vs X (reconcile; if OCF/NI < 1, flag receivables/inventory risk)

3. Valuation anchor
   - PE_TTM: x (historical percentile x%)
   - PB: x (historical percentile x%)
   - Conclusion: valuation at high/mid/low end of history

4. Earnings-day price reaction
   - Earnings-day change: ±x%, next day: ±x%
   - IV change (if options): pre-earnings IV x% → post x%

5. One-line conclusion + risks
   - Conclusion: …
   - Risks: … (e.g. revenue growth slowing, cash flow weaker than profit, valuation high)
```

**Key checks**: revenue YoY and net-profit YoY should move in the same direction; if not, explain the margin swing. If operating cash flow is negative while net profit is positive, **must flag it**.

---

## 2. Position Diagnostic Checklist

**Trigger**: when the user says "diagnose my positions", "how's my portfolio", "review my holdings".

**Data source**: `scripts/trade/get_portfolio.py --json` (returns `{"funds":..., "positions":[...]}`).

**⚠️ Mandatory field convention** (see `docs/FIELD_MAPPING.md`, aligned with the app):
- ✅ Use `unrealized_pl` (unrealized P&L, avg-cost basis), `pl_ratio_avg_cost` (P&L ratio, e.g. 5.23=5.23%), `average_cost`, `nominal_price`, `market_val`
- ❌ **Forbidden**: `cost_price`/`diluted_cost` (diluted cost), `pl_val`/`pl_ratio` (diluted basis — may mismatch the app)
- Multi-currency positions: **do not directly sum** `market_val`/`unrealized_pl` across currencies; use `accinfo_query(currency=target)` for account-level aggregates, or convert at live FX rates (never hardcode rates)

**Output structure**:

```
[Position Diagnostic] Account: XXX  Total assets: X (currency)

1. Top 3 gainers / Top 3 losers
   - Gainers: ① CODE name +x% (P&L X) ② … ③ …
   - Losers: ① CODE name -x% (P&L X) ② … ③ …

2. Concentration (⚠️ flag single-name >30% in red)
   - CODE1: x% (market val X / total assets)
   - CODE2: x%
   - Top 3 combined: x%

3. Sector exposure
   - Sector A: x%  Sector B: x%  Sector C: x% (aggregate by position sector)

4. Account risk
   - risk_status: LEVEL3(safe)/LEVEL2(warning)/LEVEL1(danger)
   - Available funds: X (available_funds)
   - Leverage/margin: power X, initial_margin X

5. Basis check + recommendations
   - Unrealized + realized: unrealized X + realized X = total X
   - Recommendation: … (e.g. "concentration too high, consider trimming CODE1"; "CODE fundamentals deteriorating, consider stop-loss")
```

**Key checks**: single-name >30% **must be flagged in red**; `risk_status` LEVEL1/LEVEL2 **must be flagged**.

---

## 3. Screener Result Ranking

**Trigger**: when the user says "screen stocks for XX" and wants ranking/shortlist.

**Data source**: `scripts/quote/get_stock_screen.py --config config.json --json` (returns `{"last_page":..., "all_count":..., "data":[...]}`). Enum names/units/Term in `docs/STOCK_SCREEN_FIELDS.md`.

**Two-stage process**:

### Stage 1: server-side filter + sort (build config.json)
- `filters`: use `simple_property`/`financial_property`/`cumulative_property` etc., pass **raw values** (ROE 15.0 not 0.15; market cap 1e10 = 100 亿)
- `sorts` (multi-key): `[{"direction":"DESC","property_type":"simple","property_params":{"name":"MARKET_CAP"}}]`
- `retrieves`: **must declare explicitly** (single name each), or only `stock_id` is returned; at minimum take `CODE`/`NAME`/`PRICE`/`MARKET_CAP` + sort fields
- Pagination: `--page-count 200`; pass `--page-from` to continue

### Stage 2: client-side refinement (AI processes returned items)
1. **Exclude**: ST/*ST/delisted (by name or code rule), extremely illiquid (tiny turnover)
2. **Liquidity filter**: drop names below a daily-turnover threshold (avoid un-sellable positions)
3. **Valuation-percentile tiering**: e.g. PE_TTM historical percentile <30% → "undervalued", 30-70% → "fair", >70% → "rich"
4. **Output Top 10 table**:

```
| # | Code | Name | Price | Mkt cap | Key factor | Val. percentile | One-line rationale |
|---|---|---|---|---|---|---|---|
| 1 | US.XXX | Name | X | X 亿 | ROE x% | x% | … |
| 2 | … | | | | | | |
```

Each row has a **one-line rationale** (why selected: e.g. "ROE 18% industry-leading + valuation at historical low").

**Key checks**: if `all_count` is large (>1000), suggest tightening filters; if `data` is empty, check for misspelled enum names (case-sensitive) or unsupported market (e.g. HK BMP permission, HK only Q1+ANNUAL).

---

## Related skills routing

- Financials/valuation scripts → `references/fundamentals.md`
- Position/fund scripts + field convention → `references/trade-commands.md` + `docs/FIELD_MAPPING.md`
- Screener script + enum mapping → `references/quote-commands.md` + `docs/STOCK_SCREEN_FIELDS.md`
- One-shot panorama data → `scripts/quote/collect.py` (see `references/quote-commands.md`)
