# CLI Parameters

Build commands with the minimum argument set: include required arguments, user-specified values, and flags needed to change CLI defaults. Do not add flags just because examples show defaults.

## Global Flags

| Flag | Default | When to pass |
| --- | --- | --- |
| `--format`, `-f` | `table` | Pass `--format json` only when the agent must parse output. Commands shown for a user to run can omit it. |
| `--token-file` | configured `token_file` | Pass only when the user asks for a non-default token file. |

Internal invocation convention: this skill always appends the hidden internal marker `--source skill` to the end of the command when invoking the CLI from Bash. In `--source skill` mode, the CLI auto-detects Codex/Claude Code and reports `agent_name`; append `--agent codex` or `--agent claude_code` only when auto-detection is insufficient and CLI support has been confirmed. Do not include these internal markers in commands shown to the user.

Securities symbols must use `MARKET.CODE`, for example `US.AAPL` or `HK.00700`. The CLI normalizes `HK.700` to `HK.00700` and `us.aapl` to `US.AAPL`; it rejects old suffix format `700.HK`, bare code `700`, and bare ticker `AAPL`.

Historical `--start` / `--end` filters are microsecond Unix timestamps. Table time columns are displayed in UTC+8, while JSON output preserves raw API fields.

Securities order and fill list commands auto-page internally. Pass `--page-size` only when changing the page size; there is no user-facing `--page-flag` for these commands.

## Auth And Status

| Command | Required | Defaults / omit | Notes |
| --- | --- | --- | --- |
| `moomoo auth status` | none | `--format table` | Shows local token, account, and permission state. |
| `moomoo check` | none | none | Checks local token usability and API reachability. |
| `moomoo auth login` | none | `--client-name` defaults to username and hostname, `--no-browser=false` | Pass `--no-browser` only in browserless environments. |
| `moomoo auth logout` | none | none | Deletes the local token. |
| `moomoo config set default_account <account-id>` | `key value` | none | Sets the default account. Commands supporting `default_account` can then omit `--account`. |

## Account Resolution

- For any command whose required column says "`--account` if no default account", do not omit `--account` unless this session has already confirmed a default account from `moomoo auth status --format json` or config.
- If no default account has been confirmed, run `moomoo account list --format json` or ask the user to choose an account, then pass `--account <account-id>` explicitly.
- If the user already provided an account ID in the request or recent context, pass it explicitly instead of relying on defaults.
- If the CLI returns `account ID is required`, do not retry the same command. Resolve the account first, then retry with `--account <account-id>` or set `default_account` only if the user asks.

## Accounts, Funds, Positions

| Command | Required | Defaults / omit | Optional flags |
| --- | --- | --- | --- |
| `moomoo account list` | none | none | none |
| `moomoo account funds` | none if `default_account` is configured | `--currency USD` | `--account`, `--currency` |
| `moomoo position` | none if `default_account` is configured | none | `--account`, `--symbol`, `--pl-ratio-min`, `--pl-ratio-max` |

Examples:

- Default account funds: `moomoo account funds`
- Specific account funds: `moomoo account funds --account <account-id>`
- Specific currency funds: `moomoo account funds --account <account-id> --currency HKD`
- Specific position: `moomoo position --symbol US.AAPL`
- Hong Kong position shorthand normalized by CLI: `moomoo position --symbol HK.700`

## Placing Orders

| Command | Required | Defaults / omit | Optional flags |
| --- | --- | --- | --- |
| `moomoo order buy <symbol> <qty>` | `symbol`, `qty`; `--account` if no default account | `--type market`, `--time-in-force DAY` | `--account`, `--price`, `--type`, `--time-in-force`, `--lot-type`, `--remark`, `--session`, `--aux-price`, `--order-class`, `--multi-leg-info` |
| `moomoo order sell <symbol> <qty>` | `symbol`, `qty`; `--account` if no default account | `--type market`, `--time-in-force DAY` | same as buy |
| `moomoo order place <qty>` | `qty`, `--side`; `--symbol` for regular orders; `--account` if no default account | `--type market`, `--time-in-force DAY` | same as buy |

