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
| `get_technical_unusual` | `moomoo-technical-anomaly` |
| `get_financial_unusual` | `moomoo-capital-anomaly` |
| `get_derivative_unusual` | `moomoo-derivatives-anomaly` |

Invoked via **`moomoo anomaly *`** — implemented in moomoo-cli (same as futu-cli); gateway/`api_base`联调待验。

### P1 — Subscribe / push (optional; WebSocket)

Former `moomooapi/scripts/subscribe/*`. Hub does not use OpenD TCP push. If product keeps push: **REST for subscribe/unsubscribe + WebSocket for stream** (same pattern as futu hub doc).

### P2 — Optional parity (see Futu hub doc for script list)

Order fee, margin ratio, account cash flow, crypto cash flow, history K-line quota, broker queue, single warrant quote, option resolve, price reminders, watchlist group CRUD, OpenD-only state probes.

Core quote + live/sim/crypto trade: covered by `moomoo` CLI and four quote/trade skills.

---

## 3. REST APIs to add

Same **SkillWrap** contract as Futu (from FutuOpenD): OpenD posts JSON to **`https://api.moomoo.com`** (moomoo) with paths below. OAuth CLI should expose the same body/response on moomoo `api_base`.

| Priority | `NN_ProtoCmd` | OpenAPI Pb | OpenD HTTP (POST) | CLI |
|----------|---------------|------------|-------------------|-----|
| P0 | **无**（OpenD 未注册） | **3801** `SkillWrap_TechnicalUnusual` | `/api/v1/get_technical_unusual` | `moomoo anomaly technical <symbol> ...` |
| P0 | **无** | **3802** `SkillWrap_FinancialUnusual` | `/api/v1/get_financial_unusual` | `moomoo anomaly capital <symbol> ...` |
| P0 | **无** | **3803** `SkillWrap_DerivativeUnusual` | `/api/v1/get_derivative_unusual` | `moomoo anomaly derivatives <symbol> ...` |

Rate limit (OpenD): 30 req / 30 s per proto 3801–3803.

| P1 | REST subscriptions + **WebSocket** quote stream | TBD |
| P2 | Order fees, margin ratio, cash logs | `moomoo order fees`, `moomoo margin-ratio`, `moomoo account cash-logs` |

Parameter enums (`language_id`, `analysis_dimensions`, `indicator_filters`) must match each anomaly SKILL.md.

Full detail (Chinese): [futu-agent-hub/docs/migration-gaps-and-rest-api.md](../futu-agent-hub/docs/migration-gaps-and-rest-api.md) §3 (OpenD file refs, request/response JSON).
