# CLI Parameters

Build commands with the minimum argument set: include required arguments, user-specified values, and flags needed to change CLI defaults. Do not add flags just because examples show defaults.

## Global Flags

| Flag | Default | When to pass |
| --- | --- | --- |
| `--format`, `-f` | `table` | Pass `--format json` only when the agent must parse output. Commands shown for a user to run can omit it. |
| `--token-file` | configured `token_file` | Pass only when the user asks for a non-default token file. |

Internal invocation convention: this skill always appends the hidden internal marker `--source skill` to the end of the command when invoking the CLI from Bash. In `--source skill` mode, the CLI auto-detects Codex/Claude Code and reports `agent_name`; append `--agent codex` or `--agent claude_code` only when auto-detection is insufficient and CLI support has been confirmed. Do not include these internal markers in commands shown to the user.

Current CLI scope is only cryptocurrency exchange trading under `moomoo crypto`.

Crypto symbols are trading pairs such as `BTCUSD` or `ETHHKD`. The CLI uppercases input and strips an optional `CC.` prefix, so `cc.btcusd` is sent as `BTCUSD`. Do not transform crypto pairs into stock-style `MARKET.CODE` symbols.

Historical filters use microsecond Unix timestamps. Table time columns are displayed in UTC+8, while JSON output preserves raw API fields.

## Auth And Accounts

| Command | Required | Defaults / omit | Notes |
| --- | --- | --- | --- |
| `moomoo auth status` | none | `--format table` | Shows local token, account, and permission state. |
| `moomoo check` | none | none | Checks local token usability and API reachability. |
| `moomoo auth login` | none | `--client-name` defaults to username and hostname, `--no-browser=false` | Pass `--no-browser` only in browserless environments. |
| `moomoo crypto account list` | none | none | Lists authorized accounts with cryptocurrency market access. |
| `moomoo crypto balance` | none if `default_account` is configured | none | Pass `--account` to select a specific account. |

## Account Resolution

- For any crypto command whose required column says "`--account` if no default account", do not omit `--account` unless this session has already confirmed a usable default account from `moomoo auth status --format json` or config.
- If no default account has been confirmed, run `moomoo crypto account list --format json` or ask the user to choose a crypto account, then pass `--account <account-id>` explicitly.
- If the user already provided an account ID in the request or recent context, pass it explicitly instead of relying on defaults.
- If the CLI returns `account ID is required`, do not retry the same command. Resolve the account first, then retry with `--account <account-id>` or set `default_account` only if the user asks.

## Max Quantity

| Command | Required | Defaults / omit | Optional flags |
| --- | --- | --- | --- |
| `moomoo crypto max-qty <symbol>` | `symbol`; `--account` if no default account | `--type LIMIT`, `--currency USD`, `--coin` inferred from `symbol`, empty `--price` | `--account`, `--type`, `--currency`, `--coin`, `--price` |

Operational rules:

- For generic "maximum buy", "maximum sell", or "maximum tradable quantity" requests, prefer `--type MARKET` and usually omit `--price`. This is task-specific behavior, not the CLI default.
- When the user explicitly asks for capacity at a limit price, pass `--type LIMIT --price <price>`.
- For non-USD pairs, pass the settlement currency from the pair suffix, for example `ETHHKD` requires `--currency HKD`; otherwise the CLI default `USD` may infer the wrong coin.
- If a read-only `max-qty` call returns `unsupported order type`, retry once with `--type MARKET` and explain that the fallback follows the API error.

Examples:

- `moomoo crypto max-qty ETHHKD --account <account-id> --currency HKD --type MARKET`
- `moomoo crypto max-qty BTCUSD --account <account-id> --type MARKET`
- `moomoo crypto max-qty BTCUSD --account <account-id> --type LIMIT --price 65000`

## Crypto Orders

| Command | Required | Defaults / omit | Optional flags |
| --- | --- | --- | --- |
| `moomoo crypto order place <symbol>` | `symbol`, `--side`; `--account` if no default account; one of `--qty` or `--cash-qty` | `--type LIMIT`, `--time-in-force TIF_GTC`, auto `--req-id` | `--account`, `--side`, `--req-id`, `--type`, `--time-in-force`, `--price`, `--qty`, `--cash-qty`, `--expire-time`, `--conditional-info` |
| `moomoo crypto order buy <symbol>` | `symbol`; `--account` if no default account; one of `--qty` or `--cash-qty` | fixed `BUY`, `--type LIMIT`, `--time-in-force TIF_GTC`, auto `--req-id` | same as place but do not pass `--side` |
| `moomoo crypto order sell <symbol>` | `symbol`; `--account` if no default account; usually `--qty` | fixed `SELL`, `--type LIMIT`, `--time-in-force TIF_GTC`, auto `--req-id` | same as place but do not pass `--side` |

Order examples:

- Limit buy: `moomoo crypto order buy BTCUSD --qty 0.01 --price 65000`
- Market cash buy: `moomoo crypto order buy BTCUSD --type MARKET --time-in-force TIF_IOC --cash-qty 100`
- Specific account sell: `moomoo crypto order sell ETHHKD --account <account-id> --qty 0.02 --price 50000`

## Modify, Cancel, Query

| Command | Required | Defaults / omit | Optional flags |
| --- | --- | --- | --- |
| `moomoo crypto order modify <order-id>` | `order-id`, `--price`, `--qty`, `--order-version`, `--conditional-info`; `--account` if no default account | auto `--req-id` | `--account`, `--req-id`, `--price`, `--qty`, `--order-version`, `--conditional-info` |
| `moomoo crypto order cancel <order-id>` | `order-id`; `--account` if no default account | auto `--req-id` | `--account`, `--req-id` |
| `moomoo crypto order list` | none if `default_account` is configured | `--page-size 50`, `--page-flag ""` | `--account`, `--page-size`, `--page-flag` |
| `moomoo crypto order history` | none if `default_account` is configured | last 3 months, `--page-size 50`, `--page-flag ""`, no filters | `--account`, `--start`, `--end`, `--page-size`, `--page-flag`, `--symbol`, `--order-status`, `--currency`, `--side`, `--type` |
| `moomoo crypto order detail <order-id> [order-id...]` | 1-20 `order-id` values; `--account` if no default account | none | `--account` |
| `moomoo crypto deal <order-id>` | `order-id`; `--account` if no default account | `--page-size 50`, `--page-flag ""`, `--group-by-order=false` | `--account`, `--page-size`, `--page-flag`, `--group-by-order` |
| `moomoo crypto deal history` | none if `default_account` is configured | last 3 months, `--page-size 50`, `--page-flag ""`, `--group-by-order=false`, no `--symbol` filter | `--account`, `--start`, `--end`, `--symbol`, `--page-size`, `--page-flag`, `--group-by-order` |

Query output notes:

- Order list/history table reads compatible aliases for `Symbol`, `Side`, `Type`, `Qty`, `Filled`, `Status`, and `Time`; use `--format json` when exact backend field names matter.
- Fill list/history table reads compatible aliases for `DealID`, `OrderID`, `Symbol`, `Side`, `Price`, `Qty`, `Amount`, and `Time`; `--group-by-order` aggregates quantity and amount by order and computes `AvgPrice = Amount / Qty`.
- If `page_flag` is returned and `completed` is false, pass it back as `--page-flag` to fetch the next page.
