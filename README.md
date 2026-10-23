
<h1 align="center">Moomoo Agent Hub</h1>
<p align="center">
  <b>Connect AI agents to Moomoo — trade, query market data, detect anomalies, and surface news / sentiment through natural language.</b>
</p>

<p align="center">
  <a href="https://openapi.moomoo.com/moomoo-api-doc/"><img src="https://img.shields.io/badge/Moomoo_API-Docs-blue?style=flat-square" alt="Moomoo API Docs" /></a>
  <a href="#license"><img src="https://img.shields.io/badge/License-MIT-yellow?style=flat-square" alt="License" /></a>
  <a href="https://modelcontextprotocol.io/"><img src="https://img.shields.io/badge/MCP-Compatible-purple?style=flat-square" alt="MCP Compatible" /></a>
</p>

<p align="center">
  <a href="#-quick-start">Quick Start</a> · <a href="#-skills-overview">Skills Overview</a> · <a href="#-quote--trade-skills">Quote & Trade Skills</a> · <a href="#-anomaly-skills">Anomaly Skills</a> · <a href="#-search--content-skills">Search & Content Skills</a> · <a href="#-architecture">Architecture</a>
</p>


---

## What is Moomoo Agent Hub?

Moomoo Agent Hub is the official AI Agent skill set by **moomoo**. Skills are installed and updated with `npx skills`, packaging the Moomoo OpenAPI plus financial-content services into standardized Skills.

It enables AI assistants to interact with real-time market data, execute trades, retrieve financial news, run anomaly detection, and gauge market sentiment — all through natural language.

Works with **Claude Code**, **Cursor**, **Claude Desktop**, **VS Code**, **JetBrains** and other MCP-compatible AI tools.

---

## Skills Overview

Moomoo Agent Hub ships **10 production-ready Skills** (quote/trade, anomaly, content). **No OpenD** required.

| Category | Skill | Description | Requires |
|----------|-------|-------------|----------|
| **Quote / Trade** | `moomoo-quote` | Market data via the `moomoo` CLI | `moomoo` CLI |
| **Quote / Trade** | `moomoo-trading` | Real securities accounts, funds, positions, orders, and fills | `moomoo` CLI |
| **Quote / Trade** | `moomoo-crypto` | Cryptocurrency accounts, balances, orders, and fills | `moomoo` CLI |
| **Quote / Trade** | `moomoo-sim-trading` | Simulated / paper accounts, positions, and orders | `moomoo` CLI |
| **Anomaly** | `moomoo-capital-anomaly` | `moomoo anomaly capital` — capital-flow signals | `moomoo` CLI |
| **Anomaly** | `moomoo-derivatives-anomaly` | `moomoo anomaly derivatives` — options / warrants | `moomoo` CLI |
| **Anomaly** | `moomoo-technical-anomaly` | `moomoo anomaly technical` — technical signals | `moomoo` CLI |
| **Search / Content** | `moomoo-news-search` | News, notices, research search | `curl` |
| **Search / Content** | `moomoo-stock-digest` | Single-stock news digest | `curl` |
| **Search / Content** | `moomoo-comment-sentiment` | Community sentiment | `curl` |

Removed: **`moomooapi` / `install-moomoo-opend`**. See [`docs/upgrade-from-opend.md`](docs/upgrade-from-opend.md) and [`docs/migration-gaps-and-rest-api.md`](docs/migration-gaps-and-rest-api.md).

---

## Quick Start

### 1. Install a skill

