# TECH_STACK - 技术栈文档

## 1. 技术选型概览

### 1.1 整体技术栈
| 层级 | 技术选型 | 用途 |
|------|---------|------|
| 数据层 | SQLite | 本地数据存储 |
| 数据获取 | akshare | A股数据API（主数据源） |
| 数据获取 | baostock | A股数据API（备用数据源） |
| 后端逻辑 | Python 3.10+ | 核心业务逻辑 |
| 数据处理 | pandas, numpy | 数据分析处理 |
| 技术指标 | pandas-ta | 技术指标计算 |
| 机器学习 | scikit-learn | 预测模型 |
| 可视化 | plotly | 交互式图表 |
| 前端界面 | Streamlit | Web GUI框架 |
| 图表库 | plotly-graph-objects | K线图等技术图表 |

### 1.2 技术选型理由
- **Python**：生态丰富，有成熟的金融库和机器学习库
- **Streamlit**：开发快速，适合数据应用，可本地运行
- **akshare**：免费开源的A股数据源，数据全面（主数据源）
- **baostock**：免费开源的A股数据源，作为 akshare 备用（备用数据源）
- **SQLite**：无需额外安装，满足本地存储需求
- **scikit-learn**：成熟稳定的机器学习库，适合快速实现

---

## 2. 核心依赖详细说明

### 2.1 akshare（数据获取）

**版本要求**：>= 1.12.0

**主要功能**：
- 获取A股历史行情数据
- 获取板块分类数据
- 获取股票基本信息
- 获取财务数据

**常用API**：
```python
import akshare as ak

# 获取行业板块列表
ak.stock_board_industry_name_em()

# 获取概念板块列表
ak.stock_board_concept_name_em()

# 获取板块成分股
ak.stock_board_industry_cons_em(symbol="板块名称")

# 获取股票历史K线数据
ak.stock_zh_a_hist(symbol="股票代码", period="daily", start_date="2018-01-01")

# 获取股票基本信息
ak.stock_individual_info_em(symbol="股票代码")
```

**注意事项**：
- akshare依赖网络请求，需要稳定网络环境
- 部分API可能有频率限制，建议串行处理并添加延迟
- 数据格式可能随时间变化，需要版本兼容
- 作为主数据源，当失败时自动切换到 baostock

---

### 2.1.2 baostock（备用数据获取）

**版本要求**：>= 0.8.8

**主要功能**：
- 获取A股历史行情数据
- 作为 akshare 的备用数据源
- 支持 k 线数据查询
- 数据前复权处理

**常用API**：
```python
import baostock as bs

# 登录系统
bs.login()

# 获取股票历史K线数据
rs = bs.query_history_k_data_plus(
    "sh.600000",  # 股票代码
    "date,code,open,high,low,close,volume,amount",
    start_date="2018-01-01",
    end_date="2023-12-31",
    frequency="d",  # 日线
    adjustflag="1"  # 前复权
)

# 登出系统
bs.logout()
```

**注意事项**：
- baostock 数据可能有延迟
- 需要先登录后查询
- 股票代码格式：sh.600000 或 sz.000001
- 作为备用数据源，只在 akshare 失败时使用

**数据切换逻辑**：
```python
try:
    # 优先使用 akshare
    df = ak.stock_zh_a_hist(symbol, start_date, end_date)
except Exception:
    # 失败时切换到 baostock
    df = baostock_query_history(symbol, start_date, end_date)
```

---

### 2.2 Streamlit（前端界面）

**版本要求**：>= 1.28.0

**主要功能**：
- 快速构建Web界面
- 自动处理用户输入和状态管理
- 内置图表组件
- 本地运行，支持离线查看

**常用功能**：
```python
import streamlit as st

# 页面标题
st.title("板块总览")

# 下拉选择框
selected_sector = st.selectbox("选择板块", sectors)

# 按钮触发
if st.button("更新数据"):
    # 执行更新操作
    pass

# 进度条
progress_bar = st.progress(0)
for i in range(100):
    progress_bar.progress(i + 1)

# 表格展示
st.dataframe(df)

# 列布局
col1, col2 = st.columns([3, 2])
with col1:
    st.plotly_chart(fig)
with col2:
    st.info("预测建议")

# 状态提示
st.success("更新成功")
st.error("更新失败")
st.warning("警告信息")

# 侧边栏
with st.sidebar:
    st.header("功能菜单")
    if st.button("更新数据"):
        pass
```

**注意事项**：
- Streamlit是声明式编程，脚本从头到尾执行
- 用户交互会触发脚本重新运行
- 使用`st.session_state`保持状态

---

### 2.3 pandas（数据处理）

**版本要求**：>= 2.0.0

**主要功能**：
- 数据清洗和转换
- 时间序列处理
- 数据聚合和分组
- 数据合并和连接

