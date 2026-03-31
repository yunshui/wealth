# 项目开发经验教训 (Project Development Lessons)

本文档记录了在人机协同A股智能投资决策系统开发过程中积累的经验和教训，涵盖从需求收集到运行时调试的完整开发周期。

---

# 第一部分：前期开发阶段

## 1. 需求收集阶段

**经验**:
- 一次问一个问题，避免用户信息过载
- 使用多选题时，选项要互斥且覆盖全面
- 对于重要决策（如技术选型），先提出多个方案并说明利弊

**教训**:
- 需要明确"人机协同"的具体含义，避免歧义
- 预测周期需要更具体的定义（天数/月数）
- GUI需要明确是原生还是Web技术

## 2. 技术选型阶段

**经验**:
- 简述技术选型的对比优势
- 考虑开发速度和后续维护成本
- 本地桌面应用不一定要用原生GUI框架

**教训**:
- 早期应该更明确性能要求
- 应该提前确认数据源的稳定性

## 3. 文档编写和设计阶段

**经验**:
- 分模块编写文档，便于维护
- 文档之间保持一致性和关联
- 使用表格清晰展示结构和参数
- 设计文档应经过代码审查

**教训**:
- 文档编写耗时较长，应该边设计边记录
- 某些细节（如具体的akshare API）需要实际测试后再确定
- 评分公式需要考虑归一化处理，不同量纲指标不能直接相加
- 准确率目标需要基于实际情况设定，避免过于理想化
- 数据库设计不能遗漏索引和必要的表
- 推理依据需要明确格式（建议JSON）
- 首次模型初始化方案不能忽略，系统才能正常启动

## 4. 设计审查阶段

**经验**:
- 设计文档审查能发现隐藏的问题
- 对比多份文档可以发现不一致之处
- 日期等基础信息容易出错，需要特别检查
- 使用代码审查工具可以提供专业反馈

**发现并修复的问题**:
- 日期年份错误（2025写成2026，当前是2026年）
- 表结构不完整（缺少sectors和model_params表）
- 索引设计缺失，影响查询性能
- sector_leaders表字段不一致（缺少market_cap_rank和volume_rank）
- 打字错误（"阘段"应为"阶段"）
- 准确率目标过于理想化，调整为更现实的值
- 股票代码显示格式不一致（缺少.SZ/.SH后缀）
- 评分公式未归一化，需要先标准化各指标
- 缺少接口设计，不便于协作开发
- 缺少异常处理设计，影响系统健壮性
- 缺少缓存策略设计，影响性能

---

# 第二部分：UI开发阶段

## 15. Streamlit按钮左对齐问题

### 问题
Streamlit的st.button默认居中对齐，当选中和未选中状态切换时，对齐方式不一致（未选中居中，选中后左对齐）。

### 原因
- Streamlit的默认样式包含居中对齐
- CSS选择器优先级不够高
- 父容器的对齐属性影响按钮位置

### 解决方案
```css
/* 容器级别强制左对齐 */
div[data-testid="stVerticalBlock"] > div[data-testid="column"] {
    display: flex !important;
    flex-direction: column !important;
    align-items: flex-start !important;
}

/* 按钮容器左对齐 */
div.stButton {
    display: flex !important;
    justify-content: flex-start !important;
    align-items: flex-start !important;
    width: 100% !important;
}

/* 按钮样式 */
div.stButton > button:first-child {
    border: none !important;
    text-align: left !important;
    display: inline-flex !important;
    justify-content: flex-start !important;
    align-items: center !important;
}

/* 移除所有可能的居中 */
[data-testid="stVerticalBlock"] {
    align-items: flex-start !important;
}
```

### 经验教训
- Streamlit默认样式很难覆盖，需要多层CSS选择器
- 使用 `!important` 提高优先级
- 需要同时处理按钮、按钮容器和父容器的对齐
- 选中状态可以用HTML渲染替代，避免样式冲突
- 使用 `display: inline-flex` 和 `justify-content: flex-start` 确保按钮内容左对齐

---

# 第三部分：运行时问题解决

## 6. 类型提示导入缺失

### 问题
```python
# ui/pages.py - 错误示例
def _get_prediction_cached(symbol: str) -> Dict:  # NameError: name 'Dict' is not defined
    storage = StockStorage(DatabaseManager())
    predictor = EnsemblePredictor(storage)
    predictor.load_models()
    return predictor.predict(symbol)
```

### 原因
使用了 `Dict` 类型提示但忘记从 `typing` 模块导入。