Node.js 18+ is required. Pick the skill from [Skills Overview](#skills-overview):

```bash
npx skills add -y -g MoomooOpen/moomoo-agent-hub --skill <slug>
npx skills update <slug> -g -y
```

**Flag meanings:** `-y` bypasses interactive prompts; `-g` installs globally for all projects. Remove `-y` to choose specific skills interactively, or omit `-g` to install only in the current project. Omit `--skill` to install every skill in the repo.

`npx skills add` auto-detects Claude Code, Cursor, VS Code, JetBrains, or OpenClaw, and writes to the correct skills directory.

`npx skills update` refreshes the current slug and leaves a renamed directory in place. If an older short name is still installed (`news-search`, `stock-digest`, `comment-sentiment`, `install-opend`, `capital-anomaly`, `derivatives-anomaly`, `technical-anomaly`), remove it once, then install again:

```bash
bash scripts/migrate-renamed-skills.sh
npx skills add -y -g MoomooOpen/moomoo-agent-hub
```

### 2. Runtime dependencies

**`moomoo` CLI** — required by the Quote/Trade skills. The skill itself tells the assistant how to install the CLI. `npx` only installs the skill files.

```bash
npx skills add -y -g MoomooOpen/moomoo-agent-hub --skill moomoo-quote
npx skills update moomoo-quote -g -y
```

Use the same commands for `moomoo-trading`, `moomoo-crypto`, and `moomoo-sim-trading`. When `moomoo` is missing, the assistant asks, then runs the [official moomoo-cli installer](https://github.com/MoomooOpen/moomoo-cli/blob/main/README.md). An existing CLI is updated with `moomoo update`.

**Anomaly skills** — same `moomoo` CLI as quote/trade; use `moomoo anomaly` subcommands when released (see [migration-gaps-and-rest-api.md](docs/migration-gaps-and-rest-api.md)).

> Quote/trade/anomaly need OAuth via `moomoo auth login` and app permissions where applicable.

### 3. Start using

```
> Show me Tesla's real-time quote
> Place a limit buy for 100 shares of TSLA at $250
> Search the latest news for NVIDIA
> 看看 NVDA 最近有没有异动？
> 帮我解读一下比亚迪最近发生了什么
```

---

## Quote & Trade Skills

Four skills that call the local [`moomoo` CLI](https://github.com/MoomooOpen/moomoo-cli) for market data and trading. They do not use OpenD.

| Skill | Use for |
|-------|---------|
| `moomoo-quote` | Quotes, K-line, snapshots, order book, capital flow, company data, and screeners. Not for placing orders. |
| `moomoo-trading` | Real securities accounts, funds, positions, orders, and fills. |
| `moomoo-crypto` | Cryptocurrency exchange accounts, balances, orders, and fills. |
| `moomoo-sim-trading` | Simulated or paper trading only. A plain "buy" or "sell" does not select this skill. |

Each skill declares `requires.bins: [moomoo]` and includes the install steps. Add or update a skill with npx:

```bash
npx skills add -y -g MoomooOpen/moomoo-agent-hub --skill moomoo-quote
npx skills update moomoo-quote -g -y
```

If `moomoo` is missing, the skill asks before installing it:

```bash
# macOS / Linux
curl -fsSL https://raw.githubusercontent.com/MoomooOpen/moomoo-cli/main/scripts/install.sh | sh
```

```powershell
# Windows PowerShell
iwr -UseBasicParsing https://raw.githubusercontent.com/MoomooOpen/moomoo-cli/main/scripts/install.ps1 -OutFile install.ps1
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

The binary is installed to `~/.moomoo/bin/moomoo` on macOS and Linux, and to `%LOCALAPPDATA%\MoomooCLI\bin\moomoo.exe` on Windows. Update an existing CLI with `moomoo update`.

**Example prompts:**
```
Show me the order book for HK.00700
Buy 100 shares of US.AAPL at 250 on my real account
Check my BTCUSD crypto balance
Paper-trade a limit buy for US.AAPL
```

---

## Anomaly Skills

Three skills for "is anything odd happening with this stock?" detection via **`moomoo anomaly`** CLI (requires CLI/API release — see [migration-gaps-and-rest-api.md](docs/migration-gaps-and-rest-api.md)).

| Skill | Triggers on | Signals |
|-------|------------|---------|
| `moomoo-capital-anomaly` | "capital flow / fund flow / short sell / who's buying" | Fund distribution, broker buy/sell, capital flow trend, short-sell volume & ratio |
| `moomoo-derivatives-anomaly` | "options / IV / PCR / warrants" | Implied volatility, put/call ratio, unusual option activity, warrant flow |
| `moomoo-technical-anomaly` | "K-line / MACD / RSI / overbought / golden cross" | Pattern detection across MACD, RSI, KDJ, CCI, K-line shapes |

**Example prompts:**
```
Are there any anomalies for NVDA today?
看看 TSLA 期权有没有异动
检查一下 AAPL 的技术面
```

---

## Search & Content Skills

Three skills calling public moomoo HTTP endpoints — **no moomoo CLI required**.

### `moomoo-news-search` — News Search

| Feature | Detail |
|---------|--------|
| Endpoint | `GET /news_search` via `ai-news-search.moomoo.com` |
| Auth | Public — no API key required |
| Languages | Simplified Chinese (`zh-CN`), Traditional Chinese (`zh-HK`), English (`en`) |
| Content types | News, Notices/Announcements, Research Reports |
| Sort | By PV, By Time, By Heat |
| Max results | 50 per request |

### `moomoo-stock-digest` — Stock Briefing

Continuously delivers the latest factual updates and core analysis for a given stock — what happened, why it matters, what's worth watching. Batch-input multiple symbols supported.

### `moomoo-comment-sentiment` — Sentiment Gauge

Aggregates community discussion + KOL views into a standardized sentiment score, so you can read the room before deciding.

**Example prompts:**
```
Search for the latest news on NVIDIA
帮我解读一下比亚迪最近发生了什么
看看社区对小米的情绪怎么样
```

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                       AI Assistant                                │
│   (Claude Code / Cursor / Claude Desktop / VS Code / JB)         │
└────────────────────────────┬─────────────────────────────────────┘
                             │ Skill protocol (SKILL.md)
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                    Moomoo Agent Hub                               │
│                                                                   │
│   npx skills add / npx skills update                              │
│                                                                   │
│  ┌─────────────────────┐ ┌────────────┐ ┌───────────────┐  │
│  │ Quote/Trade         │ │  Anomaly   │ │Search/Content │  │
│  │ quote/trading/      │ │ capital /  │ │ news-search   │  │
│  │ crypto/sim          │ │ derivatives│ │ stock-digest  │  │
│  └──────────┬──────────┘ │ / technical│ │ sentiment     │  │
│             │            └─────┬──────┘ └──────┬────────┘  │
└─────────────┼──────────────────┼───────────────┼───────────┘
              ▼                  ▼               ▼
       ┌─────────────┐                    ┌─────────────────┐
       │ moomoo CLI  │                    │  Public HTTP    │
       │ OAuth+REST  │                    │ ai-news-search  │
       └──────┬──────┘                    │  .moomoo.com    │
              ▼                           └─────────────────┘
       ┌────────────────────────────────────────┐
       │   Moomoo Servers (HK/US/CN/SG/JP)      │
       └────────────────────────────────────────┘
```

Each skill under `skills/` is self-contained. `SKILL.md` frontmatter holds `metadata.version` and `requires`. Install and update commands live in the skill.

---

## Security

- **Credentials via env vars only** — never hardcoded
- **Trade confirmation** — write operations require explicit user confirmation
- **CLI OAuth** — Token stays local; skills do not read token file contents
- **Quote/Trade CLI** — `moomoo-quote`, `moomoo-trading`, `moomoo-crypto`, and `moomoo-sim-trading` call the local `moomoo` CLI. The CLI attaches OAuth credentials; skills do not read token files
- **Read-only mode** — restrict to market data queries by omitting trade credentials
- **Rate limiting** — respects Moomoo OpenAPI's built-in limits
- **Content & Anomaly endpoints** — public HTTP, no user credentials transmitted; reference data only

---

## FAQ

**Q: Do I need OpenD for all Skills?**
A: No. **Quote/Trade** and **Anomaly** skills use the `moomoo` CLI (OAuth). **Search/Content** skills call public HTTP only. OpenD and `moomooapi` were removed — see [upgrade-from-opend.md](docs/upgrade-from-opend.md).

**Q: When is the `moomoo` CLI downloaded?**
A: When a Quote/Trade skill is in use and `moomoo` is missing. The skill asks first, then runs the official installer. `npx skills add` and `npx skills update` only install or update the skill files.

**Q: How do I update a skill?**
A: `npx skills update <slug> -g -y`. Each skill lists this command under "Update this skill" or "Install the moomoo CLI".

**Q: Is there any additional fee?**
A: No. Trading through Moomoo OpenAPI incurs no fees beyond standard brokerage commissions.

**Q: Which programming languages does the underlying SDK support?**
A: Python, Java, C#, C++, JavaScript. The Skills sit above the SDK and are language-agnostic — install and use with your AI assistant.

---

## Disclaimer

This project is for informational and educational purposes. All trading operations are at the user's own risk. AI-generated analysis does not constitute investment advice. Please fully understand the risks before using trading features. Moomoo Agent Hub is not responsible for any financial losses.

---

## License

[MIT](LICENSE)

---

<p align="center">
  Built by <a href="https://www.moomoo.com/">moomoo</a> · Powered by <a href="https://openapi.moomoo.com/">Moomoo OpenAPI</a>
</p>
