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

Invoked via **`moomoo anomaly *`** once CLI/REST is shipped.

### P1 — Subscribe / push (not migrated)

Former `moomooapi/scripts/subscribe/*`. Not offered by Skill Hub in this release.

### P2 — Optional parity (see Futu hub doc for script list)

Order fee, margin ratio, account cash flow, crypto cash flow, history K-line quota, broker queue, single warrant quote, option resolve, price reminders, watchlist group CRUD, OpenD-only state probes.

Core quote + live/sim/crypto trade: covered by `moomoo` CLI and four quote/trade skills.

---

## 3. REST APIs to add

Same contract as Futu (paths finalized by API team); use moomoo `api_base` and `moomoo` CLI subcommands:

| Priority | REST (suggested) | CLI (suggested) |
|----------|------------------|-----------------|
| P0 | `/api/v1.0/quote/unusual/technical` | `moomoo anomaly technical <symbol> ...` |
| P0 | `/api/v1.0/quote/unusual/capital` | `moomoo anomaly capital <symbol> ...` |
| P0 | `/api/v1.0/quote/unusual/derivatives` | `moomoo anomaly derivatives <symbol> ...` |
| P1 | Subscription + stream endpoints | TBD |
| P2 | Fee, cash flow, margin, etc. | TBD |

Parameter enums (`language_id`, `analysis_dimensions`, `indicator_filters`) must match each anomaly SKILL.md.

Full detail (Chinese): see FutunnOpen/futu-agent-hub `docs/migration-gaps-and-rest-api.md` (same REST contract, `futu` vs `moomoo` CLI prefix).
