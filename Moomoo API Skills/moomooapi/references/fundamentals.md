<!-- TOC: F10 Fundamentals / Research / Corporate Actions / Company Info / Brokers / Short Selling -->
# F10 Fundamentals / Research / Corporate Actions / Company Info / Brokers / Short Selling

Financial statements, revenue breakdown, analyst ratings, Morningstar, valuation, corporate actions (dividends/buybacks/splits), company info, executives, operational efficiency, top brokers, short selling.

> Shareholders/institutional/ARK see `shareholders-institutions.md`; options data see `options.md`; rankings/calendar/macro see `rankings-calendar.md`.

## F10 Fundamentals / Research / Corporate Actions / Shareholders / Company Info

The following 27 scripts cover stock fundamentals, research, corporate actions, shareholders, company info, broker data, short selling, and options data. For usage details and parameter descriptions, see the header of each script or run with `[-h]`, e.g.:
```bash
python skills/moomooapi/scripts/quote/get_financials_earnings_price_move.py -h
```

## Table of Contents

- Financials — Earnings Analysis
  - Get Earnings Day Price Move (Financials-Earnings Analysis)
  - Get Earnings Day Price History (Financials-Earnings Analysis)
- Financials — Statements & Revenue
  - Get Financial Statements (Financials-Key Metrics/Income/Balance Sheet/Cash Flow)
  - Get Revenue Breakdown (Financials-Revenue Breakdown)
- Research — Analyst Ratings
  - Get Analyst Consensus (Research-Analyst Ratings)
  - Get Rating Summary (Research-Analyst Ratings)
- Research — Morningstar Report
  - Get Morningstar Report (Research-Morningstar Report)
- Research — Valuation
  - Get Valuation Detail (Research-Valuation)
  - Get Valuation Plate Stock List (Research-Valuation)
- Corporate Actions
  - Get Dividends (Corporate Actions-Dividends)
  - Get Buybacks (Corporate Actions-Buybacks)
  - Get Stock Splits (Corporate Actions-Stock Splits)
- Shareholders
  - Get Shareholders Overview (Shareholders)
  - Get Holding Changes (Shareholders-Holding Changes)
  - Get Holder Detail (Shareholders-Holder Detail)
  - Get Institutional Holdings (Shareholders-Institutional)
  - Get Insider Holder List (Shareholders-Insiders)
  - Get Insider Trade List (Shareholders-Insiders)
- Company Info
  - Get Company Profile (Company Info)
  - Get Company Executives (Company Info-Executives)
  - Get Executive Background (Company Info-Executives)
  - Get Operational Efficiency (Company Info-Operational Efficiency)
- Brokers
  - Get Top Ten Buy/Sell Brokers (Top Ten Brokers)
- Short Selling
  - Get Daily Short Volume (Daily Short Volume)
  - Get Short Interest (Short Interest)

---

### Financials — Earnings Analysis

#### Get Earnings Day Price Move (Financials-Earnings Analysis)
When user asks about "earnings day price move", "earnings volatility", "pre/post earnings price", "IV/HV around earnings", "price performance around earnings":
```bash
python skills/moomooapi/scripts/quote/get_financials_earnings_price_move.py [--period-count N] [--json] code
```
**Market**: HK and US equities

**Parameters**:
- code: Stock code, e.g. HK.00700
- --period-count: Number of earnings periods, default 10, range 1-50

#### Get Earnings Day Price History (Financials-Earnings Analysis)
When user asks about "earnings day price history", "IV Crush", "implied volatility change around earnings", "expected move", "next/latest earnings date", "earnings date detail":
```bash
python skills/moomooapi/scripts/quote/get_financials_earnings_price_history.py [--json] code
```
**Market**: HK and US equities

**Parameters**:
- code: Stock code, e.g. HK.00700

### Financials — Statements & Revenue