**常用操作**：
```python
import pandas as pd

# 读取数据
df = pd.read_sql(query, conn)

# 时间处理
df['date'] = pd.to_datetime(df['date'])
df = df.set_index('date')

# 数据筛选
df_filtered = df[df['symbol'] == '000001.SZ']

# 数据排序
df_sorted = df.sort_values('date')

# 数据聚合
df_grouped = df.groupby('symbol').agg({
    'close': 'last',
    'volume': 'sum'
})

# 数据计算
df['ma5'] = df['close'].rolling(5).mean()
df['pct_change'] = df['close'].pct_change()

# 数据合并
df_merged = pd.merge(df1, df2, on=['date', 'symbol'])
```

---

### 2.4 numpy（数值计算）

**版本要求**：>= 1.24.0

**主要功能**：
- 高性能数值计算
- 数组操作
- 数学运算

---

### 2.5 pandas-ta（技术指标）

**版本要求**：>= 0.3.14b

**主要功能**：
- 计算各类技术指标
- 支持130+技术指标
- 与pandas DataFrame无缝集成

**常用指标**：
```python
import pandas_ta as ta

# 移动平均线
df['ma5'] = ta.sma(df['close'], length=5)
df['ma10'] = ta.sma(df['close'], length=10)
df['ema12'] = ta.ema(df['close'], length=12)

# MACD
macd = ta.macd(df['close'], fast=12, slow=26, signal=9)
df['macd'] = macd['MACD_12_26_9']
df['macd_signal'] = macd['MACDs_12_26_9']
df['macd_hist'] = macd['MACDh_12_26_9']

# KDJ
kdj = ta.stoch(df['high'], df['low'], df['close'], k=9, d=3, j=3)
df['kdj_k'] = kdj['STOCHk_9_3_3']
df['kdj_d'] = kdj['STOCHd_9_3_3']
df['kdj_j'] = 3 * df['kdj_k'] - 2 * df['kdj_d']

# RSI
df['rsi6'] = ta.rsi(df['close'], length=6)
df['rsi12'] = ta.rsi(df['close'], length=12)
df['rsi24'] = ta.rsi(df['close'], length=24)

# BOLL
boll = ta.bbands(df['close'], length=20, std=2)
df['boll_upper'] = boll['BBU_20_2.0']
df['boll_middle'] = boll['BBM_20_2.0']
df['boll_lower'] = boll['BBL_20_2.0']

# OBV
df['obv'] = ta.obv(df['close'], df['volume'])
```

**备选方案**：
如果pandas-ta不可用，可以使用TA-Lib或手动计算部分指标

---

### 2.6 scikit-learn（机器学习）

**版本要求**：>= 1.3.0

**主要功能**：
- 预测模型
- 特征工程
- 模型评估
- 数据预处理

**常用模型和工具**：
```python
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report

# 数据分割
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 特征标准化
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 随机森林模型
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

# 预测
y_pred = rf_model.predict(X_test)

# 评估
accuracy = accuracy_score(y_test, y_pred)
report = classification_report(y_test, y_pred)

# 交叉验证
cv_scores = cross_val_score(rf_model, X_train, y_train, cv=5)

# 特征重要性
feature_importance = rf_model.feature_importances_
```

---

### 2.7 plotly（数据可视化）

**版本要求**：>= 5.18.0

**主要功能**：
- 交互式图表
- K线图绘制
- 技术指标图表

**K线图示例**：
```python
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 创建子图
fig = make_subplots(
    rows=3, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.02,
    row_heights=[0.6, 0.2, 0.2]
)

# K线图
fig.add_trace(
    go.Candlestick(
        x=df.index,
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name='K线'
    ),
    row=1, col=1
)

# 移动平均线
fig.add_trace(
    go.Scatter(
        x=df.index,
        y=df['ma5'],
        name='MA5',
        line=dict(color='orange', width=1)
    ),
    row=1, col=1
)

# 成交量
fig.add_trace(
    go.Bar(
        x=df.index,
        y=df['volume'],
        name='成交量',
        marker_color='gray'
    ),
    row=2, col=1
)

# MACD
fig.add_trace(
    go.Scatter(
        x=df.index,
        y=df['macd'],
        name='MACD',
        line=dict(color='blue')
    ),
    row=3, col=1
)

# 更新布局
fig.update_layout(
    title='股票K线图',
    xaxis_rangeslider_visible=False,
    height=800
)
```

---

## 3. 数据库设计

### 3.1 SQLite

**版本要求**：Python内置（>= 3.0）

**特点**：
- 无需额外安装
- 轻量级，单文件存储
- 支持事务
- 适合中小规模数据

