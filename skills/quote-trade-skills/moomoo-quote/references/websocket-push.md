# Real-time quote push (WebSocket)

The `moomoo` CLI is for **REST** market data. It does not replace OpenD subscribe or removed `moomooapi/scripts/subscribe/*`.

For streaming quote, order book, ticker, K-line, and **broker queue**, use **MOOMOO Open API Quote Push WebSocket**:

- `wss://webapi-quote.moomoo.com/ws`
- connect → **auth** (OAuth Bearer, same family as `moomoo auth login`) → **subscribe** → handle messages by `type`
- Broker queue: **`BROKER_QUEUE`** (typically with `order_book` on eligible HK symbols)

Hub guide: [`docs/websocket-quote-push.md`](../../../../docs/websocket-quote-push.md).

Official: [Overview](https://open.moomoo.com/api/quote/push/overview) · [Subscribe](https://open.moomoo.com/api/quote/push/subscribe) · [Data format](https://open.moomoo.com/api/quote/push/data-format).

Do not fall back to OpenD or Python SDK for live push.
