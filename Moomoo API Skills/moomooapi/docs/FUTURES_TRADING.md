# Futures Trading Commands

Futures trading must use **`OpenFutureTradeContext`** (not the securities trading `OpenSecTradeContext`). Existing trading scripts (`place_order.py`, etc.) use `OpenSecTradeContext` and **are not applicable to futures**. Futures trading requires generating Python code directly.

## Key Differences: Futures vs Securities

| Feature | Securities Trading | Futures Trading |
|---------|-------------------|-----------------|
| Context | `OpenSecTradeContext` | `OpenFutureTradeContext` |
| Existing Scripts | `place_order.py` etc. available | Not available, must generate code |
| Paper Accounts | Allocated by market uniformly | Allocated independently per market (e.g., `FUTURES_SIMULATE_SG`) |
| Contract Code | Stock code (e.g., `HK.00700`) | Futures main contract code (e.g., `SG.CNmain`), automatically mapped to actual monthly contract after order |
| Quantity Unit | Shares | Contracts (lots) |

## SG Futures Contract Codes

Common SG futures main contracts (use `main` contract code to place orders, system automatically maps to current month contract):

| Code | Name | Lot Size |
|------|------|----------|
| `SG.CNmain` | A50 Index Futures Main | 1 |
| `SG.NKmain` | Nikkei Futures Main | 500 |
| `SG.FEFmain` | Iron Ore Futures Main | 100 |
| `SG.SGPmain` | MSCI SG Index Futures Main | 100 |
| `SG.TWNmain` | FTSE Taiwan Index Futures Main | 40 |

Query all SG futures contracts:
```python
from moomoo import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111, ai_type=1)
ret, data = quote_ctx.get_stock_basicinfo(Market.SG, SecurityType.FUTURE)
main_contracts = data[data['main_contract'] == True]
print(main_contracts[['code', 'name', 'lot_size']].to_string())
quote_ctx.close()
```

## Query Futures Accounts

Futures accounts are queried through `OpenFutureTradeContext`, managed separately from securities accounts:

```python
from moomoo import *
trd_ctx = OpenFutureTradeContext(host='127.0.0.1', port=11111, ai_type=1)
ret, data = trd_ctx.get_acc_list()
print(data.to_string())
trd_ctx.close()
```

Futures paper trading accounts are allocated independently per market. Check the `trdmarket_auth` field:
- `FUTURES_SIMULATE_SG`: SG futures paper trading
- `FUTURES_SIMULATE_HK`: HK futures paper trading
- `FUTURES_SIMULATE_US`: US futures paper trading
- `FUTURES_SIMULATE_JP`: JP futures paper trading
- `FUTURES`: Live futures

## Futures Paper Trading Order Flow

Paper trading (`TrdEnv.SIMULATE`) flow:

1. Query accounts with `OpenFutureTradeContext`, find the account whose `trdmarket_auth` includes the corresponding paper trading market (e.g., `FUTURES_SIMULATE_SG`)
2. Get contract quotes to confirm the price
3. Use AskUserQuestion to confirm order parameters (contract, direction, quantity, price)
4. Execute the order

```python
from moomoo import *

trd_ctx = OpenFutureTradeContext(host='127.0.0.1', port=11111, ai_type=1)

ret, data = trd_ctx.place_order(
    price=14782.0, qty=1, code='SG.CNmain',
    trd_side=TrdSide.BUY, order_type=OrderType.NORMAL,
    trd_env=TrdEnv.SIMULATE, acc_id=9492210
)

if ret == RET_OK:
    print('Order placed successfully:', data)
else:
    print('Order failed:', data)

trd_ctx.close()
```

## Futures Live Trading Order Flow

Same confirmation steps as "Live Trading Order Flow" (query accounts -> secondary confirmation -> execute), with differences:
- Use `OpenFutureTradeContext` instead of `OpenSecTradeContext`
- Filter `trdmarket_auth` containing `FUTURES`
- Confirmation prompt: "Confirm live futures order?"

```python
from moomoo import *

trd_ctx = OpenFutureTradeContext(host='127.0.0.1', port=11111, ai_type=1)

ret, data = trd_ctx.place_order(
    price=14785.0, qty=1, code='SG.CNmain',
    trd_side=TrdSide.BUY, order_type=OrderType.NORMAL,
    trd_env=TrdEnv.REAL, acc_id=281756475296104250
)

if ret == RET_OK:
    print('Live order placed successfully:', data)
else:
    print('Order failed:', data)

trd_ctx.close()
```

## Futures Position & Funds Query

```python
from moomoo import *

trd_ctx = OpenFutureTradeContext(host='127.0.0.1', port=11111, ai_type=1)

ret, data = trd_ctx.position_list_query(trd_env=TrdEnv.SIMULATE, acc_id=9492210)
if ret == RET_OK:
    print(data)

ret, data = trd_ctx.accinfo_query(trd_env=TrdEnv.SIMULATE, acc_id=9492210)
if ret == RET_OK:
    print(data)

trd_ctx.close()
```

## Futures Order Query & Cancellation

```python
from moomoo import *

trd_ctx = OpenFutureTradeContext(host='127.0.0.1', port=11111, ai_type=1)

ret, data = trd_ctx.order_list_query(trd_env=TrdEnv.SIMULATE, acc_id=9492210)
if ret == RET_OK:
    print(data)

ret, data = trd_ctx.modify_order(
    modify_order_op=ModifyOrderOp.CANCEL,
    order_id='7679570', qty=0, price=0,
    trd_env=TrdEnv.SIMULATE, acc_id=9492210
)

trd_ctx.close()
```

## Futures Contract Info Query

```python
from moomoo import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111, ai_type=1)
ret, data = quote_ctx.get_future_info(['SG.CNmain', 'SG.NKmain'])
if ret == RET_OK:
    print(data)  # Contains contract multiplier, minimum tick size, trading hours, etc.
quote_ctx.close()
```
