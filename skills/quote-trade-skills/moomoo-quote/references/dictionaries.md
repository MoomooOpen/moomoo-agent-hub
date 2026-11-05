# Quote 行情命名词典（英文审校版）

本文根据 moomoo OpenAPI 官方行情命名词典整理，用于后续编写 moomoo CLI quote skill / wrapper 时快速查阅枚举值。

来源：moomoo OpenAPI `zh-cn/api/quote/naming-dictionary`，原稿读取日期：2026-10-13。

英文语义审校日期：2026-11-05。审校范围为原稿现有的 43 个枚举表、533 条枚举释义。

## 使用约定

- 本文只覆盖行情（Quote）接口枚举；交易、模拟交易、加密货币交易枚举见对应模块文档。
- 表格中的 `取值` 应按原样传给 CLI flag 或解析 API 响应；数值型枚举保持数字。
- CLI 已统一证券代码入参为 `symbol`，格式为 `MARKET.CODE`，例如 `HK.00700`、`US.AAPL`；港股数字代码可补零。
- `N/A` 或空字符串表示官方未映射、非适用或未知状态，skill 不应把它当成异常。
- 含义列英文为按市场和业务语境审校后的释义，不是英文网页的逐字摘录；API 取值和字段名仍按原稿保留。英文网页本身存在译法和定义冲突，不能仅因其为官方页面就照搬。
- 港股新股「暗盘」统一译为 **HK IPO grey market trading**，指新股正式上市前的场外交易。美股「暗池」译为 **dark pool trading**，指通常不公开展示交易前报价的交易场所/机制。二者不可混用；美股盘前、盘后和夜盘分别是 pre-market、after-hours、overnight，也不是新股暗盘。
- financial_type 的 2 和 10 在本次核对的官网中英文页仍不一致：中文页为「2 = 二季报单季」「10 = 单季报+年报」，英文页为「2 = H1」「10 = Latest」。表内暂按中文页解释并标注冲突，未以实际接口返回验证这两个值的业务行为。
- 英文释义中的 `(%)` 表示百分比类指标，不表示已核实响应的数值缩放；金额币种、成交量单位、比较基准和计算公式仍应查对应接口。

## 目录

