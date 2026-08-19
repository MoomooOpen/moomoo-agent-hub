<!-- TOC: Script Index -->
# Script Index

Full script listing under scripts/{quote,trade,subscribe}.

```
skills/moomooapi/
├── SKILL.md
└── scripts/
    ├── common.py                      # Common utilities & config
    ├── quote/                         # Market data scripts
    │   ├── collect.py                 # One-shot panorama collector (quote+financials+rating+valuation+options)
    │   ├── get_snapshot.py            # Market snapshot (no subscription needed)
    │   ├── get_kline.py               # Candlestick data (real-time/historical)
    │   ├── get_stock_quote.py         # Real-time quotes for subscribed stocks
    │   ├── get_orderbook.py           # Order book / depth
    │   ├── get_ticker.py              # Tick-by-tick trades
    │   ├── get_broker_queue.py        # Broker bid/ask queue
    │   ├── get_rt_data.py             # Time-sharing data
    │   ├── get_rehab.py               # Rehabilitation factors
    │   ├── get_market_state.py        # Market state
    │   ├── get_global_state.py        # OpenD global state
    │   ├── get_trading_days.py        # Trading days list
    │   ├── get_capital_flow.py        # Capital flow
    │   ├── get_capital_distribution.py # Capital distribution
    │   ├── get_plate_list.py          # Plate/sector list
    │   ├── get_plate_stock.py         # Plate constituents
    │   ├── get_stock_info.py          # Stock basic info
    │   ├── get_search_quote.py        # Search quote instruments
    │   ├── get_search_news.py         # Search news
    │   ├── get_stock_filter.py        # Stock screener (V1, legacy)
    │   ├── get_stock_screen.py        # Stock screener V2 (broader factors, builder API)
    │   ├── get_owner_plate.py         # Stock's plates/sectors
    │   ├── get_referencestock_list.py # Related warrants/futures for underlying
    │   ├── get_warrant.py             # Warrants / CBBCs list
    │   ├── get_warrant_screen.py     # Warrant screener V2 (HK/SG/MY, 43 columns)
    │   ├── get_option_expiration_date.py # Option expiration dates
    │   ├── get_option_chain.py        # Option chain
    │   ├── get_option_screen.py       # Option screener (mixed underlying + option factors)
    │   ├── resolve_option_code.py     # Resolve option shorthand code
    │   ├── get_future_info.py         # Futures contract info
    │   ├── get_ipo_list.py            # IPO list
    │   ├── get_history_kl_quota.py    # Historical Candlestick quota
    │   ├── get_user_info.py           # User quote permission info
    │   ├── get_user_security.py       # User watchlist stocks
    │   ├── get_user_security_group.py # User watchlist groups
    │   ├── modify_user_security.py    # Add/remove watchlist stocks
    │   ├── get_price_reminder.py      # Price reminders list
	│   ├── set_price_reminder.py      # Set price reminder
    │   ├── get_financials_earnings_price_move.py    # Earnings day price move
    │   ├── get_financials_earnings_price_history.py # Earnings day price history
    │   ├── get_financials_statements.py             # Financial statements
    │   ├── get_financials_revenue_breakdown.py      # Revenue breakdown by segment
    │   ├── get_research_analyst_consensus.py        # Analyst consensus ratings
    │   ├── get_research_rating_summary.py           # Rating summary by institution/analyst
    │   ├── get_research_morningstar_report.py       # Morningstar research report
    │   ├── get_valuation_detail.py                  # Valuation detail & history
    │   ├── get_valuation_plate_stock_list.py        # Plate valuation stock list
    │   ├── get_corporate_actions_dividends.py       # Dividend history
    │   ├── get_corporate_actions_buybacks.py        # Buyback records
    │   ├── get_corporate_actions_stock_splits.py    # Stock split/merge records
    │   ├── get_shareholders_overview.py             # Shareholders overview
    │   ├── get_shareholders_holding_changes.py      # Holder holding changes
    │   ├── get_shareholders_holder_detail.py        # Holder detail list
    │   ├── get_shareholders_institutional.py        # Institutional holdings
    │   ├── get_insider_holder_list.py               # Insider holder list
    │   ├── get_insider_trade_list.py                # Insider trade list
    │   ├── get_company_profile.py                   # Company profile
    │   ├── get_company_executives.py                # Company directors & executives
    │   ├── get_company_executive_background.py      # Executive background
    │   ├── get_company_operational_efficiency.py    # Operational efficiency metrics
    │   ├── get_top_ten_buy_sell_brokers.py          # Top 10 buy/sell brokers HK
    │   ├── get_daily_short_volume.py                # Daily short volume US/HK
    │   ├── get_short_interest.py                    # Short interest US/HK
    │   ├── get_option_volatility.py                 # Option volatility analysis
    │   ├── get_option_exercise_probability.py       # Option exercise probability
    │   ├── get_option_strategy.py                   # Option strategy combo legs
    │   ├── get_option_strategy_spread.py            # Option strategy valid spreads
    │   ├── get_option_quote.py                      # Option snapshot quote
    │   ├── get_option_strategy_analysis.py          # Option strategy P&L analysis
    │   ├── get_option_market_statistic.py           # Option market statistics (volume/OI time series)
    │   ├── get_option_underlying_his_statistic.py   # Option underlying historical stats (P/C ratio)
    │   ├── get_option_underlying_overview.py        # Batch underlying snapshot (IV/HV multi-period)
    │   ├── get_option_underlying_his_volatility.py  # Underlying historical volatility (IV/HV series)
    │   ├── get_option_underlying_rank.py            # Underlying rank (13 sort types + filters)
    │   ├── get_option_rank.py                       # Option contract rank (10 sort types + filters)
    │   ├── get_option_event.py                      # Option unusual activity (25+ filters)
    │   ├── get_option_event_alert.py                # Get option event alert settings
    │   ├── set_option_event_alert.py                # Set option event alert conditions
    │   ├── get_option_zero_dte_screener.py          # 0DTE underlying screener
    │   ├── get_option_zero_dte_contract.py          # 0DTE contract details
    │   ├── get_option_earnings_screener.py          # Earnings option screener (IV Crush)
    │   ├── get_option_seller_screener.py            # Seller strategy screener (CC/CSP)
    │   ├── get_indicator_list.py                    # Indicator list (all available indicators)
    │   ├── get_indicator_calc_result.py             # Indicator calc result (Candlestick + params → push result)
    │   ├── get_hot_list.py                        # Hot list rank (volume ratio/price change etc.)
    │   ├── get_top_movers_rank.py                 # Top movers (gainers/losers)
    │   ├── get_period_change_rank.py              # Period change rank
    │   ├── get_us_pre_market_rank.py              # US pre-market rank
    │   ├── get_us_after_hours_rank.py             # US after-hours rank
    │   ├── get_us_overnight_rank.py               # US overnight rank
    │   ├── get_short_selling_rank.py              # Short selling rank
    │   ├── get_earnings_calendar.py               # Earnings calendar
    │   ├── get_earnings_beat_rank.py              # Earnings beat rank
    │   ├── get_economic_calendar.py               # Economic event calendar
    │   ├── get_dividend_calendar.py               # Dividend calendar
    │   ├── get_dividend_rank.py                   # Dividend rank
    │   ├── get_high_dividend_soe_rank.py          # High dividend SOE rank (HK only)
    │   ├── get_ark_fund_holding.py                # ARK fund holding
    │   ├── get_ark_active_transaction.py          # ARK active transactions
    │   ├── get_ark_stock_dynamic.py               # ARK stock dynamic
    │   ├── get_industrial_chain_list.py           # Industrial chain list
    │   ├── get_industrial_chain_detail.py         # Industrial chain detail
    │   ├── get_industrial_chain_by_plate.py       # Industrial chain by plate
    │   ├── get_industrial_plate_info.py           # Industrial plate info
    │   ├── get_industrial_plate_stock.py          # Industrial plate stocks
    │   ├── get_institution_list.py                # Institution list
    │   ├── get_institution_profile.py             # Institution profile
    │   ├── get_institution_holding_list.py        # Institution holding list
    │   ├── get_institution_holding_change.py      # Institution holding change
    │   ├── get_institution_distribution.py        # Institution distribution
    │   ├── get_macro_indicator_list.py            # Macro indicator list
    │   ├── get_macro_indicator_history.py         # Macro indicator history
    │   ├── get_fed_watch_target_rate.py           # FedWatch target rate
    │   ├── get_fed_watch_dot_plot.py              # FedWatch dot plot
    │   ├── get_heat_map_data.py                   # Heat map data
    │   ├── get_rise_fall_distribution.py          # Rise/fall distribution
    │   ├── get_rating_change.py                   # Rating change
    │   ├── get_event_contract_category.py                 # Prediction market category list
    │   ├── filter_competition.py                          # Prediction market competition filter
    │   ├── get_event_contract_series_list.py              # Prediction market series list
    │   ├── get_event_contract_event_list.py               # Prediction market event list
    │   ├── get_event_contract.py                          # Prediction market contract list
    │   ├── get_event_contract_milestone_list.py           # Prediction market milestone list
    │   ├── get_valid_combo_list.py                        # Valid combo event list (with mvc)
    │   ├── request_combo_quotes.py                        # Combo RFQ
    │   ├── get_event_contract_snapshot.py                 # Prediction market snapshot
    │   ├── get_event_contract_order_book.py               # Prediction market order book (subscribe required)
    │   ├── get_event_contract_kline.py                    # Prediction market K-line (subscribe required)
    │   ├── get_event_contract_ticker.py                   # Prediction market ticker (subscribe required)
    │   └── request_history_event_contract_kline.py        # Prediction market historical K-line (no subscription needed)
    ├── trade/                         # Trading scripts
    │   ├── get_accounts.py            # Account list
    │   ├── get_portfolio.py           # Positions & funds
    │   ├── get_all_portfolios.py      # All accounts positions & funds
    │   ├── place_order.py             # Place order
    │   ├── place_combo_order.py       # Place combo order
    │   ├── modify_order.py            # Modify order
    │   ├── cancel_order.py            # Cancel order
    │   ├── get_orders.py              # Today's orders
    │   ├── get_history_orders.py      # Historical orders
    │   ├── get_order_fill_list.py     # Today's fills
    │   ├── get_history_order_fill_list.py # Historical fills
    │   ├── get_acc_cash_flow.py       # Cash flow records
    │   ├── get_order_fee.py           # Order fees
    │   ├── get_margin_ratio.py        # Margin ratio
    │   ├── get_max_trd_qtys.py        # Max tradeable quantities
    │   ├── comboorder_tradinginfo_query.py # Query combo order trading info
    │   ├── get_crypto_accounts.py     # Crypto account list
    │   ├── get_crypto_portfolio.py    # Crypto portfolio (funds + positions)
    │   ├── place_crypto_order.py      # Crypto place order
    │   ├── cancel_crypto_order.py     # Crypto cancel / cancel-all
    │   ├── get_crypto_orders.py       # Crypto order query
    │   ├── get_crypto_cash_flow.py    # Crypto cash flow
    │   ├── get_crypto_max_trd_qtys.py # Crypto max tradable quantity (cash account only)
    │   └── get_crypto_order_fee.py    # Crypto order fee query
    └── subscribe/                     # Subscription scripts
        ├── subscribe.py               # Subscribe to market data
        ├── unsubscribe.py             # Unsubscribe
        ├── unsubscribe_all.py         # Unsubscribe all
        ├── query_subscription.py      # Query subscription status
        ├── push_quote.py              # Receive quote pushes
        ├── push_kline.py              # Receive Candlestick pushes
        ├── push_broker.py             # Receive broker queue pushes
        ├── push_orderbook.py          # Receive order book pushes
        ├── push_ticker.py             # Receive tick-by-tick pushes
        ├── push_rt_data.py            # Receive time-sharing pushes
        ├── push_option_event.py       # Receive option event pushes
        ├── subscribe_event_contract.py        # Subscribe prediction market
        ├── unsubscribe_event_contract.py      # Unsubscribe prediction market
        ├── unsubscribe_all_event_contract.py  # Unsubscribe all prediction market subscriptions
        ├── push_event_contract_orderbook.py   # Receive prediction market order book push
        ├── push_event_contract_kline.py       # Receive prediction market K-line push
        └── push_event_contract_ticker.py      # Receive prediction market ticker push
```

---

**Related skills routing:** Related: script path lookup rules in SKILL.md 'Script Path Lookup Rules'.
