# Quote 行情命名词典

本文根据 moomoo OpenAPI 官方行情命名词典整理，用于后续编写 moomoo CLI quote skill / wrapper 时快速查阅枚举值。

来源：moomoo OpenAPI `zh-cn/api/quote/naming-dictionary`，读取日期：2026-10-13。

## 使用约定

- 本文只覆盖行情（Quote）接口枚举；交易、模拟交易、加密货币交易枚举见对应模块文档。
- 表格中的 `取值` 应按原样传给 CLI flag 或解析 API 响应；数值型枚举保持数字。
- CLI 已统一证券代码入参为 `symbol`，格式为 `MARKET.CODE`，例如 `HK.00700`、`US.AAPL`；港股数字代码可补零。
- `N/A` 或空字符串表示官方未映射、非适用或未知状态，skill 不应把它当成异常。

## 目录

- [sec_status（证券状态）](#sec_status-证券状态)
- [dark_status（暗盘状态）](#dark_status-暗盘状态)
- [option_type（期权方向）](#option_type-期权方向)
- [option_area_type（期权行权类型）](#option_area_type-期权行权类型)
- [trust_assetClass（信托基金资产类别）](#trust_assetclass-信托基金资产类别)
- [ktype（K 线类型）](#ktype-k-线类型)
- [autype（复权类型）](#autype-复权类型)
- [extended_time（盘前盘后开关，仅美股 1 分 K 生效）](#extended_time-盘前盘后开关-仅美股-1-分-k-生效)
- [request_section（rt-data 交易时段，仅 get_rt_data 用）](#request_section-rt-data-交易时段-仅-get_rt_data-用)
- [capital_flow_section（capital_flow 交易时段，入参；仅 get_capital_flow 用）](#capital_flow_section-capital_flow-交易时段-入参-仅-get_capital_flow-用)
- [capital_flow_history_period_type（capital_flow_history 周期类型，入参）](#capital_flow_history_period_type-capital_flow_history-周期类型-入参)
- [trade_section（交易时段类型，出参；按市场细分）](#trade_section-交易时段类型-出参-按市场细分)
- [trade_date_type（交易日类型，出参）](#trade_date_type-交易日类型-出参)
- [ticker_direction（逐笔买卖方向）](#ticker_direction-逐笔买卖方向)
- [tick_type（逐笔成交类型，交易方式）](#tick_type-逐笔成交类型-交易方式)
- [period_type（逐笔所在时段）](#period_type-逐笔所在时段)
- [stock_type（标的类型）](#stock_type-标的类型)
- [state（证券生命周期状态）](#state-证券生命周期状态)
- [stock_child_type（窝轮子类型）](#stock_child_type-窝轮子类型)
- [action_type（公司行动事件类型，get_rehab 用）](#action_type-公司行动事件类型-get_rehab-用)
- [divi_mode（复权分红派息处理模式，get_rehab 入参用）](#divi_mode-复权分红派息处理模式-get_rehab-入参用)
- [plate_type（板块类型，出参）](#plate_type-板块类型-出参)
- [market_state（市场交易状态，get_market_state 出参）](#market_state-市场交易状态-get_market_state-出参)
- [trade_section_type（交易时段类型数值，get_market_state 出参）](#trade_section_type-交易时段类型数值-get_market_state-出参)
- [market（市场前缀）](#market-市场前缀)
- [plate_class（板块分类，板块接口用）](#plate_class-板块分类-板块接口用)
- [sort_field（板块成份股排序字段，get_plate_stock 入参用）](#sort_field-板块成份股排序字段-get_plate_stock-入参用)
- [price_type（价格类排序口径，get_plate_stock 入参用）](#price_type-价格类排序口径-get_plate_stock-入参用)
- [statement_type（财报报表类型，入参）](#statement_type-财报报表类型-入参)
- [financial_type（财报期类型，入参/出参）](#financial_type-财报期类型-入参-出参)
- [financial_structure（财报子结构编号，出参）](#financial_structure-财报子结构编号-出参)
- [expiration_cycle（期权到期周期）](#expiration_cycle-期权到期周期)
- [index_option_type（指数期权类型，入参）](#index_option_type-指数期权类型-入参)
- [filter_standard（标准/非标准期权过滤，入参）](#filter_standard-标准-非标准期权过滤-入参)
- [combo_strategy（组合期权策略类型，入参/出参）](#combo_strategy-组合期权策略类型-入参-出参)
- [option_standard_type（期权规格类型，出参）](#option_standard_type-期权规格类型-出参)
- [combo_leg_instrument（组合期权腿品类，出参）](#combo_leg_instrument-组合期权腿品类-出参)
- [combo_side（组合询价腿方向，入参/回显）](#combo_side-组合询价腿方向-入参-回显)
- [holder_type（股东类型，入参/出参）](#holder_type-股东类型-入参-出参)
- [pub_type（财报披露时点类型，出参）](#pub_type-财报披露时点类型-出参)
- [delivery_type（交割方式，get_future_info 用）](#delivery_type-交割方式-get_future_info-用)
- [query_time_period（期权波动率查询时间周期，入参）](#query_time_period-期权波动率查询时间周期-入参)
- [impvol_status（期权波动率分析状态，出参）](#impvol_status-期权波动率分析状态-出参)

## sec_status（证券状态）

| 取值 | 含义 |
| --- | --- |
| NORMAL | 正常 |
| LISTING | 待上市 |
| PURCHASING | 申购中 |
| SUBSCRIBING | 认购中 |
| BEFORE_DARK_TRADE_OPEING | 暗盘开盘前 |
| DARK_TRADING | 暗盘交易中 |
| DARK_TRAD_END | 暗盘已收盘 |
| TO_BE_OPEN | 待开盘 |
| SUSPENDED | 停牌 |
| CALLED | 已收回（牛熊证） |
| EXPIRED_LAST_TRADING_DATE | 已过最后交易日 |
| EXPIRED | 已过期 |
| DELISTED | 已退市 |
| CHANGE_TO_TEMPORARY_CODE | 已变更为临时代码 |
| TEMPORARY_CODE_TRADE_END | 临时代码交易结束 |
| CHANGED_PLATE_TRADE_END | 已变更上市板块，旧代码交易结束 |
| CHANGED_CODE_TRAD_END | 已变更代码，旧代码交易结束 |
| RECOVERABLE_CIRCUIT_BREAKER | 可恢复熔断 |
| UNRECOVERABLE_CIRCUIT_BREAKER | 不可恢复熔断 |
| AFTER_COMBINATION | 盘后撮合 |
| AFTER_TRANSACTION | 盘后交易 |
| DARK_TRADE_SUSPEND | 暗盘暂停 |
| EXPIRED_LAST_TRADING_TIME | 过最后交易时间 |
| N/A | 未知 / 无对应映射 |

## dark_status（暗盘状态）

| 取值 | 含义 |
| --- | --- |
| TRADING | 暗盘交易中 |
| END | 暗盘已收盘 |
| N/A | 非暗盘状态 |

## option_type（期权方向）

| 取值 | 含义 |
| --- | --- |
| CALL | 认购 |
| PUT | 认沽 |
| "" | 非期权品类 |

## option_area_type（期权行权类型）

| 取值 | 含义 |
| --- | --- |
| AMERICAN | 美式期权 |
| EUROPEAN | 欧式期权 |
| BERMUDA | 百慕大期权 |
| "" | 非期权品类 |

## trust_assetClass（信托基金资产类别）

| 取值 | 含义 |
| --- | --- |
| STOCK | 股票 |
| BOND | 债券 |
| COMMODITY | 商品 |
| CURRENCY_MARKET | 货币市场 |
| FUTURE | 期货 |
| SWAP | 互换 |

## ktype（K 线类型）

| 取值 | 含义 |
| --- | --- |
| 1 | 1 分钟 |
| 2 | 日 |
| 3 | 周 |
| 4 | 月 |
| 5 | 年 |
| 6 | 5 分钟 |
| 7 | 15 分钟 |
| 8 | 30 分钟 |
| 9 | 60 分钟 |
| 10 | 3 分钟 |
| 11 | 季 |
| 14 | 120 分钟 |
| 15 | 240 分钟 |
| 26 | 10 分钟 |
| 29 | 180 分钟 |

## autype（复权类型）

| 取值 | 含义 |
| --- | --- |
| 0 | 不复权 |
| 1 | 前复权（不含股息） |
| 2 | 后复权（不含股息） |
| 3 | 前复权（含股息） |
| 4 | 后复权（含股息） |

## extended_time（盘前盘后开关，仅美股 1 分 K 生效）

| 取值 | 含义 |
| --- | --- |
| 0 | 默认（不含盘前盘后） |
| 1 | 含盘前盘后 |
| 2 | 含夜盘 |

## request_section（rt-data 交易时段，仅 get_rt_data 用）

| 取值 | 含义 |
| --- | --- |
| NORMAL | 正常盘中（默认；港股自动含暗盘） |
| FULL | 完整含盘前盘后（仅美股，不含夜盘） |
| PREMARKET | 美股盘前 |
| AFTERHOURS | 美股盘后 |
| HK_DARK | 港股暗盘 |
| OVERNIGHT | 美股夜盘 |

## capital_flow_section（capital_flow 交易时段，入参；仅 get_capital_flow 用）

| 取值 | 含义 |
| --- | --- |
| NORMAL | 正常盘中（默认；港股自动含暗盘） |
| FULL | 完整含盘前盘后 |
| PREMARKET | 仅盘前 |
| AFTERHOURS | 仅盘后 |

## capital_flow_history_period_type（capital_flow_history 周期类型，入参）

| 取值 | 含义 |
| --- | --- |
| DAY | 日级聚合（默认） |
| WEEK | 周级聚合 |
| MONTH | 月级聚合 |

## trade_section（交易时段类型，出参；按市场细分）

| 取值 | 含义 |
| --- | --- |
| AUCTION | 港股竞价时段 |
| MORNING | 港股上午时段 |
| AFTERNOON | 港股下午时段 |
| NIGHT | 夜市 |
| US_PREMARKET | 美股盘前 |
| US_AFTERHOURS | 美股盘后 |
| HK_DARK | 港股暗盘 |
| FUT_PART1 | 期货第一时段 |
| FUT_PART2 | 期货第二时段 |
| STIB_AFTERHOURS | 科创板盘后 |
| US_OVERNIGHT | 美股夜盘 |
| US_REGULAR | 美股常规交易时段 |
| DEFAULT | 默认（一般市场） |
| REGULAR | 常规交易时段 |
| US_INDEX_OPT_REGULAR | 美股指数期权常规 |
| US_INDEX_OPT_GLOBAL | 美股指数期权全球 |
| US_INDEX_OPT_CURB | 美股指数期权 CURB |
| JP_INDEX_OPT_NIGHT | 日股指数期权夜盘 |
| JP_INDEX_OPT_REGULAR | 日股指数期权常规 |

## trade_date_type（交易日类型，出参）

| 取值 | 含义 |
| --- | --- |
| WHOLE | 全天交易 |
| MORNING | 仅上午交易 |
| AFTERNOON | 仅下午交易 |

## ticker_direction（逐笔买卖方向）

| 取值 | 含义 |
| --- | --- |
| BUY | 买盘 |
| SELL | 卖盘 |
| NEUTRAL | 中性盘（无法判定主动方向） |

## tick_type（逐笔成交类型，交易方式）

| 取值 | 含义 |
| --- | --- |
| UNKNOWN | 未知 |
| AUTO_MATCH | 自动对盘成交（港股最常见） |
| LATE | 后期成交 |
| NON_AUTO_MATCH | 非自动对盘成交 |
| ODD_LOT | 碎股成交 |
| AUCTION | 竞价成交 |
| BULK | 大宗交易 |
| OVERSEAS | 海外成交 |
| UNAUTO_MATCH_OFF | 非自动对盘买卖盘外 |
| NON_DIRECT_OFF | 非直接成交（场外） |
| OVERSEAS_OFF | 海外成交（场外） |
| AUTO_MATCH_OFF | 自动对盘成交（场外） |
| BULK_OFF | 大宗交易（场外） |
| LATE_OFF | 后期成交（场外） |
| AUCTION_OFF | 竞价成交（场外） |
| ODD_LOT_OFF | 碎股成交（场外） |
| EVENING | 夜市成交 |
| ACCEPT_ELECTRONIC | 接受电子盘 |
| OUT_HOUR_CONTRACT | 收盘后合约成交 |
| BANK_CHARGE | 中央结算系统收费 |
| ELECTRONIC | 电子交易 |
| HIGH_DENSITY | 高密度交易 |
| INTERMEDIATE_PRICE | 中间价交易 |
| AT_AUCTION | 竞价交易 |
| AUCTION_LIMIT | 竞价限价交易 |
| AT_AUCTION_LIMIT | 竞价限价 |
| ENHANCE_LIMIT | 增强限价 |
| HOT_QUOTE | 实时报价 |
| MARKET | 市价 |
| ROUND_LOT | 整手 |
| SPECIAL_LOT | 特殊手数 |
| ODD_AND_SPECIAL_LOT | 碎股与特殊手数 |

## period_type（逐笔所在时段）

| 取值 | 含义 |
| --- | --- |
| NORMAL | 盘中正常时段 |
| BEFORE | 盘前 |
| AFTER | 盘后 |
| OVERNIGHT | 夜盘 |

## stock_type（标的类型）

| 取值 | 含义 |
| --- | --- |
| BOND | 场内债券 |
| WEALTH_MANAGE | 财富管理基金 |
| STOCK | 正股 |
| ETF | 场内基金 / REIT / 信托 |
| WARRANT | 窝轮（认股证 / 牛熊证 / 界内证） |
| IDX | 指数 |
| PLATE | 板块 |
| DRVT | 期权 |
| FUTURE | 期货 |
| FOREX | 外汇 |
| CRYPTO | 加密货币 |
| OTC_STRUCT_NOTES | 财富管理-结构化票据 |
| PLATESET | 板块集合 |
| SECURITY_PORTFOLIO | 证券组合 |
| EC | 宏观数据 |
| OPPORTUNITY_PORTFOLIO | 机会组合 |
| OLD_OTC_STRUCT_NOTES | 财富管理-旧版结构化票据 |
| PREDICTION | 事件合约 |
| TOKENIZED_FUND | 代币化基金 |

## state（证券生命周期状态）

| 取值 | 含义 |
| --- | --- |
| NORMAL | 正常 |
| PENDING_LISTING | 待上市 |
| IPO_PURCHASING_CN | A 股申购中 |
| IPO_PURCHASING_OTHER | 其它市场申购中 |
| DARK_TRADE_PENDING | 暗盘待开盘 |
| DARK_TRADE_HAPPENING | 暗盘交易中 |
| DARK_TRADE_END | 暗盘已收盘 |
| TO_BE_OPEN | 待开盘 |
| SUSPENDED | 停牌 |
| CALLED | 强制收回（牛熊证） |
| EXPIRED_LAST_TRADING_DATE | 最后交易日 |
| EXPIRED | 已到期 |
| DELISTED | 已退市 |
| CHANGE_TO_TEMPORARY_CODE | 改临时代码 |
| TEMPORARY_CODE_END_TRADING | 临时代码停止交易 |
| CHANGED_PLATE_END_TRADING | 转板停止交易 |
| CHANGED_CODE_END_TRADING | 改代码停止交易 |
| CIRCUIT_BREAKER_RECOVERABLE | 可恢复熔断 |
| CIRCUIT_BREAKER_UNRECOVERABLE | 不可恢复熔断 |
| AFTER_COMBINATION | 盘后撮合 |
| AFTER_TRANSACTION | 盘后交易 |
| DARK_TRADE_SUSPEND | 暗盘暂停 |
| EXPIRED_LAST_TRADING_TIME | 最后交易时刻已过 |

## stock_child_type（窝轮子类型）

| 取值 | 含义 |
| --- | --- |
| N/A | 非窝轮或未知 |
| CALL | 认购证 |
| PUT | 认沽证 |
| BULL | 牛证 |
| BEAR | 熊证 |
| INLINE | 界内证 |

## action_type（公司行动事件类型，get_rehab 用）

| 取值 | 含义 |
| --- | --- |
| SPLIT | 拆股 |
| JOIN | 合股 |
| BONUS_STK | 送股 |
| INTOSHARES | 转股（公积金 / 盈余转增） |
| ALLOT | 配股 |
| ADD | 增发 |
| DIVIDEND | 派息 |
| SPECIALDIVIDEND | 特别派息 |
| SPINOFF | 分拆 |

## divi_mode（复权分红派息处理模式，get_rehab 入参用）

| 取值 | 含义 |
| --- | --- |
| compat | 旧兼容（仅保留兼容，不推荐使用） |
| exclude_divi | 排除分红派息（国际通行，雅虎 / 彭博口径） |
| include_divi | 包含分红派息（默认；A 股 / moomoo 传统口径） |

## plate_type（板块类型，出参）

| 取值 | 含义 |
| --- | --- |
| INDUSTRY | 行业板块（按 GICS / 申万等行业分类划分） |
| CONCEPT | 概念板块（题材 / 主题） |
| REGION | 地域板块（仅 SH/SZ A 股使用） |
| OTHER | 其它板块（含所有未归入上述类别的板块集合） |

## market_state（市场交易状态，get_market_state 出参）

| 取值 | 含义 |
| --- | --- |
| NONE (0) | 无交易 / 未支持市场 / 未开盘 |
| AUCTION (1) | 竞价 |
| WAITING_OPEN (2) | 早盘前等待开盘 |
| MORNING (3) | 早盘交易中 |
| REST (4) | 午间休市 |
| AFTERNOON (5) | 午盘交易中 |
| CLOSED (6) | 收盘 |
| MAAUCTION (7) | 竞价撮合（Matching Auction） |
| PRE_MARKET_BEGIN (8) | 美股盘前开始 |
| PRE_MARKET_END (9) | 美股盘前结束 |
| AFTER_HOURS_BEGIN (10) | 美股盘后开始 |
| AFTER_HOURS_END (11) | 美股盘后结束 |
| FUTU_SWITCH_DATE (12) | moomoo 切交易日 |
| NIGHT_OPEN (13) | 衍生品夜市开盘 |
| NIGHT_END (14) | 衍生品夜市收盘 |
| FUTURE_DAY_OPEN (15) | 期货日市开盘 |
| FUTURE_DAY_BREAK (16) | 期货日市休市 |
| FUTURE_DAY_CLOSE (17) | 期货日市收盘 |
| FUTURE_DAY_WAIT_OPEN (18) | 期货日市等待开盘 |
| HK_CAS (19) | 港股盘后竞价（Closing Auction Session） |
| FUTURE_NIGHT_WAIT (20) | 期货夜市等待 |
| FUTURE_AFTERNOON (21) | 期货下午开盘（已废弃） |
| FUTURE_SWITCH_DATE (22) | 衍生品切交易日 |
| FUTURE_OPEN (23) | 衍生品开盘 |
| FUTURE_BREAK (24) | 衍生品休息 |
| FUTURE_BREAK_OVER (25) | 衍生品休息后开盘 |
| FUTURE_CLOSE (26) | 衍生品收盘 |
| STIB_AFTER_HOURS_WAIT (27) | 科创板盘后撮合等待 |
| STIB_AFTER_HOURS_BEGIN (28) | 科创板盘后交易开始 |
| STIB_AFTER_HOURS_END (29) | 科创板盘后交易结束 |
| CLOSE_AUCTION (30) | 收市竞价 |
| AFTERNOON_END (31) | 已收盘 |
| NIGHT (32) | 夜市交易中 |
| OVERNIGHT_BEGIN (33) | 美股夜盘开始 |
| OVERNIGHT_END (34) | 美股夜盘结束 |
| TRADE_AT_LAST (35) | 收盘前成交 |
| TRADE_AUCTION (36) | 收盘前竞价 |
| OVERNIGHT (37) | 美股夜盘交易时段 |

## trade_section_type（交易时段类型数值，get_market_state 出参）

| 取值 | 含义 |
| --- | --- |
| US_PREMARKET (5) | 美股盘前 |
| US_AFTERHOURS (6) | 美股盘后 |
| US_OVERNIGHT (11) | 美股夜盘 |
| US_REGULAR (12) | 美股盘中常规 |
| DEFAULT (20) | 盘中默认（HK / 沪深 / 数字货币 / 外汇等通用时段） |
| REGULAR (21) | 仅一段交易时间（美股期权常规） |
| US_INDEX_OPTION_REGULAR (22) | 美股指数期权常规交易时间表 |
| US_INDEX_OPTION_GLOBAL (23) | 美股指数期权 Global 时段 |
| US_INDEX_OPTION_CURB (24) | 美股指数期权 CURB 时段 |
| JP_INDEX_OPTION_NIGHT (25) | 日本指数期权夜市时段 |
| JP_INDEX_OPTION_REGULAR (26) | 日本指数期权日市时段 |

## market（市场前缀）

板块接口 / 全市场筛选等接口的 `market` 入参取值。

SH 与 SZ 在板块接口上共用 A 股板块集合（调用 SH 或 SZ 等价）。

| 取值 | 含义 |
| --- | --- |
| HK | 港股 |
| US | 美股 |
| SH | 上证 A 股 |
| SZ | 深证 A 股 |
| SG | 新加坡股 |
| JP | 日股 |
| AU | 澳股 |
| CA | 加股 |
| MY | 马股 |
| KR | 韩股 |

## plate_class（板块分类，板块接口用）

| 取值 | 含义 |
| --- | --- |
| ALL | 全部板块 |
| INDUSTRY | 行业板块 |
| REGION | 地域板块（仅 SH / SZ 支持） |
| CONCEPT | 概念板块 |
| OTHER | 其他板块 |

## sort_field（板块成份股排序字段，get_plate_stock 入参用）

| 取值 | 含义 |
| --- | --- |
| NONE | 不排序（默认，按后端默认顺序） |
| CODE | 股票代码 |
| CHANGE_RATE | 涨跌幅 |
| NAME | 股票名称 |
| MARKET_VAL | 总市值 |
| PRICE_CHANGE_VAL | 涨跌额 |
| CUR_PRICE | 最新价 |
| PRICE_CHANGE_SPEED | 价格变动速率 |
| TURNOVER | 成交额 |
| VOLUME | 成交量 |
| PRICE_HIGHEST | 最高价 |
| PRICE_LOWEST | 最低价 |
| PRICE_OPEN | 开盘价 |
| PRICE_LAST | 昨收价 |
| PE | 市盈率 |
| ASK_PRICE | 卖一价 |
| BID_PRICE | 买一价 |
| ASK_VOL | 卖一量 |
| BID_VOL | 买一量 |
| TURNOVER_RATIO | 换手率 |
| BUYSELL_RATIO | 委比 |
| VOLUME_RATIO | 量比 |
| AMPLITUDE | 振幅 |
| TOTAL_SHARES | 总股本 |
| CIRC_TOTAL_SHARES | 流通股本 |
| CIRC_MARKET_VALUE | 流通市值 |
| DIVIDEND_RATIO_TTM | 股息率 TTM |
| DIVIDEND_RATIO_LFY | 股息率 LFY（上一财年） |
| PREMIUM | 溢价（窝轮/牛熊证用） |
| PRICE_RISE_COUNT | 连续上涨天数 |
| MARGINABLE | 可融资标的 |
| MORTGAGE_RATE | 融资按金比例 |
| SHORT_SELLING | 可沽空标的 |
| SHORT_REF_RATE | 沽空参考利率 |
| LONG_MARGIN_INITIAL_RATIO | 多头初始保证金比率 |
| SHORT_MARGIN_INITIAL_RATIO | 空头初始保证金比率 |
| IPO_PRICE | 新股发行价 |
| LIST_TIME | 上市时间 |
| IPO_PE | 新股发行 PE |
| IPO_PRICE_CHANGE_RATIO | 新股累计涨跌幅 |
| CONTINUOUS_RISE_DAY_CNT | 新股连续上涨天数 |
| FIRST_DAY_PCR | 首日涨跌幅 |
| FIRST_DAY_REAL_PCR | 首日实际涨跌幅 |
| ISSUE_SIZE | 发行规模 |
| PRE_CUR_PRICE | 盘前最新价 |
| PRE_PRICE_CHANGE_VAL | 盘前涨跌额 |
| PRE_CHANGE_RATE | 盘前涨跌幅 |
| AFTER_CUR_PRICE | 盘后最新价 |
| AFTER_PRICE_CHANGE_VAL | 盘后涨跌额 |
| AFTER_CHANGE_RATE | 盘后涨跌幅 |
| PRE_AMPLITUDE | 盘前振幅 |
| AFTER_AMPLITUDE | 盘后振幅 |
| PRE_TURNOVER | 盘前成交额 |
| AFTER_TURNOVER | 盘后成交额 |
| PRE_VOLUME | 盘前成交量 |
| AFTER_VOLUME | 盘后成交量 |
| HSG_HOLD_NUM | 沪深港通持股数 |
| HSG_HOLD_RATIO | 沪深港通持股占比 |
| CHANGE_RATIO_5_DAYS | 5 日涨跌幅 |
| CHANGE_RATIO_10_DAYS | 10 日涨跌幅 |
| CHANGE_RATIO_20_DAYS | 20 日涨跌幅 |
| CHANGE_RATIO_60_DAYS | 60 日涨跌幅 |
| CHANGE_RATIO_120_DAYS | 120 日涨跌幅 |
| CHANGE_RATIO_250_DAYS | 250 日涨跌幅 |
| CHANGE_RATIO_YEAR | 年初至今涨跌幅 |
| CHANGE_RATIO_5_MIN | 5 分钟涨跌幅 |
| ADR_CODE | ADR 关联代码 |
| ADR_PRICE | ADR 价格 |
| ADR_DIFF_PRICE | ADR 折溢价金额 |
| ADR_DIFF_PER | ADR 折溢价百分比 |
| ADR_CONVERTION_RATIO | ADR 换股比率 |
| ADR_RATIO | ADR 比率 |
| ADR_TRAD_VOL | ADR 成交量 |
| HSG_HOLD_AMOUNT | 沪深港通持股金额 |
| ADR_PRICE_HK | ADR 港股关联价 |
| HSG_DAY_FLOW | 沪深港通当日资金流 |
| HSG_WEEK_FLOW | 沪深港通近一周资金流 |
| HSG_MONTH_FLOW | 沪深港通近一月资金流 |
| HSG_QUATER_FLOW | 沪深港通近一季资金流 |
| TTM_PE | TTM 市盈率 |
| ANNUAL_PE | 静态市盈率 |
| BMP_PRICE | 暗盘价 |
| BMP_PRICE_CHANGE_VAL | 暗盘涨跌额 |
| BMP_PRICE_CHANGE_RATE | 暗盘涨跌幅 |
| WEIGHT | 板块权重 |
| EFFECT_DOT | 影响点数 |
| US_FUTURE_DEFAULT | 美股期货默认排序 |
| LAST_SETTLE_PRICE | 昨结算价（期货） |
| POSITION | 持仓量（期货） |
| POSITION_CHANGE | 日增仓（期货） |
| LAST_TRADE_TIME | 最后交易时间（期货） |
| EN_NAME | 英文名称 |
| DARK_CHANGE_RATIO | 暗盘涨跌幅（兼容字段） |
| DARK_CHANGE_VAL | 暗盘涨跌额（兼容字段） |
| PB | 市净率 |
| TRUST_AUM | 信托基金资产规模 AUM |
| TRADE_INFO | 交易信息 |
| CURRENCY_CODE | 货币代码 |
| MATURITY_DATE | 到期日（窝轮/可转债） |
| RELATION_WEIGHT | 关联权重 |
| CONVERT_PREMINUM_RATIO | 可转债溢价率 |
| STRB_PREMIUM_RATIO | 跨价权证溢价率 |
| PUT_LEVER_PRICE | 认沽证杠杆价 |
| CALL_LEVER_PRICE | 认购证杠杆价 |
| STRB_VALUE | 跨价权证价值 |
| CONVERT_STOCK_PRICE | 可转债转股价 |
| WRNT_LAST_TRADE_DATE | 窝轮最后交易日 |
| CHANGE_RATIO_3_YEAR | 3 年涨跌幅 |
| JA_NAME | 日文名称 |
| OVERNIGHT_PRICE | 夜盘价 |
| OVERNIGHT_TURNOVER | 夜盘成交额 |
| OVERNIGHT_VOLUME | 夜盘成交量 |
| OVERNIGHT_AMPLITUDE | 夜盘振幅 |
| OVERNIGHT_PRICE_CHANGE_VAL | 夜盘涨跌额 |
| OVERNIGHT_CHANGE_RATE | 夜盘涨跌幅 |
| HOT | 热度 |
| ETF_LEVERAGE | ETF 杠杆倍数 |
| DIVIDEND_TTM | TTM 股息 |
| PAYOUT_RATIO_LFY | 派息率 LFY |
| DISTRIBUTION_FREQUENCY | 派息频率 |
| MAX_DIVIDEND_GROW_YEAR | 最大连续派息增长年数 |
| DIVIDEND_INCREASE_RATE_1YEAR | 近 1 年派息增长率 |
| AVERAGE_DIVIDEND_YIELD_5YEAR | 近 5 年平均股息率 |
| CHANGE_RATIO_24H | 24 小时涨跌幅 |
| DEBT_ASSET_RATIO | 资产负债率 |
| TH_NAME | 泰文名称 |

## price_type（价格类排序口径，get_plate_stock 入参用）

| 取值 | 含义 |
| --- | --- |
| NORMAL | 正常价（默认） |
| BEFORE | 盘前价 |
| AFTER | 盘后价 |
| OVERNIGHT | 夜盘价 |

## statement_type（财报报表类型，入参）

| 取值 | 含义 |
| --- | --- |
| 1 | Income statement（利润表） |
| 2 | Balance sheet（资产负债表） |
| 3 | Cash flow statement（现金流量表） |
| 4 | Key indicators（主要指标） |

## financial_type（财报期类型，入参/出参）

| 取值 | 含义 |
| --- | --- |
| 0 | 自动匹配（仅入参；按 date 自动匹配期类型，主营构成 get_financials_revenue_breakdown 用） |
| 1 | Q1（一季报，单季） |
| 2 | Q2（二季报，单季） |
| 3 | Q3（三季报，单季） |
| 4 | Q4（四季报，单季） |
| 5 | Q6（累计中报，上半年累计） |
| 6 | Q9（累计三季报，前三季累计） |
| 7 | Annual（年报） |
| 8 | Aggregated quarterly（聚合季报，仅美股；主营构成 get_financials_revenue_breakdown 用） |
| 9 | 全部单季报（Q1~Q4），多期选择器，仅入参 |
| 10 | 单季报 + 年报（Q1~Q4 及年报），多期选择器，仅入参；get_financials_statements 默认值 |
| 11 | 全部累计季报（Q1,Q6,Q9,年报），多期选择器，仅入参 |
| 102 | 全部累计季报（Q1,Q6,Q9,年报），多期选择器，仅入参；get_company_operational_efficiency 用 |
| 70 | 马来西亚 Other 单季报（period_text 后缀 SQ） |
| 71 | 马来西亚 Other 累计季报（period_text 后缀 CQ） |

## financial_structure（财报子结构编号，出参）

不同 `statement_type` 对应不同 structure 集合；同一 `statement_type` 在不同市场可能落到不同 structure。

| 取值 | 含义 | 所属 statement_type |
| --- | --- | --- |
| 1 | Income Statement (US GAAP, Banking) | 1 利润表 |
| 2 | Income Statement (US GAAP, Insurance) | 1 利润表 |
| 3 | Income Statement (US GAAP, Industrial) | 1 利润表 |
| 4 | Balance Sheet (US GAAP, Banking) | 2 资产负债表 |
| 5 | Income Statement (HK / IAS, General) | 1 利润表 |
| 6 | Balance Sheet (HK / IAS, General) | 2 资产负债表 |
| 7 | Cash Flow Statement (US GAAP) | 3 现金流量表 |
| 8 | Income Statement (US GAAP, General) | 1 利润表 |
| 9 | Balance Sheet (US GAAP, General) | 2 资产负债表 |
| 10 | Income Statement (CN / CAS, Industrial) | 1 利润表 |
| 11 | Balance Sheet (HK / IAS, Banking) | 2 资产负债表 |
| 12 | Income Statement (HK / IAS, Banking) | 1 利润表 |
| 13 | Cash Flow Statement (HK / IAS) | 3 现金流量表 |
| 14 | Key Indicators – Per Share | 4 主要指标 |
| 15 | Key Indicators – Profitability | 4 主要指标 |
| 16 | Key Indicators – Solvency | 4 主要指标 |
| 17 | Key Indicators – Growth | 4 主要指标 |
| 18 | Key Indicators – Operating Efficiency | 4 主要指标 |
| 19 | Key Indicators – Cash Flow | 4 主要指标 |

## expiration_cycle（期权到期周期）

| 取值 | 含义 |
| --- | --- |
| MONTH | 月度合约 |
| WEEK | 周度合约 |
| END_OF_MONTH | 月末合约 |
| QUARTERLY | 季度合约 |
| WEEKMON | 周一到期 |
| WEEKTUE | 周二到期 |
| WEEKWED | 周三到期 |
| WEEKTHU | 周四到期 |
| WEEKFRI | 周五到期 |
| N/A | 未知 |

## index_option_type（指数期权类型，入参）

| 取值 | 市场 | 含义 |
| --- | --- | --- |
| 1 | HK | 恒生指数 (HSI) |
| 2 | HK | 国企指数 (HSCEI) |
| 3 | HK | 小型恒指 (Mini-HSI) |
| 4 | HK | 小型国指 (Mini-HSCEI) |
| 5 | HK | 恒生科技指数 (HSTECH) |
| 1000 | US | 兜底指数期权 |
| 1001 | US | VIX |
| 1002 | US | SPX |
| 1003 | US | XSP |
| 1004 | US | NDX |
| 1005 | US | EFS |
| 1006 | US | MXS |
| 1007 | US | DJX |
| 1008 | US | OEX |
| 1009 | US | SIXB |
| 1010 | US | SIXI |
| 1011 | US | SIXM |
| 1012 | US | SIXU |
| 1013 | US | SIXV |
| 1014 | US | XEO |
| 1015 | US | BKX |
| 1016 | US | XAU |
| 1017 | US | OSX |
| 1018 | US | SOX |
| 1019 | US | UTY |
| 1020 | US | RUT |
| 1021 | US | SIXRE |
| 1022 | US | XND |
| 1023 | US | CBTX |
| 1024 | US | MBTX |
| 2001 | JP | N225 |
| 2002 | JP | N225M |
| 2003 | JP | TOPIX |

## filter_standard（标准/非标准期权过滤，入参）

| 取值 | 含义 |
| --- | --- |
| ALL | 全部（默认） |
| STANDARD | 仅标准期权 |
| NON_STANDARD | 仅非标准期权（FLEX 等调整后合约） |

## combo_strategy（组合期权策略类型，入参/出参）

用于 组合期权策略 与 组合期权价差 的 `strategy` 字段（整数）。与交易下单的字符串枚举 `option_strategy` 不是同一套，不要混用。未列出的数值（如 `3` / `5` / `10` / `12`）不在网关枚举内，传入返回 `ret_code=-3`。

须 `spread` 的策略：不传 `spread` 时后端会业务失败（`ret_code=-5`）。请先调价差接口，再把 `default_spread` 或 `spread_list` 中的值传入策略接口。

`quote.option_strategy` 返回的 `combo_list` 一项永远是一套组合，腿在 `legs[]`。`Covered(2)` / `Collar(8)` 会在期权腿前补路径正股（`instrument=STOCK`），不下发 `side` / `quantity`；询价时由调用方填写。港股不支持 `2/8`。

| 取值 | 名称 | 含义 | 须 spread | 须 far_expire_time |
| --- | --- | --- | --- | --- |
| 1 | SingleOption | 单腿期权 | 否 | 否 |
| 2 | Covered | 备兑 | 否 | 否 |
| 4 | Spread | 垂直价差 | 是 | 否 |
| 6 | Straddle | 跨式 | 否 | 否 |
| 7 | Strangle | 宽跨式 | 是 | 否 |
| 8 | Collar | 领口 | 是 | 否 |
| 9 | Butterfly | 蝶式 | 是 | 否 |
| 11 | Condor | 鹰式 | 是 | 否 |
| 13 | IronButterfly | 铁蝶 | 是 | 否 |
| 14 | IronCondor | 铁鹰 | 是 | 否 |
| 15 | CalendarSpread | 日历价差 | 否 | 是 |
| 16 | DiagonalSpread | 对角价差 | 是 | 是 |
| 100 | Customize | 自定义 | 否 | 否 |

## option_standard_type（期权规格类型，出参）

用于期权链与组合期权腿的 `option_standard_type`。入参过滤见 filter_standard（多一个 `ALL`）。

| 取值 | 含义 |
| --- | --- |
| STANDARD | 标准期权 |
| NON_STANDARD | 非标准期权（FLEX 等调整后合约） |
| N/A | 未知 / 未映射 |

## combo_leg_instrument（组合期权腿品类，出参）

用于 组合期权策略 的 `legs[].instrument`。询价接口的腿不带该字段，靠 `code` 区分期权与正股。

| 取值 | 含义 |
| --- | --- |
| OPTION | 期权合约 |
| STOCK | 标的正股（仅 Covered / Collar 由网关补入） |

## combo_side（组合询价腿方向，入参/回显）

用于 组合期权询价 的 `legs[].side`。网关不从策略类型推断，必须由调用方传入。与逐笔 `ticker_direction` 的 BUY/SELL（买盘/卖盘）不是同一语义。

| 取值 | 含义 |
| --- | --- |
| BUY | 买入该腿 |
| SELL | 卖出该腿 |

## holder_type（股东类型，入参/出参）

用于 get_shareholders_holding_changes 的 `holder_type`（英文文本）/ `holder_type_id`（数值）。亦用于 get_shareholders_holder_detail 的 request_type（另含 1000=全部，默认 1000）。

| holder_type_id | holder_type（对外英文） | 含义 |
| --- | --- | --- |
| 1 | Other Institution | 其他机构 |
| 2 | Traditional Investment Manager | 传统投资经理 |
| 3 | Hedge Fund Manager / CTA | 对冲基金 |
| 4 | VC / PE Firm | 风险资本/私募股权 |
| 5 | Corporate Pension Plan Sponsor | 企业年金 |
| 6 | Foundation Fund Sponsor | 基金会基金 |
| 7 | Insurance Company | 保险公司 |
| 8 | Bank / Investment Bank | 银行/投资银行 |
| 9 | Family Office / Trust | 家族办公室/信托 |
| 10 | Sovereign Wealth Fund | 主权财富基金 |
| 11 | REIT / Real Estate Investment Manager | REIT |
| 12 | Structured Finance Pool Manager | 结构化融资经理 |
| 13 | Union Pension Plan Sponsor | 联合养老金 |
| 14 | Government Pension Plan Sponsor | 政府养老金 |
| 15 | Endowment Fund Sponsor | 捐赠基金 |
| 100 | Individual Insider | 个人 |
| 200 | ADR Issuer | ADS |
| 300 | Public Corporation | 上市公司 |
| 400 | Private Corporation | 未公开上市公司 |
| 500 | State-Owned Shares | 国有股 |

## pub_type（财报披露时点类型，出参）

| 取值 | 含义 |
| --- | --- |
| 0 | 当天披露（未识别出具体盘前/盘后） |
| 1 | 盘前 |
| 2 | 盘后 |

## delivery_type（交割方式，get_future_info 用）

| 取值 | 含义 |
| --- | --- |
| UNKNOWN | 未知 / 未指定 |
| PHYSICAL | 实物交割 |
| CASH | 现金交割 |

## query_time_period（期权波动率查询时间周期，入参）

| 取值 | 含义 |
| --- | --- |
| 1 | 1 周 |
| 2 | 1 月（默认） |
| 3 | 3 月 |
| 4 | 6 月 |
| 5 | 1 年 |

## impvol_status（期权波动率分析状态，出参）

| 取值 | 含义 |
| --- | --- |
| FLUCTUATING | 震荡中 |
| OVERVALUED | 高估 |
| UNDERVALUED | 低估 |