#### Get Financial Statements (Financials-Key Metrics/Income/Balance Sheet/Cash Flow)
When user asks about "financial statements", "income statement", "balance sheet", "cash flow", "key metrics", "revenue", "net profit", "gross margin", "ROE", "EPS":
```bash
python skills/moomooapi/scripts/quote/get_financials_statements.py [--statement-type STATEMENT_TYPE] [--financial-type FINANCIAL_TYPE] [--currency-code CURRENCY_CODE] [--next-key KEY] [--num N] [--json] code
```
**Market**: Equities and funds

**Parameters**:
- code: Stock code, e.g. HK.00700
- --statement-type: 1=Income (default), 2=BalanceSheet, 3=CashFlow, 4=MainIndex
- --financial-type: 1=Q1, 2=Q2, 3=Q3, 4=Q4, 5=Q6, 6=Q9, 7=Annual, 9=Quarterly, 10=QuarterlyAnnual (default), 11=MulQuarterly
- --currency-code: ISO 4217, e.g. CNY, USD, HKD; omit for native currency
- --next-key: Pagination key; omit for first page; "-1" = no more data
- --num: Results per page, default 10, range 1-50

#### Get Revenue Breakdown (Financials-Revenue Breakdown)
When user asks about "revenue breakdown", "segment revenue", "product/region/industry revenue", "revenue structure", "main business composition":
```bash
python skills/moomooapi/scripts/quote/get_financials_revenue_breakdown.py [--date DATE] [--financial-type FINANCIAL_TYPE] [--currency-code CURRENCY_CODE] [--json] code
```
**Market**: Equities and funds

**Parameters**:
- code: Stock code, e.g. HK.00700
- --date: Timestamp to filter history; use date values from screen_date_list output; omit for latest
- --financial-type: 1=Q1, 2=Q2, 3=Q3, 4=Q4, 5=SemiAnnual, 6=Q9, 7=Annual, 9=QuarterlyCombo
- --currency-code: ISO 4217, e.g. CNY, USD, HKD; omit for native currency

**Returns**: Product/Industry/Region/Business dimension data; each group in `breakdown_list` has `type` and `item_list`; `screen_date_list` only returned when neither `--date` nor `--financial-type` is specified

### Research — Analyst Ratings

#### Get Analyst Consensus (Research-Analyst Ratings)
When user asks about "analyst rating", "consensus", "target price", "buy/hold/sell ratio", "average target price", "analyst coverage count":
```bash
python skills/moomooapi/scripts/quote/get_research_analyst_consensus.py [--json] code
```
**Market**: Equities and REITs

**Parameters**:
- code: Stock code, e.g. HK.00700

#### Get Rating Summary (Research-Analyst Ratings)
When user asks about "rating summary", "institution ratings", "analyst rating list", "which institutions rate XX", "analyst target price history":
```bash
python skills/moomooapi/scripts/quote/get_research_rating_summary.py [--rating-dimension-type RATING_DIMENSION_TYPE] [--uid UID] [--next-key NEXT_KEY] [--num NUM] [--json] code
```
**Market**: US equities and REITs

**Parameters**:
- code: Stock code, e.g. US.AAPL
- --rating-dimension-type: 1=Institution (default), 2=Analyst
- --uid: Empty=summary list; non-empty=specific institution/analyst detail (analyst uid requires --rating-dimension-type 2)
- --next-key: Pagination key; omit for first page; "-1" = no more data
- --num: Results per page, default 10, range 1-20

### Research — Morningstar Report

#### Get Morningstar Report (Research-Morningstar Report)
When user asks about "Morningstar report", "Morningstar rating", "fair value", "economic moat", "bull/bear case", "analyst note", "investment thesis":
```bash
python skills/moomooapi/scripts/quote/get_research_morningstar_report.py [--json] code
```
**Market**: Equities and REITs

**Parameters**:
- code: Stock code, e.g. HK.00700

### Research — Valuation

#### Get Valuation Detail (Research-Valuation)
When user asks about "valuation", "PE", "PB", "PS", "P/E ratio", "historical valuation", "valuation percentile", "valuation trend", "sector valuation comparison":
```bash
python skills/moomooapi/scripts/quote/get_valuation_detail.py [--valuation-type VALUATION_TYPE] [--interval-type INTERVAL_TYPE] [--json] code
```
**Market**: Equities, funds and indices; PB type has no profit growth module; indices have no rank/mean/median fields

