---
name: moomoo-sim-trading
description: moomoo CLI simulated trading skill for paper/sim accounts, simulated funds, positions, max quantity, simulated order placement, modification, cancellation, order queries, and history; not for real securities or crypto trading.
allowed-tools: Bash Read
metadata:
  version: 0.0.2
  requires:
    bins:
      - moomoo
---

# moomoo Sim Trading

Use the locally available `moomoo sim ...` CLI for simulated, paper, or demo trading only. Answer in the user's language by default; keep commands, flags, JSON fields, symbols, account IDs, order IDs, and error codes unchanged.

## CLI: Version Update Check

Embed the version check into the skill's **single Bash call**. **Do not create any separate tool call** for the version check. The same inline check must detect three things:

1. whether the `moomoo-skills` manager is installed locally;
2. whether this skill has a new version available;
3. whether the `moomoo-skills` manager itself has a new version available.

Start the check as a backgrounded subprocess **before** the business command, then append `wait` **after** the business command to collect the result, all in one invocation:

```bash
( if command -v moomoo-skills >/dev/null 2>&1; then moomoo-skills check --quiet --filter cli --filter moomoo-sim-trading 2>/dev/null; else echo '__CLI_MISSING__'; fi ) > /tmp/.moomoo-sim-trading-update 2>/dev/null & moomoo ...; wait; cat /tmp/.moomoo-sim-trading-update 2>/dev/null; rm -f /tmp/.moomoo-sim-trading-update
```

Based on the `cat` output:

- **No content** (skill is up-to-date or the check failed): do not show any upgrade prompt.
- **Output `__CLI_MISSING__`** (`moomoo-skills` is not installed locally, so version check/upgrade cannot run): append a notice at the **end** of your reply:
  > The `moomoo-skills` manager is not installed yet, so I cannot auto-check or upgrade skill versions. If you agree, I can install it for you now.

  If the user agrees, first run:
  ```bash
  curl -fsSL "https://raw.githubusercontent.com/MoomooOpen/moomoo-agent-hub/main/moomoo-install.sh" | bash
  ```
  After install completes, run `moomoo-skills upgrade moomoo-sim-trading` to bring this skill to the latest version.
- **Output containing a line starting with `moomoo-sim-trading`** (this skill has an update available): append a notice at the **end** of your reply:
  > `moomoo-sim-trading` has a new version available. If you agree, I can upgrade it for you right away.

  If the user agrees, run `moomoo-skills upgrade moomoo-sim-trading` to perform the upgrade. (This command also auto-upgrades the `moomoo-skills` manager itself, so a separate CLI prompt is unnecessary when a skill update is available.)
- **Output containing only a line starting with `cli`** (this skill is up-to-date but the `moomoo-skills` manager itself has a new version): append a notice at the **end** of your reply:
  > The `moomoo-skills` manager has a new version available. If you agree, I can upgrade it for you right away.

  If the user agrees, run `moomoo-skills self-upgrade` to perform the upgrade.

  If both a `cli` line and a `moomoo-sim-trading` line appear, only show the skill upgrade prompt above — the manager will be refreshed as a side effect of `moomoo-skills upgrade moomoo-sim-trading`.

**Never** run the install command or `moomoo-skills upgrade …` without explicit user consent. Any error (command failure, network issue) must be silently skipped without affecting normal skill execution.

**Important**: The version check (write + read) must all be embedded in this single Bash call. Do not produce any additional tool calls.

## Boundary With Real Trading

- Use this skill only when the user explicitly asks for simulated trading, paper trading, demo trading, or `sim` commands.
- If the user says only "buy", "sell", "place an order", "modify order", or "cancel order" without saying simulated/paper/demo, do not assume simulation. Ask whether they mean simulated trading or real trading.
- Never use real securities commands such as `moomoo order ...`, `moomoo position`, or `moomoo account funds` from this skill. The simulated equivalents are under `moomoo sim ...`.
- Never use crypto commands such as `moomoo crypto ...` from this skill.
- A simulated order does not affect real assets, but it still mutates the user's simulated account state. Account, market, symbol, side, quantity, price/order type, and order ID must be clear before placing, modifying, or canceling simulated orders.

## Rules

- Before simulated trading commands, resolve `moomoo` from `PATH` or `~/.moomoo/bin/moomoo` (Windows: `%LOCALAPPDATA%\MoomooCLI\bin\moomoo.exe`). If neither exists, ask the user, then run `moomoo-skills upgrade moomoo-sim-trading` to install it. If `moomoo-skills` is missing, follow the version check above and install the manager first.
- For auth state, prefer `moomoo auth status --format json`; for network reachability, use `moomoo check --format json`.
- As this skill's invocation convention, always append the hidden internal marker `--source skill` to the end of the command when invoking `moomoo` from Bash. In `--source skill` mode, the CLI auto-detects Codex/Claude Code and reports `agent_name`; append `--agent codex` or `--agent claude_code` only when auto-detection is insufficient and CLI support has been confirmed. Do not include these internal markers in commands shown to the user.
- Never read or print token file contents. The CLI attaches OAuth Bearer auth automatically. `PERMISSION_DENIED` is a server-side permission denial, not proof that the token header is missing.
- Use only the merged high-level commands under `moomoo sim ...`; do not call old flat endpoint names like `sim-trade-*`.
- Build commands with the minimum required arguments: if a CLI flag already has a default and the user did not specify a different value, omit that flag.
- Prefer `moomoo sim account list --format json` to identify the simulated account, then pass `--account <sim-account-id>` explicitly. Do not treat a real securities account ID as a simulated account ID.
- Add `--format json` only when the agent needs to parse command output. Commands shown for the user to run may use default table output.
- Simulated trading symbols use `MARKET.CODE`, such as `US.AAPL` and `HK.00700`. The CLI normalizes `HK.700` to `HK.00700` and uppercases markets/tickers. Do not pass old suffix format like `700.HK` or bare tickers like `AAPL` unless the market can be confidently resolved first.
- Historical simulated order pagination uses `--next-key`; pass the previous response's `pagination.next_key` unchanged.

## References

- Read [CLI parameters](references/cli-parameters.md) when constructing simulated trading commands or deciding which flags are required, optional, or defaulted.
- Read [dictionaries](references/dictionaries.md) when selecting or interpreting simulated markets, order sides, order types, sessions, order statuses, or common simulated-trading errors.
- Use `moomoo-trading` for real securities accounts, real funds, real positions, and real securities orders. Use `moomoo-crypto` for cryptocurrency trading. Use `moomoo-quote` for market data queries.
