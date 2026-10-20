# Quote 行情接口指引

这份文档面向后续编写 skill：按当前源码整理 `Quote Commands` 下所有行情相关 CLI 命令、参数、默认值、BFF ID 和底层 API。

## 来源与范围

- 静态命令来自 `cmd/quote.go`、`cmd/basicinfo.go`、`cmd/snapshot.go`、`cmd/kline.go`、`cmd/history_kline.go`、`cmd/ticker.go`、`cmd/rtdata.go`、`cmd/depth.go`、`cmd/rank.go`、`cmd/option.go`。
- 动态 REST 命令来自 `cmd/quote_rest_specs.go` 和 `cmd/quote_rest.go`。
- 本文只覆盖 `group == quote` 的行情命令。`news` 分组和 `sim` 分组不注册为当前 CLI 行情命令。
- 所有命令都支持全局 `--format table|json`，默认 `table`；写 skill 时优先使用 `--format json`，输出结构更稳定。
- 除 `auth/config/check/version/help/update/completion` 等免登录命令外，行情命令需要已完成 OAuth 登录并具备相应行情权限。

## 全局约定

- Symbol 统一使用 `MARKET.CODE`，例如 `HK.00700`、`US.AAPL`、`CC.BTCUSD`。旧格式 `700.HK`、裸代码 `700`、裸 ticker `AAPL` 会报错。
- 港股纯数字 code 会左侧补零到 5 位：`HK.700` 会规范化为 `HK.00700`；市场前缀会转大写；纯小写字母 ticker 会转大写，例如 `us.aapl` -> `US.AAPL`。
- 多 symbol 参数会被解析后写入 `code_list`。
- 动态 REST 的 flag 名由参数名转换而来：下划线转短横线，例如 `next_key` -> `--next-key`；`stock_owner` 暴露为 `--symbol`；`filter_security` 暴露为 `--filter-symbol`。
- `moomoo search [keyword]` 的 `keyword` 是普通搜索词，例如 `腾讯`、`AAPL`、`新能源`；对外参数和 flag 都叫 `keyword`，不会按 symbol 校验，实际请求时会写入后端需要的 `symbol` query 字段。
- `json` 类型 flag 必须传合法 JSON 字符串，例如 `--strategy '{"market_category_list":[3]}'`。
- 默认值中的 `TODAY`、`TODAY+30`、`TODAY_COMPACT` 等会在运行时按本机日期解析。
- 分页接口通常使用 `--next-key` 或 `--next-time`；下一页取上一页响应里的 `pagination.next_key` / `extra.next_time`。
- Table 输出只展示常用列；需要完整字段时使用 `--format json`。

## JSON 返回形态

`quote` 和 `rank` 会输出已解包后的数组；大多数 BFF 命令输出 `data`。如果 BFF 同时返回分页或跳过项，CLI 会包装为：

```json
{
  "data": {
    "items": []
  },
  "pagination": {
    "next_key": "..."
  },
  "skipped": []
}
```

## 静态行情命令

| 命令 | BFF ID | API | 用途 |
| --- | --- | --- | --- |
| `moomoo quote <symbol...>` | `quote.stock_quote` | `POST /api/v1.0/quote/stock-quote` | 获取一个或多个标的的实时报价。美股有盘前、盘后、夜盘数据时，table 输出会额外展示会话行。 |
| `moomoo basicinfo <symbol...>` | `quote.stock_basicinfo` | `POST /api/v1.0/quote/stock-basicinfo` | 批量获取静态标的信息，不包含实时行情。 |
| `moomoo snapshot <symbol...>` | `quote.market_snapshot` | `POST /api/v1.0/quote/snapshot` | 批量获取市场快照。 |
| `moomoo kline <symbol>` | `quote.cur_kline` | `GET /api/v1.0/quote/{symbol}/cur-kline` | 获取指定标的最新 N 根 K 线。历史区间查询使用 `history-kline`。 |
| `moomoo history-kline <symbol>` | `quote.history_kline` | `GET /api/v1.0/quote/{symbol}/history-kline` | 按日期区间获取历史 K 线；分页时把上次响应的 `next_time` 传给 `--next-time`。 |
| `moomoo ticker <symbol>` | `quote.rt_ticker` | `GET /api/v1.0/quote/{symbol}/rt-ticker` | 获取最新逐笔成交。 |
| `moomoo rt-data <symbol>` | `quote.rt_data` | `GET /api/v1.0/quote/{symbol}/rt-data` | 获取分时数据，按交易会话分组。 |
| `moomoo order-book <symbol>` | `quote.order_book` | `POST /api/v1.0/quote/order-book` | 获取实时摆盘深度；行情权限决定最大深度，`--num` 只限制返回层数。 |
| `moomoo depth <symbol>` | `quote.order_book` | `POST /api/v1.0/quote/order-book` | `order-book` 的别名。 |
| `moomoo rank [type]` | `quote.stock_screen` | `POST /api/v1.0/quote/stock-screen` | 市场排行，底层通过 stock-screen 组合筛选条件实现。默认展示港股成交量 Top 20。 |
| `moomoo option chain <symbol>` | `quote.option_chain` | `GET /api/v1.0/quote/{symbol}/option-chain` | 查询指定标的期权链，支持 HK / US / JP。未传日期时，CLI 会先取到期日列表并选择未来 30 天窗口内的范围。 |

