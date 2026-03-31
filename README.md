
<h1 align="center">Futu Agent Hub</h1>
<p align="center">
  <b>Connect AI agents to Futu/moomoo — trade, query market data, and get investment insights through natural language.</b>
</p>

<p align="center">
  <a href="https://openapi.futunn.com/futu-api-doc/"><img src="https://img.shields.io/badge/Moomoo_API-Docs-blue?style=flat-square" alt="Moomoo API Docs" /></a>
  <a href="#license"><img src="https://img.shields.io/badge/License-MIT-yellow?style=flat-square" alt="License" /></a>
  <a href="https://modelcontextprotocol.io/"><img src="https://img.shields.io/badge/MCP-Compatible-purple?style=flat-square" alt="MCP Compatible" /></a>
</p>

<p align="center">
  <a href="#-quick-start">Quick Start</a> · <a href="#-skills-overview">Skills Overview</a> · <a href="#-moomoo-api-skill">Moomoo API Skill</a> · <a href="#-content-skills">Content Skills</a> · <a href="#-examples">Examples</a>
</p>


---

## What is Futu Agent Hub?

Futu Agent Hub is the official AI Agent skills center by **moomoo**, packaging the full power of the Moomoo API and financial content services into standardized Skills. It enables AI assistants to interact with real-time market data, execute trades, retrieve financial news, and gauge market sentiment — all through natural language.

Works with **Claude Code**, **Cursor**, **Claude Desktop**, **VS Code**, and other MCP-compatible AI tools.

---

## Skills Overview

Futu Agent Hub ships with **4 production-ready Skills** across two categories:

| Skill | Category | Description |
|-------|----------|-------------|
| Moomoo API | Trading & Market Data | Full Moomoo API wrapped as a Skill — quotes, K-lines, order placement, positions, account management, and more |
| News Search | Content | Search news, announcements, and research reports across the Futu platform |
| Stock Briefing | Content | Get real-time factual updates and core analysis for any stock |
| Sentiment Gauge | Content | Aggregated community sentiment, KOL opinions, and market mood as a standardized score |

---

## Moomoo API Skill