- [sec_status（证券状态）](#sec_status-证券状态)
- [dark_status（暗盘状态）](#dark_status-暗盘状态)
- [option_type（期权类型）](#option_type-期权类型)
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

| 取值 Value | 含义 Meaning |
| --- | --- |
| NORMAL | 正常 Normal |
| LISTING | 待上市 Pending listing |
| PURCHASING | 申购中 IPO subscription in progress |
| SUBSCRIBING | 认购中 Subscription in progress |
| BEFORE_DARK_TRADE_OPEING | 暗盘开盘前 Before the HK IPO grey market session opens |
| DARK_TRADING | 暗盘交易中 HK IPO grey market trading |
| DARK_TRAD_END | 暗盘已收盘 HK IPO grey market session closed |
| TO_BE_OPEN | 待开盘 Awaiting market open |
| SUSPENDED | 停牌 Suspended |
| CALLED | 已收回（牛熊证） Called following a mandatory call event (CBBC) |
| EXPIRED_LAST_TRADING_DATE | 已过最后交易日 Past last trading date |
| EXPIRED | 已过期 Expired |
| DELISTED | 已退市 Delisted |
| CHANGE_TO_TEMPORARY_CODE | 已变更为临时代码 Changed to temporary code |
| TEMPORARY_CODE_TRADE_END | 临时代码交易结束 Temporary code trading ended |
| CHANGED_PLATE_TRADE_END | 已变更上市板块，旧代码交易结束 Board changed, old code trading ended |
| CHANGED_CODE_TRAD_END | 已变更代码，旧代码交易结束 Code changed, old code trading ended |
| RECOVERABLE_CIRCUIT_BREAKER | 可恢复熔断 Resumable circuit-breaker halt |
| UNRECOVERABLE_CIRCUIT_BREAKER | 不可恢复熔断 Non-resumable circuit-breaker halt |
| AFTER_COMBINATION | 盘后撮合 After-hours order matching |
| AFTER_TRANSACTION | 盘后交易 After-hours trading |
| DARK_TRADE_SUSPEND | 暗盘暂停 HK IPO grey market trading suspended |
| EXPIRED_LAST_TRADING_TIME | 过最后交易时间 Past last trading time |
| N/A | 未知 / 无对应映射 Unknown / No mapping |

## dark_status（暗盘状态）

| 取值 Value | 含义 Meaning |
| --- | --- |
| TRADING | 暗盘交易中 HK IPO grey market trading |
| END | 暗盘已收盘 HK IPO grey market session closed |
| N/A | 非暗盘状态 No IPO grey market status |

## option_type（期权类型）

CALL/PUT 表示认购/认沽期权类型，区别于买入/卖出方向；买入 Put 仍然是买入操作。

| 取值 Value | 含义 Meaning |
| --- | --- |
| CALL | 认购 Call option |
| PUT | 认沽 Put option |
| "" | 非期权品类 Not an option |

## option_area_type（期权行权类型）

这里是行权方式（exercise style），不是上市地区；美式、欧式和百慕大式描述可行权时点。

| 取值 Value | 含义 Meaning |
| --- | --- |
| AMERICAN | 美式期权 American-style option |
| EUROPEAN | 欧式期权 European-style option |
| BERMUDA | 百慕大期权 Bermudan-style option |
| "" | 非期权品类 Not an option |

## trust_assetClass（信托基金资产类别）

| 取值 Value | 含义 Meaning |
| --- | --- |
| STOCK | 股票 Equity |
| BOND | 债券 Bond |
| COMMODITY | 商品 Commodity |
| CURRENCY_MARKET | 货币市场 Money market |
| FUTURE | 期货 Futures |
| SWAP | 互换 Swap |

## ktype（K 线类型）

| 取值 Value | 含义 Meaning |
| --- | --- |
| 1 | 1 分钟 1 minute |
| 2 | 日 Day |
| 3 | 周 Week |
| 4 | 月 Month |
| 5 | 年 Year |
| 6 | 5 分钟 5 minutes |
| 7 | 15 分钟 15 minutes |
| 8 | 30 分钟 30 minutes |
| 9 | 60 分钟 60 minutes |
| 10 | 3 分钟 3 minutes |
| 11 | 季 Quarter |
| 14 | 120 分钟 120 minutes |
| 15 | 240 分钟 240 minutes |
| 26 | 10 分钟 10 minutes |
| 29 | 180 分钟 180 minutes |

## autype（复权类型）

英文网页的 Forward/Backward 与 moomoo 英文帮助中心的解释方向相反。本表用价格基准消除歧义：qfq 为前复权（以较新价格尺度调整历史），hfq 为后复权（以历史价格尺度衔接后续价格）。例如 1 拆 2：前复权把拆股前 100 调整为 50，后复权把拆股后 50 调整为 100。含股息与不含股息单独区分；这里没有验证 REST 返回价格的实际归一化尺度。

| 取值 Value | 含义 Meaning |
| --- | --- |
| 0 | 不复权 Unadjusted |
| 1 | 前复权（不含股息） Adjusted to the latest price basis (qfq; excluding dividends) |
| 2 | 后复权（不含股息） Adjusted to the historical price basis (hfq; excluding dividends) |
| 3 | 前复权（含股息） Adjusted to the latest price basis (qfq; including dividends) |
| 4 | 后复权（含股息） Adjusted to the historical price basis (hfq; including dividends) |

## extended_time（盘前盘后开关，仅美股 1 分 K 生效）

Include overnight 不在本表中扩写成“只含夜盘”或“全部时段”；是否同时包含盘前/盘后，须按接口定义确认。

| 取值 Value | 含义 Meaning |
| --- | --- |
| 0 | 默认（不含盘前盘后） Default (exclude pre-market and after-hours trading) |
| 1 | 含盘前盘后 Include pre-market and after-hours trading |
| 2 | 含夜盘 Include overnight session |

## request_section（rt-data 交易时段，仅 get_rt_data 用）

| 取值 Value | 含义 Meaning |
| --- | --- |
| NORMAL | 正常盘中（默认；港股自动含暗盘） Regular session (default; HK includes IPO grey market data) |
| FULL | 完整含盘前盘后（仅美股，不含夜盘） Full session including pre-market and after-hours trading (US only; excludes overnight) |
| PREMARKET | 美股盘前 US pre-market session |
| AFTERHOURS | 美股盘后 US after-hours session |
| HK_DARK | 港股暗盘 HK IPO grey market session |
| OVERNIGHT | 美股夜盘 US overnight session |

## capital_flow_section（capital_flow 交易时段，入参；仅 get_capital_flow 用）

| 取值 Value | 含义 Meaning |
| --- | --- |
| NORMAL | 正常盘中（默认；港股自动含暗盘） Regular session (default; HK includes IPO grey market data) |
| FULL | 完整含盘前盘后 Full session including pre-market and after-hours trading |
| PREMARKET | 仅盘前 Pre-market only |
| AFTERHOURS | 仅盘后 After-hours only |

## capital_flow_history_period_type（capital_flow_history 周期类型，入参）

| 取值 Value | 含义 Meaning |
| --- | --- |
| DAY | 日级聚合（默认） Daily aggregation (default) |
| WEEK | 周级聚合 Weekly aggregation |
| MONTH | 月级聚合 Monthly aggregation |

## trade_section（交易时段类型，出参；按市场细分）

HK 竞价时段不应只理解为开市竞价；收市竞价为 Closing Auction Session (CAS)。夜市 night session、美国 overnight session，以及指数期权 RTH/GTH/Curb 均按各自市场定义解释。

| 取值 Value | 含义 Meaning |
| --- | --- |
| AUCTION | 港股竞价时段 HK auction session |
| MORNING | 港股上午时段 HK morning session |
| AFTERNOON | 港股下午时段 HK afternoon session |
| NIGHT | 夜市 Night session |
| US_PREMARKET | 美股盘前 US pre-market |
| US_AFTERHOURS | 美股盘后 US after-hours |
| HK_DARK | 港股暗盘 HK IPO grey market session |
| FUT_PART1 | 期货第一时段 Futures session 1 |
| FUT_PART2 | 期货第二时段 Futures session 2 |
| STIB_AFTERHOURS | 科创板盘后 STAR Market after-hours fixed-price trading |
| US_OVERNIGHT | 美股夜盘 US overnight |
| US_REGULAR | 美股常规交易时段 US regular session |
| DEFAULT | 默认（一般市场） Default (general markets) |
| REGULAR | 常规交易时段 Regular session |
| US_INDEX_OPT_REGULAR | 美股指数期权常规 US index options regular trading hours (RTH) |
| US_INDEX_OPT_GLOBAL | 美股指数期权全球 US index options global trading hours (GTH) |
| US_INDEX_OPT_CURB | 美股指数期权 CURB US index options Curb session |
| JP_INDEX_OPT_NIGHT | 日股指数期权夜盘 Japanese index options night session |
| JP_INDEX_OPT_REGULAR | 日股指数期权常规 Japanese index options regular session |

## trade_date_type（交易日类型，出参）

| 取值 Value | 含义 Meaning |
| --- | --- |
| WHOLE | 全天交易 Full-day trading |
| MORNING | 仅上午交易 Morning only |
| AFTERNOON | 仅下午交易 Afternoon only |

## ticker_direction（逐笔买卖方向）

这里是行情提供方对成交主动方向的分类，不是账户订单的买卖方向，也不是盘口 bid/ask。具体分类算法未在命名词典中说明。

| 取值 Value | 含义 Meaning |
| --- | --- |
| BUY | 买盘 Buyer-initiated trade |
| SELL | 卖盘 Seller-initiated trade |
| NEUTRAL | 中性盘（无法判定主动方向） Unclassified trade (initiating side undetermined) |

## tick_type（逐笔成交类型，交易方式）

此表包含成交条件及部分订单类型标签，不应直接当成交易下单的 order_type。Odd lot 在港股按该证券 board lot 判断；美股按适用产品和市场规则判断，不能统一写成“少于 100 股”。`*_OFF` 只保留官方的 off-exchange 标签，不代表已识别出美股 dark pool；`LATE` 不应据字面改写成“盘后交易”。少见标签的协议含义尚未确认，表内已标 definition unverified。

| 取值 Value | 含义 Meaning |
| --- | --- |
| UNKNOWN | 未知 Unknown |
| AUTO_MATCH | 自动对盘成交（港股最常见） Automatched trade (most common in HK) |
| LATE | 后期成交 Late trade |
| NON_AUTO_MATCH | 非自动对盘成交 Non-automatched trade |
| ODD_LOT | 碎股成交 Odd-lot trade |
| AUCTION | 竞价成交 Auction trade |
| BULK | 大宗交易 Block trade |
| OVERSEAS | 海外成交 Overseas trade |
| UNAUTO_MATCH_OFF | 非自动对盘买卖盘外 Non-automatch off-exchange |
| NON_DIRECT_OFF | 非直接成交（场外） Non-direct off-exchange |
| OVERSEAS_OFF | 海外成交（场外） Overseas off-exchange |
| AUTO_MATCH_OFF | 自动对盘成交（场外） Automatch off-exchange |
| BULK_OFF | 大宗交易（场外） Block trade off-exchange |
| LATE_OFF | 后期成交（场外） Late trade off-exchange |
| AUCTION_OFF | 竞价成交（场外） Auction off-exchange |
| ODD_LOT_OFF | 碎股成交（场外） Odd lot off-exchange |
| EVENING | 夜市成交 Evening session trade |
| ACCEPT_ELECTRONIC | 接受电子盘 Electronic acceptance (API label; definition unverified) |
| OUT_HOUR_CONTRACT | 收盘后合约成交 After-hours contract trade |
| BANK_CHARGE | 中央结算系统收费 CCASS charge |
| ELECTRONIC | 电子交易 Electronic trade |
| HIGH_DENSITY | 高密度交易 High-density trade (API label; definition unverified) |
| INTERMEDIATE_PRICE | 中间价交易 Mid-price trade |
| AT_AUCTION | 竞价交易 At-auction (order-type label) |
| AUCTION_LIMIT | 竞价限价交易 Auction limit (order-type label) |
| AT_AUCTION_LIMIT | 竞价限价 At-auction limit (order-type label) |
| ENHANCE_LIMIT | 增强限价 Enhanced limit (order-type label) |
| HOT_QUOTE | 实时报价 Real-time quote (API label; definition unverified) |
| MARKET | 市价 Market order |
| ROUND_LOT | 整手 Board lot / round lot (market-specific) |
| SPECIAL_LOT | 特殊手数 Special-lot trade |
| ODD_AND_SPECIAL_LOT | 碎股与特殊手数 Odd-lot and special-lot trades |

## period_type（逐笔所在时段）

| 取值 Value | 含义 Meaning |
| --- | --- |
| NORMAL | 盘中正常时段 Regular session |
| BEFORE | 盘前 Pre-market session |
| AFTER | 盘后 After-hours session |
| OVERNIGHT | 夜盘 Overnight session |

## stock_type（标的类型）

`ETF` 是此 API 的分类桶，涵盖 REIT/信托，不表示这些产品在法律或产品结构上都是 ETF。`WARRANT` 同样涵盖认股证、牛熊证、界内证；牛熊证英文全称为 Callable Bull/Bear Contract (CBBC)，不是普通股票期权。

| 取值 Value | 含义 Meaning |
| --- | --- |
| BOND | 场内债券 Exchange-traded bond |
| WEALTH_MANAGE | 财富管理基金 Wealth management fund |
| STOCK | 正股 Stock |
| ETF | 场内基金 / REIT / 信托 Exchange-traded fund / REIT / trust |
| WARRANT | 窝轮（认股证 / 牛熊证 / 界内证） Warrants / callable bull/bear contracts (CBBCs) / inline warrants |
| IDX | 指数 Index |
| PLATE | 板块 Sector / thematic group |
| DRVT | 期权 Option |
| FUTURE | 期货 Futures |
| FOREX | 外汇 Forex |
| CRYPTO | 加密货币 Cryptocurrency |
| OTC_STRUCT_NOTES | 财富管理-结构化票据 Wealth management structured notes |
| PLATESET | 板块集合 Collection of sectors / thematic groups |
| SECURITY_PORTFOLIO | 证券组合 Securities portfolio |
| EC | 宏观数据 Macroeconomic data |
| OPPORTUNITY_PORTFOLIO | 机会组合 Opportunity portfolio |
| OLD_OTC_STRUCT_NOTES | 财富管理-旧版结构化票据 Legacy structured notes |
| PREDICTION | 事件合约 Event contract |
| TOKENIZED_FUND | 代币化基金 Tokenized fund |

## state（证券生命周期状态）

`EXPIRED_LAST_TRADING_DATE` 的中文页写“最后交易日”，而 sec_status 对应词写“已过最后交易日”。此处保留原页文字，状态时序待接口方确认。

| 取值 Value | 含义 Meaning |
| --- | --- |
| NORMAL | 正常 Normal |
| PENDING_LISTING | 待上市 Pending listing |
| IPO_PURCHASING_CN | A 股申购中 A-share IPO subscription |
| IPO_PURCHASING_OTHER | 其它市场申购中 Other market IPO subscription |
| DARK_TRADE_PENDING | 暗盘待开盘 HK IPO grey market awaiting open |
| DARK_TRADE_HAPPENING | 暗盘交易中 HK IPO grey market trading |
| DARK_TRADE_END | 暗盘已收盘 HK IPO grey market session closed |
| TO_BE_OPEN | 待开盘 Awaiting open |
| SUSPENDED | 停牌 Suspended |
| CALLED | 强制收回（牛熊证） Called following a mandatory call event (CBBC) |
| EXPIRED_LAST_TRADING_DATE | 最后交易日 Last trading date |
| EXPIRED | 已到期 Expired |
| DELISTED | 已退市 Delisted |
| CHANGE_TO_TEMPORARY_CODE | 改临时代码 Changed to temporary code |
| TEMPORARY_CODE_END_TRADING | 临时代码停止交易 Temporary code trading ended |
| CHANGED_PLATE_END_TRADING | 转板停止交易 Listing board changed; trading under the old code ended |
| CHANGED_CODE_END_TRADING | 改代码停止交易 Security code changed; trading under the old code ended |
| CIRCUIT_BREAKER_RECOVERABLE | 可恢复熔断 Resumable circuit-breaker halt |
| CIRCUIT_BREAKER_UNRECOVERABLE | 不可恢复熔断 Non-resumable circuit-breaker halt |
| AFTER_COMBINATION | 盘后撮合 After-hours order matching |
| AFTER_TRANSACTION | 盘后交易 After-hours trading |
| DARK_TRADE_SUSPEND | 暗盘暂停 HK IPO grey market trading suspended |
| EXPIRED_LAST_TRADING_TIME | 最后交易时刻已过 Past last trading time |

## stock_child_type（窝轮子类型）

| 取值 Value | 含义 Meaning |
| --- | --- |
| N/A | 非窝轮或未知 Not a warrant or unknown |
| CALL | 认购证 Call warrant |
| PUT | 认沽证 Put warrant |
| BULL | 牛证 Bull CBBC |
| BEAR | 熊证 Bear CBBC |
| INLINE | 界内证 Inline warrant |

## action_type（公司行动事件类型，get_rehab 用）

港股「配股」按 Rights issue 解释，不等于 placing（配售）；「送股」为 bonus shares，「公积金/盈余转增」为 reserve capitalization，「转股」在本枚举中不是可转债 conversion；「增发」保持宽泛的 additional share issuance，不限定公开发行或私募。

| 取值 Value | 含义 Meaning |
| --- | --- |
| SPLIT | 拆股 Stock split |
| JOIN | 合股 Share consolidation (reverse stock split) |
| BONUS_STK | 送股 Bonus shares |
| INTOSHARES | 转股（公积金 / 盈余转增） Capitalization of capital or surplus reserves into shares |
| ALLOT | 配股 Rights issue |
| ADD | 增发 Additional share issuance |
| DIVIDEND | 派息 Dividend |
| SPECIALDIVIDEND | 特别派息 Special dividend |
| SPINOFF | 分拆 Spin-off |

## divi_mode（复权分红派息处理模式，get_rehab 入参用）

此处仅描述本 API 的股息调整配置；Yahoo/Bloomberg 的处理方式取决于具体价格字段和产品配置，未核实原稿的平台比较，已删除泛化的“国际通行/雅虎/彭博/传统口径”描述。

| 取值 Value | 含义 Meaning |
| --- | --- |
| compat | 旧兼容（仅保留兼容，不推荐使用） Legacy compatibility (not recommended) |
| exclude_divi | 排除分红派息 Exclude dividends |
| include_divi | 包含分红派息（默认） Include dividends (default) |

## plate_type（板块类型，出参）

| 取值 Value | 含义 Meaning |
| --- | --- |
| INDUSTRY | 行业板块（按 GICS / 申万等行业分类划分） Industry group (GICS / Shenwan classification) |
| CONCEPT | 概念板块（题材 / 主题） Thematic group |
| REGION | 地域板块（仅 SH/SZ A 股使用） Regional group (SH/SZ A-shares only) |
| OTHER | 其它板块（含所有未归入上述类别的板块集合） Other security groups |

## market_state（市场交易状态，get_market_state 出参）

| 取值 Value | 含义 Meaning |
| --- | --- |
| NONE (0) | 无交易 / 未支持市场 / 未开盘 No trading / Unsupported market / Not open |
| AUCTION (1) | 竞价 Auction |
| WAITING_OPEN (2) | 早盘前等待开盘 Waiting for open |
| MORNING (3) | 早盘交易中 Morning session |
| REST (4) | 午间休市 Lunch break |
| AFTERNOON (5) | 午盘交易中 Afternoon session |
| CLOSED (6) | 收盘 Closed |
| MAAUCTION (7) | 竞价撮合 Auction matching |
| PRE_MARKET_BEGIN (8) | 美股盘前开始 Start of US pre-market session |
| PRE_MARKET_END (9) | 美股盘前结束 End of US pre-market session |
| AFTER_HOURS_BEGIN (10) | 美股盘后开始 Start of US after-hours session |
| AFTER_HOURS_END (11) | 美股盘后结束 End of US after-hours session |
| FUTU_SWITCH_DATE (12) | moomoo 切交易日 moomoo trading-date rollover |
| NIGHT_OPEN (13) | 衍生品夜市开盘 Derivatives night session open |
| NIGHT_END (14) | 衍生品夜市收盘 Derivatives night session close |
| FUTURE_DAY_OPEN (15) | 期货日市开盘 Futures day session open |
| FUTURE_DAY_BREAK (16) | 期货日市休市 Futures day session break |
| FUTURE_DAY_CLOSE (17) | 期货日市收盘 Futures day session close |
| FUTURE_DAY_WAIT_OPEN (18) | 期货日市等待开盘 Futures day session awaiting open |
| HK_CAS (19) | 港股盘后竞价（Closing Auction Session） HK Closing Auction Session |
| FUTURE_NIGHT_WAIT (20) | 期货夜市等待 Futures night session awaiting open |
| FUTURE_AFTERNOON (21) | 期货下午开盘（已废弃） Futures afternoon open (deprecated) |
| FUTURE_SWITCH_DATE (22) | 衍生品切交易日 Derivatives trading-date rollover |
| FUTURE_OPEN (23) | 衍生品开盘 Derivatives open |
| FUTURE_BREAK (24) | 衍生品休息 Derivatives break |
| FUTURE_BREAK_OVER (25) | 衍生品休息后开盘 Derivatives trading resumes after a break |
| FUTURE_CLOSE (26) | 衍生品收盘 Derivatives close |
| STIB_AFTER_HOURS_WAIT (27) | 科创板盘后撮合等待 Awaiting STAR Market after-hours fixed-price matching |
| STIB_AFTER_HOURS_BEGIN (28) | 科创板盘后交易开始 Start of STAR Market after-hours fixed-price trading |
| STIB_AFTER_HOURS_END (29) | 科创板盘后交易结束 End of STAR Market after-hours fixed-price trading |
| CLOSE_AUCTION (30) | 收市竞价 Closing auction |
| AFTERNOON_END (31) | 已收盘 Closed |
| NIGHT (32) | 夜市交易中 Night session trading |
| OVERNIGHT_BEGIN (33) | 美股夜盘开始 Start of US overnight session |
| OVERNIGHT_END (34) | 美股夜盘结束 End of US overnight session |
| TRADE_AT_LAST (35) | 收盘前成交 Trade-at-last phase (API label; timing unverified) |
| TRADE_AUCTION (36) | 收盘前竞价 Auction trading phase (API label; timing unverified) |
| OVERNIGHT (37) | 美股夜盘交易时段 US overnight session |

## trade_section_type（交易时段类型数值，get_market_state 出参）

| 取值 Value | 含义 Meaning |
| --- | --- |
| US_PREMARKET (5) | 美股盘前 US pre-market |
| US_AFTERHOURS (6) | 美股盘后 US after-hours |
| US_OVERNIGHT (11) | 美股夜盘 US overnight |
| US_REGULAR (12) | 美股盘中常规 US regular trading session |
| DEFAULT (20) | 盘中默认（HK / 沪深 / 数字货币 / 外汇等通用时段） Default (HK / SH / SZ / Crypto / Forex) |
| REGULAR (21) | 仅一段交易时间（美股期权常规） Single trading session (US options regular trading hours) |
| US_INDEX_OPTION_REGULAR (22) | 美股指数期权常规交易时间表 US index options regular trading hours (RTH) |
| US_INDEX_OPTION_GLOBAL (23) | 美股指数期权 Global 时段 US index options global trading hours (GTH) |
| US_INDEX_OPTION_CURB (24) | 美股指数期权 CURB 时段 US index options Curb session |
| JP_INDEX_OPTION_NIGHT (25) | 日本指数期权夜市时段 Japanese index options night session |
| JP_INDEX_OPTION_REGULAR (26) | 日本指数期权日市时段 Japanese index options regular session |

## market（市场前缀）

板块接口 / 全市场筛选等接口的 `market` 入参取值。

SH 与 SZ 在板块接口上共用 A 股板块集合（调用 SH 或 SZ 等价）。

| 取值 Value | 含义 Meaning |
| --- | --- |
| HK | 港股 Hong Kong |
| US | 美股 United States |
| SH | 上证 A 股 Shanghai A-share |
| SZ | 深证 A 股 Shenzhen A-share |
| SG | 新加坡股 Singapore |
| JP | 日股 Japan |
| AU | 澳股 Australia |
| CA | 加股 Canada |
| MY | 马股 Malaysia |
| KR | 韩股 South Korea |

## plate_class（板块分类，板块接口用）

| 取值 Value | 含义 Meaning |
| --- | --- |
| ALL | 全部板块 All security groups |
| INDUSTRY | 行业板块 Industry group |
| REGION | 地域板块（仅 SH / SZ 支持） Regional group (SH / SZ only) |
| CONCEPT | 概念板块 Thematic group |
| OTHER | 其他板块 Other security groups |

## sort_field（板块成份股排序字段，get_plate_stock 入参用）

Best bid/ask price 与 size 是盘口最优买卖价及对应挂单量；Trading value 是成交金额，Volume 是成交数量，Share turnover rate 是换手率。Order-book imbalance（委比）、relative volume（量比）和 high-low price range（振幅）保留业务区别，未根据标签推定后端公式。流通股本译为 tradable shares，不自动等同于美股 free float。首日实际涨跌幅、融资按金比例和少见权证字段的计算基准待确认。

| 取值 Value | 含义 Meaning |
| --- | --- |
| NONE | 不排序（默认，按后端默认顺序） No sort (default, server order) |
| CODE | 股票代码 Stock code |
| CHANGE_RATE | 涨跌幅 Price change (%) |
| NAME | 股票名称 Stock name |
| MARKET_VAL | 总市值 Total market cap |
| PRICE_CHANGE_VAL | 涨跌额 Price change |
| CUR_PRICE | 最新价 Latest price |
| PRICE_CHANGE_SPEED | 价格变动速率 Rate of price change |
| TURNOVER | 成交额 Trading value (turnover) |
| VOLUME | 成交量 Volume |
| PRICE_HIGHEST | 最高价 High price |
| PRICE_LOWEST | 最低价 Low price |
| PRICE_OPEN | 开盘价 Opening price |
| PRICE_LAST | 昨收价 Previous close |
| PE | 市盈率 P/E ratio |
| ASK_PRICE | 卖一价 Best ask price |
| BID_PRICE | 买一价 Best bid price |
| ASK_VOL | 卖一量 Best ask size |
| BID_VOL | 买一量 Best bid size |
| TURNOVER_RATIO | 换手率 Share turnover rate |
| BUYSELL_RATIO | 委比 Order-book imbalance ratio |
| VOLUME_RATIO | 量比 Relative trading volume (volume ratio) |
| AMPLITUDE | 振幅 High-low price range (%) |
| TOTAL_SHARES | 总股本 Shares outstanding |
| CIRC_TOTAL_SHARES | 流通股本 Tradable shares |
| CIRC_MARKET_VALUE | 流通市值 Market capitalization of tradable shares |
| DIVIDEND_RATIO_TTM | 股息率 TTM Trailing twelve-month (TTM) dividend yield |
| DIVIDEND_RATIO_LFY | 股息率 LFY（上一财年） Last fiscal year (LFY) dividend yield |
| PREMIUM | 溢价（窝轮/牛熊证用） Premium (warrants/CBBCs) |
| PRICE_RISE_COUNT | 连续上涨天数 Consecutive days of price gains |
| MARGINABLE | 可融资标的 Marginable |
| MORTGAGE_RATE | 融资按金比例 Margin deposit ratio (API field; calculation basis unverified) |
| SHORT_SELLING | 可沽空标的 Eligible for short selling |
| SHORT_REF_RATE | 沽空参考利率 Reference stock borrow rate |
| LONG_MARGIN_INITIAL_RATIO | 多头初始保证金比率 Initial margin ratio for long positions |
| SHORT_MARGIN_INITIAL_RATIO | 空头初始保证金比率 Initial margin ratio for short positions |
| IPO_PRICE | 新股发行价 IPO offer price |
| LIST_TIME | 上市时间 Listing time |
| IPO_PE | 新股发行 PE IPO offer P/E ratio |
| IPO_PRICE_CHANGE_RATIO | 新股累计涨跌幅 Cumulative price change since IPO (%) |
| CONTINUOUS_RISE_DAY_CNT | 新股连续上涨天数 Consecutive days of price gains since IPO |
| FIRST_DAY_PCR | 首日涨跌幅 First-day price change (%) |
| FIRST_DAY_REAL_PCR | 首日实际涨跌幅 Actual first-day price change (%) (API-defined measure) |
| ISSUE_SIZE | 发行规模 Issue size |
| PRE_CUR_PRICE | 盘前最新价 Pre-market latest price |
| PRE_PRICE_CHANGE_VAL | 盘前涨跌额 Pre-market price change |
| PRE_CHANGE_RATE | 盘前涨跌幅 Pre-market price change (%) |
| AFTER_CUR_PRICE | 盘后最新价 After-hours latest price |
| AFTER_PRICE_CHANGE_VAL | 盘后涨跌额 After-hours price change |
| AFTER_CHANGE_RATE | 盘后涨跌幅 After-hours price change (%) |
| PRE_AMPLITUDE | 盘前振幅 Pre-market high-low price range (%) |
| AFTER_AMPLITUDE | 盘后振幅 After-hours high-low price range (%) |
| PRE_TURNOVER | 盘前成交额 Pre-market trading value |
| AFTER_TURNOVER | 盘后成交额 After-hours trading value |
| PRE_VOLUME | 盘前成交量 Pre-market volume |
| AFTER_VOLUME | 盘后成交量 After-hours volume |
| HSG_HOLD_NUM | 沪深港通持股数 Stock Connect shares held |
| HSG_HOLD_RATIO | 沪深港通持股占比 Stock Connect shareholding percentage |
| CHANGE_RATIO_5_DAYS | 5 日涨跌幅 5-day price change (%) |
| CHANGE_RATIO_10_DAYS | 10 日涨跌幅 10-day price change (%) |
| CHANGE_RATIO_20_DAYS | 20 日涨跌幅 20-day price change (%) |
| CHANGE_RATIO_60_DAYS | 60 日涨跌幅 60-day price change (%) |
| CHANGE_RATIO_120_DAYS | 120 日涨跌幅 120-day price change (%) |
| CHANGE_RATIO_250_DAYS | 250 日涨跌幅 250-day price change (%) |
| CHANGE_RATIO_YEAR | 年初至今涨跌幅 Year-to-date (YTD) price change (%) |
| CHANGE_RATIO_5_MIN | 5 分钟涨跌幅 5-minute price change (%) |
| ADR_CODE | ADR 关联代码 Associated ADR symbol |
| ADR_PRICE | ADR 价格 ADR price |
| ADR_DIFF_PRICE | ADR 折溢价金额 ADR premium/discount amount |
| ADR_DIFF_PER | ADR 折溢价百分比 ADR premium/discount percentage |
| ADR_CONVERTION_RATIO | ADR 换股比率 ADR conversion ratio |
| ADR_RATIO | ADR 比率 ADR ratio |
| ADR_TRAD_VOL | ADR 成交量 ADR trading volume |
| HSG_HOLD_AMOUNT | 沪深港通持股金额 Stock Connect holdings value |
| ADR_PRICE_HK | ADR 港股关联价 ADR-linked HK stock price (pricing basis unverified) |
| HSG_DAY_FLOW | 沪深港通当日资金流 Stock Connect daily flow |
| HSG_WEEK_FLOW | 沪深港通近一周资金流 Stock Connect weekly flow |
| HSG_MONTH_FLOW | 沪深港通近一月资金流 Stock Connect monthly flow |
| HSG_QUATER_FLOW | 沪深港通近一季资金流 Stock Connect quarterly flow |
| TTM_PE | TTM 市盈率 Trailing twelve-month (TTM) P/E ratio |
| ANNUAL_PE | 静态市盈率 P/E based on the latest full-year earnings |
| BMP_PRICE | 暗盘价 HK IPO grey market price |
| BMP_PRICE_CHANGE_VAL | 暗盘涨跌额 HK IPO grey market price change |
| BMP_PRICE_CHANGE_RATE | 暗盘涨跌幅 HK IPO grey market price change (%) |
| WEIGHT | 板块权重 Weight in the security group |
| EFFECT_DOT | 影响点数 Contribution in points |
| US_FUTURE_DEFAULT | 美股期货默认排序 US futures default sort |
| LAST_SETTLE_PRICE | 昨结算价（期货） Previous settlement price (futures) |
| POSITION | 持仓量（期货） Open interest (futures) |
| POSITION_CHANGE | 日增仓（期货） Daily change in open interest (futures) |
| LAST_TRADE_TIME | 最后交易时间（期货） Last trade time (futures) |
| EN_NAME | 英文名称 English name |
| DARK_CHANGE_RATIO | 暗盘涨跌幅（兼容字段） HK IPO grey market price change (%) (legacy field) |
| DARK_CHANGE_VAL | 暗盘涨跌额（兼容字段） HK IPO grey market price change (legacy field) |
| PB | 市净率 P/B ratio |
| TRUST_AUM | 信托基金资产规模 AUM Trust fund assets under management (AUM) |
| TRADE_INFO | 交易信息 Trade info |
| CURRENCY_CODE | 货币代码 Currency code |
| MATURITY_DATE | 到期日（窝轮/可转债） Maturity date (warrants/convertible bonds) |
| RELATION_WEIGHT | 关联权重 Related weight |
| CONVERT_PREMINUM_RATIO | 可转债溢价率 Convertible bond premium (%) (valuation basis unverified) |
| STRB_PREMIUM_RATIO | 跨价权证溢价率 Straddle warrant premium rate |
| PUT_LEVER_PRICE | 认沽证杠杆价 Put warrant leverage price |
| CALL_LEVER_PRICE | 认购证杠杆价 Call warrant leverage price |
| STRB_VALUE | 跨价权证价值 Straddle warrant value |
| CONVERT_STOCK_PRICE | 可转债转股价 Convertible bond conversion price |
| WRNT_LAST_TRADE_DATE | 窝轮最后交易日 Warrant last trade date |
| CHANGE_RATIO_3_YEAR | 3 年涨跌幅 3-year price change (%) |
| JA_NAME | 日文名称 Japanese name |
| OVERNIGHT_PRICE | 夜盘价 Overnight price |
| OVERNIGHT_TURNOVER | 夜盘成交额 Overnight trading value |
| OVERNIGHT_VOLUME | 夜盘成交量 Overnight volume |
| OVERNIGHT_AMPLITUDE | 夜盘振幅 Overnight high-low price range (%) |
| OVERNIGHT_PRICE_CHANGE_VAL | 夜盘涨跌额 Overnight price change |
| OVERNIGHT_CHANGE_RATE | 夜盘涨跌幅 Overnight price change (%) |
| HOT | 热度 Popularity |
| ETF_LEVERAGE | ETF 杠杆倍数 ETF leverage multiple |
| DIVIDEND_TTM | TTM 股息 Trailing twelve-month (TTM) dividend |
| PAYOUT_RATIO_LFY | 派息率 LFY Last fiscal year (LFY) dividend payout ratio |
| DISTRIBUTION_FREQUENCY | 派息频率 Dividend / distribution frequency |
| MAX_DIVIDEND_GROW_YEAR | 最大连续派息增长年数 Maximum consecutive years of dividend growth |
| DIVIDEND_INCREASE_RATE_1YEAR | 近 1 年派息增长率 1-year dividend growth rate |
| AVERAGE_DIVIDEND_YIELD_5YEAR | 近 5 年平均股息率 5-year average dividend yield |
| CHANGE_RATIO_24H | 24 小时涨跌幅 24-hour price change (%) |
| DEBT_ASSET_RATIO | 资产负债率 Liabilities-to-assets ratio (total liabilities / total assets) |
| TH_NAME | 泰文名称 Thai name |

## price_type（价格类排序口径，get_plate_stock 入参用）

| 取值 Value | 含义 Meaning |
| --- | --- |
| NORMAL | 正常价（默认） Regular-session price (default) |
| BEFORE | 盘前价 Pre-market price |
| AFTER | 盘后价 After-hours price |
| OVERNIGHT | 夜盘价 Overnight price |

## statement_type（财报报表类型，入参）

| 取值 Value | 含义 Meaning |
| --- | --- |
| 1 | Income statement（利润表） |
| 2 | Balance sheet（资产负债表） |
| 3 | Cash flow statement（现金流量表） |
| 4 | Key indicators（主要指标） |

## financial_type（财报期类型，入参/出参）

英文 H1 表示半年累计，不能用于 Q2 单季；Q6/Q9 是 API 原有标签，英文释义分别写成 H1/9M，不能理解为第六/第九季度。第 10 项是多期选择器的中文定义，不能在冲突未解决前擅自改成 Latest。

| 取值 Value | 含义 Meaning |
| --- | --- |
| 0 | 自动匹配（仅入参；按 date 自动匹配期类型，主营构成 get_financials_revenue_breakdown 用） Auto-match (request only; infer the period from date; used by get_financials_revenue_breakdown) |
| 1 | Q1（一季报，单季） Q1 report (first quarter only) |
| 2 | Q2（二季报，单季） Q2 report (second quarter only; documentation conflict) |
| 3 | Q3（三季报，单季） Q3 report (third quarter only) |
| 4 | Q4（四季报，单季） Q4 report (fourth quarter only) |
| 5 | Q6（累计中报，上半年累计） First-half cumulative report (H1; API label Q6) |
| 6 | Q9（累计三季报，前三季累计） Nine-month cumulative report (9M; API label Q9) |
| 7 | 年报 Annual report |
| 8 | Aggregated quarterly（聚合季报，仅美股；主营构成 get_financials_revenue_breakdown 用） Aggregated quarterly (US only; used by get_financials_revenue_breakdown) |
| 9 | 全部单季报（Q1~Q4），多期选择器，仅入参 All single-quarter reports (Q1–Q4); multi-period selector; request only |
| 10 | 单季报 + 年报（Q1~Q4 及年报），多期选择器，仅入参；get_financials_statements 默认值 Single-quarter and annual reports (Q1–Q4 and annual); multi-period selector; request only; default for get_financials_statements; documentation conflict |
| 11 | 全部累计季报（Q1,Q6,Q9,年报），多期选择器，仅入参 All cumulative-period reports (Q1, H1, 9M and annual); multi-period selector; request only |
| 102 | 全部累计季报（Q1,Q6,Q9,年报），多期选择器，仅入参；get_company_operational_efficiency 用 All cumulative-period reports (Q1, H1, 9M and annual); multi-period selector; request only; used by get_company_operational_efficiency |
| 70 | 马来西亚 Other 单季报（period_text 后缀 SQ） Other single-quarter report (Malaysia; period_text suffix SQ) |
| 71 | 马来西亚 Other 累计季报（period_text 后缀 CQ） Other cumulative-period report (Malaysia; period_text suffix CQ) |

## financial_structure（财报子结构编号，出参）

不同 `statement_type` 对应不同 structure 集合；同一 `statement_type` 在不同市场可能落到不同 structure。

| 取值 Value | 含义 Meaning | 所属 statement_type |
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

| 取值 Value | 含义 Meaning |
| --- | --- |
| MONTH | 月度合约 Monthly |
| WEEK | 周度合约 Weekly |
| END_OF_MONTH | 月末合约 End of month |
| QUARTERLY | 季度合约 Quarterly |
| WEEKMON | 周一到期 Monday expiry |
| WEEKTUE | 周二到期 Tuesday expiry |
| WEEKWED | 周三到期 Wednesday expiry |
| WEEKTHU | 周四到期 Thursday expiry |
| WEEKFRI | 周五到期 Friday expiry |
| N/A | 未知 Unknown |

## index_option_type（指数期权类型，入参）

| 取值 Value | 市场 Market | 含义 Meaning |
| --- | --- | --- |
| 1 | HK | 恒生指数 (HSI) Hang Seng Index (HSI) |
| 2 | HK | 国企指数 (HSCEI) Hang Seng China Enterprises Index (HSCEI) |
| 3 | HK | 小型恒指 (Mini-HSI) |
| 4 | HK | 小型国指 (Mini-HSCEI) |
| 5 | HK | 恒生科技指数 (HSTECH) Hang Seng TECH Index (HSTECH) |
| 1000 | US | 兜底指数期权 Fallback index option |
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

FLEX 是可定制合约条款的交易所期权；adjusted option 是因公司行动等调整交割条款的合约。二者不是同义词，FLEX 也不必是经拆股等公司行动调整而来。API 将哪些具体产品归入 NON_STANDARD 尚未逐一验证。

| 取值 Value | 含义 Meaning |
| --- | --- |
| ALL | 全部（默认） All (default) |
| STANDARD | 仅标准期权 Standard options only |
| NON_STANDARD | 仅非标准期权（如 FLEX 定制期权、公司行动调整合约） Non-standard options only (e.g., customized FLEX options or contracts adjusted for corporate actions) |

## combo_strategy（组合期权策略类型，入参/出参）

用于 组合期权策略 与 组合期权价差 的 `strategy` 字段（整数）。与交易下单的字符串枚举 `option_strategy` 不是同一套，不要混用。未列出的数值（如 `3` / `5` / `10` / `12`）不在网关枚举内，传入返回 `ret_code=-3`。

须 `spread` 的策略：不传 `spread` 时后端会业务失败（`ret_code=-5`）。请先调价差接口，再把 `default_spread` 或 `spread_list` 中的值传入策略接口。

`quote.option_strategy` 返回的 `combo_list` 一项永远是一套组合，腿在 `legs[]`。`Covered(2)` / `Collar(8)` 会在期权腿前补路径正股（`instrument=STOCK`），不下发 `side` / `quantity`；询价时由调用方填写。港股不支持 `2/8`。

| 取值 Value | 名称 Name | 含义 Meaning | 须 spread | 须 far_expire_time |
| --- | --- | --- | --- | --- |
| 1 | SingleOption | 单腿期权 Single-leg option | 否 | 否 |
| 2 | Covered | 备兑 Covered | 否 | 否 |
| 4 | Spread | 垂直价差 Vertical spread | 是 | 否 |
| 6 | Straddle | 跨式 Straddle | 否 | 否 |
| 7 | Strangle | 宽跨式 Strangle | 是 | 否 |
| 8 | Collar | 领口 Collar | 是 | 否 |
| 9 | Butterfly | 蝶式 Butterfly | 是 | 否 |
| 11 | Condor | 鹰式 Condor | 是 | 否 |
| 13 | IronButterfly | 铁蝶 Iron butterfly | 是 | 否 |
| 14 | IronCondor | 铁鹰 Iron condor | 是 | 否 |
| 15 | CalendarSpread | 日历价差 Calendar spread | 否 | 是 |
| 16 | DiagonalSpread | 对角价差 Diagonal spread | 是 | 是 |
| 100 | Customize | 自定义 Custom | 否 | 否 |

## option_standard_type（期权规格类型，出参）

FLEX 定制期权与公司行动调整合约分开解释；本表的示例不是已验证的全部分类规则。

用于期权链与组合期权腿的 `option_standard_type`。入参过滤见 filter_standard（多一个 `ALL`）。

| 取值 Value | 含义 Meaning |
| --- | --- |
| STANDARD | 标准期权 Standard option |
| NON_STANDARD | 非标准期权（如 FLEX 定制期权、公司行动调整合约） Non-standard option (e.g., customized FLEX options or contracts adjusted for corporate actions) |
| N/A | 未知 / 未映射 Unknown / unmapped |

## combo_leg_instrument（组合期权腿品类，出参）

用于 组合期权策略 的 `legs[].instrument`。询价接口的腿不带该字段，靠 `code` 区分期权与正股。

| 取值 Value | 含义 Meaning |
| --- | --- |
| OPTION | 期权合约 Option contract |
| STOCK | 标的正股（仅 Covered / Collar 由网关补入） Underlying stock (included for Covered / Collar only) |

## combo_side（组合询价腿方向，入参/回显）

用于 组合期权询价 的 `legs[].side`。网关不从策略类型推断，必须由调用方传入。与逐笔 `ticker_direction` 的 BUY/SELL（买盘/卖盘）不是同一语义。

| 取值 Value | 含义 Meaning |
| --- | --- |
| BUY | 买入该腿 Buy this leg |
| SELL | 卖出该腿 Sell this leg |

## holder_type（股东类型，入参/出参）

本次保留 holder_type 英文取值列，只审校含义列。Sponsor、manager、issuer 等机构角色不可省略成所管理的资产类别；Individual Insider 不等于所有个人股东，ADR Issuer 是发行机构而不是 ADS 本身。

用于 get_shareholders_holding_changes 的 `holder_type`（英文文本）/ `holder_type_id`（数值）。亦用于 get_shareholders_holder_detail 的 request_type（另含 1000=全部，默认 1000）。

| holder_type_id | holder_type（对外英文） | 含义 Meaning |
| --- | --- | --- |
| 1 | Other Institution | 其他机构 Other institution |
| 2 | Traditional Investment Manager | 传统投资经理 Traditional investment manager |
| 3 | Hedge Fund Manager / CTA | 对冲基金 Hedge fund manager / commodity trading advisor (CTA) |
| 4 | VC / PE Firm | 风险资本/私募股权 Venture capital / private equity firm |
| 5 | Corporate Pension Plan Sponsor | 企业年金 Corporate pension plan sponsor |
| 6 | Foundation Fund Sponsor | 基金会基金 Foundation fund sponsor |
| 7 | Insurance Company | 保险公司 Insurance company |
| 8 | Bank / Investment Bank | 银行/投资银行 Bank / Investment bank |
| 9 | Family Office / Trust | 家族办公室/信托 Family office / Trust |
| 10 | Sovereign Wealth Fund | 主权财富基金 Sovereign wealth fund |
| 11 | REIT / Real Estate Investment Manager | REIT / real estate investment manager |
| 12 | Structured Finance Pool Manager | 结构化融资经理 Structured finance pool manager |
| 13 | Union Pension Plan Sponsor | 工会养老金计划发起方 Union pension plan sponsor |
| 14 | Government Pension Plan Sponsor | 政府养老金 Government pension plan sponsor |
| 15 | Endowment Fund Sponsor | 捐赠基金 Endowment fund sponsor |
| 100 | Individual Insider | 个人内部人 Individual insider |
| 200 | ADR Issuer | ADR 发行机构 ADR issuer |
| 300 | Public Corporation | 上市公司 Public corporation |
| 400 | Private Corporation | 未公开上市公司 Private corporation |
| 500 | State-Owned Shares | 国有股 State-owned shares |

## pub_type（财报披露时点类型，出参）

| 取值 Value | 含义 Meaning |
| --- | --- |
| 0 | 当天披露（未识别出具体盘前/盘后） Disclosure on that date (pre-market / after-hours timing unspecified) |
| 1 | 盘前 Pre-market disclosure |
| 2 | 盘后 After-hours disclosure |

## delivery_type（交割方式，get_future_info 用）

| 取值 Value | 含义 Meaning |
| --- | --- |
| UNKNOWN | 未知 / 未指定 Unknown / Unspecified |
| PHYSICAL | 实物交割 Physical delivery |
| CASH | 现金交割 Cash settlement |

## query_time_period（期权波动率查询时间周期，入参）

| 取值 Value | 含义 Meaning |
| --- | --- |
| 1 | 1 周 1 week |
| 2 | 1 月（默认） 1 month (default) |
| 3 | 3 月 3 months |
| 4 | 6 月 6 months |
| 5 | 1 年 1 year |

## impvol_status（期权波动率分析状态，出参）

这里描述期权隐含波动率的相对评估，不是标的股票估值结论；高估/低估阈值未在此词典中说明。

| 取值 Value | 含义 Meaning |
| --- | --- |
| FLUCTUATING | 震荡中 Fluctuating implied volatility |
| OVERVALUED | 高估 Implied volatility assessed as high |
| UNDERVALUED | 低估 Implied volatility assessed as low |
