# Sim Trading Dictionaries

Use this reference to map user language to `moomoo sim ...` CLI values. Prefer values supported by `references/cli-parameters.md` over raw OpenAPI numeric enums.

## Scope

- This dictionary is only for simulated trading commands under `moomoo sim ...`.
- Do not reuse real trading-only values unless the simulated command reference explicitly supports them.
- If a user asks about real account markets, real order features, crypto pairs, or quote enums, use the relevant non-sim skill instead.

## Account

`--account` is the simulated trading business account ID, sourced from `moomoo sim account list` response field `accountId`.

Do not assume a real securities account ID is valid for simulation. When uncertain, list simulated accounts first:

```bash
moomoo sim account list --format json
```

## Symbol

Simulated trading symbols use `MARKET.CODE`:

| User wording | CLI symbol example |
| --- | --- |
| Apple / AAPL / 美股苹果 | `US.AAPL` |
| Tencent / 腾讯 / 700 港股 | `HK.00700` |

Rules:

- `HK.700` is normalized by the CLI to `HK.00700`.
- Bare codes such as `AAPL` or `700` require market resolution before command execution.
- Old suffix format such as `700.HK` should not be passed directly.

## Market

| CLI value | Meaning | Typical symbols |
| --- | --- | --- |
| `HK` | Hong Kong simulated trading | `HK.00700` |
| `US` | US simulated trading | `US.AAPL` |
| `US_OPTION` | US option simulated trading | US option-related symbols |
| `HKCC` | China Connect / Hong Kong Connect simulated market | eligible connect symbols |
| `CN` | Alias accepted by current guide for China/HKCC-style simulated market | use only when the user or CLI help indicates it |

CLI values are strings; do not pass the backend numeric market enum unless a command explicitly asks for it.

## Side

| CLI value | Meaning | Usage |
| --- | --- | --- |
| `BUY` | Buy | `moomoo sim order place <qty> --side BUY`, or `moomoo sim order buy` |
| `SELL` | Sell | `moomoo sim order place <qty> --side SELL`, or `moomoo sim order sell` |

The `buy` and `sell` subcommands fix the side automatically. Only `moomoo sim order place` needs `--side`.

## Order Type

| CLI value | Meaning | Usage |
| --- | --- | --- |
| `market` | Market order | Default; omit `--type` unless changing behavior or clarity is needed. |
| `limit` | Limit order | Usually requires `--price`. |

For max quantity checks, use `--type limit --price <price>` only when the user asks for capacity at a specific price.

## Session

| CLI value | Meaning | Usage |
| --- | --- | --- |
| `RTH` | Regular trading hours | Pass only when the user explicitly asks for regular session. |
| `EXTENDED` | Extended session, mainly US pre/post market | Pass when the user asks for pre-market, after-hours, or extended session. |

If the user does not specify a session, omit `--session` and let the backend default apply.

## Order Status

When interpreting simulated order statuses, preserve the raw returned value and add a plain-language explanation. Common meanings:

| Meaning | Explanation |
| --- | --- |
| Waiting / submitting | The order is still being submitted and should not be treated as filled. |
| Submitted | The order reached the simulated matching system or market. |
| Partially filled | Some quantity filled and the rest may remain active or later be canceled. |
| Fully filled | The full order quantity filled. |
| Canceled | The order was canceled, possibly after a partial fill. |
| Failed / disabled / deleted | The order did not remain active; inspect the returned error or status fields. |

Do not classify unknown statuses as filled or canceled without evidence from the response.

## Common Errors

| Error | Likely action |
| --- | --- |
| `account ID is required` | Run `moomoo sim account list --format json`, select a simulated account, then retry with `--account`. |
| `order_id is required` | Ask for an order ID or run `moomoo sim order list` to find the target simulated order. |
| `unsupported market` | Check `--market`, symbol market, and simulated account market compatibility. |
| `unsupported order type` | Use an order type supported by the simulated market, commonly `market` or `limit`. |
| `PERMISSION_DENIED` | Treat as server-side permission or entitlement denial, not missing OAuth header. |
