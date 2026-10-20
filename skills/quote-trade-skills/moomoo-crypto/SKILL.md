---
name: moomoo-crypto
description: moomoo CLI cryptocurrency trading skill for crypto accounts, balances, max quantity, crypto orders, and crypto fills; answer in the user's language.
allowed-tools: Bash Read
metadata:
  version: 0.0.2
  requires:
    bins:
      - moomoo
---

# moomoo Crypto

Use the locally available `moomoo` CLI for cryptocurrency exchange trading. Answer in the user's language by default; keep commands, flags, JSON fields, token symbols, and error codes unchanged.

## CLI: Version Update Check

Embed the version check into the skill's **single Bash call**. **Do not create any separate tool call** for the version check. The same inline check must detect three things:

1. whether the `moomoo-skills` manager is installed locally;
2. whether this skill has a new version available;
3. whether the `moomoo-skills` manager itself has a new version available.

Start the check as a backgrounded subprocess **before** the business command, then append `wait` **after** the business command to collect the result, all in one invocation:

```bash
( if command -v moomoo-skills >/dev/null 2>&1; then moomoo-skills check --quiet --filter cli --filter moomoo-crypto 2>/dev/null; else echo '__CLI_MISSING__'; fi ) > /tmp/.moomoo-crypto-update 2>/dev/null & moomoo ...; wait; cat /tmp/.moomoo-crypto-update 2>/dev/null; rm -f /tmp/.moomoo-crypto-update
```

Based on the `cat` output:

- **No content** (skill is up-to-date or the check failed): do not show any upgrade prompt.
- **Output `__CLI_MISSING__`** (`moomoo-skills` is not installed locally, so version check/upgrade cannot run): append a notice at the **end** of your reply:
  > The `moomoo-skills` manager is not installed yet, so I cannot auto-check or upgrade skill versions. If you agree, I can install it for you now.

  If the user agrees, first run:
  ```bash
  curl -fsSL "https://raw.githubusercontent.com/MoomooOpen/moomoo-agent-hub/main/moomoo-install.sh" | bash
  ```
  After install completes, run `moomoo-skills upgrade moomoo-crypto` to bring this skill to the latest version.
- **Output containing a line starting with `moomoo-crypto`** (this skill has an update available): append a notice at the **end** of your reply:
  > `moomoo-crypto` has a new version available. If you agree, I can upgrade it for you right away.

  If the user agrees, run `moomoo-skills upgrade moomoo-crypto` to perform the upgrade. (This command also auto-upgrades the `moomoo-skills` manager itself, so a separate CLI prompt is unnecessary when a skill update is available.)
- **Output containing only a line starting with `cli`** (this skill is up-to-date but the `moomoo-skills` manager itself has a new version): append a notice at the **end** of your reply:
  > The `moomoo-skills` manager has a new version available. If you agree, I can upgrade it for you right away.

  If the user agrees, run `moomoo-skills self-upgrade` to perform the upgrade.

  If both a `cli` line and a `moomoo-crypto` line appear, only show the skill upgrade prompt above — the manager will be refreshed as a side effect of `moomoo-skills upgrade moomoo-crypto`.

**Never** run the install command or `moomoo-skills upgrade …` without explicit user consent. Any error (command failure, network issue) must be silently skipped without affecting normal skill execution.

**Important**: The version check (write + read) must all be embedded in this single Bash call. Do not produce any additional tool calls.

## Rules

- Before account or trading commands, resolve `moomoo` from `PATH` or `~/.moomoo/bin/moomoo` (Windows: `%LOCALAPPDATA%\MoomooCLI\bin\moomoo.exe`). If neither exists, ask the user, then run `moomoo-skills upgrade moomoo-crypto` to install it. If `moomoo-skills` is missing, follow the version check above and install the manager first.
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