### 静态命令参数

- `quote/basicinfo/snapshot`: 只接受一个或多个 `<symbol>`，无命令专属 flag。
- `kline`: `--num, -n` 默认 `100`，范围 1-370；`--ktype` 默认 `2`；`--autype` 默认 `1`；`--extended-time` 默认 `0`；`--pred-side` 默认 `0`。
- `history-kline`: `--start`、`--end`，默认 `end=today`；`--next-time` 默认 `0`，优先级高于 `--end`；`--ktype` 同 `kline`；`--autype` 默认 `1`；`--num, -n` 默认 `100`，最大 370；`--extended-time`、`--pred-side` 同 `kline`。
- `ticker`: `--num, -n` 默认 `20`，范围 1-750；`--count, -c` 是 `--num` 的兼容别名；`--period` 可重复，`NORMAL / BEFORE / AFTER / OVERNIGHT`。
- `rt-data`: `--section` 默认 `NORMAL`，可选 `NORMAL / FULL / PREMARKET / AFTERHOURS / HK_DARK / OVERNIGHT`。
- `order-book/depth`: `--num, -n` 默认 `0`，表示返回行情权限允许的最大深度；显式传值范围 1-60。
- `rank`: `[type]` 默认 `volume`，可选 `volume / turnover / gainers / losers / amplitude`；`--market, -m` 默认 `HK`，可选 `HK / US / CN`；`--count, -c` 默认 `20`。
- `option chain`: `--start`、`--end` 为到期日范围；不传时自动选择未来 30 天窗口；`--index-option-type` 可手动指定指数期权类型；`--filter-standard` 默认 `ALL`，可选 `ALL / STANDARD / NON_STANDARD`。

### 静态命令示例

```bash
moomoo quote HK.00700 US.AAPL --format json
moomoo basicinfo HK.00700 US.AAPL --format json
moomoo snapshot HK.00700 US.AAPL --format json
moomoo kline US.AAPL --ktype 1 --extended-time 2 --format json
moomoo history-kline HK.00700 --start 2026-01-01 --end 2026-03-01 --num 100 --format json
moomoo ticker US.AAPL --num 50 --period OVERNIGHT --format json
moomoo rt-data US.AAPL --section PREMARKET --format json
moomoo order-book HK.00700 --num 10 --format json
moomoo rank gainers --market US --count 30 --format json
moomoo option chain HK.00700 --start 2026-05-01 --end 2026-05-31 --format json
```

### 静态返回示例

```json
[
  {
    "code": "HK.00700",
    "sc_name": "腾讯控股",
    "last_price": 380.8,
    "prev_close_price": 375.4,
    "volume": 25500123,
    "turnover": 9680012345.67
  }
]
```

```json
{
  "kline_list": [
    {
      "time_key": 1760227200000,
      "open_price": 190.1,
      "high_price": 191.2,
      "low_price": 188.9,
      "close_price": 190.8,
      "volume": 61234567
    }
  ]
}
```

## 聚合 REST 行情命令

旧的单 endpoint 命令名大多不作为 root command 使用，应该使用聚合命令和 selector flag：

```bash
moomoo broker HK.00700 --view current --format json
moomoo capital HK.00700 --view history --period-type WEEK --format json
moomoo plate --view list --market HK --plate-class INDUSTRY --format json
```

selector 值大小写不敏感。聚合命令会注册该组所有变体的 flag，但只有当前 selector 选中的 endpoint 会读取对应参数。

