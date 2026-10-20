# Sim Trade 模拟交易接口指引

这份文档面向后续编写 skill：按当前源码整理 `Sim Trade Commands` 下所有模拟交易相关 CLI 命令、参数、默认值、BFF ID、底层 API 和返回示例。

## 来源与范围

- 命令实现来自 `cmd/sim.go`。
- 底层 API 信息来自 `.local_docs/moomoo-cli/docs/mcp-tools-list.md` 的 `sim_trade_*` 接口。
- 当前只暴露合并后的 `moomoo sim ...` 子命令，不注册 root 级 `sim-trade-*` 平铺动态命令。
- 所有命令都支持全局 `--format table|json`，默认 `table`；写 skill 时优先使用 `--format json`，输出结构更稳定。

## 全局约定

- 模拟交易接口仍需要 OAuth 登录态；skill 调用前优先检查 `moomoo auth status --format json` 或 `moomoo check --format json`。
- 账号 ID 使用模拟交易业务账号 `acc_id`，来源于 `sim_trade_account_list` 返回的 `accountId`。
- Symbol 统一使用 `MARKET.CODE`，例如 `HK.00700`、`US.AAPL`。如果用户传 `HK.700`，应规范化为 `HK.00700`；裸代码或 `700.HK` 不应直接传入。
- 所有命令支持全局 `--format table|json`，默认 `table`；skill 自动化解析时一律使用 `--format json`。
- 分页接口使用 `--next-key`；下一页取上一页响应里的 `pagination.next_key`。
- 时间参数 `--start` / `--end` 建议使用微秒级 Unix timestamp，与证券交易历史查询保持一致。
- 模拟交易不是实盘，但仍会改变模拟账户订单和持仓；下单、改单、撤单前应向用户确认账户、市场、symbol、方向、数量和价格。

## 命令总览

当前实现为一个顶层 `sim` 命令，避免把 `sim-trade-*` endpoint 直接注册成 root command。

| CLI 命令 | BFF ID | API | 用途 |
| --- | --- | --- | --- |
| `moomoo sim account list` | `sim_trade.account_list` | `GET /api/v1.0/sim-trade/accounts` | 获取当前用户可用的模拟交易账户列表。 |
| `moomoo sim account funds` | `sim_trade.cash_info` | `GET /api/v1.0/sim-trade/{acc_id}/cash-info` | 查询模拟账户资金、资产、购买力和盈亏。 |
| `moomoo sim position` | `sim_trade.position_list` | `GET /api/v1.0/sim-trade/{acc_id}/positions` | 查询模拟账户持仓。 |
| `moomoo sim order list` | `sim_trade.order_list` | `GET /api/v1.0/sim-trade/{acc_id}/orders` | 查询模拟账户当前订单。 |
| `moomoo sim order history` | `sim_trade.history_order_list` | `GET /api/v1.0/sim-trade/{acc_id}/history-orders` | 查询模拟账户历史订单，支持分页和时间范围。 |
| `moomoo sim order max-qty <symbol>` | `sim_trade.max_buy_sell` | `GET /api/v1.0/sim-trade/{acc_id}/max-buy-sell` | 查询指定 symbol 的模拟最大可买、可卖、可卖空等数量。 |
| `moomoo sim order buy <symbol> <qty>` | `sim_trade.input_order` | `POST /api/v1.0/sim-trade/{acc_id}/orders` | 买入模拟订单。 |
| `moomoo sim order sell <symbol> <qty>` | `sim_trade.input_order` | `POST /api/v1.0/sim-trade/{acc_id}/orders` | 卖出模拟订单。 |
| `moomoo sim order place <qty>` | `sim_trade.input_order` | `POST /api/v1.0/sim-trade/{acc_id}/orders` | 通用模拟下单，用 `--symbol` 和 `--side` 指定标的和方向。 |
| `moomoo sim order modify <order-id>` | `sim_trade.modify_order` | `POST /api/v1.0/sim-trade/{acc_id}/orders/{order_id}/modify` | 修改模拟订单数量和价格。 |
| `moomoo sim order cancel <order-id>` | `sim_trade.cancel_order` | `POST /api/v1.0/sim-trade/{acc_id}/orders/{order_id}/cancel` | 撤销模拟订单。 |

## 枚举和默认值

### 市场

CLI 暴露字符串市场，运行时映射到底层整数：

