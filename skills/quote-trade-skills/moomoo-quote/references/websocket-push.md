# Real-time quote push (WebSocket)

The `moomoo` CLI is for **REST** market data. It does not replace OpenD subscribe or removed `moomooapi/scripts/subscribe/*`.

For streaming quote, order book, ticker, K-line, and **broker queue**, use **MOOMOO Open API Quote Push WebSocket**:

- `wss://webapi-quote.moomoo.com/ws`
- connect → **auth** (OAuth Bearer, same family as `moomoo auth login`) → **subscribe** → handle messages by `type`
- Subscribe fields map to push `type` values: `quote` → `QUOTE`, `order_book` → `ORDER_BOOK`, `ticker` → `TICKER`, `kline` → `KLINE`
- Broker queue: **`BROKER_QUEUE`** (typically with `order_book` on eligible HK symbols; not a separate subscribe field)

Hub guide: [`docs/websocket-quote-push.md`](../../../../docs/websocket-quote-push.md).

Official: [Overview](https://open.moomoo.com/api/quote/push/overview) · [Authentication](https://open.moomoo.com/api/quote/push/auth) · [Subscribe](https://open.moomoo.com/api/quote/push/subscribe) · [Data format](https://open.moomoo.com/api/quote/push/data-format) · [Keep-alive](https://open.moomoo.com/api/quote/push/heartbeat).

Do not fall back to OpenD or Python SDK for live push.
