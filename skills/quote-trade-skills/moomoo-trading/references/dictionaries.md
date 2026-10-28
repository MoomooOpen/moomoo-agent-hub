# Dictionaries

## Accounts And Markets

Account types:

| Value | Meaning |
| --- | --- |
| `cash` | Cash account |
| `margin` | Margin account |

`security_firm` (for `moomoo margin-ratio --security-firm`): `FUTUSECURITIES`, `FUTUINC`, `FUTUSG`, `FUTUCA`, `FUTUMY`, `FUTUAU`. Read from `moomoo account list --format json` when unknown.

Account `markets` numeric values:

| Value | Meaning |
| --- | --- |
| `1` | Hong Kong |
| `2` | United States |
| `4` | China Connect |
| `5` | Futures |
| `6` | Singapore |
| `7` | Cryptocurrency |
| `8` | Australia |
| `9` | Foreign Exchange |
| `10` | Bonds |
| `11` | Malaysia |
| `12` | Canada |
| `14` | Mutual Funds |
| `15` | Japan |
| `16` | Structured Notes |
| `17` | Event Contracts |
| `18` | South Korea |

Common `--market` values: `HK`, `US`, `HKCC`, `SG`, `JP`, `AU`, `MY`, `KR`.

`--exchange` is used by modify, cancel, and order detail. Common values: use `US` for US securities, and `HK` or API-required `SEHK` for Hong Kong securities.

## Symbols

- US stocks: `US.AAPL`
- Hong Kong stocks: `HK.00700`
- Always use `MARKET.CODE` for securities symbols. Do not use old suffix format such as `700.HK`, bare code `700`, or bare ticker `AAPL`.
- The CLI normalizes lowercase input and Hong Kong numeric codes: `us.aapl` becomes `US.AAPL`; `HK.700` becomes `HK.00700`.
- Let the CLI parse symbols into the API format. If the market is ambiguous, ask the user.

## Securities Order Sides

| Value | Meaning |
| --- | --- |
| `BUY` | Buy |
| `SELL` | Sell |
| `SELL_SHORT` | Sell short |
| `BUY_BACK` | Buy back |

## Securities Order Types

The CLI uppercases supported input. If the user does not specify an order type, omit `--type market`.

| Value | Meaning |
| --- | --- |
| `limit` / `LIMIT` | Limit order |
| `market` / `MARKET` | Market order |
| `AUCTION` | Auction market order |
| `AUCTION_LIMIT` | Auction limit order |
| `STOP` | Stop order |
| `STOP_LIMIT` | Stop-limit order |
| `MARKET_IF_TOUCHED` | Market-if-touched order |
| `LIMIT_IF_TOUCHED` | Limit-if-touched order |

## Other Order Enums

| Flag | Values |
| --- | --- |
| `--time-in-force` | `DAY`, `GTC` |
| `--lot-type` | `ROUND`, `ODD` |
| `--session` | `RTH`, `RTH+Pre/Post-Mkt`, `OVERNIGHT`, `ALL_DAY` |
| `--order-class` | `MLEG` |

## Order Status

| Value | Meaning |
| --- | --- |
| `WAITING_SUBMIT` | Waiting to submit |
| `SUBMITTING` | Submitting |
| `SUBMITTED` | Submitted |
| `FILLED_PART` | Partially filled |
| `FILLED_ALL` | Fully filled |
| `CANCELLED_PART` | Partially filled then cancelled |
| `CANCELLED_ALL` | Fully cancelled |
| `FAILED` | Failed |
| `DISABLED` | Disabled |
| `DELETED` | Deleted |

## Output Field Normalization

Order JSON:

| CLI field | Backend fields accepted |
| --- | --- |
| `symbol` | `symbol`, `code` |
| `side` | `side`, `trd_side` |
| `type` | `type`, `order_type` |
| `filled_qty` | `filled_qty`, `dealt_qty` |
| `status` | `status`, `order_status` |
| `create_time` | `create_time` |

Deal JSON:

| CLI field | Backend fields accepted |
| --- | --- |
| `symbol` | `symbol`, `code` |
| `side` | `side`, `trd_side` |
| `time` | `time`, `create_time` |
| `counter_broker_id` | string or numeric `counter_broker_id` |

Table time columns are displayed in UTC+8. JSON output keeps raw timestamp values.

## Common Errors

- `account ID is required`: no `default_account` is configured and `--account` was omitted; list accounts or ask the user to choose one.
- `unsupported order type`: the order type is not supported by the current endpoint, market, or symbol. For read-only queries, retry with a broader order type when appropriate; for real orders, ask the user before changing order type.
- `symbol must use MARKET.CODE format`: ask the user for market or normalize to `US.AAPL` / `HK.00700` before retrying.
- `PERMISSION_DENIED`: server-side permission denial, not a missing token header.