| CLI 值 | API `market` | 说明 |
| --- | --- | --- |
| `HK` 默认 | `1` | 港股 |
| `US` | `2` | 美股 |
| `US_OPTION` / `OPTION` | `3` | 美股期权 |
| `HKCC` / `CN` | `4` | 港股通 / 中国股票模拟市场 |

### 订单类型

| CLI 值 | API `order_type` | 说明 |
| --- | --- | --- |
| `market` 默认 | `3` | 市价单 |
| `limit` | `1` | 限价单，通常需要 `--price` |

### 方向

| CLI 值 | API `order_side` | 说明 |
| --- | --- | --- |
| `BUY` | `1` | 买入 |
| `SELL` | `2` | 卖出 |

### 交易时段

| CLI 值 | API `order_trade_time_type` | 说明 |
| --- | --- | --- |
| 空 | 不传 | 使用后端默认 |
| `RTH` | `1` | 常规交易时段 |
| `EXTENDED` | `2` | 包含盘前/盘后，主要用于美股模拟账户 |

## 命令参数

### `moomoo sim account list`

无命令专属参数。

```bash
moomoo sim account list --format json
```

### `moomoo sim account funds`

| 参数 | 默认 | 说明 |
| --- | --- | --- |
| `--account, -a` | 首个模拟账户 | 模拟交易 `acc_id` |

```bash
moomoo sim account funds --account <sim-account-id> --format json
```

### `moomoo sim position`

| 参数 | 默认 | 说明 |
| --- | --- | --- |
| `--account, -a` | 首个模拟账户 | 模拟交易 `acc_id` |
| `--market, -m` | `HK` | `HK / US / US_OPTION / HKCC` |

```bash
moomoo sim position --account <sim-account-id> --market US --format json
```

### `moomoo sim order list`

| 参数 | 默认 | 说明 |
| --- | --- | --- |
| `--account, -a` | 首个模拟账户 | 模拟交易 `acc_id` |
| `--market, -m` | `HK` | `HK / US / US_OPTION / HKCC` |

```bash
moomoo sim order list --account <sim-account-id> --market US --format json
```

### `moomoo sim order history`

| 参数 | 默认 | 说明 |
| --- | --- | --- |
| `--account, -a` | 首个模拟账户 | 模拟交易 `acc_id` |
| `--market, -m` | `HK` | `HK / US / US_OPTION / HKCC` |
| `--start` | 不传 | 开始时间，微秒级 timestamp |
| `--end` | 不传 | 结束时间，微秒级 timestamp |
| `--page-size` | `50` | 分页大小 |
| `--next-key` | 空 | 分页游标 |

```bash
moomoo sim order history --account <sim-account-id> --market US --page-size 50 --format json
moomoo sim order history --account <sim-account-id> --market US --next-key <next-key> --format json
```

### `moomoo sim order max-qty <symbol>`

| 参数 | 默认 | 说明 |
| --- | --- | --- |
| `<symbol>` | 必填 | `MARKET.CODE` 格式 |
| `--account, -a` | 首个模拟账户 | 模拟交易 `acc_id` |
| `--market, -m` | `HK` | `HK / US / US_OPTION / HKCC` |
| `--type, -t` | `market` | `market / limit` |
| `--price` | 空 | 限价场景传参考价格 |
| `--order-id` | 空 | 改单场景传原订单 ID |

```bash
moomoo sim order max-qty US.AAPL --account <sim-account-id> --market US --type market --format json
moomoo sim order max-qty HK.00700 --type limit --price 380 --format json
```

### `moomoo sim order buy <symbol> <qty>`

| 参数 | 默认 | 说明 |
| --- | --- | --- |
| `<symbol>` | 必填 | `MARKET.CODE` 格式 |
| `<qty>` | 必填 | 数量，必须大于 0 |
| `--account, -a` | 首个模拟账户 | 模拟交易 `acc_id` |
| `--market, -m` | `HK` | `HK / US / US_OPTION / HKCC` |
| `--type, -t` | `market` | `market / limit` |
| `--price` | 空 | 限价单价格 |
| `--text` | 空 | 订单备注 |
| `--session` | 空 | `RTH / EXTENDED` |

```bash
moomoo sim order buy US.AAPL 2 --account <sim-account-id> --market US --type limit --price 180.5 --format json
```

### `moomoo sim order sell <symbol> <qty>`

参数同 `sim order buy`，方向固定为 `SELL`。

```bash
moomoo sim order sell US.AAPL 2 --account <sim-account-id> --market US --type market --format json
```

