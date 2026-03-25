# 股票预测系统设计文档

**日期**: 2026-03-25
**项目**: 人机协同A股智能投资决策系统
**版本**: V1.0-MVP

---

## 目录

1. [项目概述](#1-项目概述)
2. [系统架构](#2-系统架构)
3. [核心功能设计](#3-核心功能设计)
4. [数据模型](#4-数据模型)
5. [技术选型](#5-技术选型)
6. [预测模型设计](#6-预测模型设计)
7. [非功能需求](#7-非功能需求)
8. [实现计划](#8-实现计划)
9. [接口设计](#9-接口设计)
10. [异常处理设计](#10-异常处理设计)
11. [缓存策略设计](#11-缓存策略设计)
12. [风险和应对](#12-风险和应对)
13. [附录](#13-附录)

---

## 1. 项目概述

### 1.1 目标
构建一个本地桌面应用，基于7年A股历史数据，通过AI模型对板块龙头股进行短中长期预测，为个人投资者提供买卖操作建议。

### 1.2 核心价值
- 数据驱动：基于历史数据和技术指标
- 人机协同：系统提供建议，用户自主决策
- 本地化：所有计算在本地完成，保护隐私
- 多周期：短中长期预测满足不同投资策略

---

## 2. 系统架构

### 2.1 分层架构

```
┌─────────────────────────────────────────────────────────┐
│                      前端层 (UI Layer)                   │
│                    Streamlit Application                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │ 板块总览    │  │ 股票详情    │  │ 历史回顾    │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
└────────────────────────┬────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────┐
│                    业务逻辑层 (Business Layer)            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │ 板块分析    │  │ 特征工程    │  │ 预测集成    │     │
│  │  sector     │  │  features   │  │  ensemble   │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
└────────────────────────┬────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────┐
│                   服务层 (Service Layer)                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │ 数据获取    │  │ 数据存储    │  │ 预测服务    │     │
│  │  fetcher    │  │  storage    │  │ prediction  │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
└────────────────────────┬────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────┐
│                   数据层 (Data Layer)                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │ akshare API │  │ SQLite DB   │  │ 模型文件    │     │
│  │             │  │             │  │  .pkl       │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
└─────────────────────────────────────────────────────────┘
```

### 2.2 模块职责

| 模块 | 职责 |
|------|------|
| data/ | 数据获取、存储、模型管理 |
| analysis/ | 技术指标计算、板块分析、特征工程 |
| prediction/ | 预测模型、模型训练、集成预测 |
| ui/ | 界面组件、页面布局、图表展示 |
| utils/ | 配置管理、日志、辅助函数 |

---

## 3. 核心功能设计

### 3.1 数据管理

#### 3.1.1 数据源
- **主要数据源**: akshare（免费开源）
- **数据类型**:
  - A股历史行情数据（7年）
  - 板块分类数据（行业板块、概念板块）
  - 股票基本信息
  - 财务数据
- **更新频率**: 每日收盘后更新（用户手动触发）

#### 3.1.2 板块龙头股识别

**筛选标准**:
- 市值: 板块内市值排名
- 成交量: 近期（20日）平均成交量
- 综合评分计算（所有指标先归一化到0-1）:

```python
# 1. 市值归一化（值越大越好）
market_cap_score = (market_cap - min_market_cap) / (max_market_cap - min_market_cap)

# 2. 成交量归一化（值越大越好）
volume_score = (avg_volume - min_volume) / (max_volume - min_volume)

# 3. 收益率归一化（近期收益率，绝对值越大越好）
return_score = abs(recent_return - min_return) / (max_return - min_return)

# 4. 稳定性（价格波动率，值越小越好，取反）
stability = 1 - (volatility - min_volatility) / (max_volatility - min_volatility)

# 5. 综合评分
final_score = market_cap_score * 0.4 + volume_score * 0.3 + return_score * 0.2 + stability * 0.1
```

**覆盖范围**: 先覆盖主要板块（科技、医药、消费、金融、制造等）

#### 3.1.3 技术指标

**基础指标**:
- MA5, MA10, MA20, MA60
- VOL

**趋势指标**:
- MACD (DIF, DEA, MACD柱)
- BOLL (上中下轨)

**震荡指标**:
- RSI (6日, 12日, 24日)
- KDJ (K, D, J值)

**动量指标**:
- OBV

### 3.2 预测功能

#### 3.2.1 三周期预测

| 周期 | 时间范围 | 特征侧重 | 输出 |
|------|----------|----------|------|
| 短期 | 1-5天 | 技术指标、量价关系 | 信号 + 置信度 + 依据 |
| 中期 | 1-3个月 | 趋势判断、基本面 | 信号 + 置信度 + 依据 |
| 长期 | 3个月以上 | 价值分析、行业周期 | 信号 + 置信度 + 依据 |

#### 3.2.2 预测信号
- **买入**: 看好上涨，建议考虑买入
- **卖出**: 看好下跌，建议考虑卖出
- **持有**: 趋势不明确，建议观望

#### 3.2.3 集成策略

综合建议计算公式：
```
综合得分 = 短期得分×30% + 中期得分×40% + 长期得分×30%
最终信号 = 得分最高的动作
```

**冲突处理**:
- 当三周期信号不一致时，采用加权得分最高的信号
- 当最高得分的两个信号得分接近（差距<10%），倾向于更保守的信号（持有优先于买入/卖出）
- 综合置信度 = max(短期置信度, 中期置信度, 长期置信度) × 0.9 + 加权置信度 × 0.1

### 3.3 界面设计

#### 3.3.1 首页（板块总览）

**布局**:
```
┌─────────────────────────────────────────────────────────┐
│                        板块总览                          │
├─────────────────────────────────────────────────────────┤
│  选择板块： [科技 ▼]                    [更新数据]     │
│                                                         │
│  板块龙头股列表                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │ 代码    │ 名称   │ 最新价  │ 涨跌 │ 综合 │ 操作 │ │
│  ├─────────┼────────┼─────────┼──────┼──────┼──────┤ │
│  │ 00001.SZ│ 平安银 │ 12.34   │ +1.2%│ 买   │[详情]│ │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
│  板块整体趋势K线图                                      │
│  ┌───────────────────────────────────────────────────┐ │
│  │  [K线图区域]                                       │ │
│  │  [1月] [3月] [6月] [1年] [全部]                  │ │
│  └───────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

#### 3.3.2 股票详情页

**布局**:
```
┌─────────────────────────────────────────────────────────┐
│  股票详情          ← 返回    平安银行 (000001.SZ)      │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────────┬─────────────────────────────────┐ │
│  │  图表区域 (60%)  │  预测建议区域 (40%)            │ │
│  │                  │                                 │ │
│  │  ┌────────────┐  │  ┌─────────────────────────┐  │ │
│  │  │  K线图     │  │  │ 股票信息                │  │ │
│  │  │  [600px]   │  │  ┌─────────────────────┐  │ │ │
│  │  └────────────┘  │  │ 000001.SZ 平安银行   │  │ │ │
│  │                  │  │ 12.34 ↗ +1.23%      │  │ │ │
│  │  ┌────────────┐  │  └─────────────────────┘  │ │ │
│  │  │  成交量图  │  │                         │  │ │
│  │  └────────────┘  │  ┌─────────────────────┐  │ │ │
│  │                  │  │ 📈 短期预测         │  │ │ │
│  │  ┌────────────┐  │  │       买入           │  │ │ │
│  │  │  技术指标  │  │  │    ████████░ 78%     │  │ │ │
│  │  └────────────┘  │  └─────────────────────┘  │ │ │
│  │                  │  [中期预测] [长期预测]    │  │ │
│  │                  │  ┌─────────────────────┐  │ │ │
│  │                  │  │ 🎯 综合建议         │  │ │ │
│  │                  │  │      买入            │  │ │ │
│  │                  │  │   ████████░░ 82%     │  │ │ │
│  │                  │  └─────────────────────┘  │ │ │
│  └──────────────────┴─────────────────────────────────┘ │
│                                                         │
│  [1月] [3月] [6月] [1年] [全部]                         │
│  [MACD] [KDJ] [RSI] [BOLL]                              │
└─────────────────────────────────────────────────────────┘
```

---

## 4. 数据模型

### 4.1 数据库表结构

#### sectors 表（板块信息）

```sql
CREATE TABLE sectors (
    sector_id TEXT PRIMARY KEY,
    sector_name TEXT NOT NULL,
    sector_type TEXT NOT NULL,  -- 'industry' 或 'concept'
    leader_count INTEGER DEFAULT 0,
    updated_at TEXT
);

CREATE INDEX idx_sectors_type ON sectors(sector_type);
```

#### stocks 表（股票基本信息）

```sql
CREATE TABLE stocks (
    symbol TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    industry TEXT,
    sector TEXT,
    market_cap REAL,
    pe_ratio REAL,
    pb_ratio REAL,
    list_date TEXT,
    updated_at TEXT
);

CREATE INDEX idx_stocks_industry ON stocks(industry);
CREATE INDEX idx_stocks_sector ON stocks(sector);
```

#### stock_data 表（历史数据）

```sql
CREATE TABLE stock_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    symbol TEXT NOT NULL,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    volume REAL,
    amount REAL,
    ma5 REAL, ma10 REAL, ma20 REAL, ma60 REAL,
    macd REAL, macd_signal REAL, macd_hist REAL,
    kdj_k REAL, kdj_d REAL, kdj_j REAL,
    rsi6 REAL, rsi12 REAL, rsi24 REAL,
    boll_upper REAL, boll_middle REAL, boll_lower REAL,
    obv REAL,
    FOREIGN KEY (symbol) REFERENCES stocks(symbol)
);

CREATE INDEX idx_stock_data_date ON stock_data(date);
CREATE INDEX idx_stock_data_symbol ON stock_data(symbol);
CREATE INDEX idx_stock_data_date_symbol ON stock_data(date, symbol);
```

#### predictions 表（预测结果）

```sql
CREATE TABLE predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    symbol TEXT NOT NULL,
    horizon TEXT NOT NULL,  -- 'short', 'medium', 'long'
    action TEXT NOT NULL,   -- 'buy', 'sell', 'hold'
    confidence REAL,        -- 0-1
    reasoning TEXT,         -- JSON格式
    model_version TEXT,
    created_at TEXT,
    FOREIGN KEY (symbol) REFERENCES stocks(symbol)
);

CREATE INDEX idx_predictions_date ON predictions(date);
CREATE INDEX idx_predictions_symbol ON predictions(symbol);
CREATE INDEX idx_predictions_date_symbol_horizon ON predictions(date, symbol, horizon);
```

#### sector_leaders 表（板块龙头股）

```sql
CREATE TABLE sector_leaders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sector_id TEXT NOT NULL,
    sector_name TEXT NOT NULL,
    symbol TEXT NOT NULL,
    score REAL,
    rank INTEGER,
    market_cap_rank INTEGER,
    volume_rank INTEGER,
    updated_at TEXT,
    FOREIGN KEY (symbol) REFERENCES stocks(symbol)
);

CREATE INDEX idx_sector_leaders_sector ON sector_leaders(sector_id);
```

#### model_params 表（模型参数）

```sql
CREATE TABLE model_params (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_name TEXT NOT NULL,     -- 'short_term', 'medium_term', 'long_term'
    model_version TEXT NOT NULL,
    params TEXT,                  -- JSON格式，存储模型参数
    accuracy REAL,
    trained_at TEXT,
    is_active INTEGER DEFAULT 1
);

CREATE INDEX idx_model_params_name ON model_params(model_name);
```

### 4.2 首次模型初始化方案

**初始化流程**:

1. **首次启动检测**:
   - 检查 `models/` 目录是否存在模型文件
   - 检查数据库中是否有 `model_params` 记录

2. **数据准备**:
   - 如果数据库为空，执行完整数据更新
   - 获取至少6个月的历史数据作为训练基础

3. **模型训练**:
   - 使用已获取的历史数据训练三个模型
   - 训练参数使用默认值：
     - Random Forest: n_estimators=100, max_depth=10
     - 验证集比例: 20%

4. **模型保存**:
   - 保存模型文件到 `models/` 目录
   - 记录模型参数到 `model_params` 表

5. **初始预测**:
   - 使用训练好的模型对所有板块龙头股进行预测
   - 结果保存到 `predictions` 表

**首次启动提示**:
```
首次使用，需要进行以下操作：
1. 获取历史数据（约需5-10分钟）
2. 训练预测模型（约需3-5分钟）
3. 生成初始预测（约需1-2分钟）

总计约需10-20分钟，是否继续？
```

---

## 5. 技术选型

| 组件 | 技术选择 | 理由 |
|------|---------|------|
| 后端语言 | Python 3.10+ | 生态丰富，金融库成熟 |
| 界面框架 | Streamlit | 开发快速，可本地运行 |
| 数据获取 | akshare | 免费，数据全面 |
| 数据存储 | SQLite | 轻量级，无需额外安装 |
| 数据处理 | pandas, numpy | 成熟稳定 |
| 技术指标 | pandas-ta | 支持130+指标 |
| 机器学习 | scikit-learn | 成熟稳定，易用 |
| 图表库 | plotly | 交互式图表 |

---

## 6. 预测模型设计

### 6.1 模型选择
- **基础模型**: Random Forest Classifier
- **原因**: 可解释性强，适合快速实现，对特征不敏感

### 6.2 特征工程

**短期特征 (20日，共30个特征)**:

| 类别 | 特征 | 计算 |
|------|------|------|
| 价格 | 最近1/3/5/10日收益率 | (close_t - close_t-n) / close_t-n |
| 价格 | 收益率标准差 | std(returns_n) |
| 价格 | 价格相对位置 | (close_t - min_n) / (max_n - min_n) |
| 均线 | MA5/MA10/MA20状态 | close - MA_n |
| 均线 | 均线多头排列 | MA5 > MA10 > MA20 |
| 量价 | 量价比 | volume / price |
| 量价 | 量价背离 | 价格涨成交量跌 |
| MACD | DIF值、DEA值、金叉死叉 | |
| RSI | RSI6/12/24值 | |
| KDJ | K值、D值、J值、超买超卖 | |

**中期特征 (120日，共25个特征)**:

| 类别 | 特征 | 计算 |
|------|------|------|
| 趋势 | 20/60/120日趋势方向 | 回归斜率 |
| 趋势 | 均线多头/空头排列 | MA5 > MA10 > MA20 > MA60 |
| 趋势 | 价格在均线上的比例 | days_above_MA / total_days |
| 成交量 | 成交量趋势 | 回归斜率 |
| 成交量 | 量能放大 | avg_volume_n / avg_volume_m |
| 波动率 | 20/60日波动率 | std(returns) |
| 波动率 | ATR | |
| MACD | MACD长期状态 | |
| RSI | RSI长期超买超卖 | |
| 相对表现 | 相对沪深300 | (stock_return - index_return) |

**长期特征 (全部历史，共20个特征)**:

| 类别 | 特征 | 计算 |
|------|------|------|
| 长期趋势 | 长期回归斜率 | |
| 极值 | 距离历史高点/低点 | (close - all_time_high) / all_time_high |
| 周期 | 涨跌周期特征 | FFT分析 |
| 周期 | 季节性特征 | 月度/季度效应 |
| 价值 | 市盈率相对位置 | (pe - min_pe) / (max_pe - min_pe) |
| 价值 | 市净率相对位置 | (pb - min_pb) / (max_pb - min_pb) |
| 行业 | 行业相对表现 | (sector_return - market_return) |
| 稳定性 | 长期波动率 | std(returns_all) |

**特征标准化**:
- 使用 StandardScaler 进行标准化
- 训练集拟合，测试集转换
- 保存scaler参数用于后续预测

### 6.3 标签生成
- 根据未来N日的涨跌确定标签
- **短期**: 未来5日最高涨幅 > 3% → 买入，最大跌幅 < -3% → 卖出，其他 → 持有
- **中期**: 未来60日最高涨幅 > 10% → 买入，最大跌幅 < -10% → 卖出，其他 → 持有
- **长期**: 未来120日最高涨幅 > 20% → 买入，最大跌幅 < -15% → 卖出，其他 → 持有

---

## 7. 非功能需求

### 7.1 性能目标
- 数据更新: < 5分钟
- 单股预测: < 3秒
- 页面加载: < 5秒
- 界面响应: < 2秒

### 7.2 准确率目标
- 短期预测: > 52%（调整）
- 中期预测: > 50%（调整）
- 长期预测: > 48%（调整）

### 7.3 安全性
- 数据本地存储
- 不上传用户数据
- 不收集用户行为

---

## 8. 实现计划

### 8.1 实现阶段

| 阶段 | 内容 | 预计时间 |
|------|------|----------|
| 阶段1 | 项目初始化、数据层基础 | 2天 |
| 阶段2 | 数据获取和存储、指标计算 | 3天 |
| 阶段3 | 预测模型基础、特征工程 | 3天 |
| 阶段4 | 基础UI界面（首页） | 2天 |
| 阶段5 | 股票详情页、预测展示 | 2天 |
| 阶段6 | 集成测试、优化、文档完善 | 2天 |

### 8.2 里程碑
- V0.1: 项目初始化完成
- V0.2: 数据层完成
- V0.3: 预测层完成
- V0.4: 基础UI完成
- V0.5: 详情页完成
- V1.0: MVP版本发布

---

## 9. 接口设计

### 9.1 数据获取接口

```python
class DataFetcher:
    """数据获取器接口"""

    def get_industry_sectors(self) -> pd.DataFrame:
        """获取行业板块列表"""
        pass

    def get_concept_sectors(self) -> pd.DataFrame:
        """获取概念板块列表"""
        pass

    def get_sector_stocks(self, sector_name: str, sector_type: str) -> pd.DataFrame:
        """获取板块成分股

        Args:
            sector_name: 板块名称
            sector_type: 板块类型 ('industry' 或 'concept')

        Returns:
            DataFrame 包含 symbol, name 列
        """
        pass

    def get_stock_info(self, symbol: str) -> dict:
        """获取股票基本信息

        Args:
            symbol: 股票代码

        Returns:
            dict 包含 symbol, name, industry, sector, market_cap, pe_ratio 等
        """
        pass

    def get_stock_history(self, symbol: str, start_date: str = None) -> pd.DataFrame:
        """获取股票历史数据

        Args:
            symbol: 股票代码
            start_date: 起始日期，格式 YYYY-MM-DD

        Returns:
            DataFrame 包含 date, open, high, low, close, volume, amount 列
        """
        pass

    def get_stock_latest(self, symbol: str) -> dict:
        """获取股票最新数据

        Args:
            symbol: 股票代码

        Returns:
            dict 包含最新交易日数据
        """
        pass
```

### 9.2 数据存储接口

```python
class StockStorage:
    """数据存储器接口"""

    def save_sector(self, sector_data: dict) -> bool:
        """保存板块信息"""
        pass

    def save_stock(self, stock_data: dict) -> bool:
        """保存股票基本信息"""
        pass

    def save_stock_data(self, df: pd.DataFrame) -> bool:
        """保存股票历史数据（批量）"""
        pass

    def get_stock(self, symbol: str) -> dict:
        """获取股票信息"""
        pass

    def get_stock_data(self, symbol: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """获取股票历史数据"""
        pass

    def save_prediction(self, prediction_data: dict) -> bool:
        """保存预测结果

        Args:
            prediction_data: {
                'date': str,
                'symbol': str,
                'horizon': str,
                'action': str,
                'confidence': float,
                'reasoning': list[str],
                'model_version': str
            }
        """
        pass

    def get_prediction(self, symbol: str, horizon: str, date: str = None) -> dict:
        """获取预测结果"""
        pass

    def save_sector_leaders(self, sector_id: str, leaders: List[dict]) -> bool:
        """保存板块龙头股"""
        pass

    def get_sector_leaders(self, sector_id: str) -> List[dict]:
        """获取板块龙头股"""
        pass
```

### 9.3 预测服务接口

```python
class EnsemblePredictor:
    """集成预测器接口"""

    def predict(self, symbol: str) -> dict:
        """预测单只股票

        Args:
            symbol: 股票代码

        Returns:
            {
                'short': {
                    'action': str,  # 'buy', 'sell', 'hold'
                    'confidence': float,  # 0-1
                    'reasoning': list[str]
                },
                'medium': { ... },
                'long': { ... },
                'ensemble': {
                    'action': str,
                    'confidence': float,
                    'breakdown': dict
                }
            }
        """
        pass

    def batch_predict(self, symbols: List[str]) -> dict:
        """批量预测"""
        pass
```

### 9.4 API请求/响应格式

**推理依据格式（JSON）**:
```json
{
  "reasoning": [
    "MACD金叉形成，短期看涨",
    "量价配合良好，资金流入",
    "突破20日均线，趋势向上"
  ]
}
```

---

## 10. 异常处理设计

### 10.1 异常类型定义

```python
class WealthException(Exception):
    """基础异常"""
    pass

class DataFetchException(WealthException):
    """数据获取异常"""
    pass

class StorageException(WealthException):
    """存储异常"""
    pass

class PredictionException(WealthException):
    """预测异常"""
    pass

class ModelException(WealthException):
    """模型异常"""
    pass
```

### 10.2 错误码定义

| 错误码 | 错误类型 | 说明 |
|--------|----------|------|
| E0001 | DATA_FETCH_ERROR | 数据获取失败 |
| E0002 | DATA_PARSE_ERROR | 数据解析失败 |
| E0003 | STORAGE_ERROR | 数据存储失败 |
| E0004 | MODEL_NOT_FOUND | 模型未找到 |
| E0005 | MODEL_LOAD_ERROR | 模型加载失败 |
| E0006 | PREDICTION_ERROR | 预测失败 |
| E0007 | NETWORK_ERROR | 网络连接错误 |
| E0008 | DATABASE_ERROR | 数据库错误 |

### 10.3 异常处理策略

**数据获取失败**:
- 记录错误日志
- 返回空数据
- 用户可重试
- 显示友好错误提示

**存储失败**:
- 事务回滚
- 记录错误日志
- 提示用户重试

**预测失败**:
- 记录错误日志
- 返回默认预测（持有，置信度0.5）
- 继续处理其他股票

**模型加载失败**:
- 记录错误日志
- 使用备份模型或默认模型
- 提示用户重新训练

---

## 11. 缓存策略设计

### 11.1 数据缓存

**数据库查询缓存**:
- 缓存热点数据（板块龙头股、股票列表）
- 缓存时间: 1小时
- 使用LRU淘汰策略

**API请求缓存**:
- 缓存akshare API响应
- 缓存时间: 24小时
- 数据更新后清除缓存

### 11.2 模型缓存

**模型加载缓存**:
- 模型文件加载后缓存在内存
- 使用单例模式管理模型实例
- 避免重复加载

**预测结果缓存**:
- 缓存已计算的预测结果
- 缓存时间: 直到下次数据更新
- 使用 (symbol, horizon, date) 作为缓存key

### 11.3 缓存实现

```python
from functools import lru_cache
import hashlib
import pickle
import os
import time

class CacheManager:
    """缓存管理器"""

    def __init__(self, cache_dir: str = 'data/cache'):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

    def get(self, key: str, expire: int = 3600) -> any:
        """获取缓存"""
        cache_file = os.path.join(self.cache_dir, f"{key}.cache")
        if not os.path.exists(cache_file):
            return None

        with open(cache_file, 'rb') as f:
            data = pickle.load(f)

        if time.time() - data['timestamp'] > expire:
            os.remove(cache_file)
            return None

        return data['value']

    def set(self, key: str, value: any) -> None:
        """设置缓存"""
        cache_file = os.path.join(self.cache_dir, f"{key}.cache")
        with open(cache_file, 'wb') as f:
            pickle.dump({
                'value': value,
                'timestamp': time.time()
            }, f)

    def clear(self, key: str = None) -> None:
        """清除缓存"""
        if key:
            cache_file = os.path.join(self.cache_dir, f"{key}.cache")
            if os.path.exists(cache_file):
                os.remove(cache_file)
        else:
            for file in os.listdir(self.cache_dir):
                os.remove(os.path.join(self.cache_dir, file))
```

---

## 12. 风险和应对

| 风险 | 应对措施 |
|------|----------|
| akshare API变化 | 使用稳定版本，添加版本检查，兼容处理 |
| 数据获取速度慢 | 批量请求，添加缓存，并行处理 |
| 模型准确率不达标 | 后续优化模型，尝试其他算法 |
| Streamlit性能问题 | 优化数据加载，使用缓存，懒加载 |
| 数据库容量过大 | 定期清理旧数据，数据压缩 |
| 模型训练耗时 | 使用增量训练，参数调优 |

---

## 13. 附录

### 13.1 参考资料
- akshare: https://akshare.akfamily.xyz/
- Streamlit: https://docs.streamlit.io/
- pandas-ta: https://github.com/twopirllc/pandas-ta
- scikit-learn: https://scikit-learn.org/

### 13.2 相关文档
- PRD.md - 产品需求文档
- APP_FLOW.md - 应用流程文档
- TECH_STACK.md - 技术栈文档
- FRONTEND_GUIDELINES.md - 前端设计指南
- BACKEND_STRUCTURE.md - 后端结构文档
- IMPLEMENTATION_PLAN.md - 实现计划

### 13.3 版本历史

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| V1.0 | 2026-03-25 | 初始版本，基于审查报告修复 |