---
name: moomoo-trading
description: moomoo CLI securities trading skill for OAuth status, accounts, funds, cash logs, order fees, margin ratio, positions, buy/sell/place/modify/cancel orders, order queries, fills, and max tradable quantity; answer in the user's language.
allowed-tools: Bash Read
metadata:
  version: 0.0.4
  requires:
    bins:
      - moomoo
---

# moomoo Trading

Use the locally available `moomoo` CLI for securities trading. Answer in the user's language by default; keep commands, flags, JSON fields, error codes, and symbols unchanged.

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
npx skills add -y -g MoomooOpen/moomoo-agent-hub --skill moomoo-trading
npx skills update moomoo-trading -g -y
```

## Rules

- Before account or trading commands, if `moomoo` cannot be resolved, follow [Install the moomoo CLI](#install-the-moomoo-cli).
- For auth state, prefer `moomoo auth status --format json`; for network reachability, use `moomoo check --format json`.
- As this skill's invocation convention, always append the hidden internal marker `--source skill` to the end of the command when invoking `moomoo` from Bash. In `--source skill` mode, the CLI auto-detects Codex/Claude Code and reports `agent_name`; append `--agent codex` or `--agent claude_code` only when auto-detection is insufficient and CLI support has been confirmed. Do not include these internal markers in commands shown to the user.
- Never read or print token file contents. The CLI attaches OAuth Bearer auth automatically. `PERMISSION_DENIED` is a server-side permission denial, not proof that the token header is missing.
- Build commands with the minimum required arguments: if a CLI flag already has a default and the user did not specify a different value, omit that flag.
- Do not assume a default account exists. Omit `--account` only after this session has confirmed a configured default account via `moomoo auth status` or config; otherwise list accounts or ask the user to choose one, then pass `--account` explicitly.
- Add `--format json` only when the agent needs to parse command output. Commands shown for the user to run may use default table output.
- Securities symbol arguments are `symbol` values in `MARKET.CODE` format, such as `US.AAPL` and `HK.00700`. `HK.700` is normalized to `HK.00700`, and lowercase markets/tickers are uppercased. Do not pass old suffix format like `700.HK` or bare tickers like `AAPL`.
- Historical `--start` / `--end` filters are microsecond Unix timestamps. Table time columns are displayed in UTC+8; JSON output keeps raw API fields.
- Order and fill list commands auto-page internally. The user-facing CLI only exposes `--page-size`, not `--page-flag`, for securities order/fill lists.
- `account cash-logs` returns one page per call. Use `--format json`, then pass `--page-flag` from the prior response until `completed` is true.
- `order fees` requires a concrete `order_id`. FX order fees are not supported by the Open API yet.
- `margin-ratio` requires `--security-firm` and `--codes` (max 10 symbols). Prefer `security_firm` from `account list --format json`.
- Real account mutations require explicit user confirmation first: `order buy`, `order sell`, `order place`, `order modify`, and `order cancel`.
- Do not invent broker confirmation. If the CLI reports broker confirmation because the API returned `need_order_confirm=true` / `confirm_id`, relay the prompt and wait for explicit approval before sending `y`.

## References

- Read [CLI parameters](references/cli-parameters.md) when constructing commands or deciding which flags are required, optional, or defaulted.
- Read [dictionaries](references/dictionaries.md) when selecting or interpreting market, side, order type, status, or account-market values.
- Use `moomoo-crypto` for cryptocurrency exchange trading.
