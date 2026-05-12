# API Limits (Must Consider Before Calling)

These limits must be considered when calling APIs to avoid request failures due to insufficient quota or rate limiting.

## Rate Limits

Rate limit rule: Maximum n calls within 30 seconds; the interval between the 1st and (n+1)th call must exceed 30 seconds.

| API | Rate Limit |
|-----|------------|
| `place_order` | 15/30s |
| `modify_order` | 20/30s |
| `order_list_query` | 10/30s |

**Batch Operation Note**: When making loop calls to rate-limited APIs (e.g., batch orders, batch historical Candlestick requests), you must add appropriate `time.sleep()` intervals in the loop to avoid triggering rate limits.

## Subscription Quota Limits

- Each stock subscribed to one type consumes 1 subscription quota; unsubscribing releases the quota
- Different SubTypes for the same stock are counted separately
- Must wait at least 1 minute after subscribing before unsubscribing
- After unsubscribing, all connections must unsubscribe from the same stock for the quota to be released
- Closing a connection less than 1 minute after subscribing will not release the subscription quota; it will auto-unsubscribe after 1 minute
- Use `query_subscription.py` to check used quota
- HK market requires LV1 or above permissions to subscribe
- US pre-market/after-hours requires `--extended-time`

## Historical Candlestick Quota Limits

- Within the last 30 days, each unique stock's historical Candlestick request consumes 1 quota
- Repeated requests for the same stock within 30 days do not consume additional quota
- Different Candlestick periods for the same stock only consume 1 quota
- **Before calling `request_history_kline`**, check remaining quota via `get_history_kl_quota(get_detail=True)`
- **When batch-fetching Candlesticks for multiple stocks**, check quota first and confirm remaining quota >= number of stocks to request before executing

## Quota Tiers

Subscription quota and historical Candlestick quota are tiered based on user assets and trading activity:

| User Type | Subscription Quota | Historical Candlestick Quota |
|-----------|-------------------|------------------------|
| Account holder | 100 | 100 |
| Total assets >= 10K HKD | 300 | 300 |
| Total assets >= 500K HKD / Monthly trades > 200 / Monthly volume > 2M HKD (any one) | 1000 | 1000 |
| Total assets >= 5M HKD / Monthly trades > 2000 / Monthly volume > 20M HKD (any one) | 2000 | 2000 |

## Other Limits

| API | Limit |
|-----|-------|
| `get_market_snapshot` | Max 400 stocks per call |
| `get_order_book` | num max 10 (crypto supports 1/5/10/20/40) |
| `get_rt_ticker` | num max 1000 |
| `get_cur_kline` | num max 1000 |
| `request_history_kline` | max_count max 1000 per call, use page_req_key for pagination |
| `get_stock_filter` | Max 200 results per call |

## Cryptocurrency Limits

### Connection Restrictions

- `OpenQuoteContext(security_firm=...)` Crypto quotes only work when `security_firm` is `FUTUSECURITIES/FUTUINC/FUTUSG`; `MY/AU/JP/CA` or invalid values raise error
- `OpenCryptoTradeContext(security_firm=...)` only supports `FUTUSECURITIES/FUTUINC/FUTUSG`; other brokers return empty
- Crypto trading **only supports REAL**, SIMULATE not supported
- Crypto does not support margin/financing; `get_margin_ratio` on crypto code raises error

### Subscription & Quota

- Crypto subscription quota is calculated the same way as securities: 1 quota per coin/pair per type
- **Coin (`CC.BTC`) and pair (`CC.BTCUSD`) are different instruments**, each consumes 1 quota
- Different K-line periods for the same instrument consume only 1 quota
- Historical K-line quota is consumed the same way as securities; **multi-broker consumes 1 quota**
- Crypto indices (`CC.BTC`) **do not support order book**; only pairs support order book
- Crypto does not support broker queue (`get_broker_queue` is invalid)
- Total asset threshold covers crypto assets (to be optimized to use max assets across brokers)

### Order Placement Restrictions

| Broker | Limit Order | Market Order | Note |
|--------|-------------|--------------|------|
| FUTUSECURITIES (FUTUHK) | ✅ | ✅ | Other order types raise "unsupported order type" |
| FUTUINC (moomoo US) | ✅ | ✅ | Same as above |
| FUTUSG (moomoo SG) | ✅ | ❌ | Market order raises "unsupported order type" |

- **Fractional quantity**: Crypto `qty` is float, supports decimals like `0.000136`
- **Code must be in the account's whitelist**, otherwise raises: "{security_firm}{acc_type}{acc_id} does not support trading {code}"
- **Session not validated** (crypto trades 24/7)
- **Time in force**: Limit orders fixed to `GTC`, market orders fixed to `IOC` (user cannot override)
- **Modify/disable/enable/delete**: not supported, raises "unsupported order operation, please cancel and resubmit if modification is needed"; only `ModifyOrderOp.CANCEL` and `cancel_all_order` are supported
- **Margin accounts cannot trade crypto**; `acctradinginfo_query` cannot query crypto max buy/sell from margin accounts

### Cash Flow Restrictions

- Crypto `get_acc_cash_flow` requires `start` + `end`, queries by creation time (`create_time`) over range
- Securities/futures accounts require `clearing_date`, queries by clearing date (single day)
- Parameter mismatch raises: "{account} only supports querying cash flow by {parameter}"

### Market State

| Mapping | Enum | EST Time |
|---------|------|---------|
| Settlement (pre-open) | `NONE` | EST 19:00:00 |
| Trading (morning) | `MORNING` | EST 19:00:01 – 18:59:58 |
| Closed | `CLOSED` | EST 18:59:59 |