### `moomoo sim order place <qty>`

| 参数 | 默认 | 说明 |
| --- | --- | --- |
| `<qty>` | 必填 | 数量，必须大于 0 |
| `--symbol` | 必填 | `MARKET.CODE` 格式 |
| `--side` | 必填 | `BUY / SELL` |
| `--account, -a` | 首个模拟账户 | 模拟交易 `acc_id` |
| `--market, -m` | `HK` | `HK / US / US_OPTION / HKCC` |
| `--type, -t` | `market` | `market / limit` |
| `--price` | 空 | 限价单价格 |
| `--text` | 空 | 订单备注 |
| `--session` | 空 | `RTH / EXTENDED` |

```bash
moomoo sim order place 2 --symbol US.AAPL --side BUY --market US --type limit --price 180.5 --format json
```

### `moomoo sim order modify <order-id>`

| 参数 | 默认 | 说明 |
| --- | --- | --- |
| `<order-id>` | 必填 | 原模拟订单 ID |
| `--account, -a` | 首个模拟账户 | 模拟交易 `acc_id` |
| `--market, -m` | `HK` | `HK / US / US_OPTION / HKCC` |
| `--qty` | 必填 | 新数量 |
| `--price` | 必填 | 新价格 |

`--qty` 和 `--price` 都必须传入。

```bash
moomoo sim order modify <order-id> --account <sim-account-id> --market US --qty 3 --price 181 --format json
```

### `moomoo sim order cancel <order-id>`

| 参数 | 默认 | 说明 |
| --- | --- | --- |
| `<order-id>` | 必填 | 原模拟订单 ID |
| `--account, -a` | 首个模拟账户 | 模拟交易 `acc_id` |
| `--market, -m` | `HK` | `HK / US / US_OPTION / HKCC` |

```bash
moomoo sim order cancel <order-id> --account <sim-account-id> --market US --format json
```

## 返回示例

### 账户列表

```json
{
  "accounts": [
    {
      "accountId": "1234567890123456789",
      "accountTitle": "模拟交易账户",
      "accountType": 1,
      "brokerId": 1,
      "intraAccountId": "88888888",
      "marketId": 2
    }
  ]
}
```

### 资金

```json
{
  "cash_info": {
    "balance": "1000000",
    "hold": "0",
    "maxPowerLong": "1000000",
    "totalAsset": "1000000",
    "mv": "0",
    "unrealizedProfit": "0",
    "realizedProfit": "0"
  }
}
```

### 订单

```json
{
  "orders": [
    {
      "orderId": "900000001",
      "symbol": "US.AAPL",
      "stockName": "Apple",
      "market": 2,
      "side": 1,
      "orderType": 1,
      "qty": "2",
      "price": "180.5",
      "cumQty": "0",
      "avgFillPrice": "0",
      "status": 1,
      "createTime": 1760227200000000,
      "updateTime": 1760227200000000,
      "text": "paper test"
    }
  ]
}
```

### 下单 / 改单 / 撤单

```json
{
  "orderId": "900000001"
}
```

### 最大可交易数量

```json
{
  "maxCashBuyQtyRoundLot": "500",
  "maxMarginBuyQtyRoundLot": "500",
  "maxSellQtyRoundLot": "100",
  "maxSellShortQty": "0",
  "maxBuyBackQty": "0",
  "requiredImLong": "0",
  "requiredImShort": "0"
}
```

### 持仓

```json
{
  "positions": [
    {
      "symbol": "US.AAPL",
      "stockName": "Apple",
      "market": 2,
      "qty": "2",
      "costPrice": "180.5",
      "marketVal": "365.0",
      "plVal": "4.0",
      "plRatio": "0.011"
    }
  ]
}
```

## Skill 编写建议

- 先调用账户列表，让用户确认模拟账户；不要默认把真实交易账户当作模拟账户。
- 用户只说“下单/改单/撤单”时，必须追问或确认是实盘还是模拟；如果选择模拟，再走本文的 `sim` 命令。
- 如果用户给出裸代码，先补齐或追问市场；不要把 `AAPL`、`700` 直接传入。
- 下单前确认账户、市场、symbol、方向、数量、订单类型和价格；市价单可省略价格，限价单应要求价格。
- 查询类命令优先加 `--format json`；下单、改单、撤单也建议加 `--format json` 以便读取 `orderId`。
- 历史订单分页时，把上一页响应的 `pagination.next_key` 传给 `--next-key`。