### 解决方案
```python
# ui/pages.py - 正确示例
from typing import Dict

def _get_prediction_cached(symbol: str) -> Dict:
    storage = StockStorage(DatabaseManager())
    predictor = EnsemblePredictor(storage)
    predictor.load_models()
    return predictor.predict(symbol)
```

### 经验教训
- 在使用类型提示时，确保从 `typing` 模块导入所有需要的类型
- Streamlit 的缓存装饰器 `@st.cache_data` 会在每次缓存命中时重新执行函数，因此必须确保所有导入都在函数外部完成
- 使用 IDE 的类型检查工具可以帮助及早发现这类问题

## 6. Streamlit 会话状态不匹配

### 问题
```python
# app.py - 错误示例
if "page" not in st.session_state:
    st.session_state.page = "首页"  # 错误：与导航选项不匹配

page = st.radio(
    "导航",
    ["首页/板块总览", "股票详情", "数据更新", "历史回顾"],
    index=["首页/板块总览", "股票详情", "数据更新", "历史回顾"].index(st.session_state.page)
)
# ValueError: '首页' is not in list
```

### 原因
初始会话状态值与导航选项列表中的值不匹配。

### 解决方案
```python
# app.py - 正确示例
if "page" not in st.session_state:
    st.session_state.page = "首页/板块总览"  # 与导航选项完全匹配

page = st.radio(
    "导航",
    ["首页/板块总览", "股票详情", "数据更新", "历史回顾"],
    index=["首页/板块总览", "股票详情", "数据更新", "历史回顾"].index(st.session_state.page)
)
```

### 经验教训
- 确保会话状态的初始值与 UI 控件（如 `st.radio`）的选项列表完全一致
- 使用常量或配置文件来管理这些字符串值，避免硬编码和拼写错误
- 在开发过程中，可以使用 `st.write(st.session_state)` 调试会话状态

## 7. 数据库表不存在错误

### 问题
```python
# 运行时错误
utils.exceptions.StorageException: [E0003] Failed to get sectors: no such table: sectors
```

### 原因
- 数据库文件已存在，但表结构未创建
- `check_database_exists()` 只检查文件是否存在，不检查表是否存在
- 应用启动时没有确保表已创建

### 解决方案
```python
# app.py - 正确示例
# Initialize database
db_manager = DatabaseManager()
if not db_manager.check_database_exists():
    db_manager.create_tables()
    Logger.info("Database initialized successfully")
```

```python
# data/database.py - 改进的 check_database_exists()
def check_database_exists(self) -> bool:
    """Check if database file exists and has tables.

    Returns:
        True if database exists with tables, False otherwise
    """
    import os
    if not os.path.exists(self.db_path):
        return False

    try:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table'")
        count = cursor.fetchone()[0]
        return count > 0
    except Exception:
        return False
```

### 经验教训
- 在应用启动时始终检查并初始化数据库
- `check_database_exists()` 应该同时检查文件和表的存在性
- 对于 SQLite，`INSERT OR REPLACE` 可以处理表结构不完全匹配的情况，但不能处理表不存在的情况

## 8. akshare API 列名变化

### 问题
```python
# ui/pages.py - 错误示例
for _, sector in industry_sectors.iterrows():
    storage.save_sector({
        'sector_id': sector['行业'],  # KeyError: '行业'
        'sector_name': sector['行业名称'],
        'sector_type': 'industry'
    })
```

### 原因
akshare API 的返回数据列名发生了变化，从 `'行业'`/`'行业名称'` 改为 `'板块代码'`/`'板块名称'`。

### 解决方案
```python
# ui/pages.py - 正确示例
for _, sector in industry_sectors.iterrows():
    storage.save_sector({
        'sector_id': sector['板块代码'],  # 更新为新的列名
        'sector_name': sector['板块名称'],
        'sector_type': 'industry'
    })
```

### 验证方法
```bash
# 使用 Python 脚本验证 API 返回的列名
python3 -c "import akshare as ak; df = ak.stock_board_industry_name_em(); print(df.columns)"
```

### 经验教训
- 外部 API 可能随时发生变化，需要定期验证
- 使用常量或配置文件来管理 API 列名，便于维护和更新
- 在处理 API 数据时，添加列名检查和错误处理
- 记录 API 版本和列名映射关系

## 9. 函数级导入在 Streamlit 中的作用域问题

### 问题
```python
# ui/pages.py - 错误示例
def _update_stocks_data(storage: StockStorage):
    """Update stock data for all sectors."""
    from data.fetcher import DataFetcher
    # 缺少 IndicatorCalculator 导入
    calculator = IndicatorCalculator()  # NameError: name 'IndicatorCalculator' is not defined
```

