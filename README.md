# Alpha Quant

股票量化分析工具，基于 Tushare 金融数据接口。

## 项目结构

```
etf_quat/
├── config.json              # 配置文件（Tushare token）
├── main.py                  # 主入口
├── data_fetcher/            # 数据获取模块
│   ├── fetcher.py          # Tushare API 初始化
│   ├── sources.py          # 数据源接口（带缓存）
│   ├── tushare_api.py      # Tushare API 封装（分页/重试）
│   └── utils.py            # Parquet 缓存工具
├── tasks/                   # 任务调度模块
│   ├── base.py             # Task 抽象基类
│   ├── scheduler.py        # 任务调度器
│   └── fetch_tasks.py      # 数据获取任务
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

## 数据缓存

数据按类型分层存储，以 Parquet 格式缓存在 `data/` 目录：

```
data/
├── stock_list/          # 股票列表
├── trade_cal/           # 交易日历
├── daily_basic/         # 日频指标
├── index_daily/         # 指数日线
└── fund/                # 基金数据
```
