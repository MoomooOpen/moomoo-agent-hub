
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
  <a href="#-quick-start">Quick Start</a> · <a href="#-skills-overview">Skills Overview</a> · <a href="#-quote--trade-skills">Quote & Trade Skills</a> · <a href="#-technical-analysis-skills">Technical Analysis Skills</a> · <a href="#-search--content-skills">Search & Content Skills</a> · <a href="#-quantitative-strategy">Quantitative Strategy</a> · <a href="#-architecture">Architecture</a>
</p>


---

## What is Moomoo Agent Hub?

Moomoo Agent Hub is the official AI Agent skill set by **moomoo**. Skills are installed and updated with `npx skills`, packaging the Moomoo OpenAPI plus financial-content services into standardized Skills.

It enables AI assistants to interact with real-time market data, execute trades, retrieve financial news, run anomaly detection, and gauge market sentiment — all through natural language.

Works with **Claude Code**, **Cursor**, **Claude Desktop**, **VS Code**, **JetBrains** and other MCP-compatible AI tools.

---

## Skills Overview

Moomoo Agent Hub ships **11 Skills** in four groups: quote and trade, content analysis, technical analysis, and quantitative strategy. The quantitative skill in this repo is the grid strategy `moomoo-grid-strategy`. **No OpenD** is required.

| Category | Skill | Description | Requires |
|----------|-------|-------------|----------|
| **Quote / Trade** | `moomoo-quote` | Quotes for stocks, options, futures, and crypto. Does not place orders | `moomoo` CLI |
| **Quote / Trade** | `moomoo-trading` | The user's selected live stock account, funds, positions, orders, and fills | `moomoo` CLI |
| **Quote / Trade** | `moomoo-sim-trading` | The user's selected paper account via `moomoo sim` | `moomoo` CLI |
| **Quote / Trade** | `moomoo-crypto` | Crypto account, balance, orders, and fills. Quotes stay on `moomoo-quote` | `moomoo` CLI |
| **Technical analysis** | `moomoo-unusual-technical-signal-alerts` | K-line and indicator alerts — `moomoo unusual technical-signals` | `moomoo` CLI |
| **Technical analysis** | `moomoo-unusual-capital-flows` | Fund distribution, flow, brokers, and short sell — `moomoo unusual capital-flows` | `moomoo` CLI |
| **Technical analysis** | `moomoo-unusual-derivatives-activity` | Options and warrant alerts — `moomoo unusual derivatives-activity` | `moomoo` CLI |
| **Content analysis** | `moomoo-news-search` | News, notices, and research | `curl` |
| **Content analysis** | `moomoo-stock-digest` | Stock briefing with source time and links | `curl` |
| **Content analysis** | `moomoo-comment-sentiment` | Community sentiment with window and sample size | `curl` |
| **Quantitative strategy** | `moomoo-grid-strategy` | Single-symbol base-price grid. Paper account by default | OpenAPI |

Removed: **`moomooapi` / `install-moomoo-opend`**. See [`docs/upgrade-from-opend.md`](docs/upgrade-from-opend.md) and [`docs/migration-gaps-and-rest-api.md`](docs/migration-gaps-and-rest-api.md). Skills pull REST through the CLI. Continuous push and broker queue have no `moomoo subscribe` command; connect to the Open API WebSocket yourself — [`docs/websocket-quote-push.md`](docs/websocket-quote-push.md).

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

**Technical analysis** uses the same `moomoo` CLI: `moomoo unusual technical-signals`, `capital-flows`, and `derivatives-activity`.

**Quantitative strategy** is `moomoo-grid-strategy`. It writes a grid program from the OpenAPI docs and accepts it on a paper account.

> Quote, trade, and technical analysis need OAuth via `moomoo auth login` and the matching account permission. Content analysis does not. Installing a skill does not grant an account or market-data permission. The CLI is installed once.

### 3. Start using

```
> Show me Tesla's real-time quote
> List my live accounts, then submit a limit buy only after I confirm
> Search the latest news for NVIDIA
> 看看 NVDA 最近有没有异动？
> 帮我写一个 AAPL 的网格策略
```

---

## Quote & Trade Skills

