<!-- TOC: Subscribe / Push -->
# Subscribe / Push

Subscribe/unsubscribe/query, quote/Candlestick/order book/ticker/RT data push. Prediction market subscribe/push see `prediction-market.md`.

## Subscription Management Commands

### Subscribe to Market Data
When the user needs to subscribe to real-time data:
```bash
python skills/moomooapi/scripts/subscribe/subscribe.py HK.00700 --types QUOTE ORDER_BOOK [--json]
```
- `--types`: Subscription type list (required)
- `--no-first-push`: Do not immediately push cached data
- `--push`: Enable push callbacks
- `--extended-time`: US pre-market and after-hours data
- `--session`: US stock trading session, options: NONE/RTH/ETH/ALL (only for US Candlestick/intraday/tick-by-tick, OVERNIGHT not supported)

**Available subscription types**: QUOTE, ORDER_BOOK, ORDER_BOOK_ODD, TICKER, RT_DATA, BROKER, K_1M, K_5M, K_15M, K_30M, K_60M, K_DAY, K_WEEK, K_MON

> `ORDER_BOOK_ODD` is the odd lot order book subscription type, only supported for MY/SG markets.

### Unsubscribe
```bash
# Unsubscribe specific types
python skills/moomooapi/scripts/subscribe/unsubscribe.py HK.00700 --types QUOTE ORDER_BOOK [--json]

# Unsubscribe all
python skills/moomooapi/scripts/subscribe/unsubscribe.py --all [--json]
```
- **Note**: Must wait at least 1 minute after subscribing before unsubscribing

### Query Subscription Status
When the user asks about "current subscriptions" or "subscription status":
```bash
python skills/moomooapi/scripts/subscribe/query_subscription.py [--current] [--json]
```
- `--current`: Only query the current connection (default queries all connections)

---

## Push Reception Commands

### Receive Quote Pushes
When the user needs real-time quote pushes:
```bash
python skills/moomooapi/scripts/subscribe/push_quote.py HK.00700 US.AAPL --duration 60 [--json]
```
- `--duration`: Duration to receive pushes (seconds, default 60)
- Press Ctrl+C to stop early

### Receive Candlestick Pushes
When the user needs real-time Candlestick pushes:
```bash
python skills/moomooapi/scripts/subscribe/push_kline.py HK.00700 --ktype K_1M --duration 300 [--json]
```
- `--ktype`: K_1M, K_5M, K_15M, K_30M, K_60M, K_DAY, K_WEEK, K_MON (default: K_1M)
- `--duration`: Duration to receive pushes (seconds, default 300)
- `--session`: US stock trading session, options: NONE/RTH/ETH/ALL (US only, OVERNIGHT not supported)

---

---

**Related skills routing:** Related: prediction market subscribe/push → prediction-market.md; subscription quota → docs/API_LIMITS.md.