| 聚合命令 | selector | BFF ID | API |
| --- | --- | --- | --- |
| `broker <symbol>` | `--view current` 默认 | `quote.top_ten_brokers` | `GET /api/v1.0/quote/{symbol}/top-brokers` |
| `broker <symbol>` | `--view history` | `quote.top_ten_brokers_history` | `GET /api/v1.0/quote/{symbol}/top-brokers-history` |
| `capital <symbol>` | `--view intraday` 默认 | `quote.capital_flow` | `GET /api/v1.0/quote/{symbol}/capital-flow` |
| `capital <symbol>` | `--view history` | `quote.capital_flow_history` | `GET /api/v1.0/quote/{symbol}/capital-flow/history` |
| `capital <symbol>` | `--view distribution` | `quote.capital_distribution` | `GET /api/v1.0/quote/{symbol}/capital-distribution` |
| `company <symbol> [leader]` | `--view profile` 默认 | `quote.company_profile` | `GET /api/v1.0/quote/{symbol}/company/profile` |
| `company <symbol> [leader]` | `--view executives` | `quote.company_executives` | `GET /api/v1.0/quote/{symbol}/company/executives` |
| `company <symbol> [leader]` | `--view background` | `quote.company_executive_background` | `GET /api/v1.0/quote/{symbol}/company/executive-background` |
| `company <symbol> [leader]` | `--view efficiency` | `quote.company_operational_efficiency` | `GET /api/v1.0/quote/{symbol}/company/operational-efficiency` |
| `corporate-actions <symbol>` | `--type dividends` 默认 | `quote.corporate_actions_dividends` | `GET /api/v1.0/quote/{symbol}/corporate-actions/dividends` |
| `corporate-actions <symbol>` | `--type splits` | `quote.corporate_actions_stock_splits` | `GET /api/v1.0/quote/{symbol}/corporate-actions/splits` |
| `corporate-actions <symbol>` | `--type buybacks` | `quote.corporate_actions_buybacks` | `GET /api/v1.0/quote/{symbol}/corporate-actions/buybacks` |
| `corporate-actions <symbol>` | `--type rehab` | `quote.corporate_actions_rehab` | `GET /api/v1.0/quote/{symbol}/corporate-actions/rehab` |
| `economic-calendar [keyword]` | `--view hot` 默认 | `quote.economic_calendar_hot` | `GET /api/v1.0/quote/economic-calendar/hot` |
| `economic-calendar [keyword]` | `--view search` | `quote.economic_calendar_search` | `GET /api/v1.0/quote/economic-calendar/search` |
| `financials <symbol>` | `--view statements` 默认 | `quote.financials_statements` | `GET /api/v1.0/quote/{symbol}/financials/statements` |
| `financials <symbol>` | `--view revenue` | `quote.financials_revenue_breakdown` | `GET /api/v1.0/quote/{symbol}/financials/revenue-breakdown` |
| `financials <symbol>` | `--view earnings-history` | `quote.financials_earnings_price_history` | `GET /api/v1.0/quote/{symbol}/financials/earnings-price-history` |
| `financials <symbol>` | `--view earnings-move` | `quote.financials_earnings_price_move` | `GET /api/v1.0/quote/{symbol}/financials/earnings-price-move` |
| `ipo-list` | `--market HK/US/SG/MY/CN` | `quote.ipo_list_*` | `GET /api/v1.0/quote/ipo-list/{market}` |
| `option-data <symbol>` | `--view expiration/strategy/spread/probability/volatility` | `quote.option_*` | `GET /api/v1.0/quote/{symbol}/option-*` |
| `plate [symbol]` | `--view list` 默认 | `quote.plate_list` | `GET /api/v1.0/quote/plate-list` |
| `plate [symbol]` | `--view stocks` | `quote.plate_stock` | `GET /api/v1.0/quote/plate-stock` |
| `plate [symbol]` | `--view owner` | `quote.owner_plate` | `GET /api/v1.0/quote/{symbol}/owner-plate` |
| `research <symbol>` | `--type consensus/morningstar/rating` | `quote.research_*` | `GET /api/v1.0/quote/{symbol}/research/*` |
| `search [keyword]` | `--type news/community/feed` | `quote.news_search` / `quote.community_search` / `quote.stock_feed` | `GET /api/v1.0/quote/find-*` |
| `shareholders <symbol>` | `--view overview/institutional/changes/holder-detail/insider-holders/insider-trades` | `quote.shareholders_*` | `GET /api/v1.0/quote/{symbol}/shareholders/*` |
| `short <symbol>` | `--type volume` 默认 | `quote.daily_short_volume` | `GET /api/v1.0/quote/{symbol}/short/daily-volume` |
| `short <symbol>` | `--type interest` | `quote.short_interest` | `GET /api/v1.0/quote/{symbol}/short/interest` |
| `watchlist [symbol...]` | `--action list/groups/add/delete/move-out` | `quote.user_security*` / `quote.modify_user_security` | `GET/POST /api/v1.0/quote/*user-security*` |
| `valuation [symbol]` | `--view detail/plate-stocks/index-stocks/index-plates` | `quote.valuation_*` | `GET /api/v1.0/quote/valuation/*` |

### 聚合命令示例

