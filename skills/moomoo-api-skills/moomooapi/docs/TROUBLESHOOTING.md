# Known Issues & Error Handling

## Known Issues

### Slow OpenD Connection / Multi-Account Query Timeout

**Symptom**: OpenD response slows down or times out when querying multiple accounts in succession, especially when creating multiple `OpenSecTradeContext` connections.

**Solution**:
- **Reuse the same connection**: Create `OpenSecTradeContext` only once, use the same `trd_ctx` to query all accounts, avoid repeatedly creating/closing connections
- **Do not loop-call scripts**: Do not run `get_portfolio.py` separately for each account (each run creates/closes a connection); instead, write Python code that completes all queries within a single connection
- **Add `sys.stdout.flush()`**: Flush output after each print in loops to avoid output buffering hiding intermediate results

### Non-Margin Account Fields Return N/A

**Symptom**: For non-margin accounts like TFSA, RRSP, the `accinfo_query` return has `initial_margin`, `maintenance_margin`, `available_funds`, and other margin-related fields as `N/A`, causing `ValueError` when directly converting with `float()`.

**Solution**:
- Use safe conversion for all numeric fields: `float(val) if val != 'N/A' else 0.0`
- When `available_funds` is N/A: for margin accounts, calculate with `total_assets - initial_margin`; for non-margin accounts (TFSA/RRSP), available funds equals `total_assets` (since there are no margin requirements)

### pandas and numpy Version Incompatibility

**Symptom**: Error `ValueError: numpy.dtype size changed` when running code.

**Solution**: `pip install --upgrade pandas`

## Error Handling

| Error | Solution |
|-------|----------|
| Connection failed | Start OpenD |
| Order not found | Check with get_orders.py |
| Account not found | Check with get_accounts.py. If no live trading accounts found, it may be a `security_firm` mismatch — run the brokerage auto-detection flow (get_accounts.py iterates all SecurityFirm values), or have the user confirm their region and manually specify `--security-firm` |
| OpenSecTradeContext cannot fetch live accounts | `create_trade_context()` defaults to `filter_trdmarket=TrdMarket.NONE` (no market filtering), but if you manually create `OpenSecTradeContext` with a specific market (e.g., `TrdMarket.US`, `TrdMarket.HK`), some accounts may be filtered out. Fix: change `filter_trdmarket` to `TrdMarket.NONE` and re-fetch to get all accounts |
| Trade unlock failed / `unlock needed` | Must unlock the trade password manually in the OpenD GUI |
| Insufficient market data permissions (e.g., subscription failed, BMP permission not supported) | Prompt the user to activate market data permissions, reference: https://openapi.moomoo.com/moomoo-api-doc/en/intro/authority.html |
| Insufficient futures buying power | Prompt the user to deposit funds or close some contracts to release margin |
| Futures order failed with OpenSecTradeContext | Futures must use `OpenFutureTradeContext`, not the securities trading context |
| Live order `Nonexisting acc_id` | The acc_id from `get_accounts.py --json` may have lost precision for large integers due to `int(float())` in `safe_int` (fixed). If still encountered, create context with `filter_trdmarket=TrdMarket.NONE` and print DataFrame directly to verify the real acc_id |
| Live order `unlock needed` | Live trading requires the user to first click "Unlock Trade" in the **OpenD GUI** and enter the trade password. The API cannot replace this operation. After unlocking, retry the order |
| Insufficient buying power | Account available funds are insufficient to complete the order. Use `get_portfolio.py` to view fund details; consider reducing quantity, selling positions to free up funds, or depositing and retrying |
| Paper trading account insufficient funds | Two ways to recover: 1) Sell existing positions to free up funds; 2) Reset the paper trading account in the moomoo app (go to Me -> Paper Trading -> tap your avatar -> My Items -> Revival Card; see https://openapi.moomoo.com/moomoo-api-doc/qa/trade.html#1690). Note: Resetting restores the initial balance but clears all historical order records |

## Custom Handler Template

For push types not covered by existing scripts (e.g., order book, tick-by-tick, trade pushes), generate temporary code:

```python
import time
from moomoo import *

class MyHandler(OrderBookHandlerBase):
    def on_recv_rsp(self, rsp_pb):
        ret_code, data = super().on_recv_rsp(rsp_pb)
        if ret_code != RET_OK:
            print("error:", data)
            return RET_ERROR, data
        print("Received push:")
        print(data)
        return RET_OK, data

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111, ai_type=1)
quote_ctx.set_handler(MyHandler())
ret, data = quote_ctx.subscribe(['HK.00700'], [SubType.ORDER_BOOK], subscribe_push=True)
if ret == RET_OK:
    print('Subscription successful, waiting for pushes...')
time.sleep(60)
quote_ctx.close()
```

## Brokerage Auto-Detection (security_firm)

On the first trading operation, if the environment variable `FUTU_SECURITY_FIRM` is not set, you need to determine the user's brokerage:

1. Run `get_accounts.py --json` to get all accounts (the script automatically iterates through all SecurityFirm values)
2. Check the `security_firm` field of accounts where `trd_env` is `REAL`
3. Use that value as the `--security-firm` parameter for all subsequent trading commands
4. If no live trading accounts are found after iterating, inform the user they may not have completed account opening, or confirm their region

Detection code example:

```python
from moomoo import *

FIRMS = ['FUTUSECURITIES', 'FUTUINC', 'FUTUSG', 'FUTUAU', 'FUTUCA', 'FUTUJP', 'FUTUMY']

for firm in FIRMS:
    trd_ctx = OpenSecTradeContext(
        filter_trdmarket=TrdMarket.NONE,
        host='127.0.0.1', port=11111,
        security_firm=getattr(SecurityFirm, firm),
        ai_type=1
    )
    ret, data = trd_ctx.get_acc_list()
    trd_ctx.close()
    if ret == RET_OK and not data.empty:
        real_accounts = data[data['trd_env'] == 'REAL']
        if not real_accounts.empty:
            print(f'Found live trading account, brokerage: {firm}')
            print(real_accounts.to_string())
            break
```
