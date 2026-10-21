---
name: moomoo-crypto
description: moomoo CLI cryptocurrency trading skill for crypto accounts, balances, max quantity, crypto orders, and crypto fills; answer in the user's language.
allowed-tools: Bash Read
metadata:
  version: 0.0.3
  requires:
    bins:
      - moomoo
---

# moomoo Crypto

Use the locally available `moomoo` CLI for cryptocurrency exchange trading. Answer in the user's language by default; keep commands, flags, JSON fields, token symbols, and error codes unchanged.

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
npx skills add -y -g MoomooOpen/moomoo-agent-hub --skill moomoo-crypto
npx skills update moomoo-crypto -g -y
```

## Rules

- Before account or trading commands, if `moomoo` cannot be resolved, follow [Install the moomoo CLI](#install-the-moomoo-cli).
- For auth state, prefer `moomoo auth status --format json`; for network reachability, use `moomoo check --format json`.
- As this skill's invocation convention, always append the hidden internal marker `--source skill` to the end of the command when invoking `moomoo` from Bash. In `--source skill` mode, the CLI auto-detects Codex/Claude Code and reports `agent_name`; append `--agent codex` or `--agent claude_code` only when auto-detection is insufficient and CLI support has been confirmed. Do not include these internal markers in commands shown to the user.
- Never read or print token file contents. The CLI attaches OAuth Bearer auth automatically. `PERMISSION_DENIED` is a server-side permission denial, not proof that the token header is missing.
- Build commands with the minimum required arguments: if a CLI flag already has a default and the user did not specify a different value, omit that flag.
- Do not assume a default account exists. Omit `--account` only after this session has confirmed a configured default account via `moomoo auth status` or config; otherwise list crypto accounts or ask the user to choose one, then pass `--account` explicitly.
- Add `--format json` only when the agent needs to parse command output. Commands shown for the user to run may use default table output.
- Current CLI scope is crypto exchange trading only: accounts, balances, max quantity, orders, and fills under `moomoo crypto`. Do not use or suggest Web3 wallet, swap, or transfer commands.
- Crypto pair arguments are `symbol` values such as `BTCUSD` and `ETHHKD`; the CLI uppercases input and strips an optional `CC.` prefix. Do not convert crypto pairs to stock-style `MARKET.CODE` symbols.
- Historical `--start` / `--end` filters are microsecond Unix timestamps. Table time columns are displayed in UTC+8; JSON output keeps raw API fields.
- For generic max quantity checks, prefer `--type MARKET`; for a limit-price capacity check, pass `--type LIMIT --price <price>`. For non-USD pairs, pass `--currency` explicitly.
- Crypto orders may affect real assets; confirm account, pair, side, quantity, and price or cash amount before mutation.
- Do not invent broker confirmation. If the CLI prompts for confirmation or broker confirmation, relay the prompt and wait for explicit approval before sending `y`.

## References

- Read [CLI parameters](references/cli-parameters.md) when constructing commands or deciding which flags are required, optional, or defaulted.
- Read [dictionaries](references/dictionaries.md) when selecting or interpreting pairs, currencies, order types, or order/fill fields.
- Use `moomoo-trading` for securities accounts, funds, positions, securities orders, and securities fills.