```bash
moomoo broker HK.00700 --format json
moomoo broker HK.00700 --view history --days-before 5 --format json
moomoo capital HK.00700 --view distribution --format json
moomoo company US.AAPL --view efficiency --limit 20 --format json
moomoo corporate-actions HK.00700 --type rehab --divi-mode exclude_divi --format json
moomoo economic-calendar CPI --view search --format json
moomoo financials US.AAPL --view revenue --financial-type 1 --format json
moomoo ipo-list --market US --format json
moomoo option-data US.AAPL --view volatility --format json
moomoo plate HK.00700 --view owner --format json
moomoo research US.AAPL --type rating --format json
moomoo search 腾讯 --type news --size 20 --format json
moomoo search AAPL --type feed --size 20 --format json
moomoo shareholders US.AAPL --view changes --limit 50 --format json
moomoo short US.AAPL --type interest --count 60 --format json
moomoo watchlist HK.00700 US.AAPL --action add --group-name All --format json
moomoo valuation HK.800000 --view index-stocks --sort-type 2 --sort-id 51 --format json
```

## 独立 REST 行情命令

这些 `quote` endpoint 没有被聚合，当前仍作为 root command 注册。

| 命令 | BFF ID | API | Flags / 说明 |
| --- | --- | --- | --- |
| `moomoo future-info <symbol...>` | `quote.future_info` | `POST /api/v1.0/quote/future-info` | 一个或多个期货 symbol，写入 body `code_list`。 |
| `moomoo market-state <symbol...>` | `quote.market_state` | `POST /api/v1.0/quote/market-state` | 一个或多个 symbol；`--is-contain-ba` 默认 `false`；`--is-contain-overnight` 默认 `false`；`--is-need-crypto-multi-broker` 默认 `false`。 |
| `moomoo combo-option-quote` | `quote.combo_option_quote` | `POST /api/v1.0/quote/combo-option-quote` | `--combo-list` 必填，默认 `[]`，JSON 数组。 |
| `moomoo referencefuture-list <symbol>` | `quote.referencefuture_list` | `GET /api/v1.0/quote/{symbol}/reference-future` | 获取指定标的的关联期货合约列表。 |
| `moomoo stock-screen` | `quote.stock_screen` | `POST /api/v1.0/quote/stock-screen` | `--screen-queries` 必填；`--retrieve-queries`；`--sort`；`--sorts`；`--next-key`；`--limit` 默认 `20`；`--watchlist-stock-ids`；`--holding-stock-ids`；`--user-stock-list-mode`。 |
| `moomoo warrant-screen` | `quote.warrant_screen` | `POST /api/v1.0/quote/warrant-screen` | `--market-type` 默认 `1`；`--is-delay` 默认 `false`；`--only-count` 默认 `false`；`--symbol`；`--screen-groups`；`--sorts`；`--next-key`；`--limit` 默认 `20`。未传 `--symbol`/`--screen-groups` 且 `--market-type` 为默认或 `1` 时，CLI 自动补 `stock_owner=HK.00700`。 |
| `moomoo option-screen` | `quote.option_screen` | `POST /api/v1.0/quote/option-screen` | `--strategy` 必填，默认 `{"market_category_list":[3]}`；`--strategy-param`；`--field-filter`；`--sort-obj`；`--next-key`；`--limit` 默认 `20`；`--request-exact-data` 默认 `1`。 |
| `moomoo trading-days` | `quote.trading_days` | `GET /api/v1.0/quote/trading-days` | `--market` 默认 `HK`；`--start` 默认 `TODAY`；`--end` 默认 `TODAY+30`。 |

### 独立 REST 示例

```bash
moomoo future-info HK.HSImain --format json
moomoo market-state HK.00700 US.AAPL --is-contain-overnight true --format json
moomoo combo-option-quote --combo-list '[{"code":"US.AAPL260116C200000","side":"BUY","qty":1}]' --format json
moomoo referencefuture-list HK.800000 --format json
moomoo stock-screen --limit 20 --format json
moomoo warrant-screen --symbol HK.00700 --limit 20 --format json
moomoo option-screen --strategy '{"market_category_list":[3]}' --limit 20 --format json
moomoo trading-days --market US --start 2026-10-01 --end 2026-10-31 --format json
```

## Skill 编写建议

- 优先使用最短可跑通命令，再按用户需求补 flag。
- 需要完整字段或二次解析时一律加 `--format json`。
- 对聚合 REST 命令，先确定 selector：例如资金相关用 `capital --view intraday/history/distribution`，公司资料用 `company --view profile/executives/background/efficiency`。
- 用户提到旧 endpoint 名时，映射到当前聚合命令；不要直接调用未注册的旧命令名。
- 用户给出的 symbol 不含市场前缀时，先补齐或追问；不要把裸 `AAPL`、`700` 直接传给需要 symbol 的命令。`moomoo search` 例外，它接收普通 keyword。
