# 开发者指南

## 项目架构

### 技术栈

- **语言**: Python 3.10+
- **前端**: Streamlit
- **数据源**: akshare
- **机器学习**: scikit-learn
- **数据库**: SQLite
- **数据**: pandas, numpy

### 目录结构

```
wealth/
├── app.py                       # Streamlit主应用
├── requirements.txt             # Python依赖
├── CLAUDE.md                    # Claude Code项目说明
├── README.md                    # 项目概述
├── PROGRESS.md                  # 项目进度
├── docs/                        # 文档目录
│   ├── PRD.md                   # 产品需求文档
│   ├── APP_FLOW.md              # 应用流程文档
│   ├── TECH_STACK.md            # 技术栈文档
│   ├── FRONTEND_GUIDELINES.md   # 前端设计指南
│   ├── BACKEND_STRUCTURE.md     # 后端结构文档
│   ├── IMPLEMENTATION_PLAN.md   # 实现计划
│   ├── USER_GUIDE.md            # 用户使用手册
│   └── DEVELOPER_GUIDE.md       # 开发者指南（本文件）
├── data/                        # 数据层模块
│   ├── __init__.py
│   ├── database.py              # 数据库初始化和连接管理
│   ├── fetcher.py               # akshare数据获取
│   ├── storage.py               # SQLite存储操作
│   └── models.py                # 数据模型定义
├── analysis/                    # 分析层模块
│   ├── __init__.py
│   ├── indicators.py            # 技术指标计算
│   ├── sector.py                # 板块识别和龙头筛选
│   └── features.py              # 特征工程
├── prediction/                  # 预测层模块
│   ├── __init__.py
│   ├── base.py                  # 预测模型基类
│   ├── short_term.py            # 短期预测模型
│   ├── medium_term.py           # 中期预测模型
│   ├── long_term.py             # 长期预测模型
│   ├── ensemble.py              # 集成预测
│   └── trainer.py               # 模型训练
├── ui/                          # 界面层模块
│   ├── __init__.py
│   ├── pages.py                 # 各页面组件
│   ├── components.py            # 可复用组件
│   ├── charts.py                # 图表组件
│   ├── layout.py                # 布局组件
│   └── prediction.py            # 预测显示组件
├── utils/                       # 工具模块
│   ├── __init__.py
│   ├── config.py                # 配置管理
│   ├── logger.py                # 日志工具
│   ├── helpers.py               # 辅助函数
│   ├── cache.py                 # 缓存管理
│   └── error_handler.py         # 错误处理
├── models/                      # 预训练模型目录
├── data/                        # 数据文件目录
│   ├── cache/                   # 缓存目录
│   └── stock_data.db            # SQLite数据库
├── tests/                       # 测试目录
│   ├── conftest.py              # pytest配置
│   └── integration/             # 集成测试
└── logs/                        # 日志目录
```

### 分层架构

```
┌─────────────────────────────────────────┐
│         前端层 (UI Layer)               │
│         Streamlit Components             │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│         业务逻辑层 (Business Layer)       │
│    板块分析 | 特征工程 | 预测集成         │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│         服务层 (Service Layer)           │
│  数据获取 | 数据存储 | 预测服务           │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│         数据层 (Data Layer)              │
│  akshare | SQLite | 模型文件             │
└─────────────────────────────────────────┘
```

---

## 开发环境设置

### 1. 克隆项目

```bash
git clone <repository-url>
cd wealth
```

### 2. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置

编辑 `utils/config.py` 修改配置：

```python
DB_PATH = "data/stock_data.db"
LOG_FILE = "logs/app.log"
LOG_LEVEL = "INFO"
CACHE_DIR = "data/cache"
```

---

## 开发指南

### 代码规范

遵循 PEP 8 规范：

- 使用4空格缩进
- 行长度不超过88字符
- 使用有意义的变量和函数名
- 添加类型注解
- 编写docstring

### 日志规范

使用 `utils.logger.Logger`：

```python
from utils.logger import Logger

Logger.debug("详细调试信息")
Logger.info("一般信息")
Logger.warning("警告信息")
Logger.error("错误信息")
```

### 错误处理

使用自定义异常：

```python
from utils.exceptions import StorageException
from utils.logger import Logger

try:
    # 你的代码
    pass
except Exception as e:
    Logger.error(f"操作失败: {str(e)}")
    raise StorageException(f"操作失败: {str(e)}")
```

### 单元测试

运行测试：

```bash
# 运行所有测试
pytest

# 运行特定模块测试
pytest tests/test_database.py

# 查看覆盖率
pytest --cov=. --cov-report=html
```

---

## 模块开发

### 数据层 (data/)

#### DatabaseManager

负责数据库连接和表创建：

```python
from data.database import DatabaseManager

db = DatabaseManager()
db.create_tables()
```

#### StockStorage

负责数据CRUD操作：