### 原因
在函数内部导入其他模块时，容易遗漏某些导入，导致运行时错误。

### 解决方案
```python
# ui/pages.py - 正确示例
def _update_stocks_data(storage: StockStorage):
    """Update stock data for all sectors."""
    from data.fetcher import DataFetcher
    from analysis.indicators import IndicatorCalculator  # 添加缺失的导入
    calculator = IndicatorCalculator()
```

### 经验教训
- 在函数内部进行导入时，确保所有需要的模块都已导入
- 使用 IDE 的自动导入功能来避免遗漏
- 对于频繁使用的模块，考虑在文件顶部统一导入
- Streamlit 的缓存机制可能会影响导入的时机，需要注意

## 10. 集成测试数据污染问题

### 问题
```python
# tests/integration/test_app_integration.py - 错误示例
@pytest.fixture(scope="module")
def sample_stock_data():
    dates = pd.date_range(end=datetime.now(), periods=100)
    data = []
    for i, date in enumerate(dates):
        data.append({
            'date': date.strftime('%Y-%m-%d'),
            'symbol': 'INTEG001.SH',  # 固定的 symbol
            'open': base_price,
            # ... 其他字段
        })
    return pd.DataFrame(data)

def test_complete_stock_workflow(self, test_storage, sample_stock_data):
    # 多个测试使用相同的 sample_stock_data，导致数据污染
    test_storage.save_stock_data(sample_data)
    retrieved = test_storage.get_stock_data(unique_symbol)
    assert len(retrieved) == 100  # 可能失败，因为其他测试已经插入了相同 symbol 的数据
```

### 原因
- 多个测试共享相同的测试数据 fixture
- 使用相同的 symbol 导致数据在测试之间相互影响
- 数据库事务未正确隔离

### 解决方案
```python
# tests/integration/test_app_integration.py - 正确示例
@pytest.fixture(scope="module")
def sample_stock_data():
    dates = pd.date_range(end=datetime.now(), periods=100)
    data = []
    for i, date in enumerate(dates):
        data.append({
            'date': date.strftime('%Y-%m-%d'),
            'symbol': 'INTEG001.SH',  # 作为模板
            'open': base_price,
            # ... 其他字段
        })
    return pd.DataFrame(data)

def test_complete_stock_workflow(self, test_storage, sample_stock_data):
    # 使用唯一的 symbol 避免冲突
    unique_symbol = 'E2E001.SH'
    sample_data = sample_stock_data.copy()
    sample_data['symbol'] = unique_symbol

    # 保存数据
    test_storage.save_stock(sample_data)

    # 使用范围断言而不是精确断言
    retrieved = test_storage.get_stock_data(unique_symbol)
    assert len(retrieved) >= 100  # 至少包含原始数据
```

### 经验教训
- 在集成测试中，为每个测试使用唯一的数据标识符
- 使用 pytest 的 fixture 来管理测试数据的生命周期
- 对于可能重复插入数据的场景，使用范围断言而不是精确断言
- 考虑使用事务回滚来隔离测试数据

## 11. DataFrame 原地操作性能优化

### 问题
```python
# analysis/indicators.py - 低效示例
@staticmethod
def calculate_ma(df: pd.DataFrame, periods: List[int] = [5, 10, 20, 60]) -> pd.DataFrame:
    df_copy = df.copy()  # 不必要的复制
    for period in periods:
        col_name = f'ma{period}'
        df_copy[col_name] = df_copy['close'].rolling(window=period).mean()
    return df_copy
```

### 原因
不必要的 DataFrame 复制导致性能下降，特别是在处理大量数据时。

### 解决方案
```python
# analysis/indicators.py - 高效示例
@staticmethod
def calculate_ma(df: pd.DataFrame, periods: List[int] = [5, 10, 20, 60]) -> pd.DataFrame:
    # 避免不必要的复制 - 原地修改
    for period in periods:
        col_name = f'ma{period}'
        df[col_name] = df['close'].rolling(window=period).mean()
    return df
```

### 经验教训
- 对于只需要添加列的操作，避免使用 `.copy()`
- 使用 `df.copy()` 只在需要保留原始数据时
- 考虑使用 `df.assign()` 作为函数式链式调用的替代方案
- 对于大数据集，性能差异可能非常显著

## 12. 数据库索引创建性能优化

### 问题
```python
# data/database.py - 不完整示例
def _create_indexes(self, cursor) -> None:
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_stock_data_symbol_date
        ON stock_data(symbol, date)
    ''')
    # ... 其他索引
    conn.commit()  # 可能导致 NameError: name 'conn' is not defined
```

