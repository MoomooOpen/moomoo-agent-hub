# Upgrade from OpenD / moomooapi to CLI skills

If you previously used **`moomooapi`** or **`install-moomoo-opend`**, migrate as follows. New installs do **not** need OpenD or the `moomoo-api` Python SDK.

## 1. Clean old skill directories

```bash
bash scripts/migrate-renamed-skills.sh
```

Removes `moomooapi`, `install-moomoo-opend`, and legacy short names.

## 2. Reinstall hub skills

```bash
npx skills add -y -g MoomooOpen/moomoo-agent-hub
npx skills update -g
```

## 3. Install moomoo CLI (once)

See [moomoo-install.md](./moomoo-install.md) and quote/trade skills.

```bash
moomoo version
moomoo auth login
moomoo auth status --format json
moomoo check
```

## 4. Skill mapping

| Old use | New skill |
|---------|-----------|
| Market data | `moomoo-quote` |
| Live trading | `moomoo-trading` |
| Paper trading | `moomoo-sim-trading` |
| Crypto | `moomoo-crypto` |
| Anomalies | `moomoo-*-anomaly` via `moomoo anomaly` (see [migration-gaps-and-rest-api.md](./migration-gaps-and-rest-api.md)) |
| Monolithic moomooapi | **Removed** |

## 5. Former OpenD subscribe / push / broker queue

| Former moomooapi | Now |
|------------------|-----|
| `subscribe/*`, `push_*` | **WebSocket** quote push: auth → `subscribe` (`quote`, `order_book`, `ticker`, `kline`) |
| `get_broker_queue`, `push_broker` | Same WebSocket; message type **`BROKER_QUEUE`** (often with `order_book` on eligible HK symbols) |

Step-by-step: [websocket-quote-push.md](./websocket-quote-push.md). Other gaps: [migration-gaps-and-rest-api.md](./migration-gaps-and-rest-api.md).
