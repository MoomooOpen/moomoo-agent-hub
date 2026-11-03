# OpenD / moomooapi migration: gaps and REST API backlog

After removing `skills/moomoo-api-skills/` (`moomooapi`, `install-moomoo-opend`), this document lists **missing capabilities** and **REST APIs for CLI/API teams**. Quote and trade flows use existing `moomoo-*` skills + `moomoo` CLI.

Upgrade path: [upgrade-from-opend.md](./upgrade-from-opend.md).

---

## 1. Removed packages

| Former skill | Contents |
|--------------|----------|
| `install-moomoo-opend` | OpenD installer + `moomoo-api` Python SDK |
| `moomooapi` | ~64 Python scripts (quote / trade / subscribe) via OpenD |

---

## 2. Missing or out-of-scope after migration

### P0 — Three anomaly APIs (blocking)

| Former SDK method | Skill |
|-------------------|--------|
| `get_technical_unusual` | `moomoo-unusual-technical-signal-alerts`（Technical Signal Alerts） |
| `get_financial_unusual` | `moomoo-unusual-capital-flows`（Unusual Capital Flows） |
| `get_derivative_unusual` | `moomoo-unusual-derivatives-activity`（Unusual Derivatives Activity） |

Invoked via **`moomoo unusual *`** (`anomaly` alias) — implemented in moomoo-cli (same as futu-cli); gateway/`api_base`联调待验。

### P1 — Subscribe / push (WSS) — handled in Hub

Former `moomooapi/scripts/subscribe/*`. **Open API WSS** replaces OpenD TCP push. Hub: [websocket-quote-push.md](./websocket-quote-push.md), [upgrade-from-opend.md](./upgrade-from-opend.md) §5, **`moomoo-quote`** → `references/websocket-push.md`. Endpoint `wss://webapi-quote.moomoo.com/ws`; broker queue via **`BROKER_QUEUE`**. No `moomoo subscribe` CLI subcommand (integrators run their own WSS client; OAuth same as `moomoo auth login`). Details: [Futu hub §2.2](../futu-agent-hub/docs/migration-gaps-and-rest-api.md).

### P2 — Optional parity (see Futu hub doc for script list)

Order fee, margin ratio, account cash flow, crypto cash flow, broker queue (WSS), warrant/option (CLI), watchlist (CLI), OpenD-only state probes. **Not planned:** price reminders, history K-line **quota** (distinct from `history-kline` data API).

Core quote + live/sim/crypto trade: covered by `moomoo` CLI and four quote/trade skills.

---

## 3. REST APIs to add

OAuth CLI calls these paths on the configured `api_base`. `symbol` is a path parameter; the JSON body does not include `stock_symbol`.

| Priority | HTTP | CLI |
|----------|------|-----|
| P0 | `POST /api/v1.0/quote/{symbol}/unusual/technical` | `moomoo unusual technical-signals <symbol> ...` |
| P0 | `POST /api/v1.0/quote/{symbol}/unusual/capital` | `moomoo unusual capital-flows <symbol> ...` |
| P0 | `POST /api/v1.0/quote/{symbol}/unusual/derivatives` | `moomoo unusual derivatives-activity <symbol> ...` |

Rate limit (OpenD): 30 req / 30 s per proto 3801–3803.

| P1 | WSS quote push + `BROKER_QUEUE` | **Hub done** — §2 P1 above + [websocket-quote-push.md](./websocket-quote-push.md) |
| P2 | Open API implemented | CLI/Skill row-level status: [Futu hub §2.3 / §3 P2](../futu-agent-hub/docs/migration-gaps-and-rest-api.md) (`moomoo-trading` documents fees, margin-ratio, cash-logs) |

Parameter enums (`language_id`, `analysis_dimensions`, `indicator_filters`) must match each anomaly SKILL.md.

Full detail (Chinese): [futu-agent-hub/docs/migration-gaps-and-rest-api.md](../futu-agent-hub/docs/migration-gaps-and-rest-api.md) §3 (OpenD file refs, request/response JSON).
