# Quote 行情接口分页约定

这份文档面向后续编写 skill：按 moomoo OpenAPI 行情分页约定和当前 `moomoo` CLI 实现整理分页参数、返回结构、停止条件和命令映射。

## 来源与范围

- 官方页面：`https://open.moomoo.com/zh-cn/api/quote/pagination`
- 阅读日期：2026-10-13
- 本文只覆盖行情接口分页。证券交易、模拟交易、加密货币交易的分页规则不在本文范围内。
- 写 skill 时优先使用 `--format json`，因为 table 输出通常不会展示完整 `pagination` / `extra` 字段。

## 官方分页约定

所有涉及列表分页的行情接口遵循统一约定。

### 入参

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `next_key` | string | 翻页游标。首页留空；下一页把上一页响应里的 `pagination.next_key` 原样回传。 |
| `limit` | int | 每页条数。默认值和上限由各接口自行定义。 |

### 出参

分页信息放在响应顶层的 `pagination` 对象，不在 `data` 内。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `has_more` | bool | 是否还有下一页。以 `has_more=false` 作为停止翻页的唯一可靠信号。 |
| `next_key` | string | 下一页游标；无更多数据时通常为 `"-1"`。 |
| `total` | int | 可选字段。部分筛选、评级、内部人、估值、板块成分股等接口会返回满足条件的总条数。 |

`next_key` 对调用方不透明，不能自行解析、拼接或构造，只能原样传回。

## CLI 映射

- 动态 REST 命令会把参数名中的下划线转为短横线：`next_key` 对应 `--next-key`，`next_time` 对应 `--next-time`。
- 首页通常不传 `--next-key`；如果必须显式传空值，也应传空字符串。
- 下一页使用上一页 JSON 输出中的 `pagination.next_key`：

```bash
moomoo plate HK.LIST1045 --view stocks --limit 20 --format json
moomoo plate HK.LIST1045 --view stocks --limit 20 --next-key 'eyJsYXN0X2lkIjo0MH0=' --format json
```

- 大多数 BFF 命令在 `--format json` 时会输出如下结构：

```json
{
  "data": {
    "items": []
  },
  "pagination": {
    "has_more": true,
    "next_key": "eyJsYXN0X2lkIjo0MH0=",
    "total": 156
  }
}
```

- 如果响应存在 `skipped`，CLI 会和 `data`、`pagination` 一起输出：

```json
{
  "data": {},
  "pagination": {},
  "skipped": []
}
```

## 通用翻页算法

1. 首次调用只传业务参数和 `--limit`，不传 `--next-key`。
2. 解析 JSON 顶层 `pagination`。
3. 如果没有 `pagination`，认为当前接口没有分页或本次数据已完整返回。
4. 如果 `pagination.has_more == false`，停止翻页。
5. 如果 `pagination.has_more == true`，读取 `pagination.next_key` 并原样传给下一次请求的 `--next-key`。
6. 不要用 `data` 条数是否小于 `limit` 来判断是否结束；只能作为调试线索。
7. 如果 `next_key` 为空或为 `"-1"` 但 `has_more == true`，应停止并把响应记录为异常数据，避免死循环。

## `next_time` 例外

少数历史类接口不用 `next_key`，而是通过时间游标向更早数据翻页。

### `moomoo history-kline <symbol>`

- 参数：`--next-time`
- 类型：毫秒时间戳
- 来源：上一页响应中的 `extra.next_time`
- 优先级：传入 `--next-time` 后会优先于 `--end`

```bash
moomoo history-kline HK.00700 --start 2026-01-01 --end 2026-03-01 --num 100 --format json
moomoo history-kline HK.00700 --start 2026-01-01 --next-time 1779163200000 --num 100 --format json
```

### `moomoo capital <symbol> --view history`

- 参数：`--next-time`
- 类型：整数时间游标，默认 `0`
- 搭配参数：`--period-type`、`--start`、`--end`、`--count`
- 下一页优先沿用上一页响应中的下一页时间游标；如果响应只给出更早日期边界，则按接口返回的边界调整 `--end`。

```bash
moomoo capital HK.00700 --view history --period-type DAY --count 100 --format json
moomoo capital HK.00700 --view history --period-type DAY --count 100 --next-time 1779163200000 --format json
```

