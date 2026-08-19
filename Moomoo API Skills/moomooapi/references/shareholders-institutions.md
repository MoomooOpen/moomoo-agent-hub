<!-- TOC: Shareholders / Institutional Holdings / ARK -->
# Shareholders / Institutional Holdings / ARK

Holding statistics, holding changes, holder detail, institutional holdings, insider trading, ARK fund holdings/transactions/dynamics.

## Table of Contents

- Shareholders
  - Get Shareholders Overview (Shareholders)
  - Get Holding Changes (Shareholders-Holding Changes)
  - Get Holder Detail (Shareholders-Holder Detail)
  - Get Institutional Holdings (Shareholders-Institutional)
  - Get Insider Holder List (Shareholders-Insiders)
  - Get Insider Trade List (Shareholders-Insiders)
- ARK Fund
  - Get ARK Fund Holding
  - Get ARK Active Transaction
  - Get ARK Stock Dynamic
- Institutional Holdings
  - Get Institution List
  - Get Institution Profile
  - Get Institution Holding List
  - Get Institution Holding Change
  - Get Institution Distribution

---

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



---

### ARK Fund

#### Get ARK Fund Holding
When the user asks about "ARK holding", "ARK fund", "ark invest":
```bash
python skills/moomooapi/scripts/quote/get_ark_fund_holding.py [--holding-type POSITION] [--cycle ONE_DAY] [--sort-field SHARES] [--sort-dir 0] [--count 20] [--json]
```

**Parameters**:
- --holding-type: Holding type (POSITION/INCREASE/DECREASE/NEW/SOLD_OUT)
- --cycle: Cycle (ONE_DAY/FIVE_DAY/TEN_DAY/THIRTY_DAY/SIXTY_DAY)
- --sort-field: Sort field (SHARES/WEIGHT_CHANGE/SHARES_CHANGE/MARKET_VALUE/WEIGHT)
- --sort-dir: Sort direction (0=descending, 1=ascending)
- --count: Page size
- Auto-pagination

#### Get ARK Active Transaction
When the user asks about "ARK trades", "ARK buys sells", "ark transactions":
```bash
python skills/moomooapi/scripts/quote/get_ark_active_transaction.py [--holding-type INCREASE] [--cycle ONE_DAY] [--sort-field CHANGE_AMOUNT] [--sort-dir 0] [--count 20] [--json]
```

**Parameters**:
- --holding-type: Holding type (INCREASE/DECREASE/NEW/SOLD_OUT)
- --cycle: Cycle (same as above)
- --sort-field: Sort field (CHANGE_AMOUNT/CHANGE_SHARES)
- Auto-pagination

#### Get ARK Stock Dynamic
When the user asks about "ARK stock", "does ARK hold", "ark stock dynamic":
```bash
python skills/moomooapi/scripts/quote/get_ark_stock_dynamic.py --code US.TSLA [--json]
```

**Parameters**:
- --code: Stock code (e.g. US.TSLA), required



---

### Institutional Holdings

#### Get Institution List
When the user asks about "institution list", "fund companies", "institutional investors":
```bash
python skills/moomooapi/scripts/quote/get_institution_list.py --market US [--sort-field POSITION_VALUE] [--sort-dir 0] [--count 20] [--name Bridgewater] [--json]
```

**Parameters**:
- --market: Market (HK/US), required
- --sort-field: Sort field (POSITION_VALUE/POSITION_VALUE_CHANGE/POSITION_COUNT/POSITION_COUNT_CHANGE)
- --name: Institution name fuzzy search
- Auto-pagination

#### Get Institution Profile
When the user asks about "institution profile", "fund info":
```bash
python skills/moomooapi/scripts/quote/get_institution_profile.py --market US --institution-id 123 [--json]
```

**Parameters**:
- --market: Market (HK/US), required
- --institution-id: Institution ID (required)

#### Get Institution Holding List
When the user asks about "institution holdings", "fund top holdings", "institutional positions":
```bash
python skills/moomooapi/scripts/quote/get_institution_holding_list.py --market US --institution-id 123 [--change-type INCREASE] [--sort-field HOLDING_VALUE] [--sort-dir 0] [--count 20] [--keyword TSLA] [--json]
```

**Parameters**:
- --market: Market (HK/US), required
- --institution-id: Institution ID (required)
- --change-type: Change type filter (NEW/SOLD_OUT/INCREASE/DECREASE)
- --sort-field: Sort field (HOLDING_VALUE/HOLDING_PCT/LAST_HOLDING_PCT/CHANGE_SHARES/CHANGE_PCT/PORTFOLIO_PCT/INDUSTRY/HOLDING_DATE)
- --keyword: Search keyword
- Auto-pagination

#### Get Institution Holding Change
When the user asks about "institution changes", "new positions", "institutional buying":
```bash
python skills/moomooapi/scripts/quote/get_institution_holding_change.py --market US --institution-id 123 [--change-type NEW] [--sort-field CHANGE_PCT] [--sort-dir 0] [--count 20] [--json]
```

**Parameters**:
- --market: Market (HK/US), required
- --institution-id: Institution ID (required)
- --change-type: Change type (NEW/SOLD_OUT/INCREASE/DECREASE)
- --sort-field: Sort field (CHANGE_PCT/CHANGE_SHARES/HOLDING_DATE)
- Auto-pagination

#### Get Institution Distribution
When the user asks about "institution distribution", "sector allocation":
```bash
python skills/moomooapi/scripts/quote/get_institution_distribution.py --market US --institution-id 123 [--json]
```

**Parameters**:
- --market: Market (HK/US), required
- --institution-id: Institution ID (required)

---

**Related skills routing:** Related: fundamentals → fundamentals.md; institutional rankings → rankings-calendar.md.
