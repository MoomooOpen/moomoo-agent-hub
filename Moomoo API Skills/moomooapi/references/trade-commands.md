<!-- TOC: Trading Commands -->
# Trading Commands

Accounts, positions, place/cancel/modify orders, combo orders, order queries, margin, max trade quantities.

## Trading Commands

## Table of Contents

- Get Account List
  - Singapore / Malaysia / Japan Markets (SG / MY / JP)
  - Japan (FUTUJP) Sub-Account Types
  - `asset_category` Filter on Funds & Positions
  - `acctradinginfo_query` JP Parameters
  - `place_order` JP Parameters
- Get Positions & Funds
- Place Order
  - Prediction Market Hard Constraints
- Place Combo Order (Option Combo/Strategy / Prediction Market Combo)
  - Prediction Market Combo Hard Constraints
- Query Combo Order Trading Info
  - US Stock Trading Session Confirmation
  - Paper Trading Order Flow
  - Live Trading Order Flow
- Modify Order
- Cancel Order
- Query Today's Orders
- Query Historical Orders
- Query Historical Deals

---

### Get Account List
When the user asks about "my accounts" or "account list":
```bash
python skills/moomooapi/scripts/trade/get_accounts.py [--json]
```
The script iterates through all `SecurityFirm` values and fetches accounts from both **securities** (`OpenSecTradeContext`) and **futures** (`OpenFutureTradeContext`), then deduplicates by `acc_id`. JSON field `ctx_type` is `SEC` or `FUTURE`.

> **Tip**: The last 4 digits of a live account's `uni_card_num` match the account number shown in the moomoo app and desktop client. When displaying live account info, **prefer showing `uni_card_num`** (rather than `acc_id`), as this is the number users recognize from the app. Paper trading accounts do not need this field.

> **Account fetching issue**: `create_trade_context()` defaults to `filter_trdmarket=TrdMarket.NONE` (no market filtering), but if you manually create `OpenSecTradeContext` with a specific market (e.g., `TrdMarket.US`, `TrdMarket.HK`), some accounts may be filtered out. Change `filter_trdmarket` to `TrdMarket.NONE` and re-fetch to get all accounts.

JSON output includes a `trdmarket_auth` field indicating trading permissions (e.g., `["HK", "US", "HKCC", "SG", "MY", "JP"]`; futures/prediction markets may also include `FUTURES`, `PREDICTION`, etc.); `acc_role` indicates role (e.g. `MASTER`). When placing orders, select an account whose `trdmarket_auth` includes the target market and `acc_role` is not `MASTER`. For **prediction markets**, pick `ctx_type=FUTURE`, live env, non-MASTER, with `PREDICTION` in `trdmarket_auth`.

#### Singapore / Malaysia / Japan Markets (SG / MY / JP)

| Market | Code Prefix | Broker | Example |
|--------|-------------|--------|---------|
| Singapore | `SG.` | `FUTUSG` | `SG.D05` (DBS) |
| Malaysia | `MY.` | `FUTUMY` | `MY.1155` (Maybank) |
| Japan | `JP.` | `FUTUJP` | `JP.7203` (Toyota) |

Usage notes:
- Trading scripts infer `SG` / `MY` / `JP` from the `--code` prefix; `--market` is usually unnecessary
- Confirm the account's `trdmarket_auth` includes the target market and pass the matching `--security-firm`
- Trade scripts with `--market` now accept `SG`, `MY`, and `JP` (e.g. `get_portfolio.py`, `get_orders.py`, `get_max_trd_qtys.py`)
- For MY/SG odd-lot order book, use `get_orderbook.py --type ODD` (MY/SG only)

#### Japan (FUTUJP) Sub-Account Types

`get_acc_list()` returns an extra `jp_acc_type` field for Japan accounts (`security_firm == FUTUJP`). The value is a `SubAccType` enum that distinguishes Japan-specific sub-accounts. For non-Japan accounts the value is `NONE` (or N/A).