**连接方式**：
```python
import sqlite3

# 连接数据库
conn = sqlite3.connect('data/stock_data.db')

# 创建游标
cursor = conn.cursor()

# 执行SQL
cursor.execute("SELECT * FROM stocks")

# 使用pandas
import pandas as pd
df = pd.read_sql(query, conn)
df.to_sql('table_name', conn, if_exists='append', index=False)

# 提交和关闭
conn.commit()
conn.close()
```

---

### 3.2 数据表结构

#### stocks 表（股票基本信息）
```sql
CREATE TABLE stocks (
    symbol TEXT PRIMARY KEY,      -- 股票代码
    name TEXT NOT NULL,           -- 股票名称
    industry TEXT,                -- 所属行业
    sector TEXT,                  -- 所属板块
    market_cap REAL,              -- 市值（亿元）
    pe_ratio REAL,                -- 市盈率
    pb_ratio REAL,                -- 市净率
    list_date TEXT,               -- 上市日期
    updated_at TEXT               -- 更新时间
);

CREATE INDEX idx_stocks_industry ON stocks(industry);
CREATE INDEX idx_stocks_sector ON stocks(sector);
```

#### sectors 表（板块信息）
```sql
CREATE TABLE sectors (
    sector_id TEXT PRIMARY KEY,   -- 板块ID
    sector_name TEXT NOT NULL,    -- 板块名称
    sector_type TEXT,             -- 板块类型（行业/概念）
    leader_count INTEGER,         -- 龙头股数量
    updated_at TEXT               -- 更新时间
);
```

#### stock_data 表（历史数据）
```sql
CREATE TABLE stock_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,           -- 日期
    symbol TEXT NOT NULL,         -- 股票代码
    open REAL,                    -- 开盘价
    high REAL,                    -- 最高价
    low REAL,                     -- 最低价
    close REAL,                   -- 收盘价
    volume REAL,                  -- 成交量
    amount REAL,                  -- 成交额
    ma5 REAL,                     -- 5日均线
    ma10 REAL,                    -- 10日均线
    ma20 REAL,                    -- 20日均线
    ma60 REAL,                    -- 60日均线
    macd REAL,                    -- MACD
    macd_signal REAL,             -- MACD信号线
    macd_hist REAL,               -- MACD柱
    kdj_k REAL,                   -- KDJ-K值
    kdj_d REAL,                   -- KDJ-D值
    kdj_j REAL,                   -- KDJ-J值
    rsi6 REAL,                    -- RSI-6日
    rsi12 REAL,                   -- RSI-12日
    rsi24 REAL,                   -- RSI-24日
    boll_upper REAL,              -- 布林线上轨
    boll_middle REAL,             -- 布林线中轨
    boll_lower REAL,              -- 布林线下轨
    obv REAL,                     -- OBV能量潮
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
    date TEXT NOT NULL,           -- 预测日期
    symbol TEXT NOT NULL,         -- 股票代码
    horizon TEXT NOT NULL,        -- 预测周期（short/medium/long）
    action TEXT NOT NULL,         -- 信号（买入/卖出/持有）
    confidence REAL,              -- 置信度（0-1）
    reasoning TEXT,               -- 推理依据（JSON格式）
    model_version TEXT,           -- 模型版本
    created_at TEXT,              -- 创建时间
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
    sector_id TEXT NOT NULL,      -- 板块ID
    sector_name TEXT NOT NULL,    -- 板块名称
    symbol TEXT NOT NULL,         -- 股票代码
    score REAL,                   -- 综合得分
    rank INTEGER,                 -- 排名
    market_cap_rank INTEGER,      -- 市值排名
    volume_rank INTEGER,          -- 成交量排名
    updated_at TEXT,              -- 更新时间
    FOREIGN KEY (symbol) REFERENCES stocks(symbol)
);

CREATE INDEX idx_sector_leaders_sector ON sector_leaders(sector_id);
```

#### model_params 表（模型参数）
```sql
CREATE TABLE model_params (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_name TEXT NOT NULL,     -- 模型名称
    model_version TEXT NOT NULL,  -- 模型版本
    params TEXT,                  -- 模型参数（JSON格式）
    accuracy REAL,                -- 准确率
    trained_at TEXT,              -- 训练时间
    is_active INTEGER DEFAULT 1   -- 是否启用
);
```

---

## 4. 项目目录结构