```python
from data.storage import StockStorage
from data.database import DatabaseManager

storage = StockStorage(DatabaseManager())

# 保存股票
storage.save_stock({
    'symbol': '000001.SZ',
    'name': '平安银行',
    'industry': '金融',
    'sector': '银行',
    'market_cap': 100000000000,
    'pe_ratio': 10.5,
    'pb_ratio': 1.2
})

# 获取股票
stock = storage.get_stock('000001.SZ')
```

#### DataFetcher

负责从akshare获取数据：

```python
from data.fetcher import DataFetcher

fetcher = DataFetcher()

# 获取行业板块
sectors = fetcher.get_industry_sectors()

# 获取股票历史数据
history = fetcher.get_stock_history('000001', '20230101', '20231231')
```

### 分析层 (analysis/)

#### IndicatorCalculator

计算技术指标：

```python
from analysis.indicators import IndicatorCalculator
import pandas as pd

# 准备数据
df = pd.DataFrame({
    'close': [10.0, 10.5, 11.0, 10.8, 11.2],
    'high': [10.2, 10.8, 11.2, 11.0, 11.5],
    'low': [9.8, 10.2, 10.8, 10.5, 10.9],
    'volume': [1000000, 1200000, 1500000, 1300000, 1400000]
})

# 计算指标
df = IndicatorCalculator.calculate_all(df)
```

#### SectorAnalyzer

识别板块龙头：

```python
from analysis.sector import SectorAnalyzer
from data.storage import StockStorage
from data.database import DatabaseManager

analyzer = SectorAnalyzer(StockStorage(DatabaseManager()))

# 识别龙头股
leaders = analyzer.identify_leaders('BANK001', '银行', limit=10)
```

### 预测层 (prediction/)

#### EnsemblePredictor

集成预测服务：

```python
from prediction.ensemble import EnsemblePredictor
from data.storage import StockStorage
from data.database import DatabaseManager

predictor = EnsemblePredictor(StockStorage(DatabaseManager()))

# 加载模型
predictor.load_models()

# 预测
result = predictor.predict('000001.SZ')
```

#### ModelTrainer

训练模型：

```python
from prediction.trainer import ModelTrainer
from data.storage import StockStorage
from data.database import DatabaseManager

trainer = ModelTrainer(StockStorage(DatabaseManager()))

# 训练所有模型
trainer.train_all_models()
```

### 界面层 (ui/)

#### 页面组件

```python
from ui.pages import show_homepage, show_stock_detail

# 显示首页
show_homepage()

# 显示股票详情
show_stock_detail('000001.SZ')
```

#### 图表组件

```python
from ui.charts import plot_kline_chart
import pandas as pd

# K线图
plot_kline_chart(df, height=400)

# 成交量图
plot_volume_chart(df, height=200)
```

---

## 调试技巧

### 1. 查看日志

```bash
tail -f logs/app.log
```

### 2. 使用Streamlit调试

```bash
streamlit run app.py --logger.level=debug
```

### 3. 数据库查询

```bash
sqlite3 data/stock_data.db
```

### 4. 检查缓存

```bash
ls -la data/cache/
```

---

## 性能优化

### 1. 使用缓存

```python
import streamlit as st

@st.cache_data(ttl=3600)
def expensive_function():
    # 耗时操作
    pass
```

### 2. 数据采样

```python
# 大数据集时采样
if len(df) > 1000:
    df = df.sample(n=1000)
```

### 3. 批量操作

```python
# 批量插入而非逐条插入
storage.save_stock_data(batch_df)
```

---

## 部署

### 1. 打包

```bash
pip install pyinstaller
pyinstaller --onefile app.py
```

### 2. Docker部署

```dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "app.py"]
```

### 3. 云部署

支持部署到：
- Streamlit Cloud
- Heroku
- 阿里云
- 腾讯云

---

## 贡献指南

### 1. Fork项目

2. 创建功能分支

```bash
git checkout -b feature/your-feature
```

3. 提交更改

```bash
git commit -m "feat: add your feature"
```

4. 推送到分支

```bash
git push origin feature/your-feature
```

5. 创建Pull Request

### Commit消息格式

```
feat: 新功能
fix: 修复bug
refactor: 代码重构
docs: 文档更新
test: 测试更新
chore: 其他更改
```

---

## 常见问题

### Q: 如何添加新的技术指标？

A: 在 `analysis/indicators.py` 中添加新方法，然后在 `calculate_all()` 中调用。

### Q: 如何修改预测权重？

A: 在 `prediction/ensemble.py` 中修改 `DEFAULT_WEIGHTS` 字典。

### Q: 如何添加新的板块？

A: 系统会自动从akshare获取所有板块，无需手动添加。

### Q: 数据库太大怎么办？

A: 可以定期清理旧数据，或考虑使用MySQL/PostgreSQL替代SQLite。

---

## 参考资料

- [akshare文档](https://akshare.akfamily.xyz/)
- [Streamlit文档](https://docs.streamlit.io/)
- [scikit-learn文档](https://scikit-learn.org/)
- [pandas文档](https://pandas.pydata.org/)