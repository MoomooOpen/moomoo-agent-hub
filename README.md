
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
  <a href="#-quick-start">Quick Start</a> · <a href="#-skills-overview">Skills Overview</a> · <a href="#-moomoo-api-skills">Moomoo API Skills</a> · <a href="#-anomaly-skills">Anomaly Skills</a> · <a href="#-search--content-skills">Search & Content Skills</a> · <a href="#-architecture">Architecture</a>
</p>


---

## What is Moomoo Agent Hub?

Moomoo Agent Hub is the official AI Agent **SkillHub** by **moomoo**. It is a distributable, self-upgrading skill registry that AI clients can auto-discover, packaging the full power of the Moomoo OpenAPI plus financial-content services into standardized Skills.

It enables AI assistants to interact with real-time market data, execute trades, retrieve financial news, run anomaly detection, and gauge market sentiment — all through natural language.

Works with **Claude Code**, **Cursor**, **Claude Desktop**, **VS Code**, **JetBrains** and other MCP-compatible AI tools.

---

## Skills Overview

Moomoo Agent Hub ships **8 production-ready Skills** across **3 categories**:

| Category | Skill | Description | OpenD Required |
|----------|-------|-------------|----------------|
| **Moomoo API** | `moomooapi` | Full Moomoo OpenAPI — quotes, K-lines, order placement, positions, account management | ✅ |
| **Moomoo API** | `install-moomoo-opend` | One-shot installer for Moomoo OpenD + Python SDK | — |
| **Anomaly** | `moomoo-capital-anomaly` | Capital-flow anomalies — fund distribution, broker activity, short-sell signals | ✅ |
| **Anomaly** | `moomoo-derivatives-anomaly` | Derivatives anomalies — option IV / PCR / unusual activity / warrants | ✅ |
| **Anomaly** | `moomoo-technical-anomaly` | Technical anomalies — K-line patterns, MACD / RSI / KDJ, golden/death cross | ✅ |
| **Search / Content** | `moomoo-news-search` | Search news, notices, research reports across the moomoo platform | — |
| **Search / Content** | `moomoo-stock-digest` | Aggregated single-stock news digest with directional analysis | — |
| **Search / Content** | `moomoo-comment-sentiment` | Community comment sentiment + KOL viewpoints | — |

`/install-moomoo-opend` is **only** required by the API and Anomaly skills. Search/Content skills call public HTTP endpoints and work without it.

---

## Quick Start

### 1. Install the SkillHub manager (`moomoo-skills`)

The manager is a stdlib-Python CLI that installs / upgrades / uninstalls skills, generates a self-discovery skill for your AI client, and OTA-upgrades itself. One-line installer:

```bash
curl -fsSL "https://gitlab.futunn.com/futu-common/futu-skills-hub/-/raw/v20260428-futu-cli_v2/internal/moomoo/moomoo-install.sh" | bash
```

This deploys the manager under `~/.moomoo-skillhub/`, drops a `moomoo-skills` wrapper into `~/.local/bin/`, and adds it to your PATH.

Verify:

```bash
moomoo-skills --version
moomoo-skills detect          # show which AI client / skills dir was detected
```

### 2. Install a skill