Four skills that call the local [`moomoo` CLI](https://github.com/MoomooOpen/moomoo-cli) for market data and trading. They do not use OpenD.

| Skill | Use for |
|-------|---------|
| `moomoo-quote` | Quotes, K-line, snapshots, order book, capital flow, company data, and screeners for stocks, options, futures, and crypto. A quote includes symbol, price, change, currency, time, and source. Adding or removing a watchlist symbol is a write. Not for placing orders. |
| `moomoo-trading` | The live stock account the user picked. List accounts first and keep that choice. Confirm account, symbol, side, quantity, order type, and price before an order. Return the order id and status. A submit is not a fill. |
| `moomoo-sim-trading` | Paper stock accounts only, via `moomoo sim` with the account the user picked. Do not auto-pick the first account, and do not call live or crypto order commands. |
| `moomoo-crypto` | The crypto account the user picked, balances, `BTCUSD`-style pairs, orders, and fills. Crypto quotes stay on `moomoo-quote`. |

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
List my live stock accounts, then show positions for the one I pick
Check my selected crypto account's BTCUSD buying power
Paper-trade a limit buy for US.AAPL on the paper account I choose
```

---

## Technical Analysis Skills

Three skills for "is anything odd happening with this stock?": **Technical Signal Alerts**, **Unusual Capital Flows**, and **Unusual Derivatives Activity**. A broad request such as "any anomaly in NVDA" calls all three. Separate no-anomaly, no-data, not-applicable, permission-denied, and request-failed results. Signals come from `moomoo unusual`, not from ordinary quote indicators.

| Skill | Triggers on | Signals |
|-------|------------|---------|
| `moomoo-unusual-technical-signal-alerts` | "K-line / MACD / RSI / overbought / golden cross" | Pattern detection across MACD, RSI, KDJ, CCI, K-line shapes |
| `moomoo-unusual-capital-flows` | "capital flow / fund flow / short sell / who's buying" | Fund distribution, broker buy/sell, capital flow trend, short-sell volume and ratio |
| `moomoo-unusual-derivatives-activity` | "options / IV / PCR / warrants" | Implied volatility, put/call ratio, unusual option activity, warrant flow |

**Example prompts:**
```
Are there any anomalies for NVDA today?
看看 TSLA 期权有没有异动
检查一下 AAPL 的技术面
```

---

## Search & Content Skills

Three skills calling public moomoo HTTP endpoints. **No moomoo CLI or trade authorization is required.**

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

Summarizes what happened for the chosen symbols, with the news time and links behind the conclusion. Mark a static sample as an example. Batch input of several symbols is supported.

### `moomoo-comment-sentiment` — Sentiment Gauge

Aggregates community discussion and KOL views into bull/bear share and representative comments. Include the time window, sample size, and source. Say when the sample is too small.

**Example prompts:**
```
Search for the latest news on NVIDIA
帮我解读一下比亚迪最近发生了什么
看看社区对小米的情绪怎么样
```

---

## Quantitative Strategy

The quantitative skill in this repo is `moomoo-grid-strategy`. It guides an agent to write a single-symbol base-price grid program from the OpenAPI docs: check the parameters first, then write a restart-safe limit-order reconciliation loop.

| Item | Detail |
|------|--------|
| Scope | One stock or ETF: `HK.00700`, `US.AAPL`, `SH.600519`, `SZ.000001` |
| Orders | Percentage-spaced day limit orders, replaced across days by the reconciliation loop |
| Environment | Paper account by default. Live pages are used only after the user explicitly asks for live trading in that conversation |
| Out of scope | Options, futures, crypto, multiple symbols, and market orders |

Request fields come from [OpenAPI llms.md](https://open.moomoo.com/zh-cn/llms.txt). Calls go to `webapi.moomoo.com`. The skill does not copy request bodies or read token files.

```bash
npx skills add -y -g MoomooOpen/moomoo-agent-hub --skill moomoo-grid-strategy
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
│  │ Quote/Trade         │ │ Technical  │ │Search/Content │  │
│  │ quote/trading/      │ │ technical/ │ │ news-search   │  │
│  │ crypto/sim          │ │ capital/   │ │ stock-digest  │  │
│  └──────────┬──────────┘ │ derivatives│ │ sentiment     │  │
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

- **Do not store credentials in the repo or the chat** — the CLI keeps the OAuth token locally and attaches the bearer token. The grid skill follows the OpenAPI docs and does not write tokens into code
- **Trade confirmation** — the user confirms account, symbol, side, quantity, and price. The agent does not confirm on the user's behalf
- **A submit is not a fill** — return the order id and the actual status. Query first when the status is unknown
- **Quote/Trade/Technical CLI** — `moomoo-quote`, `moomoo-trading`, `moomoo-crypto`, `moomoo-sim-trading`, and the three `moomoo-unusual-*` skills call the local `moomoo` CLI. They do not read token files
- **Content skills** — public HTTP only. No user credentials are sent
- **Rate limiting** — respects Moomoo OpenAPI's built-in limits

---

## FAQ

**Q: Do I need OpenD for all Skills?**
A: No. **Quote/Trade** and **Technical Analysis** skills use the `moomoo` CLI (OAuth). **Search/Content** skills call public HTTP only. The grid strategy follows the OpenAPI docs. OpenD and `moomooapi` were removed — see [upgrade-from-opend.md](docs/upgrade-from-opend.md).

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