## 当前 CLI 中支持 `--next-key` 的行情命令

| 命令 | selector | 相关 BFF ID | 分页 flags |
| --- | --- | --- | --- |
| `moomoo company <symbol>` | `--view efficiency` | `quote.company_operational_efficiency` | `--next-key`、`--limit` |
| `moomoo corporate-actions <symbol>` | `--type buybacks` | `quote.corporate_actions_buybacks` | `--next-key`、`--limit` |
| `moomoo economic-calendar` | `--view hot` | `quote.economic_calendar_hot` | `--next-key`、`--limit` |
| `moomoo economic-calendar [keyword]` | `--view search` | `quote.economic_calendar_search` | `--next-key`、`--limit` |
| `moomoo financials <symbol>` | `--view statements` | `quote.financials_statements` | `--next-key`、`--limit` |
| `moomoo plate [symbol]` | `--view stocks` | `quote.plate_stock` | `--next-key`、`--limit` |
| `moomoo research <symbol>` | `--type rating` | `quote.research_rating_summary` | `--next-key`、`--limit` |
| `moomoo shareholders <symbol>` | `--view institutional` | `quote.shareholders_institutional` | `--next-key`、`--limit` |
| `moomoo shareholders <symbol>` | `--view changes` | `quote.shareholders_holding_changes` | `--next-key`、`--limit` |
| `moomoo shareholders <symbol>` | `--view holder-detail` | `quote.shareholders_holder_detail` | `--next-key`、`--limit` |
| `moomoo shareholders <symbol>` | `--view insider-holders` | `quote.insider_holder_list` | `--next-key`、`--limit` |
| `moomoo shareholders <symbol>` | `--view insider-trades` | `quote.insider_trade_list` | `--next-key`、`--limit` |
| `moomoo stock-screen` | 独立命令 | `quote.stock_screen` | `--next-key`、`--limit` |
| `moomoo warrant-screen` | 独立命令 | `quote.warrant_screen` | `--next-key`、`--limit` |
| `moomoo option-screen` | 独立命令 | `quote.option_screen` | `--next-key`、`--limit` |
| `moomoo valuation [symbol]` | `--view plate-stocks` | `quote.valuation_plate_stock_list` | `--next-key`、`--limit` |
| `moomoo valuation [symbol]` | `--view index-stocks` | `quote.valuation_index_component_stock_list` | `--next-key`、`--limit` |

## 当前 CLI 中支持 `--next-time` 的行情命令

| 命令 | selector | 相关 BFF ID | 分页 flags |
| --- | --- | --- | --- |
| `moomoo history-kline <symbol>` | 无 | `quote.history_kline` | `--next-time`、`--num` |
| `moomoo capital <symbol>` | `--view history` | `quote.capital_flow_history` | `--next-time`、`--count` |

## 只有数量限制但无游标的命令

这些命令可以控制返回条数，但当前 CLI 没有暴露 `--next-key` / `--next-time`：

| 命令 | 参数 | 说明 |
| --- | --- | --- |
| `moomoo kline <symbol>` | `--num` | 获取最新 N 根 K 线，不做历史分页。 |
| `moomoo ticker <symbol>` | `--num` / `--count` | 获取最新逐笔成交。 |
| `moomoo rank [type]` | `--count` | 市场排行，底层固定取当前页结果。 |
| `moomoo option-data <symbol>` | `--view probability --limit` | 只限制返回条数。 |
| `moomoo financials <symbol>` | `--view earnings-move --count --overview-count` | 只限制返回条数。 |
| `moomoo short <symbol>` | `--count` | 查询最近 N 条卖空数据。 |

## Skill 编写建议

- 所有需要分页的行情命令都加 `--format json`。
- 优先设置合理 `--limit`，减少分页次数；不要超过接口文档或 CLI 约束的上限。
- 循环请求时保存每次的原始 JSON，便于排查游标异常。
- 聚合命令必须先确定 selector，再决定是否支持分页。例如 `plate --view list` 不需要 `--next-key`，`plate --view stocks` 才支持。
- 遇到 `has_more=true` 但 `next_key` 缺失、为空或重复时，应停止并提示接口分页状态异常，避免重复请求。
- `history-kline` 和 `capital --view history` 使用 `--next-time`，不要误用 `--next-key`。
