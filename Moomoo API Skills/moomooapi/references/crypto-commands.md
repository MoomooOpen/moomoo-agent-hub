<!-- TOC: Cryptocurrency Commands (Crypto) -->
# Cryptocurrency Commands (Crypto)

BTC/ETH etc. crypto market data and trading. Requires `moomoo-api >= 10.5.6508` (`OpenCryptoTradeContext`).

## Cryptocurrency (Crypto)

## Table of Contents

- Scope
- Code Naming Convention
- Crypto Market Data
- Crypto Trading Commands
  - Query Crypto Accounts
  - Query Crypto Portfolio
  - Place Crypto Order
  - Cancel Crypto Order
  - Query Crypto Orders / Deals
  - Query Crypto Cash Flow
  - Query Crypto Max Tradable Quantity
  - Query Crypto Order Fee
- Crypto Ordering Rules

---

### Scope

| Item | Description |
|------|-------------|
| Brokers | FUTUSECURITIES (Futu Securities HK), FUTUINC (Futu US), FUTUSG (Futu SG) |
| Instruments | Spot pairs (BTC/USD, ETH/USD, etc.) |
| Trade type | Cash buy only (no margin, no paper trading) |
| Order types | FUTUHK / FUTUINC: limit + market; FUTUSG: limit only |
| Trading hours | 7×24, no trading session or validity period; limit orders use GTC, market orders use IOC |
| Modify | Not supported; only cancel (single or cancel-all) |
| Quantity | Supports decimals (e.g. `0.000136`) |

### Code Naming Convention

| Scenario | Format | Example |
|----------|--------|---------|
| Currency / index | `CC.{Base currency}` | `CC.BTC`, `CC.ETH`, `CC.SOL` |
| Pair (order, subscription, fills) | `CC.{Base}{Quote}` | `CC.BTCUSD`, `CC.ETHUSD`, `CC.BTCHKD` |
| Position query response code | Base currency only | `CC.BTC` |

> Do not include `/` in code (e.g. `CC.BTC/USD` is invalid).

### Crypto Market Data

Currency/index quotes (BTC, ETH, etc.) always use global data; pair quotes follow the broker's upstream (HK→Hashkey, US→Coinbase, SG→DDEX) selected via `security_firm` on `OpenQuoteContext`.

```bash
# Subscribe to crypto market data (CC.BTCUSD or CC.BTC)
python skills/moomooapi/scripts/subscribe/subscribe.py CC.BTCUSD --types QUOTE ORDER_BOOK

# Crypto Candlesticks (extra periods available: 1m/3m/5m/10m/15m/30m/60m/120m/180m/240m/1d/1w/1M/1Q/1Y)
python skills/moomooapi/scripts/quote/get_kline.py CC.BTCUSD --ktype 1m --num 10

# Crypto snapshot (currency or pair)
python skills/moomooapi/scripts/quote/get_snapshot.py CC.BTC CC.BTCUSD

# Crypto market state (MORNING = trading, covers EST 00:00-24:00)
python skills/moomooapi/scripts/quote/get_market_state.py CC.BTCUSD

# Capital flow / distribution (code can be currency or pair)
python skills/moomooapi/scripts/quote/get_capital_flow.py CC.BTC
python skills/moomooapi/scripts/quote/get_capital_distribution.py CC.BTC
```

**Order book notes**: Tradable pairs support 1/5/10/20/40 level order book; indexes return no order book. Push frequency matches the client, and there is no broker queue for crypto.

### Crypto Trading Commands

All crypto trading scripts are built on `OpenCryptoTradeContext`.

#### Query Crypto Accounts

```bash
python skills/moomooapi/scripts/trade/get_crypto_accounts.py [--json]
```
- Automatically iterates FUTUSECURITIES / FUTUINC / FUTUSG
- Returns `acc_id`, `uni_card_num`, `security_firm`, `trdmarket_auth` (contains `CRYPTO`)

#### Query Crypto Portfolio

```bash
python skills/moomooapi/scripts/trade/get_crypto_portfolio.py --acc-id 12345 --security-firm FUTUINC [--json]
```
- Extra fund fields: `crypto_mv`, `exposure_level`, `exposure_limit`, `used_limit`, `remaining_limit`
- Position `code` returns the base currency (e.g. `CC.BTC`); new `currency` field (default USD)
- `exposure_level` enum: `NORMAL` / `NEAR_LIMIT` / `RESTRICTED` / `SAFE` / `MODERATE` / `WARNING` / `MARGIN_CALL`

#### Place Crypto Order