**Parameters**:
- code: Stock or index code, e.g. HK.00700
- --valuation-type: 1=PE, 2=PB, 3=PS (default: server recommendation)
- --interval-type: 1=3Month, 2=6Month, 3=1Year (default), 4=3Year, 5=Since2019, 6=5Year, 7=10Year, 8=2Year, 9=20Year, 10=30Year

#### Get Valuation Plate Stock List (Research-Valuation)
When user asks about "sector valuation", "index constituent valuation", "valuation ranking in sector", "cheapest/most expensive constituents":
```bash
python skills/moomooapi/scripts/quote/get_valuation_plate_stock_list.py [--valuation-type VALUATION_TYPE] [--next-key NEXT_KEY] [--num NUM] [--sort-type SORT_TYPE] [--sort-id SORT_ID] [--filter-security FILTER_SECURITY] [--json] code
```
**Market**: Plates and indices only; for index input, first request additionally returns owned plate list

**Parameters**:
- code: Plate or index code, e.g. HK.800000
- --valuation-type: 1=PE (default), 2=PB, 3=PS
- --next-key: Pagination key; omit for first page; "-1" = no more data
- --num: Results per page, default 10, range 1-50
- --sort-type: 1=Desc, 2=Asc (default)
- --sort-id: Sort column (Qot_Common.SortField): 51=MarketCap (default), 52=Valuation, 53=ForwardValuation, 54=HistoricalPercentile
- --filter-security: Index only: filter constituents by plate/sector (e.g. HK.LIST23363); omit = no filter

### Corporate Actions

#### Get Dividends (Corporate Actions-Dividends)
When user asks about "dividends", "dividend history", "ex-dividend date", "record date", "payable date", "dividend per share":
```bash
python skills/moomooapi/scripts/quote/get_corporate_actions_dividends.py [--json] code
```
**Market**: Equities and funds

**Parameters**:
- code: Stock code, e.g. HK.00700

#### Get Buybacks (Corporate Actions-Buybacks)
When user asks about "buybacks", "stock buyback", "share repurchase", "buyback history", "buyback amount":
```bash
python skills/moomooapi/scripts/quote/get_corporate_actions_buybacks.py [--next-key NEXT_KEY] [--num NUM] [--json] code
```
**Market**: HK and A-share equities and funds; HK and A-share data returned in separate tables with different fields

**Parameters**:
- code: Stock code, e.g. HK.00700
- --next-key: Pagination key; omit for first page; "-1" = no more data
- --num: Results per page, default 10, range 1-50

#### Get Stock Splits (Corporate Actions-Stock Splits)
When user asks about "stock split", "reverse split", "stock merge", "bonus share", "split history", "split ratio":
```bash
python skills/moomooapi/scripts/quote/get_corporate_actions_stock_splits.py [--next-key KEY] [--num N] [--json] code
```
**Market**: HK and US equities and funds

**Parameters**:
- code: Stock code, e.g. HK.00700
- --next-key: Pagination key; omit for first page; "-1" = no more data
- --num: Results per page, default 10, range 1-50

### Shareholders

#### Get Shareholders Overview (Shareholders)
When user asks about "shareholder overview", "ownership structure", "major shareholders", "shareholder type breakdown", "free float":
```bash
python skills/moomooapi/scripts/quote/get_shareholders_overview.py [--period-id PERIOD_ID] [--json] code
```
**Market**: HK and US equities and funds; when period_id=0 or omitted, also returns available period list

**Parameters**:
- code: Stock code, e.g. HK.00700
- --period-id: Report period ID; 0 or omit = latest data, also returns available period list

#### Get Holding Changes (Shareholders-Holding Changes)
When user asks about "holding changes", "increased stake", "reduced stake", "new position", "closed position", "who is buying/selling":
```bash
python skills/moomooapi/scripts/quote/get_shareholders_holding_changes.py [--next-key NEXT_KEY] [--num NUM] [--sort-type SORT_TYPE] [--sort-column SORT_COLUMN] [--filter-type FILTER_TYPE] [--json] code
```
**Market**: HK and US equities and funds; max 50 per page, default 10