```
wealth/
├── app.py                       # Streamlit主应用入口
├── requirements.txt             # Python依赖列表
├── README.md                    # 项目说明
├── CLAUDE.md                    # Claude Code指导文档
│
├── docs/                        # 文档目录
│   ├── PRD.md                   # 产品需求文档
│   ├── APP_FLOW.md              # 应用流程文档
│   ├── TECH_STACK.md            # 技术栈文档
│   ├── FRONTEND_GUIDELINES.md   # 前端设计指南
│   ├── BACKEND_STRUCTURE.md     # 后端结构文档
│   ├── IMPLEMENTATION_PLAN.md   # 实现计划
│   └── specs/                   # 详细设计文档
│
├── data/                        # 数据层模块
│   ├── __init__.py
│   ├── fetcher.py               # akshare数据获取
│   ├── storage.py               # SQLite存储操作
│   ├── database.py              # 数据库初始化和连接管理
│   └── models.py                # 数据模型定义
│
├── analysis/                    # 分析层模块
│   ├── __init__.py
│   ├── indicators.py            # 技术指标计算
│   ├── sector.py                # 板块识别和龙头筛选
│   └── features.py              # 特征工程
│
├── prediction/                  # 预测层模块
│   ├── __init__.py
│   ├── base.py                  # 预测模型基类
│   ├── short_term.py            # 短期预测模型
│   ├── medium_term.py           # 中期预测模型
│   ├── long_term.py             # 长期预测模型
│   ├── ensemble.py              # 集成预测
│   └── trainer.py               # 模型训练
│
├── ui/                          # 界面层模块
│   ├── __init__.py
│   ├── pages.py                 # 各页面组件
│   ├── components.py            # 可复用组件
│   ├── charts.py                # 图表组件
│   └── layout.py                # 布局组件
│
├── utils/                       # 工具模块
│   ├── __init__.py
│   ├── config.py                # 配置管理
│   ├── logger.py                # 日志工具
│   └── helpers.py               # 辅助函数
│
├── models/                      # 预训练模型目录
│   ├── short_term.pkl
│   ├── medium_term.pkl
│   └── long_term.pkl
│
├── data/                        # 数据文件目录
│   ├── stock_data.db            # SQLite数据库
│   └── cache/                   # 缓存目录
│
└── logs/                        # 日志目录
    └── app.log
```

---

## 5. requirements.txt

```txt
# 数据获取
akshare>=1.12.0

# 数据处理
pandas>=2.0.0
numpy>=1.24.0

# 技术指标
pandas-ta>=0.3.14b

# 机器学习
scikit-learn>=1.3.0

# 可视化
plotly>=5.18.0

# 界面
streamlit>=1.28.0

# 数据库（SQLite内置）
# 无需额外安装

# 可选依赖（后续扩展）
# lightgbm>=4.0.0
# xgboost>=2.0.0
# tensorflow>=2.13.0
```

---

## 6. 环境要求

### 6.1 Python版本
- Python 3.10 或更高版本

### 6.2 操作系统
- Windows 10/11
- macOS 10.15+
- Linux (主流发行版)

### 6.3 硬件要求
- CPU：双核及以上
- 内存：4GB及以上（建议8GB）
- 存储：至少2GB可用空间

### 6.4 网络
- 需要网络连接（仅用于数据更新）
- 建议稳定网络环境

---

## 7. 开发环境配置

### 7.1 虚拟环境创建

```bash
# 使用venv
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 7.2 依赖安装

```bash
# 安装依赖
pip install -r requirements.txt

# 或使用国内镜像加速
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 7.3 运行应用

```bash
# 启动Streamlit应用
streamlit run app.py
```

---

## 8. 可选技术扩展

### 8.1 高级预测模型（V2.0）

如果需要更强的预测能力，可以考虑：

| 模型 | 用途 | 依赖 |
|------|------|------|
| LightGBM | 梯度提升树 | lightgbm |
| XGBoost | 极端梯度提升 | xgboost |
| LSTM | 时间序列深度学习 | tensorflow/keras |
| Transformer | 序列建模 | torch/transformers |

### 8.2 实时数据

如果需要实时数据：

| 方案 | 说明 |
|------|------|
| akshare实时API | 免费但可能有延迟 |
| 东方财富API | 需要申请 |
| 腾讯API | 免费但数据有限 |

### 8.3 数据备份

| 方案 | 说明 |
|------|------|
| SQLite备份 | 定期复制db文件 |
| 云端备份 | 上传到云存储 |
| 版本控制 | 使用git管理代码（不含db） |

---

## 9. 技术债务和限制

### 9.1 已知限制
1. **数据源依赖**：依赖akshare，API变化可能影响功能
2. **模型局限**：基于历史数据，不保证未来表现
3. **计算资源**：本地运行，大规模计算受限于硬件
4. **实时性**：非实时交易系统

### 9.2 技术债务
1. **预测模型**：V1.0使用基础模型，准确率有待提升
2. **界面定制**：Streamlit定制能力有限
3. **错误处理**：需要完善异常处理和日志
4. **测试覆盖**：需要补充单元测试和集成测试

---

## 10. 安全和隐私

### 10.1 数据安全
- SQLite数据库文件存储在本地
- 可选：数据库加密（使用sqlcipher）

### 10.2 隐私保护
- 不上传用户数据到云端
- 不收集用户行为数据
- 所有计算在本地完成

### 10.3 网络安全
- 仅使用HTTPS连接
- 不存储敏感信息（密码、token等）