```bash
# Limit buy 0.000136 BTC at 72873.22 USD
python skills/moomooapi/scripts/trade/place_crypto_order.py \
    --code CC.BTCUSD --side BUY --quantity 0.000136 --price 72873.22 \
    --order-type NORMAL --security-firm FUTUINC --acc-id 12345 --confirmed

# Market buy (FUTUHK/FUTUINC only, FUTUSG does not support market orders)
python skills/moomooapi/scripts/trade/place_crypto_order.py \
    --code CC.BTCUSD --side BUY --quantity 0.000136 \
    --order-type MARKET --security-firm FUTUINC --acc-id 12345 --confirmed
```

Key notes:
- **Live only**: no paper trading; the script always uses `TrdEnv.REAL`
- **Must pass `--confirmed`**: without it, the script prints a preview and exits
- **Fractional quantity**: unlike other markets, crypto quantity can be a float
- **Time-in-force**: limit → GTC, market → IOC (auto); users don't need to pass `--session` or TIF
- **Unsupported params**: `session`, TIF overrides, `fill-outside-rth`
- Always use AskUserQuestion to confirm code/side/qty/price before the first real send

#### Cancel Crypto Order

```bash
# Cancel single
python skills/moomooapi/scripts/trade/cancel_crypto_order.py \
    --order-id 12345678 --security-firm FUTUINC --acc-id 12345

# Cancel all
python skills/moomooapi/scripts/trade/cancel_crypto_order.py \
    --all --security-firm FUTUINC --acc-id 12345
```

**No modify support**: to change an order, cancel and re-submit.

#### Query Crypto Orders / Deals

```bash
# Today / open orders
python skills/moomooapi/scripts/trade/get_crypto_orders.py \
    --security-firm FUTUINC --acc-id 12345

# History orders (supports --code / --start / --end, default last 90 days)
python skills/moomooapi/scripts/trade/get_crypto_orders.py --history \
    --code CC.BTCUSD --start 2026-01-01 --end 2026-03-01 \
    --security-firm FUTUINC --acc-id 12345
```

> **Note**: `history_order_list_query` does **not** accept the `refresh_cache` parameter. The script only passes `refresh_cache=True` to `order_list_query` (today's orders); the history branch omits it. Mirror this when you write code by hand — passing `refresh_cache` to `history_order_list_query` will raise.

#### Query Crypto Cash Flow

```bash
python skills/moomooapi/scripts/trade/get_crypto_cash_flow.py \
    --start 2026-01-01 --end 2026-04-29 \
    --security-firm FUTUINC --acc-id 12345
```

- Crypto cash flow requires `--start` + `--end` (queried by `create_time` range); `clearing_date` is not accepted
- Response adds `create_time`; `settlement_date` is always `N/A`

#### Query Crypto Max Tradable Quantity

```bash
python skills/moomooapi/scripts/trade/get_crypto_max_trd_qtys.py \
    --code CC.BTCUSD --price 72873.22 \
    --security-firm FUTUINC --acc-id 12345 [--json]
```

- **Cash account only**: crypto does not support margin financing. Response only contains `max_cash_buy` and `max_position_sell`; **no** `max_cash_and_margin_buy`
- Quantities are floats (matches the trading pair's decimal precision)
- `code` must be a trading pair (e.g. `CC.BTCUSD`), not a base currency `CC.BTC`
- Real trading only (`TrdEnv.REAL`)

#### Query Crypto Order Fee

```bash
python skills/moomooapi/scripts/trade/get_crypto_order_fee.py 12345678 87654321 \
    --security-firm FUTUINC --acc-id 12345 [--json]
```

- API limits: max 10 calls per 30 seconds; up to 20 `order_id`s per call
- Real trading only (`TrdEnv.REAL`); built on `OpenCryptoTradeContext`
- `security_firm` only supports `FUTUSECURITIES` / `FUTUINC` / `FUTUSG`
- Typical flow: run `get_crypto_orders.py --history --json` first to collect `order_id`s, then pass them into this script for fee details

### Crypto Ordering Rules

1. **Live confirmation**: always use AskUserQuestion to get explicit user confirmation before submitting
2. **Broker detection**: map user's region/account to `security_firm`:
   - HK / FUTUHK → `FUTUSECURITIES`
   - US / moomoo US → `FUTUINC`
   - SG / moomoo SG → `FUTUSG`
3. **Account detection**: when `acc_id` is unknown, run `get_crypto_accounts.py --json` first
4. **Forbidden operations**: do not call `modify_order` with `NORMAL`/`DISABLE`/`ENABLE`/`DELETE` on crypto orders; only `CANCEL` is available
5. **Paper trading request**: if the user asks for crypto paper trading, clearly state "crypto does not support paper trading — live only" and ask whether to proceed

---

---

**Related skills routing:** Related: market data → quote-commands.md; requires SDK>=10.5.6508; crypto is live-only (no paper trading).
