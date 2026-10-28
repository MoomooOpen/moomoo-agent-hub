# Real-time quote push and broker queue (WebSocket)

After removing OpenD / `moomooapi`, do **not** use local TCP subscribe or removed `moomooapi/scripts/subscribe/*`. Use **MOOMOO Open API Quote Push WebSocket** instead.

Official docs:

- [Overview](https://open.moomoo.com/api/quote/push/overview)
- [Authentication](https://open.moomoo.com/api/quote/push/auth)
- [Subscribe / unsubscribe](https://open.moomoo.com/api/quote/push/subscribe)
- [Data format](https://open.moomoo.com/api/quote/push/data-format)
- [Keep-alive](https://open.moomoo.com/api/quote/push/heartbeat)

Futu-branded accounts use the same protocol on `wss://webapi-quote.futunn.com/ws`; see the [Futu hub guide](../futu-agent-hub/docs/websocket-quote-push.md) (Chinese) for parallel examples.

---

## Endpoint

```
wss://webapi-quote.moomoo.com/ws
```

**`moomoo-quote` / Agents use the `moomoo` CLI for REST.** For streaming, implement a WebSocket client in your app or service.

---

## Flow

1. Connect to the WSS URL.
2. **Authenticate first** (OAuth Bearer from `moomoo auth login` is recommended).
3. Send **`subscribe`** JSON with symbol lists per data type.
4. Dispatch incoming messages by top-level **`type`**.
5. Keep the connection alive with **WebSocket ping/pong**; refresh tokens and **re-auth + re-subscribe** after reconnect.

### Auth example

```json
{
  "action": "auth",
  "data": {
    "auth_type": "oauth2",
    "authorization": "Bearer {access_token}"
  }
}
```

---

## Subscribe → push types

| Request field | Push `type` | Former moomooapi (approx.) |
|---------------|-------------|----------------------------|
| `quote` | `QUOTE` | `push_quote` |
| `order_book` | `ORDER_BOOK` | `push_orderbook` |
| `ticker` | `TICKER` | `push_ticker` |
| `kline` | `KLINE` | `push_kline` |

Symbols: **`MARKET.CODE`** (e.g. `HK.00700`, `US.AAPL`).

```json
{
  "id": "sub-001",
  "action": "subscribe",
  "quote": ["HK.00700"],
  "order_book": ["HK.00700"],
  "ticker": ["US.AAPL"]
}
```

---

## Broker queue (former `get_broker_queue` / `push_broker`)

- Push message type: **`BROKER_QUEUE`** (not a separate subscribe field).
- Often sent when **`order_book`** is subscribed for eligible **Hong Kong** symbols; depends on market, category, and permissions.
- Parse `bid_brokers` / `ask_brokers` under `data` — see [data format](https://open.moomoo.com/api/quote/push/data-format).

**Note:** `moomoo broker <symbol>` is REST top-broker holdings, not the same as live **order-book broker queue** on WebSocket.

---

## Skill Hub

| Need | Use |
|------|-----|
| Ad-hoc quotes, K-lines, snapshots | **`moomoo-quote`** + CLI |
| Streaming quotes, book, ticker, broker queue | **WebSocket** (this doc + Open API) |

See also [upgrade-from-opend.md](./upgrade-from-opend.md) and [migration-gaps-and-rest-api.md](./migration-gaps-and-rest-api.md).