**Parameters**:
- code: Stock code, e.g. HK.00700
- --next-key: Pagination key; omit for first page; "-1" = no more data
- --num: Results per page, default 10, range 1-50
- --sort-type: 1=Desc (default), 2=Asc
- --sort-column: Qot_Common.SortField: 62=Share Change Num (default), 63=Holding Date, 64=Ratio Change, 65=Change Amount, 66=Holder Pct
- --filter-type: 0=All (default), 1=Increase, 2=Decrease, 3=NewIn, 4=CloseOut

#### Get Holder Detail (Shareholders-Holder Detail)
When user asks about "holder detail", "top shareholders", "who holds XX", "shareholder list", "institutional holders":
```bash
python skills/moomooapi/scripts/quote/get_shareholders_holder_detail.py [--request-type REQUEST_TYPE] [--next-key NEXT_KEY] [--num NUM] [--sort-column SORT_COLUMN] [--sort-type SORT_TYPE] [--period-id PERIOD_ID] [--holder-id HOLDER_ID] [--json] code
```
**Market**: HK and US equities and funds; pagination key is string type

**Parameters**:
- code: Stock code, e.g. HK.00700
- --request-type: 0=Default, 1000=All, 1=OtherInstitution, 2=TraditionalInvestmentManager, 3=HedgeFund, 4=VentureCapital, 5=CorporatePension, 6=FoundationFund, 7=InsuranceCompany, 8=Bank/InvestmentBank, 9=FamilyOffice/Trust, 10=SovereignWealthFund, 11=REIT, 12=StructuredFinanceManager, 13=JointPension, 14=GovernmentPension, 15=Endowment, 100=Individual, 200=ADS, 300=ListedCompany, 400=UnlistedCompany, 500=StateOwnedShares
- --next-key: Pagination key; omit for first page; "-1" = no more data
- --num: Results per page, default 10, range 1-50
- --sort-column: Qot_Common.SortField: 61=Holder Quantity (default), 62=Share Change Num
- --sort-type: 1=Desc (default), 2=Asc
- --period-id: Report period ID, 0=latest
- --holder-id: Holder ID, 0=no filter

#### Get Institutional Holdings (Shareholders-Institutional)
When user asks about "institutional holdings", "institutional investors", "13F", "institutional ownership", "fund holdings":
```bash
python skills/moomooapi/scripts/quote/get_shareholders_institutional.py [--next-key NEXT_KEY] [--num NUM] [--json] code
```
**Market**: HK and US equities and funds

**Parameters**:
- code: Stock code, e.g. HK.00700
- --next-key: Pagination key; omit for first page; "-1" = no more data
- --num: Results per page, default 10, range 1-50

#### Get Insider Holder List (Shareholders-Insiders)
When user asks about "insider holdings", "executive holdings", "director holdings", "insider ownership", "insider list":
```bash
python skills/moomooapi/scripts/quote/get_insider_holder_list.py [--next-key NEXT_KEY] [--num NUM] [--json] code
```
**Market**: US equities and funds only; first page additionally returns insider summary (total/bought/sold count)

**Parameters**:
- code: Stock code, e.g. US.AAPL
- --next-key: Pagination key; omit for first page; "-1" = no more data
- --num: Results per page, default 10, range 1-20

#### Get Insider Trade List (Shareholders-Insiders)
When user asks about "insider trading", "insider buys/sells", "executive trades", "Form 4", "who is buying/selling insider":
```bash
python skills/moomooapi/scripts/quote/get_insider_trade_list.py [--holder-id HOLDER_ID] [--next-key NEXT_KEY] [--num NUM] [--json] code
```
**Market**: US equities and funds only

**Parameters**:
- code: Stock code, e.g. US.AAPL
- --holder-id: Holder ID; omit to query all insiders; available from GetInsiderHolderList or this API
- --next-key: Pagination key; omit for first page; "-1" = no more data
- --num: Results per page, default 10, range 1-50