| `jp_acc_type` | Sub-Account Meaning |
|---|---|
| `NONE` | Non-Japan account / not applicable |
| `JP_GENERAL` | 一般口座 (General account) - long |
| `JP_TOKUTEI` | 特定口座 (Tokutei / specified account) - long |
| `JP_NISA_GENERAL` | 一般NISA (General NISA) |
| `JP_NISA_TSUMITATE` | 累計NISA (Tsumitate / accumulating NISA) |
| `JP_GENERAL_SHORT` | 一般口座 - short |
| `JP_TOKUTEI_SHORT` | 特定口座 - short |
| `JP_HONPO_GENERAL` | Domestic margin collateral - general |
| `JP_GAIKOKU_GENERAL` | Foreign margin collateral - general |
| `JP_HONPO_TOKUTEI` | Domestic margin collateral - tokutei |
| `JP_GAIKOKU_TOKUTEI` | Foreign margin collateral - tokutei |
| `JP_DERIVATIVE_LONG` | Derivatives - long |
| `JP_DERIVATIVE_SHORT` | Derivatives - short |
| `JP_HONPO_DERIVATIVE_GENERAL` | Domestic derivative margin - general |
| `JP_GAIKOKU_DERIVATIVE_GENERAL` | Foreign derivative margin - general |
| `JP_HONPO_DERIVATIVE_TOKUTEI` | Domestic derivative margin - tokutei |
| `JP_GAIKOKU_DERIVATIVE_TOKUTEI` | Foreign derivative margin - tokutei |

JP usage notes:
- A single JP user may have multiple records under `FUTUJP` differing only by `jp_acc_type` (e.g., one `JP_TOKUTEI` cash record + one `JP_NISA_GENERAL` record). Treat each as a distinct sub-account when selecting `acc_id` for trading.
- Tax/settlement behavior differs across `JP_GENERAL` vs `JP_TOKUTEI` vs `JP_NISA_*`. Surface `jp_acc_type` to the user before placing JP orders so they can pick the right sub-account.
- NISA accounts (`JP_NISA_GENERAL` / `JP_NISA_TSUMITATE`) have annual contribution limits and product restrictions enforced server-side; orders that violate them are rejected by the API.
- Margin / derivative sub-accounts (`JP_HONPO_*`, `JP_GAIKOKU_*`, `JP_DERIVATIVE_*`) are short-selling or collateral records — do not pick them for plain cash buy orders.
- When the user does not specify which JP sub-account to use, prefer `JP_TOKUTEI` (most common for retail) or ask via AskUserQuestion before submitting.

`jp_acc_type` is also returned by the following order queries (already exposed in the corresponding scripts):

