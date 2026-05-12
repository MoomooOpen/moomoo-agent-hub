# Position & Funds Field Mapping (Aligned with moomoo App)

## Single Position Fields

Among the fields returned by `position_list_query`, there are several easily confused cost/P&L fields. **You must use fields consistent with the moomoo app**, otherwise P&L data will not match what the user sees in the app, which may confuse users.

| moomoo App Display | Correct API Field | Description |
|-------------|-------------------|-------------|
| Average Cost | `average_cost` | Actual average purchase price |
| Current Price | `nominal_price` | Current market price |
| Market Value | `market_val` | Single position market value (in the position's original currency) |
| Quantity | `qty` | Number of shares held |
| Sellable Quantity | `can_sell_qty` | Number of shares available to sell |
| Unrealized P&L | `unrealized_pl` | Floating P&L based on average cost |
| Unrealized P&L Ratio | `pl_ratio_avg_cost` | P&L percentage based on average cost (e.g., 5.23 means 5.23%) |
| Realized P&L | `realized_pl` | P&L from closed positions |
| Total P&L | `unrealized_pl + realized_pl` | Unrealized + Realized |
| Today's P&L | `today_pl_val` | P&L for the day |

## Position Summary Fields (moomoo app top bar)

| moomoo App Display | Correct Source | Description |
|-------------|---------------|-------------|
| Market Value (CAD) | `accinfo_query(currency=CAD).market_val` | Use the account funds API with CAD denomination; **do not** directly sum position `market_val` values (positions may be in different currencies, e.g., USD and CAD mixed) |
| Position P&L | Must be converted to CAD denomination before aggregation | Directly summing `unrealized_pl` will be inaccurate due to mixed currencies; use account-level summary data |
| Today's P&L | Must be converted to CAD denomination before aggregation | Same as above |

> **Currency Conversion Note**: When positions involve multiple currencies (e.g., holding both USD and CAD stocks), aggregated market value and P&L **require currency conversion** — do not directly sum values in different currencies. Prefer using `accinfo_query(currency=target_currency)` to get account-level summary data; if manual conversion is needed, look up the real-time exchange rate online (e.g., search "USD to CAD exchange rate") to get the latest rate, avoid using hardcoded rates.

## Forbidden Fields

Diluted cost basis, inconsistent with moomoo app display:
- `cost_price` / `diluted_cost`: Diluted cost, includes adjustments for dividends, stock splits, etc., which lowers the cost price
- `pl_val`: P&L calculated on diluted cost, may show profit when there is actually a loss
- `pl_ratio`: P&L ratio calculated on diluted cost

> **Verified**: The above field mapping has been verified by comparing moomoo app screenshots with API return values field by field (2026-03-20). All static values match exactly; minor differences in real-time price fields are due to price fluctuations between queries.

## Account Funds Field Mapping

Field mapping between `accinfo_query` return values and the moomoo app:

| moomoo App Display | API Field | Description |
|-------------|-----------|-------------|
| Total Assets | `total_assets` | Account net asset value |
| Securities Market Value | `market_val` | Total market value of all positions |
| Long Market Value | `long_mv` | Long position market value |
| Short Market Value | `short_mv` | Short position market value |
| Available Funds | `total_assets - initial_margin` | API's `available_funds` returns N/A for Canadian accounts, manual calculation needed |
| Frozen Cash | `frozen_cash` | |
| Total Cash | `cash` | Cash in the queried currency |
| USD Cash | `us_cash` | |
| CAD Cash | `ca_cash` | |
| Withdrawable Total | `avl_withdrawal_cash` | |
| USD Withdrawable | `us_avl_withdrawal_cash` | |
| CAD Withdrawable | `ca_avl_withdrawal_cash` | |
| Max Buying Power | `power` | |
| CAD Buying Power | `cad_net_cash_power` | |
| USD Buying Power | `usd_net_cash_power` | |
| Risk Status | `risk_status` | LEVEL3=Safe, LEVEL2=Warning, LEVEL1=Danger |
| Initial Margin | `initial_margin` | |
| Maintenance Margin | `maintenance_margin` | |
| Remaining Liquidity | No direct field | Not returned by API, must be calculated manually |
| Leverage Ratio | No direct field | Not returned by API, must be calculated manually |

**Notes**:
- Canadian accounts (FUTUCA) must specify `currency` (`USD` or `CAD`) when querying funds, otherwise it will return error "This account does not support converting to this currency"
- `available_funds` returns N/A for some account types; in such cases, use `total_assets - initial_margin` to calculate available funds
- `max_withdrawal` returns N/A for some account types

## Cryptocurrency Account Fields (OpenCryptoTradeContext only)

### New Fields in `accinfo_query`

| moomoo App Display | API Field | Type | Description |
|-------------|-----------|------|-------------|
| Crypto Market Value | `crypto_mv` | float | Crypto position market value |
| Total Assets | `total_assets` | float | = crypto_mv + total cash |
| Exposure Limit | `exposure_limit` | float | In USD |
| Used Exposure Limit | `used_limit` | float | In USD; = crypto position MV + crypto open buy order amount |
| Remaining Exposure Limit | `remaining_limit` | float | In USD; = exposure_limit - used_limit, min 0 |
| Exposure Limit Status | `exposure_level` | ExposureLevel | Only returned for crypto accounts; see below |

### ExposureLevel Enum

| Value | Meaning | Condition |
|-------|---------|-----------|
| `NORMAL` | Normal | remaining/limit > 10%, buying allowed |
| `NEAR_LIMIT` | Near limit | 0% < remaining/limit ≤ 10% |
| `RESTRICTED` | Restricted | remaining = 0%, buying forbidden |
| `SAFE` | Safe | equity with loan ≥ initial margin requirement |
| `MODERATE` | Moderate | remaining liquidity ≥ 10% × equity with loan |
| `WARNING` | Warning | remaining liquidity < 10% × equity with loan |
| `MARGIN_CALL` | Margin call | equity with loan ≤ maintenance margin requirement |

> The original `CltRiskStatus` field is preserved; the new `exposure_level` only applies to crypto accounts.

### Position Fields (`position_list_query`)

Crypto positions largely mirror securities positions, with these differences:

| Field | Crypto Handling |
|-------|----------------|
| `code` | Base currency only, e.g., `CC.BTC` (not `CC.BTCUSD`) |
| `stock_name` | Full coin name, e.g., "Bitcoin" |
| `position_market` | `CRYPTO` |
| `qty` / `can_sell_qty` | float (fractional quantities supported, e.g., `0.00004765`) |
| `position_side` | Fixed `LONG` |
| `currency` | **New field**, only returned for crypto, default USD |
| Today's statistics | No "today" concept for crypto; related fields have no value |
| Other fields | Return N/A when no value |

### Cash Flow Fields (`get_acc_cash_flow`)

| Field | Securities/Futures Account | Crypto Account |
|-------|---------------------------|----------------|
| Query param | `clearing_date` required (single day) | `start` + `end` required (range) |
| Query basis | Clearing date | Creation time (`create_time`) |
| `settlement_date` | Has value | Returns `N/A` |
| `create_time` | Hidden | **New field**, returns creation time |

> Missing required params raises: "{account} only supports querying cash flow by {parameter}"
