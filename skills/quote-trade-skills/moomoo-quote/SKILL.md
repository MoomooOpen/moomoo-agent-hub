---
name: moomoo-quote
description: moomoo CLI market data skill for stock, option, futures, quote, K-line, snapshot, ticker, order book, ranking, capital flow, company, financials, shareholders, valuation, plate, IPO, calendar, watchlist, and screening quote commands; not for trading orders.
allowed-tools: Bash Read
metadata:
  version: 0.0.3
  requires:
    bins:
      - moomoo
---

# moomoo Quote

Use the locally available `moomoo` CLI for market data and quote queries. Answer in the user's language by default; keep commands, flags, JSON fields, symbols, enum values, and error codes unchanged.

## Install the moomoo CLI

This skill requires the [`moomoo` CLI](https://github.com/MoomooOpen/moomoo-cli). Resolve the binary from `PATH`, `~/.moomoo/bin/moomoo`, or `%LOCALAPPDATA%\MoomooCLI\bin\moomoo.exe` on Windows.

If the binary is missing, ask the user, then install it. Do not run the installer without explicit consent.

macOS / Linux:

```bash
curl -fsSL https://raw.githubusercontent.com/MoomooOpen/moomoo-cli/main/scripts/install.sh | sh
```

Windows PowerShell:

```powershell
iwr -UseBasicParsing https://raw.githubusercontent.com/MoomooOpen/moomoo-cli/main/scripts/install.ps1 -OutFile install.ps1
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

To update an existing CLI, run `moomoo update`.

Add or update this skill with npx:

```bash
npx skills add -y -g MoomooOpen/moomoo-agent-hub --skill moomoo-quote
npx skills update moomoo-quote -g -y
```

## Rules

- Before quote commands, if `moomoo` cannot be resolved, follow [Install the moomoo CLI](#install-the-moomoo-cli).
- Before any authenticated market data command, prefer `moomoo auth status --format json`; for network reachability, use `moomoo check --format json`.
- As this skill's invocation convention, always append the hidden internal marker `--source skill` to the end of the command when invoking `moomoo` from Bash. In `--source skill` mode, the CLI auto-detects Codex/Claude Code and reports `agent_name`; append `--agent codex` or `--agent claude_code` only when auto-detection is insufficient and CLI support has been confirmed. Do not include these internal markers in commands shown to the user.
- Never read or print token file contents. The CLI attaches OAuth Bearer auth automatically. `PERMISSION_DENIED` is a server-side permission or market data entitlement denial, not proof that the token header is missing.
- Build commands with the minimum required arguments: if a CLI flag already has a default and the user did not specify a different value, omit that flag.
- Add `--format json` only when the agent needs to parse command output. Commands shown for the user to run may use default table output.
- Quote symbols use `MARKET.CODE`, such as `US.AAPL`, `HK.00700`, `SH.600519`, `SZ.000001`, and `CC.BTCUSD`. The CLI normalizes `HK.700` to `HK.00700` and uppercases markets/tickers. Do not pass old suffix format like `700.HK` or bare tickers like `AAPL` unless the market can be confidently resolved first.
- User mentions of old REST endpoint command names must be mapped to the current aggregate command and selector flag. Do not call unregistered flat endpoint commands.
- For paginated quote interfaces, use `--format json` and follow `pagination.has_more` / `pagination.next_key` exactly. `next_key` is opaque and must not be parsed or constructed.
- `history-kline` and `capital --view history` use `--next-time`, not `--next-key`.
- `watchlist --action add/delete/move-out` mutates the user's watchlist. Confirm target group and symbols unless the user has already explicitly requested that mutation.
- Do not execute securities, crypto, or simulated trading orders. Use `moomoo-trading` for securities trading, `moomoo-crypto` for cryptocurrency trading, and the simulation trading skill for simulated trading.

## References

- Read [CLI parameters](references/cli-parameters.md) when constructing quote commands, selecting aggregate command variants, or checking required/default flags.
- Read [dictionaries](references/dictionaries.md) when mapping user language to markets, security types, K-line types, adjustment types, sessions, plate classes, option filters, or interpreting quote enum fields.
- Read [pagination](references/pagination.md) when fetching multiple pages or explaining how quote pagination works.
