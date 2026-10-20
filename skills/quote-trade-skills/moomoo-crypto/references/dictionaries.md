# Dictionaries

## Pairs And Currency Inference

- `symbol` is uppercased automatically and may include or omit the `CC.` prefix.
- Crypto `symbol` values are trading pairs such as `BTCUSD`, not stock-style `MARKET.CODE` symbols.
- If `--coin` is omitted, the CLI infers the trading coin by removing the settlement currency suffix from `symbol`.
- `--currency` defaults to `USD`. For non-USD pairs, pass the settlement currency explicitly.

Examples:

| Pair | Recommended params |
| --- | --- |
| `BTCUSD` | `--currency` can be omitted, or pass `--currency USD` |
| `ETHHKD` | pass `--currency HKD` |
| `CC.ETHHKD` | pass `--currency HKD` |

## Crypto Sides And Order Types

| Field | Values | Notes |
| --- | --- | --- |
| `--side` | `BUY`, `SELL` | Required for `order place`; fixed by `buy` / `sell` subcommands, so do not pass it there. |
| `--type` | `LIMIT`, `MARKET` | CLI default is `LIMIT`; omit only when a default limit order is intended. |
| `--time-in-force` | `TIF_GTC`, `TIF_IOC` | CLI default is `TIF_GTC`; market cash buys commonly use `TIF_IOC`. |

## max-qty Fields

| Field | Meaning |
| --- | --- |
| `max_cash_buy_qty` | Maximum cash-buy quantity |
| `max_cash_buy_amount` | Maximum cash-buy amount |
| `max_sell_qty` | Maximum sell quantity |

`max-qty` is read-only. If `max_cash_buy_qty` and `max_cash_buy_amount` are `0` but `max_sell_qty` is positive, the account likely has sellable holdings but no cash buying power in the settlement currency.

## Order And Fill Filters

- `--order-status`: order status filter; use values returned by the API, comma-separated values allowed.
- `--side`: `BUY`, `SELL`, comma-separated values allowed.
- `--type`: order type filter, comma-separated values allowed.
- `--currency`: settlement currency filter, comma-separated values allowed.
- `--start` / `--end`: microsecond timestamps; historical orders/fills default to the last 3 months.
- Table time columns are displayed in UTC+8. JSON output keeps raw timestamp fields from the API.

## Table Field Aliases

Order tables:

| Column | Backend fields read by CLI |
| --- | --- |
| `OrderID` | `order_id` |
| `Symbol` | `symbol`, `code`, `trade_pair`, `trading_pair`, `symbol_pair.symbol`, or inferred from base/quote fields |
| `Side` | `side`, `trd_side` |
| `Type` | `ord_type`, `order_type`, `type` |
| `Qty` | `qty`, `quantity`, `order_qty`, `order_quantity` |
| `Filled` | `filled_qty`, `dealt_qty`, `filled_quantity`, `dealt_quantity`, `cum_qty` |
| `Status` | `status`, `order_status`, `ord_status`, `order_state` |
| `Time` | `create_time`, `created_time`, `time` |

Fill tables:

| Column | Backend fields read by CLI |
| --- | --- |
| `DealID` | `fill_id`, `deal_id`, `id` |
| `OrderID` | `order_id`, `ord_id`, `order_show_id` |
| `Symbol` | `symbol`, `code`, `trade_pair`, `trading_pair`, `symbol_pair.symbol`, or inferred from base/quote fields |
| `Side` | `side`, `trd_side` |
| `Price` | `price`, `fill_price`, `deal_price` |
| `Qty` | `qty`, `quantity`, `fill_qty`, `deal_qty` |
| `Amount` | `amount`, `fill_amount`, `deal_amount`, `exec_amount` |
| `Time` | `fill_time`, `filled_time`, `deal_time`, `trade_time`, `create_time`, `created_time`, `time`, `update_time` |

## Common Errors

- `unsupported order type`: the current pair or endpoint does not accept the given order type. For read-only `max-qty`, retry once with `--type MARKET`; for real orders, ask the user before changing order type.
- `account ID is required`: no `default_account` is configured and `--account` was omitted; list accounts or ask the user to choose one.
- `PERMISSION_DENIED`: server-side permission denial, not a missing token header.