Pick the skill you need from [Skills Overview](#skills-overview), then either:

```bash
# via npx skills (community tool, requires Node 18+)
npx skills add -y -g https://gitlab.futunn.com/futu-common/futu-skills-hub.git#v20260428-futu-cli_v2 \
  --path internal/moomoo/<category>/<slug>

# or via moomoo-skills (recommended — handles deps + version-check injection)
moomoo-skills install <slug>
```

The manager auto-detects whether you are running inside Claude Code, Cursor, VS Code, JetBrains, or OpenClaw, and writes to the correct skills directory.

### 3. (Optional) Install OpenD

Required only for **API** and **Anomaly** skills. Easiest path: just say it to your AI assistant and it will run the installer skill for you:

```
/install-moomoo-opend
```

> Using the Moomoo API requires API access enabled — complete the questionnaire and agreement in the moomoo app. See the [permission guide](https://openapi.moomoo.com/moomoo-api-doc/intro/authority.html).

### 4. Start using

```
> Show me Tesla's real-time quote
> Place a limit buy for 100 shares of TSLA at $250
> Search the latest news for NVIDIA
> 看看 NVDA 最近有没有异动？
> 帮我解读一下比亚迪最近发生了什么
```

---

## Moomoo API Skills

### `moomooapi` — Trading & Market Data

Wraps the entire [Moomoo OpenAPI](https://openapi.moomoo.com/moomoo-api-doc/) into an AI-callable interface.

| Capability | Description |
|------------|-------------|
| Real-time Quotes | Live prices for stocks, ETFs, options, futures, indices |
| K-line / Candlestick | Historical and real-time K-line at any granularity |
| Order Book | Full depth bid/ask order book |
| Tick-by-Tick | Trade-level tick data |
| Time-sharing | Intraday time-sharing chart data |
| Snapshots | Batch market snapshots |
| Sector Quotes | Sector / industry lists and constituents |
| Options Chain | Expiry dates, strike prices, full options chain |
| Place / Modify / Cancel Order | Market / limit / conditional, all amend/cancel paths |
| Account & Funds | Account list, available cash, buying power, margin |
| Positions | Current holdings with P&L |

**Supported markets:** Hong Kong, US (NYSE/AMEX/NASDAQ), China A-shares, Singapore, Japan.

### `install-moomoo-opend` — OpenD Installer

Detects your platform (Windows / macOS / CentOS / Ubuntu), downloads the matching Moomoo OpenD release, sets up the Python SDK, and verifies the local TCP gateway. The API and Anomaly skills declare it as a `requires.skills` dependency, so the manager will pull it in automatically when needed.

---

## Anomaly Skills

Three skills for "is anything odd happening with this stock?" detection. Each calls Moomoo OpenD's `get_*_unusual()` family via local Python scripts.

| Skill | Triggers on | Signals |
|-------|------------|---------|
| `moomoo-capital-anomaly` | "capital flow / fund flow / short sell / who's buying" | Fund distribution, broker buy/sell, capital flow trend, short-sell volume & ratio |
| `moomoo-derivatives-anomaly` | "options / IV / PCR / warrants" | Implied volatility, put/call ratio, unusual option activity, warrant flow |
| `moomoo-technical-anomaly` | "K-line / MACD / RSI / overbought / golden cross" | Pattern detection across MACD, RSI, KDJ, CCI, K-line shapes |

Each skill declares `metadata.requires.skills: [install-moomoo-opend, moomooapi]`, so installing one of them via `moomoo-skills install` will pull in OpenD setup automatically.

**Example prompts:**
```
Are there any anomalies for NVDA today?
看看 TSLA 期权有没有异动
检查一下 AAPL 的技术面
```

---

## Search & Content Skills

Three skills calling public moomoo HTTP endpoints — **no OpenD required**.

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

## SkillHub manager (`moomoo-skills`)

The manager isn't required for skills to work — but it gives you self-upgrade, dependency resolution, and a self-discovery skill that lets your AI client suggest uninstalled skills when relevant.

Subcommand cheatsheet:

```
moomoo-skills search <q>            # search the skill index
moomoo-skills list                  # already-installed skills
moomoo-skills install <slug>        # install (recursively pulls deps)
moomoo-skills upgrade [<slug>]      # upgrade one or all
moomoo-skills uninstall <slug>
moomoo-skills check                 # CLI + skill update check
moomoo-skills self-upgrade          # upgrade the CLI itself
moomoo-skills detect                # show the AI client + skills dir it picks
moomoo-skills refresh-discovery     # regenerate the auto-discovery SKILL.md
```

**Auto self-upgrade.** On every invocation the CLI silently checks `cli_update_manifest.json`; if a newer version is published it `git clone`s the new manager code and `os.execv`s itself with the same args. Disable with `--skip-self-upgrade` or `MOOMOO_SKILLHUB_SKIP_SELF_UPGRADE=1`.

**Self-discovery skill.** Every install/uninstall/upgrade refreshes `<skills-dir>/_moomoo-skillhub/SKILL.md`, listing all *not-yet-installed* skills together with their `discovery_hint` and the exact `npx skills add` command. AI clients load it as a regular skill, so when a user query matches an uninstalled skill's hint, the assistant prompts the user to install it. Once everything is installed, the discovery skill is removed.

**Per-product isolation.** This hub manages only `product=moomoo` skills. Coexists cleanly with `futu-skillhub` on the same machine — each manager touches only its own product.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       AI Assistant                           │
│   (Claude Code / Cursor / Claude Desktop / VS Code / JB)    │
└────────────────────────────┬────────────────────────────────┘
                             │ Skill protocol (SKILL.md)
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    Moomoo Agent Hub                          │
│                                                              │
│   moomoo-skills CLI ─── install / upgrade / self-discovery   │
│                                                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │  Moomoo API     │  │  Anomaly        │  │  Search /    │ │
│  │  Skills         │  │  Skills         │  │  Content     │ │
│  │                 │  │                 │  │  Skills      │ │
│  │  moomooapi      │  │  capital        │  │  news-search │ │
│  │  install-opend  │  │  derivatives    │  │  stock-digest│ │
│  │                 │  │  technical      │  │  sentiment   │ │
│  └────────┬────────┘  └────────┬────────┘  └──────┬───────┘ │
│           │                    │                  │         │
└───────────┼────────────────────┼──────────────────┼─────────┘
            │                    │                  │
            ▼                    ▼                  ▼
   ┌────────────────┐   ┌────────────────┐  ┌─────────────────┐
   │     OpenD      │   │     OpenD      │  │  Public HTTP    │
   │  (local TCP)   │   │  (local TCP)   │  │  ai-news-search │
   └───────┬────────┘   └───────┬────────┘  │  .moomoo.com    │
           │                    │            └─────────────────┘
           ▼                    ▼
   ┌────────────────────────────────────┐
   │     Moomoo Servers (HK/US/CN/SG/JP) │
   └────────────────────────────────────┘
```

Source-of-truth files in this repo:

| File | Purpose |
|------|---------|
| `manager/version.json` | CLI version baseline (OTA gate) |
| `manager/cli_update_manifest.json` | OTA manifest — bump version + push to roll out new CLI |
| `manager/metadata.json` | Hub config (`hub_name`, repo URL/ref, etc.) |
| `manager/skill_index.json` | Skill catalog with discovery hints, drives search + self-discovery |
| `manager/skill_catalog.json` | Per-skill latest version + deprecation/migration table |
| `skill-self-upgrade.md` | Maintainer guide for embedding the CLI version-check block in SKILL.md |

---

## Security

- **Credentials via env vars only** — never hardcoded
- **Trade confirmation** — write operations require explicit user confirmation
- **Local-first** — Moomoo API traffic routes through your local OpenD via encrypted TCP
- **Read-only mode** — restrict to market data queries by omitting trade credentials
- **Rate limiting** — respects Moomoo OpenAPI's built-in limits
- **Content & Anomaly endpoints** — public HTTP, no user credentials transmitted; reference data only

---

## FAQ

**Q: Do I need OpenD for all Skills?**
A: No. Only the **API** and **Anomaly** skills need OpenD. **Search/Content** skills call public HTTP and work without it.

**Q: Can I install skills without `moomoo-skills`?**
A: Yes — `npx skills add` works directly. But you'll lose auto-upgrade, dependency resolution, and the self-discovery skill.

**Q: Can `moomoo-skills` and `futu-skills` coexist?**
A: Yes. Each manager manages only its own product (`hub_name` in `metadata.json` carries the product), so they don't interfere.

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