| API | Script |
|---|---|
| `get_acc_list()` | `get_accounts.py` |
| `order_list_query()` (today's / pending orders) | `get_orders.py` |
| `history_order_list_query()` (history orders) | `get_history_orders.py` |

Use the `jp_acc_type` column in order responses to attribute fills to the correct JP sub-account (e.g., split P&L between `JP_TOKUTEI` and `JP_NISA_GENERAL`).

#### `asset_category` Filter on Funds & Positions

`accinfo_query()` and `position_list_query()` accept an `asset_category` parameter (`AssetCategory` enum: `NONE` / `JP` / `US`) to scope the result to a specific sub-account asset category instead of returning the consolidated view.

```bash
# Query JP sub-account funds & positions only
python skills/moomooapi/scripts/trade/get_portfolio.py \
    --acc-id 12345 --security-firm FUTUJP --asset-category JP --trd-env REAL [--json]

# Same filter when iterating all accounts
python skills/moomooapi/scripts/trade/get_all_portfolios.py --asset-category JP [--json]
```

Behavior:
- `NONE` (default): aggregated account view; no asset-category filtering
- `JP`: returns only Japan sub-account funds/positions; pair with `jp_acc_type` from `get_accounts.py` to identify which JP sub-account a row belongs to
- `US`: returns only US sub-account funds/positions
- If the local moomoo-api SDK does not yet expose `AssetCategory`, the script errors out and asks for an SDK upgrade — it does not silently drop the filter

#### `acctradinginfo_query` JP Parameters

For JP accounts, `acctradinginfo_query()` (max tradable quantity) takes two extra optional parameters:

- `jp_acc_type` (`SubAccType` enum): which JP sub-account's buying power to use. Required when the account holds multiple JP sub-accounts and you want a non-default one. Defaults to `JP_GENERAL` server-side.
- `position_id`: the position record id (from `position_list_query()`) to query max sellable against. Use it on JP margin / collateral sub-accounts where positions can be closed individually.

```bash
# Max buyable on JP TOKUTEI sub-account
python skills/moomooapi/scripts/trade/get_max_trd_qtys.py JP.7203 \
    --price 3000 --security-firm FUTUJP --acc-id 12345 \
    --trd-env REAL --jp-acc-type JP_TOKUTEI

# Max sellable for a specific JP margin position
python skills/moomooapi/scripts/trade/get_max_trd_qtys.py JP.7203 \
    --price 3000 --security-firm FUTUJP --acc-id 12345 \
    --trd-env REAL --jp-acc-type JP_HONPO_TOKUTEI --position-id 9876543210
```

Notes:
- `jp_acc_type` choices in the script mirror the full `SubAccType` enum (long/short/NISA/derivative variants).
- For non-JP accounts these parameters are irrelevant; do not pass them.

#### `place_order` JP Parameters

`place_order()` accepts the same `jp_acc_type` and `position_id` extras as `acctradinginfo_query()` to route a JP order to a specific sub-account / position record.

```bash
# Buy 100 Toyota shares on JP NISA general sub-account
python skills/moomooapi/scripts/trade/place_order.py \
    --code JP.7203 --side BUY --quantity 100 --price 3000 \
    --security-firm FUTUJP --acc-id 12345 --trd-env REAL \
    --jp-acc-type JP_NISA_GENERAL --confirmed

# Cover (sell) a specific JP margin short position
python skills/moomooapi/scripts/trade/place_order.py \
    --code JP.7203 --side SELL --quantity 100 --price 3000 \
    --security-firm FUTUJP --acc-id 12345 --trd-env REAL \
    --jp-acc-type JP_HONPO_TOKUTEI --position-id 9876543210 --confirmed
```

JP order rules:
- Pick `jp_acc_type` consistent with the trade intent: `JP_GENERAL`/`JP_TOKUTEI` for cash long, `JP_NISA_*` for NISA-eligible products only, `JP_*_SHORT` to open short, `JP_HONPO_*`/`JP_GAIKOKU_*` for margin.
- `position_id` is required when closing/covering a specific JP margin or short position; pass the ID returned by `position_list_query()` for the row you want to close. For ordinary long buys leave it unset.
- The order preview (without `--confirmed`) prints the chosen `jp_acc_type` and `position_id` so the user can verify before live submission.
- When the user requests a JP trade without specifying the sub-account, default to `JP_TOKUTEI` (most common for retail) or use AskUserQuestion to confirm.





---

### Get Positions & Funds
When the user asks about "positions", "funds", or "my stocks":
```bash
python skills/moomooapi/scripts/trade/get_portfolio.py [--market HK] [--trd-env SIMULATE] [--acc-id 12345] [--ctx-type SEC|FUTURE] [--security-firm FUTUSECURITIES] [--json]
```
- `--market`: US, HK, HKCC, CN, SG, MY, JP
- `--trd-env`: REAL, SIMULATE (default SIMULATE)
- `--ctx-type`: `SEC` (securities, default) or `FUTURE` (futures/prediction market accounts; same as `get_accounts.ctx_type`)
- `--show-option-strategy-view`: query positions in option strategy view (`position_list_query(show_option_strategy_view=True)`)
- `position_list_query` response adds: `combo_id`, `strategy_type`, `position_type`, `acc_id`, `jp_acc_type`

> For prediction market/futures account portfolio, orders, fills, cancel/modify, cash flow, etc., pass `--ctx-type FUTURE` (align with `get_accounts.ctx_type`). Scripts that take an `EC.` code (e.g. `get_max_trd_qtys`, `get_history_orders --code`) auto-switch to the futures context.

> Full position & funds field mapping (aligned with moomoo App) is in `docs/FIELD_MAPPING.md`. **Key rules**: Use `unrealized_pl` / `pl_ratio_avg_cost` (average cost basis) for P&L. Do NOT use `cost_price` / `pl_val` (diluted cost basis). Multi-currency aggregation must use `accinfo_query(currency=target_currency)` for account-level data.

### Place Order
When the user asks to "buy", "sell", "place an order", or "prediction market order":
```bash
# Stocks / options etc.
python skills/moomooapi/scripts/trade/place_order.py --code US.AAPL --side BUY --quantity 10 --price 150.0 [--order-type NORMAL] [--trd-env SIMULATE] [--time-in-force DAY] [--expire-time 2026-12-31] [--confirmed] [--security-firm FUTUSECURITIES] [--json]

# Prediction market (code EC.xxx; live only + pred_side required; amount vs quantity mutually exclusive, amount preferred)
python skills/moomooapi/scripts/trade/place_order.py --code EC.xxx --side BUY --amount 100 --price 0.55 --pred-side YES --trd-env REAL --acc-id {acc_id} --confirmed [--security-firm FUTUSECURITIES] [--json]
```
- `--code`: Instrument code (required). Equities use market prefix; **prediction market codes are `EC.xxx` (no US./HK. prefix)** and the script uses `OpenFutureTradeContext`
- `--side`: BUY/SELL (required)
- `--quantity`: Quantity; mutually exclusive with `--amount`. If both are set, **amount wins** and qty is forced to 0
- `--amount`: Order amount; **prediction market only**; when set, SDK receives `qty=0`
- `--pred-side`: YES/NO; **required for prediction market orders** (whether using quantity or amount)
- `--price`: Price (required for limit orders); prediction markets are usually 0.01~0.99
- `--order-type`: NORMAL (limit) / MARKET
- `--time-in-force`: default DAY; for `GTD`, pass `--expire-time yyyy-MM-dd`
- `--expire-time`: only valid when `time_in_force=GTD`
- `--session`: US stock session NONE/RTH/ETH/OVERNIGHT/ALL (US only)
- `--confirmed`: Required for live trading (hard constraint — without it, preview and exit)
- **Always confirm code, side, quantity/amount, price (and pred_side for prediction markets) with the user**

#### Prediction Market Hard Constraints
- Live only (`--trd-env REAL`); `SIMULATE` exits with an error (paper trading does not support prediction markets)
- Futures account context; `trdmarket_auth` must include **`PREDICTION`**, otherwise report that prediction markets are unsupported
- Select accounts via `get_accounts.py --json`: `ctx_type=FUTURE`, `trd_env=REAL`, non-`MASTER`, and `trdmarket_auth` contains `PREDICTION`
- Regular futures still follow "Futures Trading Commands" (generate `OpenFutureTradeContext` code). **Prediction markets can be placed via this script**

### Place Combo Order (Option Combo/Strategy / Prediction Market Combo)
When the user asks to place an "option combo order", "strategy combo order", "multi-leg combo order", or "prediction market combo":

**Option combo:**
```bash
python skills/moomooapi/scripts/trade/place_combo_order.py \
  '[{"code":"US.AAPL260529C302500","trd_side":"BUY","qty_ratio":1},{"code":"US.AAPL","trd_side":"SELL","qty_ratio":100}]' \
  --price 9.9 --quantity 1 [--order-type NORMAL] [--trd-env SIMULATE] [--confirmed] [--security-firm FUTUSECURITIES] [--json]
```
- Combo leg JSON fields: `code`, `trd_side`, `qty_ratio`, `position_id` (JP close scenario)
- `trd_side` supports `BUY` / `SELL` / `SELLSHORT` / `BUYBACK` (`SELL_SHORT` / `BUY_BACK` aliases also supported)
- FUTUJP combo rules:
  - open legs: use `BUY` / `SELLSHORT` (do not pass `position_id`)
  - close legs: use `SELL` / `BUYBACK` (must pass `position_id`)
  - close-leg `position_id` must come from `position_list_query(show_option_strategy_view=True)` result (or this skill's `get_portfolio.py --show-option-strategy-view`)
- **`--price` pricing**: prefer `bid1`/`ask1` from `get_option_strategy_analysis.py` for the same legs (buy usually near `ask1`, sell near `bid1`); **do not** derive combo price from per-leg `get_snapshot.py`
- `--quote-id`: **ignored** for option combos (silently not passed to SDK)
- `--price` and `--quantity` are required; leg actual qty = `quantity * qty_ratio`
- `--time-in-force` defaults to `DAY`; for `GTD`, pass `--expire-time yyyy-MM-dd`
- `--confirmed`: required for live combo order submit (without it, script returns preview only)

**Prediction market combo (every leg must be `EC.`):**
```bash
# 1) Agent generates Python: get_valid_combo_list → mvc
# 2) Agent generates Python: request_combo_quotes(combo_leg_list, mvc) → quote_id + bid/ask
# 3) Call this script with price + quote_id from step 2
python skills/moomooapi/scripts/trade/place_combo_order.py \
  '[{"code":"EC.xxx","trd_side":"BUY","qty_ratio":1,"pred_side":"YES"},{"code":"EC.yyy","trd_side":"BUY","qty_ratio":1,"pred_side":"YES"}]' \
  --price {ask_or_bid} --quantity 1 --quote-id {quote_id} --trd-env REAL --acc-id {acc_id} --confirmed [--security-firm FUTUINC]
```

#### Prediction Market Combo Hard Constraints
1. **Leg validity**: every leg `code` must start with `EC.`; mixing EC. and non-EC → script errors with invalid combo
2. **Same side**: all legs must share the same `trd_side`; otherwise error. Price from **first leg**: `BUY` → `ask_price`, `SELL` → `bid_price`
3. **Each leg requires** `pred_side`: `YES` / `NO`
4. **RFQ chain** (no dedicated skill yet — Agent generates Python for steps 1–2):
   - `OpenQuoteContext.get_valid_combo_list()` → **`mvc` (required)** and optional combo list
   - `OpenQuoteContext.request_combo_quotes(combo_leg_list, mvc)` → **`quote_id`**, `bid_price`, `ask_price`; retry briefly if `should_retry=True`
   - **`--price` must** come from that RFQ ask/bid; **`--quote-id` is required**
5. **Trade context**: script uses `OpenFutureTradeContext`; `--trd-env REAL` only; account `trdmarket_auth` must include **`PREDICTION`**; paper trading exits with error
6. Confirm legs, side, pred_side, qty, price, and quote_id with the user before live submit

RFQ reference (Agent may adapt and run):
```python
from moomoo import *
qot_ctx = OpenQuoteContext(security_firm=SecurityFirm.FUTUINC)
ret, combo_df, mvc, _ = qot_ctx.get_valid_combo_list()  # mvc required downstream
# Build ComboLeg with code/trd_side/qty_ratio/pred_side; all trd_side identical
ret, quote = qot_ctx.request_combo_quotes(combo_leg_list, mvc)
# quote['quote_id'], quote['ask_price'], quote['bid_price']; honor should_retry
qot_ctx.close()
```
- **Always confirm combo legs, direction, quantity, and price before live submission**

### Query Combo Order Trading Info
When the user asks about "combo margin change", "combo buying power impact", or "combo trading info":
```bash
python skills/moomooapi/scripts/trade/comboorder_tradinginfo_query.py \
  '[{"code":"US.AAPL260529C302500","trd_side":"BUY","qty_ratio":1},{"code":"US.AAPL","trd_side":"SELL","qty_ratio":100}]' \
  --price 100 --quantity 1 [--order-type NORMAL] [--order-id 123456789] [--trd-env SIMULATE] [--security-firm FUTUSECURITIES] [--json]
```
- Returns key fields: `nlv_change`, `initial_margin_change`, `maintenance_margin_change`, `option_bp`, `max_withdraw_change`, `bp_decrease`
- `--price` should prefer `bid1`/`ask1` from `get_option_strategy_analysis.py`; do not compute from single-leg snapshots
- `--order-id` is optional and used for modify-order scenario

#### US Stock Trading Session Confirmation

When the order code is a **US stock** (starts with `US.`) and the user has **not explicitly specified a trading session**, **you must use AskUserQuestion to let the user choose a trading session** before placing the order:

```
Question: "Please select a US stock trading session:"
  header: "Session"
  Options:
    - "Regular Hours Only" : Only fill during regular trading hours (ET 9:30-16:00)
    - "Allow Pre/Post Market" : Allow fills during pre-market (4:00-9:30) and after-hours (16:00-20:00); note: market orders are NOT supported in pre/post market
```

- User selects "Regular Hours Only": Place order normally, do NOT add `--fill-outside-rth`
- User selects "Allow Pre/Post Market": Add `--fill-outside-rth` to the order command
- If the user has already mentioned "pre-market", "after-hours", "extended hours", "盘前", "盘后", or "盘前盘后" in the conversation, add `--fill-outside-rth` directly without asking again
- If the user explicitly says "regular hours" or "盘中", do NOT add `--fill-outside-rth`, no need to ask again
- **Note**: Market orders (`--order-type MARKET`) are NOT supported during pre/post market sessions. If the user selects pre/post market and uses a market order, prompt them to switch to a limit order

#### Paper Trading Order Flow

Paper trading (`--trd-env SIMULATE`, default) — simply execute the order command:
```bash
python skills/moomooapi/scripts/trade/place_order.py --code {code} --side {side} --quantity {qty} --price {price} --trd-env SIMULATE
```

#### Live Trading Order Flow

When the user requests live trading (`--trd-env REAL`), **the following flow must be executed**:

0. **Confirm Brokerage Identifier (first time)**:
   If the user's `security_firm` has not been determined yet, first check if the environment variable `MOOMOO_SECURITY_FIRM` (or legacy `FUTU_SECURITY_FIRM`) is set. If not, run `get_accounts.py --json` and check the `security_firm` field of the returned live trading accounts to determine it. All subsequent trading commands should include the `--security-firm {firm}` parameter. See the "Brokerage Auto-Detection" section for details.

1. **Query account list and select an authorized account**:
   First run `get_accounts.py --json` to get all accounts, determine the target trading market from the stock code (e.g., HK.00700 → HK), and filter for accounts where `trd_env` is `REAL`, `trdmarket_auth` includes the target market, **and `acc_role` is not `MASTER`**. The primary account (MASTER) is not allowed to place orders and must be excluded.
   - If there is only 1 matching account, use it directly
   - If there are multiple matching accounts, use AskUserQuestion to let the user choose:
     ```
     Question: "Please select a trading account:"
       header: "Account"
       Options: (list all matching accounts)
         - "Account {acc_id} ({card_num})" : Role: {acc_role}, Market permissions: {trdmarket_auth}
     ```
   - If there are no matching accounts, inform the user that there are no live trading accounts supporting this market (note: MASTER role accounts cannot be used for placing orders)

2. **Use AskUserQuestion for secondary confirmation**, clearly displaying order details:
   ```
   Question: "Confirm live order? This will use real funds."
     header: "Live Confirm"
     Options:
       - "Confirm Order" : Account: {acc_id}, Code: {code}, Side: {BUY/SELL}, Quantity: {qty}, Price: {price}
       - "Cancel" : Do not place the order
   ```
   Only proceed after the user selects "Confirm Order"; if "Cancel" is selected, abort.

3. **Execute the order command** with `--acc-id`:
   ```bash
   python skills/moomooapi/scripts/trade/place_order.py --code {code} --side {side} --quantity {qty} --price {price} --trd-env REAL --acc-id {acc_id} --security-firm {firm}
   ```

   > **Note**: If the API returns `unlock needed` or a similar unlock error, prompt the user to first **manually unlock the trade password in the OpenD GUI** (the "Unlock Trade" button in the menu or interface), then retry the order.

### Modify Order
When the user asks to "modify order", "change price", or "change quantity":
```bash
python skills/moomooapi/scripts/trade/modify_order.py --order-id 12345678 [--price 410] [--quantity 200] [--market HK] [--trd-env SIMULATE] [--acc-id 12345] [--security-firm FUTUSECURITIES] [--json]
```
- `--order-id`: Order ID (required)
- `--price`: New price (optional, keeps original price if not provided)
- `--quantity`: New total quantity, not incremental (optional, keeps original quantity if not provided)
- At least one of `--price` or `--quantity` must be provided
- Missing parameters are automatically filled from the original order (e.g., if only changing price, quantity is taken from the original order)
- A-share Connect (HKCC) market does not support order modification
- If the user hasn't provided the order ID, first query with `get_orders.py`

### Cancel Order
When the user asks to "cancel order" or "revoke order":
```bash
python skills/moomooapi/scripts/trade/cancel_order.py --order-id 12345678 [--acc-id 12345] [--market HK] [--trd-env SIMULATE] [--security-firm FUTUSECURITIES] [--json]
```
- If the user hasn't provided the order ID, first query with `get_orders.py`

### Query Today's Orders
When the user asks about "orders" or "my orders":
```bash
python skills/moomooapi/scripts/trade/get_orders.py [--market HK] [--trd-env SIMULATE] [--acc-id 12345] [--security-firm FUTUSECURITIES] [--json]
```

### Query Historical Orders
When the user asks about "historical orders" or "past orders":
- **Important**: If the user asks for "all orders" / "all historical orders" (e.g., "全部订单", "所有订单", "all orders"), you MUST proactively inform them **before** querying: "The API only returns orders from the last 90 days by default. You can specify a start and end date to retrieve older historical orders."
```bash
python skills/moomooapi/scripts/trade/get_history_orders.py [--acc-id 12345] [--market HK] [--trd-env SIMULATE] [--start 2026-01-01] [--end 2026-03-01] [--code US.AAPL] [--status FILLED_ALL CANCELLED_ALL] [--limit 200] [--security-firm FUTUSECURITIES] [--json]
```

### Query Historical Deals
When the user asks about "historical deals", "past fills", or "deal records":
- **Important**: If the user asks for "all deals" / "all historical deals" (e.g., "全部成交", "所有成交", "all deals"), you MUST proactively inform them **before** querying: "The API only returns deals from the last 90 days by default. You can specify a start and end date to retrieve older historical deals."
```bash
python skills/moomooapi/scripts/trade/get_history_order_fill_list.py [--acc-id 12345] [--market HK] [--trd-env SIMULATE] [--start 2026-01-01] [--end 2026-03-01] [--security-firm FUTUSECURITIES] [--json]
```

---

---

**Related skills routing:** Related: combo option order-book price (--price source) → options.md (hard constraint); position field mapping → docs/FIELD_MAPPING.md; position diagnostic checklist → `references/analysis-frameworks.md`.