The Moomoo API Skill wraps the entire [Moomoo API](https://openapi.futunn.com/futu-api-doc/) into an AI-callable interface. One Skill, full coverage.

### Market Data

| Capability | Description |
|------------|-------------|
| Real-time Quotes | Live prices for stocks, ETFs, options, futures, indices |
| K-line / Candlestick | Historical and real-time K-line data at any granularity |
| Order Book | Full depth bid/ask order book |
| Tick-by-Tick | Trade-level tick data |
| Time-sharing | Intraday time-sharing chart data |
| Snapshots | Batch market snapshots |
| Sector Quotes | Sector/industry lists and constituent stocks |
| Options Chain | Expiry dates, strike prices, and full options chain |

### Trading

| Capability | Description |
|------------|-------------|
| Place Order | Market / limit / conditional orders |
| Modify Order | Amend pending orders |
| Cancel Order | Cancel open orders |
| Order History | Today's and historical orders |
| Trade History | Today's and historical fills |

### Account & Portfolio

| Capability | Description |
|------------|-------------|
| Account List | Query available trading accounts |
| Funds | Available cash, buying power, margin status |
| Positions | Current holdings with P&L |

### Supported Markets

| Market | Instruments |
|--------|------------|
| Hong Kong | Stocks, ETFs, Warrants, CBBCs, Options, Futures, Indices |
| United States | NYSE / AMEX / NASDAQ Stocks, ETFs, Options, Futures |
| China A-shares | Stocks, ETFs, Indices |
| Singapore | Stocks |
| Japan | Stocks |

---

## Content Skills

### News Search / 资讯搜索

Search news, announcements, and research reports on the moomoo platform. Returns structured results with title, publish time, and deep links.

| Feature | Detail |
|---------|--------|
| Endpoint | `GET /news_search` via `ai-news-search.futunn.com` |
| Auth | Public — no API key required |
| Languages | Simplified Chinese (`zh-CN`), Traditional Chinese (`zh-HK`), English (`en`) |
| Content Types | News (`1`), Notices/Announcements (`2`), Research Reports (`3`) |
| Sort Options | By PV (`1`), By Time (`2`), By Heat (`3`) |
| Max Results | Up to 50 per request |

**Example prompts:**
```
Search for the latest news on NVIDIA
搜索一下腾讯最近的重要新闻
Find recent announcements for Tesla
```

---

### Stock Briefing / 个股解读

Continuously delivers the latest factual updates and core analysis for the stocks you care about. One entry point to quickly learn what happened, why it matters, and what's worth watching.

**Example prompts:**
```
帮我解读一下比亚迪最近发生了什么
What's going on with Apple lately?
Give me a quick briefing on Alibaba
```

---

### Sentiment Gauge / 情绪温度计

Aggregates community sentiment, trending discussion topics, and KOL (Key Opinion Leader) views into a standardized sentiment reference — helping you gauge the market mood before making decisions.

**Example prompts:**
```
看看社区对小米的情绪怎么样
What's the market sentiment on TSLA?
How are people feeling about Meituan?
```

---

## Quick Start

### Prerequisites

1. A [moomoo](https://www.moomoo.com/) or [Futu NiuNiu](https://www.futunn.com/) account
2. [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed

---

### Content Skills (News Search / Stock Briefing / Sentiment Gauge)

Content Skills call public HTTP endpoints directly — **no OpenD or API SDK required**.

Install with a single command:

```bash
npx skills add https://github.com/anthropics/futu-agent-hub
```

Start using right away:

```
> Search for the latest news on NVIDIA
> Give me a briefing on Tesla
> What's the market sentiment on AAPL?
```

---

### Moomoo API Skill (Trading & Market Data)

The Moomoo API Skill requires **OpenD** (local gateway) and the **API SDK**. Copy the following prompt and send it to your AI assistant — it will handle the full installation automatically:

```
Please follow the Moomoo API Skills Quick Start guide to install Skills and OpenD.
Documentation: https://openapi.moomoo.com/moomoo-api-doc/file/moomoo-openapi-skills-CN.html
```

> **Note:** Using the Moomoo API Skill requires API access to be enabled. Complete the questionnaire assessment and agreement confirmation in the app — see [permission guide](https://openapi.futunn.com/futu-api-doc/intro/authority.html).

The agent will automatically:
1. Download and install the Skills to your global skills directory
2. Download and install OpenD for your platform
3. Set up the Python SDK

Supported platforms: **Windows** / **macOS** / **CentOS** / **Ubuntu**

After the agent completes the setup, confirm the following skills are available:

- `install-opend` — OpenD Installation Assistant
- `futuapi` — Trading & Market Data Assistant

Start using:

```
> Show me Tesla's real-time quote
> Place a limit buy for 100 shares of TSLA at $250
> What's my current buying power?
```

---

## Examples

Once configured, interact with your AI assistant in natural language:

### Market Data
```
查一下腾讯的实时报价
Show me Tesla's daily K-line for the past 30 days
美团的买卖盘情况怎么样？
What's the current snapshot for AAPL?
```

### Trading
```
以150港元限价买入腾讯1000股
Place a limit buy for 100 shares of MSFT at $420
撤销我最近的挂单
Show me today's filled orders
```

### Account
```
我的港股账户还有多少可用资金？
Show me my US stock positions
What's my current buying power?
```

### News & Insights
```
搜索一下英伟达最近的重要新闻
Give me a briefing on BYD — what happened recently?
看看社区对小米的情绪怎么样
What's the sentiment on Tesla right now?
```

---

## Architecture

```
┌──────────────────────────────────────────────┐
│              AI Assistant                     │
│  (Claude Code / Cursor / Claude Desktop)     │
└──────────────────┬───────────────────────────┘
                   │ Skills Protocol
                   ▼
┌──────────────────────────────────────────────┐
│           Futu Agent Hub                     │
│                                              │
│  ┌────────────┐  ┌────────────────────────┐  │
│  │ Moomoo API │  │    Content Skills      │  │
│  │   Skill    │  │                        │  │
│  │            │  │  ┌──────────────────┐  │  │
│  │  Trading   │  │  │  News Search     │  │  │
│  │  Quotes    │  │  ├──────────────────┤  │  │
│  │  Account   │  │  │  Stock Briefing  │  │  │
│  │  Options   │  │  ├──────────────────┤  │  │
│  │   ...      │  │  │  Sentiment Gauge │  │  │
│  └─────┬──────┘  │  └────────┬─────────┘  │  │
│        │         │           │             │  │
└────────┼─────────┴───────────┼─────────────┘  │
         │                     │
         ▼                     ▼
┌────────────────┐  ┌──────────────────────┐
│     OpenD      │  │  moomoo Content APIs │
│   (Gateway)    │  │  (Public HTTP)       │
│                │  │                      │
│  Local TCP     │  │  ai-news-search      │
│  Connection    │  │  .futunn.com         │
└────────┬───────┘  └──────────────────────┘
         │
         ▼
┌────────────────┐
│ moomoo Servers │
│  (HK/US/CN/   │
│   SG/JP)       │
└────────────────┘
```

---

## Security

- **Credentials via env vars only** — never hardcoded in config or source files
- **Trade confirmation** — write operations (order placement, modification, cancellation) require explicit user confirmation
- **Local-first** — Moomoo API traffic routes through your local OpenD gateway via encrypted TCP
- **Read-only mode** — restrict to market data queries only by omitting trade credentials
- **Rate limiting** — respects Moomoo API's built-in rate limits and access controls
- **Content Skills** — public endpoints with no user credentials transmitted; response data is non-financial reference only

---

## FAQ

**Q: Do I need OpenD for all Skills?**
A: No. Only the Moomoo API Skill requires OpenD. The Content Skills (News Search, Stock Briefing, Sentiment Gauge) call public HTTP APIs directly and work without OpenD.

**Q: Is there any additional fee for using Futu Agent Hub?**
A: No. Trading through the Moomoo API incurs no additional fees beyond standard brokerage commissions.

**Q: Which programming languages are supported?**
A: The Moomoo API SDK supports Python, Java, C#, C++, and JavaScript. The Agent Hub Skills work at a higher level and are language-agnostic — just install and use with your AI assistant.

**Q: Can I use this with moomoo instead of Futu NiuNiu?**
A: Yes. Futu NiuNiu and moomoo share the same API infrastructure. Both are fully supported.

---

## Disclaimer

This project is for informational and educational purposes. All trading operations performed through Futu Agent Hub are at the user's own risk. AI-generated analysis and recommendations do not constitute investment advice. Please fully understand the associated risks before using trading features. Futu Agent Hub is not responsible for any financial losses.

---

## License

[MIT](LICENSE)

---

<p align="center">
  Built by <a href="https://www.futunn.com/">Futu</a> · Powered by <a href="https://openapi.futunn.com/">Moomoo API</a>
</p>
