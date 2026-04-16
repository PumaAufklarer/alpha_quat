# Alpha Quant

股票量化分析工具，基于 Tushare 金融数据接口。

## 项目结构

```
alpha_quat/
├── config.json              # 配置文件（Tushare token）
├── data_fetcher/            # 数据获取模块
│   ├── fetcher.py          # Tushare API 初始化
│   ├── sources.py          # 数据源接口（带缓存）
│   ├── tushare_api.py      # Tushare API 封装（分页/重试）
│   └── utils.py            # Parquet 缓存工具
├── tasks/                   # 任务调度模块
│   ├── base.py             # Task 抽象基类
│   ├── scheduler.py        # 任务调度器
│   └── fetch_tasks.py      # 数据获取任务
├── backtest/                # 回测框架模块
│   ├── engine.py           # 回测引擎
│   ├── data.py             # 数据馈送
│   ├── strategy.py         # 策略基类
│   ├── portfolio.py        # 投资组合管理
│   ├── order.py            # 订单/交易管理
│   └── metrics.py          # 绩效指标计算
├── features/                # 特征工程模块
│   ├── base.py             # Feature 抽象基类
│   ├── basic.py            # 基础特征（收益率、波动率等）
│   ├── technical.py        # 技术指标（SMA、EMA、RSI、MACD等）
│   └── pipeline.py         # 特征流水线
├── examples/                # 示例策略
│   ├── turtle_strategy.py  # 海龟策略实现
│   └── backtest_mainboard.py  # 主板股票回测脚本
└── scripts/
    └── daily_run.py        # 日常运行脚本
```

## 快速开始

### 配置

复制 `config.json.example` 为 `config.json` 并填入你的 Tushare token：

```json
{
    "tushare": {
        "token": "your_token_here"
    }
}
```

### 运行

```bash
# 日常运行（限制股票数量用于测试）
uv run -m scripts.daily_run --limit 10

# 完整参数
uv run -m scripts.daily_run \
    --start-date 20200101 \
    --end-date 20241231 \
    --exchange SSE \
    --list-status L \
    --force-refresh
```

### 回测

```bash
# 回测海龟策略（限制 10 只股票测试）
uv run -m examples.backtest_mainboard --limit 10

# 完整参数（包含 ATR 头寸管理）
uv run -m examples.backtest_mainboard \
    --limit 100 \
    --days 5000 \
    --entry-period 20 \
    --exit-period 10 \
    --include-st \
    --use-atr
```

## 数据缓存

数据按类型分层存储，以 Parquet 格式缓存在 `data/` 目录：

```
data/
├── stock_list/          # 股票列表
├── trade_cal/           # 交易日历
├── daily_basic/         # 日频指标
├── daily/               # 日线 OHLC 数据
├── index_daily/         # 指数日线
└── fund/                # 基金数据
```

## 特征工程

使用 features 模块计算技术指标和特征：

```python
import pandas as pd
from features import FeaturePipeline, Returns, SMA, RSI, MACD

# 创建特征流水线
pipeline = FeaturePipeline([
    Returns(periods=1),
    SMA(period=20),
    SMA(period=60),
    RSI(period=14),
    MACD(),
])

# 计算特征
df_with_features = pipeline.calculate(df)
```

### 可用特征

**基础特征**：
- `Returns` - 简单收益率
- `LogReturns` - 对数收益率
- `Volatility` - 滚动波动率

**技术指标**：
- `SMA` - 简单移动平均
- `EMA` - 指数移动平均
- `RSI` - 相对强弱指标
- `MACD` - 指数平滑异同移动平均线
- `BollingerBands` - 布林带
- `ATR` - 平均真实波幅
- `DonchianChannels` - 唐奇安通道（海龟策略核心）