### Company Info

#### Get Company Profile (Company Info)
When user asks about "company profile", "company overview", "company intro", "business description", "company website", "headquarters":
```bash
python skills/moomooapi/scripts/quote/get_company_profile.py [--json] code
```
**Market**: Equities and funds

**Parameters**:
- code: Stock code, e.g. HK.00700

#### Get Company Executives (Company Info-Executives)
When user asks about "company executives", "board members", "management team", "who is CEO/CFO", "executive compensation", "executive age/gender":
```bash
python skills/moomooapi/scripts/quote/get_company_executives.py [--json] code
```
**Market**: Equities and funds

**Parameters**:
- code: Stock code, e.g. HK.00700

#### Get Executive Background (Company Info-Executives)
When user asks about "executive background", "executive biography", "CEO background", "executive experience":
**Note**: When passing Chinese names in Git Bash, use Unicode escape sequences (e.g. `张三` → `\u5f20\u4e09`); the script auto-decodes them.
```bash
python skills/moomooapi/scripts/quote/get_company_executive_background.py [--json] code leader_name
```
**Market**: Equities and funds

**Parameters**:
- code: Stock code, e.g. HK.00700
- leader_name: Executive name from get_company_executives.py leader_name field; supports direct text or Unicode escape sequences (e.g. `\u9a6c\u5316\u817e`)

#### Get Operational Efficiency (Company Info-Operational Efficiency)
When user asks about "operational efficiency", "employee count", "headcount", "revenue per employee", "profit per employee":
```bash
python skills/moomooapi/scripts/quote/get_company_operational_efficiency.py [--next-key NEXT_KEY] [--num NUM] [--currency-code CURRENCY_CODE] [--json] code
```
**Market**: Equities and funds

**Parameters**:
- code: Stock code, e.g. HK.00700
- --next-key: Pagination key; omit for first page; "-1" = no more data
- --num: Results per page, default 10, range 1-50
- --currency-code: ISO 4217, e.g. CNY, USD, HKD; omit for default currency

### Brokers

#### Get Top Ten Buy/Sell Brokers (Top Ten Brokers)
When user asks about "top brokers", "net buy brokers", "net sell brokers", "broker ranking", "HK broker flow":
```bash
python skills/moomooapi/scripts/quote/get_top_ten_buy_sell_brokers.py [--days-before DAYS_BEFORE] [--json] code
```
**Market**: HK equities and funds only; days_before=0 returns real-time data (avg price/total volume/total turnover); days_before>0 returns net volume and broker name only

**Parameters**:
- code: Stock code, e.g. HK.00700
- --days-before: Trading days before current date; 0=real-time, >0=Nth historical trading day (default: real-time)

### Short Selling

#### Get Daily Short Volume (Daily Short Volume)
When user asks about "daily short volume", "short selling data", "short volume ratio", "short sell amount":
```bash
python skills/moomooapi/scripts/quote/get_daily_short_volume.py [--next-key NEXT_KEY] [--num NUM] [--json] code
```
**Market**: HK and US equities and funds

**Parameters**:
- code: Stock code, e.g. HK.00700
- --next-key: Pagination key; omit for first page; "-1" = no more data
- --num: Results per page, default 10, range 1-50

#### Get Short Interest (Short Interest)
When user asks about "short interest", "short interest ratio", "days to cover", "float short percentage":
```bash
python skills/moomooapi/scripts/quote/get_short_interest.py [--next-key NEXT_KEY] [--num NUM] [--json] code
```
**Market**: HK and US equities and funds; max 50 per request, default 10

**Parameters**:
- code: Stock code, e.g. HK.00700
- --next-key: Pagination key; omit for first page; "-1" = no more data
- --num: Results per page, default 10, range 1-50

---

**Related skills routing:** Related: shareholders/institutional/ARK → shareholders-institutions.md; valuation percentile rankings → rankings-calendar.md; earnings review card → `references/analysis-frameworks.md`.
