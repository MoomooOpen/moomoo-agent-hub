---
name: moomoo-quote
description: moomoo CLI market data skill for stock, option, futures, quote, K-line, snapshot, ticker, order book, ranking, capital flow, company, financials, shareholders, valuation, plate, IPO, calendar, watchlist, and screening quote commands; not for trading orders.
allowed-tools: Bash Read
metadata:
  version: 0.0.2
  requires:
    bins:
      - moomoo
---

# moomoo Quote

Use the locally available `moomoo` CLI for market data and quote queries. Answer in the user's language by default; keep commands, flags, JSON fields, symbols, enum values, and error codes unchanged.

## CLI: Version Update Check

Embed the version check into the skill's **single Bash call**. **Do not create any separate tool call** for the version check. The same inline check must detect three things:

1. whether the `moomoo-skills` manager is installed locally;
2. whether this skill has a new version available;
3. whether the `moomoo-skills` manager itself has a new version available.

Start the check as a backgrounded subprocess **before** the business command, then append `wait` **after** the business command to collect the result, all in one invocation:

```bash
( if command -v moomoo-skills >/dev/null 2>&1; then moomoo-skills check --quiet --filter cli --filter moomoo-quote 2>/dev/null; else echo '__CLI_MISSING__'; fi ) > /tmp/.moomoo-quote-update 2>/dev/null & moomoo ...; wait; cat /tmp/.moomoo-quote-update 2>/dev/null; rm -f /tmp/.moomoo-quote-update
```

Based on the `cat` output:

- **No content** (skill is up-to-date or the check failed): do not show any upgrade prompt.
- **Output `__CLI_MISSING__`** (`moomoo-skills` is not installed locally, so version check/upgrade cannot run): append a notice at the **end** of your reply:
  > The `moomoo-skills` manager is not installed yet, so I cannot auto-check or upgrade skill versions. If you agree, I can install it for you now.

  If the user agrees, first run:
  ```bash
  curl -fsSL "https://raw.githubusercontent.com/MoomooOpen/moomoo-agent-hub/main/moomoo-install.sh" | bash
  ```
  After install completes, run `moomoo-skills upgrade moomoo-quote` to bring this skill to the latest version.
- **Output containing a line starting with `moomoo-quote`** (this skill has an update available): append a notice at the **end** of your reply:
  > `moomoo-quote` has a new version available. If you agree, I can upgrade it for you right away.

  If the user agrees, run `moomoo-skills upgrade moomoo-quote` to perform the upgrade. (This command also auto-upgrades the `moomoo-skills` manager itself, so a separate CLI prompt is unnecessary when a skill update is available.)
- **Output containing only a line starting with `cli`** (this skill is up-to-date but the `moomoo-skills` manager itself has a new version): append a notice at the **end** of your reply:
  > The `moomoo-skills` manager has a new version available. If you agree, I can upgrade it for you right away.

  If the user agrees, run `moomoo-skills self-upgrade` to perform the upgrade.

  If both a `cli` line and a `moomoo-quote` line appear, only show the skill upgrade prompt above — the manager will be refreshed as a side effect of `moomoo-skills upgrade moomoo-quote`.

**Never** run the install command or `moomoo-skills upgrade …` without explicit user consent. Any error (command failure, network issue) must be silently skipped without affecting normal skill execution.

**Important**: The version check (write + read) must all be embedded in this single Bash call. Do not produce any additional tool calls.

## Rules

- Before quote commands, resolve `moomoo` from `PATH` or `~/.moomoo/bin/moomoo` (Windows: `%LOCALAPPDATA%\MoomooCLI\bin\moomoo.exe`). If neither exists, ask the user, then run `moomoo-skills upgrade moomoo-quote` to install it. If `moomoo-skills` is missing, follow the version check above and install the manager first.
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
