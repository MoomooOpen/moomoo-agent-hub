---
name: moomoo-sim-trading
description: moomoo CLI simulated trading skill for paper/sim accounts, simulated funds, positions, max quantity, simulated order placement, modification, cancellation, order queries, and history; not for real securities or crypto trading.
allowed-tools: Bash Read
metadata:
  version: 0.0.3
  requires:
    bins:
      - moomoo
---

# moomoo Sim Trading

Use the locally available `moomoo sim ...` CLI for simulated, paper, or demo trading only. Answer in the user's language by default; keep commands, flags, JSON fields, symbols, account IDs, order IDs, and error codes unchanged.

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
npx skills add -y -g MoomooOpen/moomoo-agent-hub --skill moomoo-sim-trading
npx skills update moomoo-sim-trading -g -y
```

## Boundary With Real Trading

- Use this skill only when the user explicitly asks for simulated trading, paper trading, demo trading, or `sim` commands.
- If the user says only "buy", "sell", "place an order", "modify order", or "cancel order" without saying simulated/paper/demo, do not assume simulation. Ask whether they mean simulated trading or real trading.
- Never use real securities commands such as `moomoo order ...`, `moomoo position`, or `moomoo account funds` from this skill. The simulated equivalents are under `moomoo sim ...`.
- Never use crypto commands such as `moomoo crypto ...` from this skill.
- A simulated order does not affect real assets, but it still mutates the user's simulated account state. Account, market, symbol, side, quantity, price/order type, and order ID must be clear before placing, modifying, or canceling simulated orders.

## Rules

- Before simulated trading commands, if `moomoo` cannot be resolved, follow [Install the moomoo CLI](#install-the-moomoo-cli).
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
