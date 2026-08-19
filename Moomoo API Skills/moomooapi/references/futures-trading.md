<!-- TOC: Futures Trading Commands -->
# Futures Trading Commands

Full futures documentation (contract codes, accounts, orders, positions, cancels) in `docs/FUTURES_TRADING.md`.

## Futures Trading Commands

> Full futures trading documentation (contract codes, account queries, order flow, positions, cancellation, etc.) is in `docs/FUTURES_TRADING.md`.

**Key point**: Futures must use `OpenFutureTradeContext` (not `OpenSecTradeContext`). Ordinary futures orders may still need generated Python code. **Script path**: prediction markets (`EC.`) via `place_order.py` / `place_combo_order.py`; query/cancel/modify for futures/EC accounts with `--ctx-type FUTURE` (or auto-switch on `EC.` codes). Common SG futures main contracts: `SG.CNmain` (A50), `SG.NKmain` (Nikkei).

---

---

**Related skills routing:** Related: full futures docs → docs/FUTURES_TRADING.md; prediction market → prediction-market.md.
