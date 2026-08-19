<!-- TOC: Prediction Market Commands (Event Contract) -->
# Prediction Market Commands (Event Contract)

## Prediction Market Commands

Prediction markets are YES/NO binary contracts on future events (elections, economic data, sports, etc.). Contract code format is `EC.xxx` (e.g. `EC.KXODIMATCH-26JUL140600INDENG-IND`). Full call chain:

```
category(get_event_contract_category) -> filter_competition -> Series -> Event -> Contract -> snapshot/orderbook/kline/ticker
```

**Hard constraint (subscribe before querying)**: `get_event_contract_order_book` / `get_event_contract_kline` / `get_event_contract_ticker` require subscribing to the corresponding type (`SubType.ORDER_BOOK` / `K_DAY` etc. / `TICKER`) first; otherwise an error is returned. These scripts auto-subscribe by default (use `--no-auto-subscribe` to skip). `request_history_event_contract_kline` (historical K-line) and `get_event_contract_snapshot` require no subscription.

**K-line type limit**: Prediction market K-line only supports `K_1M`/`K_5M`/`K_60M`/`K_DAY`; others raise an error.

**Pagination**: `event_list` / `get_event_contract` / `milestone_list` / `valid_combo_list` return only the first page by default; to continue, pass the previous `next_page` via `--next-page`.

**SDK note**: Prediction market requires an SDK version that supports it. If the current moomoo-api does not support it, the scripts print a clear upgrade hint and exit (no crash).

## Table of Contents

- Get Prediction Market Category
- Filter Competition
- Get Prediction Market Series List
- Get Prediction Market Event List
- Get Prediction Market (Contract) List
- Get Prediction Market Milestone List
- Get Valid Combo Event List
- Combo RFQ
- Get Prediction Market Snapshot
- Get Prediction Market Order Book
- Get Prediction Market K-line
- Get Prediction Market Ticker
- Fetch Prediction Market Historical K-line
- Subscribe Prediction Market
- Unsubscribe Prediction Market
- Receive Prediction Market Pushes

---

### Get Prediction Market Category
```bash
python skills/moomooapi/scripts/quote/get_event_contract_category.py [--category Sports] [--json]
```

### Filter Competition
```bash
python skills/moomooapi/scripts/quote/filter_competition.py --category Sports [--tag Baseball] [--json]
```
- competition names can be passed as `--competition` to `get_event_contract_milestone_list`

### Get Prediction Market Series List
```bash
python skills/moomooapi/scripts/quote/get_event_contract_series_list.py --category Sports [--tag Football] [--json]
```

### Get Prediction Market Event List
```bash
python skills/moomooapi/scripts/quote/get_event_contract_event_list.py EC.KXUFCVICROUND.SERIES [--count 20] [--status EVENT_ACTIVE] [--next-page KEY] [--json]
```

### Get Prediction Market (Contract) List
```bash
python skills/moomooapi/scripts/quote/get_event_contract.py EC.KXUFCVICROUND-26JUL11SAIPIM.EVENT [--count 20] [--next-page KEY] [--json]
```
- the returned `contract_code` (`EC.xxx`) can be used as the `code` for snapshot/orderbook/kline/ticker

### Get Prediction Market Milestone List
```bash
python skills/moomooapi/scripts/quote/get_event_contract_milestone_list.py [--category Sports] [--competition "FIFA World Cup"] [--related-event EC.xxx] [--count 20] [--json]
```

### Get Valid Combo Event List
```bash
python skills/moomooapi/scripts/quote/get_valid_combo_list.py [--category Sports] [--count 20] [--json]
```
- the returned `mvc` must be passed through to `request_combo_quotes`

### Combo RFQ
```bash
python skills/moomooapi/scripts/quote/request_combo_quotes.py '[{"code":"EC.xxx-FRA","trd_side":"BUY","qty_ratio":1,"pred_side":"YES"},{"code":"EC.xxx-ENG","trd_side":"BUY","qty_ratio":1,"pred_side":"YES"}]' --mvc KALSHI.KXMVECROSSCATEGORY-R [--json]
```
- each leg: `code` (required) / `trd_side` (BUY/SELL/SELL_SHORT/BUY_BACK, required) / `qty_ratio` (required) / `pred_side` (YES/NO, required)
- at least 2 legs; can come from different events; `mvc` is passed through from `get_valid_combo_list`
- `quote_id` has a time limit; place the order soon via `place_combo_order.py` with `quote_id`

### Get Prediction Market Snapshot
```bash
python skills/moomooapi/scripts/quote/get_event_contract_snapshot.py EC.KXODIMATCH-26JUL140600INDENG-IND [--json]
```
- snapshot only returns the first bid/ask level; for multi-level depth use `get_event_contract_order_book`

### Get Prediction Market Order Book
```bash
python skills/moomooapi/scripts/quote/get_event_contract_order_book.py EC.KXODIMATCH-26JUL140600INDENG-IND [--num 5] [--json]
```

### Get Prediction Market K-line
```bash
python skills/moomooapi/scripts/quote/get_event_contract_kline.py EC.KXODIMATCH-26JUL140600INDENG-IND --ktype K_DAY --pre-side YES [--kline-source ORDER_BOOK_YES] [--max-count 10] [--json]
```

### Get Prediction Market Ticker
```bash
python skills/moomooapi/scripts/quote/get_event_contract_ticker.py EC.KXODIMATCH-26JUL140600INDENG-IND [--count 30] [--json]
```

### Fetch Prediction Market Historical K-line
```bash
python skills/moomooapi/scripts/quote/request_history_event_contract_kline.py EC.KXNFLAFCCHAMP-27-CIN --start 2026-07-05 --end 2026-07-09 --pre-side YES --ktype K_DAY [--max-count 10] [--json]
```

### Subscribe Prediction Market
```bash
python skills/moomooapi/scripts/subscribe/subscribe_event_contract.py EC.KXODIMATCH-26JUL140600INDENG-IND --types ORDER_BOOK TICKER K_DAY [--kline-source ORDER_BOOK_YES] [--json]
```
- to receive pushes, use the corresponding push scripts (`push_event_contract_*`) which set the handler, or register `EventContract*HandlerBase` yourself

### Unsubscribe Prediction Market
```bash
python skills/moomooapi/scripts/subscribe/unsubscribe_event_contract.py EC.xxx --types TICKER [--json]
python skills/moomooapi/scripts/subscribe/unsubscribe_all_event_contract.py [--json]
```

### Receive Prediction Market Pushes
```bash
python skills/moomooapi/scripts/subscribe/push_event_contract_orderbook.py EC.xxx --duration 60 [--json]
python skills/moomooapi/scripts/subscribe/push_event_contract_kline.py EC.xxx --ktype K_DAY [--duration 300] [--json]
python skills/moomooapi/scripts/subscribe/push_event_contract_ticker.py EC.xxx --duration 60 [--json]
```

---

**Related skills routing:** Related: options/strategy → options.md; combo order → trade-commands.md; EC push in-body subscribe section.