### 原因
- 在索引创建方法中使用了未定义的变量
- 每个索引单独提交可能导致性能问题

### 解决方案
```python
# data/database.py - 完整示例
def _create_indexes(self, cursor) -> None:
    """Create indexes for query performance optimization."""
    # 索引 stock_data
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_stock_data_symbol_date
        ON stock_data(symbol, date)
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_stock_data_date
        ON stock_data(date DESC)
    ''')
    # ... 其他索引

    # 统一在 create_tables() 中提交
```

```python
# data/database.py - 调用位置
def create_tables(self) -> None:
    Logger.info("Creating database tables...")
    conn = self.get_connection()
    cursor = conn.cursor()

    # 创建表
    cursor.execute('''CREATE TABLE IF NOT EXISTS ...''')

    # 创建索引
    self._create_indexes(cursor)

    # 统一提交
    conn.commit()
```

### 经验教训
- 将索引创建逻辑与表创建逻辑分离，但使用相同的连接和提交
- 使用 `CREATE INDEX IF NOT EXISTS` 避免重复创建
- 根据查询模式设计复合索引
- 定期监控查询性能，调整索引策略

## 13. Streamlit 后台任务管理

### 问题
```python
# 错误示例
import subprocess
process = subprocess.Popen(["streamlit", "run", "app.py"])
# 无法监控进程状态，无法优雅关闭
```

### 原因
直接使用 subprocess 无法有效管理 Streamlit 后台进程。

### 解决方案
```python
# 使用 Bash 工具的 run_in_background 参数
Bash(command="streamlit run app.py", run_in_background=True)

# 检查任务状态
TaskOutput(task_id="task_id", block=False, timeout=5000)

# 停止任务
TaskStop(task_id="task_id")
```

### 经验教训
- 使用专门的工具来管理后台任务，而不是直接使用 subprocess
- 为长时间运行的任务设置合理的超时时间
- 在开发过程中，使用非阻塞方式检查任务状态
- 确保在任务完成或出错时正确清理资源

## 14. SQLite 自增主键与数据重复

### 问题
```python
# 使用 INSERT OR REPLACE 时的问题
cursor.execute('''
    INSERT OR REPLACE INTO stock_data (date, symbol, close, ...)
    VALUES (?, ?, ?, ...)
''', values)
```

### 原因
- 使用 `INSERT OR REPLACE` 时，如果主键（自增 ID）不同，会插入新行而不是替换
- 导致相同的数据被插入多次

### 解决方案
```python
# 使用唯一约束和 INSERT OR REPLACE
cursor.execute('''
    CREATE TABLE IF NOT EXISTS stock_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        symbol TEXT NOT NULL,
        close REAL,
        ...
        UNIQUE(date, symbol)  -- 添加唯一约束
    )
''')

cursor.execute('''
    INSERT OR REPLACE INTO stock_data (date, symbol, close, ...)
    VALUES (?, ?, ?, ...)
''', values)
```

### 经验教训
- 对于需要唯一性的数据，使用 `UNIQUE` 约束而不是仅依赖主键
- 在设计数据库模式时，考虑数据的业务键（如 date + symbol）
- 使用事务来确保数据的一致性
- 定期检查和清理重复数据

---

# 总结

## 最佳实践

### 1. 导入管理
- 在文件顶部统一导入常用模块
- 在函数内部导入时确保完整性
- 使用类型提示时导入相应的类型

### 2. 会话状态管理
- 使用常量定义状态值
- 确保初始值与 UI 选项匹配
- 定期使用调试工具验证状态

### 3. 数据库初始化
- 应用启动时检查并初始化数据库
- 检查表的存在性而不仅仅是文件
- 使用事务确保一致性

### 4. 外部 API 处理
- 验证 API 返回数据的结构
- 使用配置文件管理列名映射
- 添加错误处理和重试逻辑

### 5. 测试隔离
- 使用唯一的测试数据标识符
- 使用 fixture 管理测试数据生命周期
- 使用范围断言处理可变数据

### 6. 性能优化
- 避免不必要的 DataFrame 复制
- 使用原地操作添加列
- 根据查询模式设计索引

### 7. 进程管理
- 使用专门工具管理后台任务
- 设置合理的超时时间
- 正确清理资源

## 持续改进

- 定期更新此文档，记录新遇到的问题
- 使用版本控制跟踪问题和解决方案
- 建立问题追踪系统
- 定期审查代码，识别潜在问题