Examples:

- User says "buy 1 Apple share" and a default account exists: `moomoo order buy US.AAPL 1`
- User says "buy 1 Apple share at 280 limit": `moomoo order buy US.AAPL 1 --price 280 --type limit`
- User specified an account: `moomoo order buy US.AAPL 1 --account <account-id> --price 280 --type limit`
- Multi-leg order: `moomoo order place 1 --side BUY --order-class MLEG --multi-leg-info '<json-object>'`

Order placement body mapping:

| CLI value | API field |
| --- | --- |
| `<symbol>` / `--symbol` | `code` |
| `--side` / buy / sell | `side` |
| `--type` | `order_type` |
| `<qty>` | `qty` |
| `--price` | `price` |
| `--time-in-force` | `time_in_force` |
| `--lot-type` | `lot_type` |
| `--remark` | `remark` |
| `--session` | `session` |
| `--aux-price` | `aux_price` |
| `--order-class` | `order_class` |
| `--multi-leg-info` | `multi_leg_info` |

## Modify, Cancel, Query

| Command | Required | Defaults / omit | Optional flags |
| --- | --- | --- | --- |
| `moomoo order modify <order-id>` | `order-id`, `--exchange`, `--qty`; `--account` if no default account | omit `--price` to leave price unchanged; omit `--aux-price` to leave trigger price unchanged | `--account`, `--exchange`, `--qty`, `--price`, `--aux-price` |
| `moomoo order cancel <order-id>` | `order-id`, `--exchange`; `--account` if no default account | none | `--account`, `--exchange` |
| `moomoo order list` | none if `default_account` is configured | `--market HK`, `--page-size 50` | `--account`, `--market`, `--page-size` |
| `moomoo order history` | none if `default_account` is configured | `--market HK`, `--page-size 50`, `--start 0`, `--end 0`, no `--symbol` filter | `--account`, `--market`, `--start`, `--end`, `--symbol`, `--page-size` |
| `moomoo order detail <order-id> [order-id...]` | `order-id`, `--exchange`; `--account` if no default account | none | `--account`, `--exchange` |
| `moomoo order max-qty <symbol>` | `symbol`; `--account` if no default account | `--type market`, empty `--price`, empty `--order-id` | `--account`, `--price`, `--type`, `--order-id` |
| `moomoo deal` | none if `default_account` is configured | `--market HK`, `--page-size 50` | `--account`, `--market`, `--page-size` |
| `moomoo deal history` | none if `default_account` is configured | `--market HK`, `--page-size 50`, `--start 0`, `--end 0`, no `--symbol` filter | `--account`, `--market`, `--start`, `--end`, `--symbol`, `--page-size` |

Query output notes:

- Order JSON normalizes backend `code` into `symbol`, `trd_side` into `side`, `order_type` into `type`, `dealt_qty` into `filled_qty`, and `order_status` into `status`; other backend fields remain as extras in JSON output.
- Deal JSON normalizes backend `code` into `symbol`, `trd_side` into `side`, and `create_time` into `time` when `time` is absent; backend list fields may be `order_fills`, `orders`, or `fills`.
- Order and deal table time columns use UTC+8 formatting. Detail rows ending in `_time` are also formatted when the value is numeric.

Query examples:

- Current orders with default market: `moomoo order list`
- Current US orders: `moomoo order list --market US`
- Specific order detail: `moomoo order detail <order-id> --exchange US`
- Max market quantity for Apple: `moomoo order max-qty US.AAPL`
- Max quantity for Apple at 280 limit: `moomoo order max-qty US.AAPL --price 280 --type limit`
- Max quantity with no confirmed default account: `moomoo order max-qty US.AAPL --account <account-id> --price 280 --type limit`
