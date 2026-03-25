# BACKEND_STRUCTURE - 后端结构文档

## 1. 后端架构概览

### 1.1 分层架构

```
┌─────────────────────────────────────────────────────────┐
│                      前端层 (UI Layer)                   │
│                    Streamlit Application                 │
└────────────────────────┬────────────────────────────────┘
                         │ API调用
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

### 1.2 模块划分

| 模块 | 路径 | 职责 |
|------|------|------|
| 数据层 | `data/` | 数据获取、存储、模型管理 |
| 分析层 | `analysis/` | 技术指标计算、板块分析、特征工程 |
| 预测层 | `prediction/` | 预测模型、模型训练、集成预测 |
| 工具层 | `utils/` | 配置、日志、辅助函数 |

---

## 2. 数据层 (data/)

### 2.1 模块结构

```
data/
├── __init__.py
├── database.py      # 数据库初始化和连接管理
├── fetcher.py       # akshare数据获取
├── storage.py       # SQLite存储操作
└── models.py        # 数据模型定义
```

### 2.2 database.py

**职责**：数据库初始化、连接管理、表结构维护

**核心类**：
```python
class DatabaseManager:
    """数据库管理器"""

    def __init__(self, db_path: str = 'data/stock_data.db'):
        """初始化数据库连接"""
        pass

    def create_tables(self):
        """创建所有数据表"""
        pass

    def get_connection(self):
        """获取数据库连接"""
        pass

    def close(self):
        """关闭数据库连接"""
        pass

    def check_database_exists(self) -> bool:
        """检查数据库是否存在"""
        pass

    def get_last_update_date(self) -> str:
        """获取最后更新日期"""
        pass
```

**数据库初始化流程**：
1. 检查数据库文件是否存在
2. 如果不存在，创建新数据库
3. 创建所有必需的表
4. 创建索引
5. 初始化配置表

### 2.3 fetcher.py

**职责**：从akshare获取各种数据

**核心类**：
```python
class DataFetcher:
    """数据获取器"""

    def __init__(self):
        """初始化数据获取器"""
        pass

    # 板块相关
    def get_industry_sectors(self) -> pd.DataFrame:
        """获取行业板块列表"""
        pass

    def get_concept_sectors(self) -> pd.DataFrame:
        """获取概念板块列表"""
        pass

    def get_sector_stocks(self, sector_name: str, sector_type: str) -> pd.DataFrame:
        """获取板块成分股"""
        pass

    # 股票相关
    def get_stock_info(self, symbol: str) -> dict:
        """获取股票基本信息"""
        pass

    def get_stock_history(self, symbol: str, start_date: str = None) -> pd.DataFrame:
        """获取股票历史数据（开高低收、成交量）"""
        pass

    def get_stock_latest(self, symbol: str) -> dict:
        """获取股票最新数据"""
        pass

    # 财务数据
    def get_financial_data(self, symbol: str) -> dict:
        """获取财务数据"""
        pass

    # 批量操作
    def get_all_stocks_info(self) -> pd.DataFrame:
        """获取所有股票基本信息"""
        pass

    def get_batch_history(self, symbols: List[str], start_date: str = None) -> Dict[str, pd.DataFrame]:
        """批量获取历史数据"""
        pass
```

**API封装说明**：
- 对akshare的API进行封装和标准化
- 统一数据格式返回
- 添加错误处理和重试机制
- 添加缓存避免重复请求

### 2.4 storage.py

**职责**：数据的CRUD操作

**核心类**：
```python
class StockStorage:
    """股票数据存储"""

    def __init__(self, db_manager: DatabaseManager):
        """初始化存储器"""
        pass

    # 板块数据
    def save_sector(self, sector_data: dict) -> bool:
        """保存板块信息"""
        pass

    def save_sector_stocks(self, sector_id: str, stocks: List[str]) -> bool:
        """保存板块成分股"""
        pass

    def get_all_sectors(self) -> List[dict]:
        """获取所有板块"""
        pass

    def get_sector_stocks(self, sector_id: str) -> List[str]:
        """获取板块成分股"""
        pass

    # 股票数据
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

    def get_latest_stock_data(self, symbol: str) -> dict:
        """获取股票最新数据"""
        pass

    # 预测数据
    def save_prediction(self, prediction_data: dict) -> bool:
        """保存预测结果"""
        pass

    def save_predictions(self, predictions: List[dict]) -> bool:
        """批量保存预测结果"""
        pass

    def get_prediction(self, symbol: str, horizon: str, date: str = None) -> dict:
        """获取预测结果"""
        pass

    def get_predictions(self, symbol: str) -> List[dict]:
        """获取股票所有预测结果"""
        pass

    # 龙头股数据
    def save_sector_leaders(self, sector_id: str, leaders: List[dict]) -> bool:
        """保存板块龙头股"""
        pass

    def get_sector_leaders(self, sector_id: str) -> List[dict]:
        """获取板块龙头股"""
        pass

    def get_all_leaders(self) -> List[dict]:
        """获取所有板块龙头股"""
        pass

    # 查询辅助
    def search_stocks(self, keyword: str) -> List[dict]:
        """搜索股票"""
        pass

    def get_stock_list(self) -> List[dict]:
        """获取股票列表"""
        pass
```

### 2.5 models.py

**职责**：数据模型定义

**数据模型**：
```python
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

@dataclass
class Stock:
    """股票基本信息"""
    symbol: str
    name: str
    industry: Optional[str] = None
    sector: Optional[str] = None
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    list_date: Optional[str] = None

@dataclass
class StockData:
    """股票历史数据"""
    date: str
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    amount: Optional[float] = None
    # 技术指标
    ma5: Optional[float] = None
    ma10: Optional[float] = None
    ma20: Optional[float] = None
    ma60: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_hist: Optional[float] = None
    kdj_k: Optional[float] = None
    kdj_d: Optional[float] = None
    kdj_j: Optional[float] = None
    rsi6: Optional[float] = None
    rsi12: Optional[float] = None
    rsi24: Optional[float] = None
    boll_upper: Optional[float] = None
    boll_middle: Optional[float] = None
    boll_lower: Optional[float] = None
    obv: Optional[float] = None

@dataclass
class Prediction:
    """预测结果"""
    date: str
    symbol: str
    horizon: str  # 'short', 'medium', 'long'
    action: str  # 'buy', 'sell', 'hold'
    confidence: float  # 0-1
    reasoning: List[str]
    model_version: str

@dataclass
class Sector:
    """板块信息"""
    sector_id: str
    sector_name: str
    sector_type: str  # 'industry', 'concept'
    leader_count: int = 0

@dataclass
class SectorLeader:
    """板块龙头股"""
    sector_id: str
    sector_name: str
    symbol: str
    score: float
    rank: int
    market_cap_rank: int
    volume_rank: int
```

---

## 3. 分析层 (analysis/)

### 3.1 模块结构

```
analysis/
├── __init__.py
├── indicators.py    # 技术指标计算
├── sector.py        # 板块分析和龙头筛选
└── features.py      # 特征工程
```

### 3.2 indicators.py

**职责**：计算各类技术指标

**核心类**：
```python
class IndicatorCalculator:
    """技术指标计算器"""

    @staticmethod
    def calculate_ma(df: pd.DataFrame, periods: List[int] = [5, 10, 20, 60]) -> pd.DataFrame:
        """计算移动平均线"""
        pass

    @staticmethod
    def calculate_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
        """计算MACD指标"""
        pass

    @staticmethod
    def calculate_kdj(df: pd.DataFrame, k: int = 9, d: int = 3, j: int = 3) -> pd.DataFrame:
        """计算KDJ指标"""
        pass

    @staticmethod
    def calculate_rsi(df: pd.DataFrame, periods: List[int] = [6, 12, 24]) -> pd.DataFrame:
        """计算RSI指标"""
        pass

    @staticmethod
    def calculate_boll(df: pd.DataFrame, period: int = 20, std: int = 2) -> pd.DataFrame:
        """计算布林线指标"""
        pass

    @staticmethod
    def calculate_obv(df: pd.DataFrame) -> pd.DataFrame:
        """计算OBV指标"""
        pass

    @staticmethod
    def calculate_all(df: pd.DataFrame) -> pd.DataFrame:
        """计算所有技术指标"""
        pass
```

**使用示例**：
```python
# 获取原始数据
df = storage.get_stock_data('000001.SZ')

# 计算所有指标
df_with_indicators = IndicatorCalculator.calculate_all(df)

# 保存更新后的数据
storage.save_stock_data(df_with_indicators)
```

### 3.3 sector.py

**职责**：板块分析和龙头股筛选

**核心类**：
```python
class SectorAnalyzer:
    """板块分析器"""

    def __init__(self, storage: StockStorage):
        """初始化分析器"""
        pass

    def identify_leaders(self, sector_id: str, limit: int = 20) -> List[SectorLeader]:
        """识别板块龙头股"""
        pass

    def calculate_sector_score(self, symbol: str) -> float:
        """计算股票在板块内的综合得分"""
        pass

    def get_sector_trend(self, sector_id: str) -> dict:
        """获取板块整体趋势"""
        pass

    def rank_by_market_cap(self, stocks: List[str], sector_id: str) -> List[tuple]:
        """按市值排名"""
        pass

    def rank_by_volume(self, stocks: List[str], sector_id: str, days: int = 20) -> List[tuple]:
        """按成交量排名"""
        pass

    def update_all_sector_leaders(self):
        """更新所有板块的龙头股"""
        pass
```

**龙头股筛选算法**：
```python
# 综合得分计算公式
score = (market_cap_score * 0.4 +
         volume_score * 0.3 +
         recent_return_score * 0.2 +
         stability_score * 0.1)

# 各项分数归一化到0-1
# 按得分排序，取前N只
```

### 3.4 features.py

**职责**：特征工程，为预测模型准备特征

**核心类**：
```python
class FeatureEngineer:
    """特征工程器"""

    @staticmethod
    def extract_short_term_features(df: pd.DataFrame, lookback: int = 20) -> np.ndarray:
        """提取短期特征（用于短期预测）"""
        pass

    @staticmethod
    def extract_medium_term_features(df: pd.DataFrame, lookback: int = 120) -> np.ndarray:
        """提取中期特征（用于中期预测）"""
        pass

    @staticmethod
    def extract_long_term_features(df: pd.DataFrame) -> np.ndarray:
        """提取长期特征（用于长期预测）"""
        pass

    @staticmethod
    def extract_price_features(df: pd.DataFrame) -> np.ndarray:
        """提取价格相关特征"""
        pass

    @staticmethod
    def extract_volume_features(df: pd.DataFrame) -> np.ndarray:
        """提取成交量相关特征"""
        pass

    @staticmethod
    def extract_indicator_features(df: pd.DataFrame) -> np.ndarray:
        """提取技术指标特征"""
        pass

    @staticmethod
    def create_labels(df: pd.DataFrame, horizon: int) -> np.ndarray:
        """创建标签（未来涨跌）"""
        pass

    @staticmethod
    def normalize_features(X: np.ndarray) -> np.ndarray:
        """特征标准化"""
        pass
```

**特征列表**：

**短期特征（20日）**：
- 最近N日的收益率
- 收益率的标准差
- 移动平均线状态
- 量价关系
- 技术指标的当前值和变化

**中期特征（120日）**：
- 中期趋势方向
- 均线多头/空头排列
- 成交量趋势
- 波动率
- 技术指标的长期状态

**长期特征（全部历史）**：
- 长期趋势
- 历史高点/低点
- 周期性特征
- 行业相对表现
- 基本面指标

---

## 4. 预测层 (prediction/)

### 4.1 模块结构

```
prediction/
├── __init__.py
├── base.py          # 预测模型基类
├── short_term.py    # 短期预测模型
├── medium_term.py   # 中期预测模型
├── long_term.py     # 长期预测模型
├── ensemble.py      # 集成预测
└── trainer.py       # 模型训练
```

### 4.2 base.py

**职责**：定义预测模型的基类接口

**核心类**：
```python
from abc import ABC, abstractmethod
from typing import Tuple, List

class BasePredictor(ABC):
    """预测模型基类"""

    def __init__(self, model_path: str = None):
        """初始化模型"""
        self.model = None
        self.model_path = model_path
        self.is_loaded = False

    @abstractmethod
    def train(self, X: np.ndarray, y: np.ndarray) -> None:
        """训练模型"""
        pass

    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        """预测"""
        pass

    @abstractmethod
    def get_feature_importance(self) -> dict:
        """获取特征重要性"""
        pass

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """预测概率"""
        pass

    def save_model(self, path: str) -> None:
        """保存模型"""
        pass

    def load_model(self, path: str) -> None:
        """加载模型"""
        pass

    def is_trained(self) -> bool:
        """检查模型是否已训练"""
        return self.model is not None

    def get_version(self) -> str:
        """获取模型版本"""
        pass
```

### 4.3 short_term.py

**职责**：短期预测模型（1-5天）

**核心类**：
```python
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression

class ShortTermPredictor(BasePredictor):
    """短期预测模型"""

    def __init__(self, model_type: str = 'random_forest'):
        """初始化模型"""
        super().__init__()
        self.model_type = model_type
        self._init_model()

    def _init_model(self):
        """初始化具体模型"""
        if self.model_type == 'random_forest':
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
        elif self.model_type == 'gradient_boosting':
            self.model = GradientBoostingClassifier(
                n_estimators=100,
                max_depth=5,
                random_state=42
            )
        elif self.model_type == 'logistic':
            self.model = LogisticRegression(
                max_iter=1000,
                random_state=42
            )

    def train(self, X: np.ndarray, y: np.ndarray) -> None:
        """训练模型"""
        self.model.fit(X, y)

    def predict(self, X: np.ndarray) -> np.ndarray:
        """预测"""
        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """预测概率"""
        return self.model.predict_proba(X)

    def get_feature_importance(self) -> dict:
        """获取特征重要性"""
        if hasattr(self.model, 'feature_importances_'):
            return self.model.feature_importances_
        return None

    def generate_reasoning(self, X: np.ndarray, prediction: int, proba: float) -> List[str]:
        """生成推理依据"""
        reasons = []
        # 根据特征和预测结果生成推理
        return reasons
```

**特征说明**：
- 使用最近20日数据
- 重点技术指标和量价关系
- 短期趋势判断

### 4.4 medium_term.py

**职责**：中期预测模型（1-3个月）

**核心类**：
```python
class MediumTermPredictor(BasePredictor):
    """中期预测模型"""

    def __init__(self, model_type: str = 'random_forest'):
        """初始化模型"""
        super().__init__()
        self.model_type = model_type
        self._init_model()

    # 类似ShortTermPredictor的实现
    # 使用不同的特征和参数
```

**特征说明**：
- 使用最近120日数据
- 中期趋势判断
- 均线系统分析
- 成交量趋势
- 基本面辅助

### 4.5 long_term.py

**职责**：长期预测模型（3个月以上）

**核心类**：
```python
class LongTermPredictor(BasePredictor):
    """长期预测模型"""

    def __init__(self, model_type: str = 'random_forest'):
        """初始化模型"""
        super().__init__()
        self.model_type = model_type
        self._init_model()

    # 类似ShortTermPredictor的实现
    # 使用不同的特征和参数
```

**特征说明**：
- 使用全部历史数据
- 长期趋势分析
- 价值指标
- 行业周期
- 基本面数据

### 4.6 ensemble.py

**职责**：集成三周期预测，生成综合建议

**核心类**：
```python
class EnsemblePredictor:
    """集成预测器"""

    def __init__(self, storage: StockStorage):
        """初始化"""
        self.storage = storage
        self.short_predictor = ShortTermPredictor()
        self.medium_predictor = MediumTermPredictor()
        self.long_predictor = LongTermPredictor()

    def load_models(self):
        """加载所有模型"""
        self.short_predictor.load_model('models/short_term.pkl')
        self.medium_predictor.load_model('models/medium_term.pkl')
        self.long_predictor.load_model('models/long_term.pkl')

    def predict(self, symbol: str) -> dict:
        """预测单只股票"""
        # 获取数据
        df = self.storage.get_stock_data(symbol)

        # 提取特征
        X_short = FeatureEngineer.extract_short_term_features(df)
        X_medium = FeatureEngineer.extract_medium_term_features(df)
        X_long = FeatureEngineer.extract_long_term_features(df)

        # 各周期预测
        short_pred = self.short_predictor.predict(X_short)
        short_proba = self.short_predictor.predict_proba(X_short)
        medium_pred = self.medium_predictor.predict(X_medium)
        medium_proba = self.medium_predictor.predict_proba(X_medium)
        long_pred = self.long_predictor.predict(X_long)
        long_proba = self.long_predictor.predict_proba(X_long)

        # 生成推理
        short_reasoning = self.short_predictor.generate_reasoning(X_short, short_pred, short_proba)
        medium_reasoning = self.medium_predictor.generate_reasoning(X_medium, medium_pred, medium_proba)
        long_reasoning = self.long_predictor.generate_reasoning(X_long, long_pred, long_proba)

        # 集成建议
        ensemble = self._ensemble_predictions(
            short_pred, short_proba,
            medium_pred, medium_proba,
            long_pred, long_proba
        )

        return {
            'short': {
                'action': short_pred,
                'confidence': short_proba,
                'reasoning': short_reasoning
            },
            'medium': {
                'action': medium_pred,
                'confidence': medium_proba,
                'reasoning': medium_reasoning
            },
            'long': {
                'action': long_pred,
                'confidence': long_proba,
                'reasoning': long_reasoning
            },
            'ensemble': ensemble
        }

    def _ensemble_predictions(self, short_pred, short_proba, medium_pred, medium_proba,
                             long_pred, long_proba) -> dict:
        """集成预测结果"""
        # 定义权重
        weights = {
            'short': 0.3,
            'medium': 0.4,
            'long': 0.3
        }

        # 计算加权得分
        action_scores = {'buy': 0, 'sell': 0, 'hold': 0}

        # 短期贡献
        action_scores[short_pred] += short_proba * weights['short']
        # 中期贡献
        action_scores[medium_pred] += medium_proba * weights['medium']
        # 长期贡献
        action_scores[long_pred] += long_proba * weights['long']

        # 选择得分最高的动作
        ensemble_action = max(action_scores, key=action_scores.get)
        ensemble_confidence = action_scores[ensemble_action]

        return {
            'action': ensemble_action,
            'confidence': ensemble_confidence,
            'breakdown': action_scores
        }

    def batch_predict(self, symbols: List[str]) -> dict:
        """批量预测"""
        results = {}
        for symbol in symbols:
            results[symbol] = self.predict(symbol)
        return results
```

### 4.7 trainer.py

**职责**：模型训练和管理

**核心类**：
```python
class ModelTrainer:
    """模型训练器"""

    def __init__(self, storage: StockStorage):
        """初始化"""
        self.storage = storage
        self.short_predictor = ShortTermPredictor()
        self.medium_predictor = MediumTermPredictor()
        self.long_predictor = LongTermPredictor()

    def prepare_training_data(self, horizon: str) -> Tuple[np.ndarray, np.ndarray]:
        """准备训练数据"""
        # 获取所有股票的历史数据
        stocks = self.storage.get_stock_list()

        X_list = []
        y_list = []

        for stock in stocks:
            df = self.storage.get_stock_data(stock['symbol'])

            # 提取特征和标签
            if horizon == 'short':
                X = FeatureEngineer.extract_short_term_features(df)
                y = FeatureEngineer.create_labels(df, horizon=5)
            elif horizon == 'medium':
                X = FeatureEngineer.extract_medium_term_features(df)
                y = FeatureEngineer.create_labels(df, horizon=60)
            else:  # long
                X = FeatureEngineer.extract_long_term_features(df)
                y = FeatureEngineer.create_labels(df, horizon=120)

            X_list.append(X)
            y_list.append(y)

        # 合并所有数据
        X_all = np.vstack(X_list)
        y_all = np.hstack(y_list)

        return X_all, y_all

    def train_short_term_model(self) -> float:
        """训练短期模型"""
        X, y = self.prepare_training_data('short')
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        self.short_predictor.train(X_train, y_train)

        # 评估
        y_pred = self.short_predictor.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)

        # 保存模型
        self.short_predictor.save_model('models/short_term.pkl')

        return accuracy

    def train_medium_term_model(self) -> float:
        """训练中期模型"""
        # 类似train_short_term_model
        pass

    def train_long_term_model(self) -> float:
        """训练长期模型"""
        # 类似train_short_term_model
        pass

    def train_all_models(self) -> dict:
        """训练所有模型"""
        results = {
            'short': self.train_short_term_model(),
            'medium': self.train_medium_term_model(),
            'long': self.train_long_term_model()
        }
        return results

    def evaluate_model(self, predictor: BasePredictor, X_test: np.ndarray, y_test: np.ndarray) -> dict:
        """评估模型"""
        y_pred = predictor.predict(X_test)

        return {
            'accuracy': accuracy_score(y_test, y_pred),
            'classification_report': classification_report(y_test, y_pred),
            'confusion_matrix': confusion_matrix(y_test, y_pred)
        }
```

---

## 5. 工具层 (utils/)

### 5.1 模块结构

```
utils/
├── __init__.py
├── config.py        # 配置管理
├── logger.py        # 日志工具
└── helpers.py       # 辅助函数
```

### 5.2 config.py

**职责**：配置管理

**核心类**：
```python
class Config:
    """配置类"""

    # 数据库
    DB_PATH = 'data/stock_data.db'

    # 数据源
    DATA_START_DATE = '2018-01-01'  # 7年历史数据
    DATA_UPDATE_TIME = '15:30'  # 收盘后更新时间

    # 板块
    MAIN_SECTORS = [
        '科技', '医药', '消费', '金融', '制造',
        '能源', '材料', '公用', '地产', '交运'
    ]
    LEADER_COUNT = 20  # 每个板块取前20只龙头股

    # 预测
    SHORT_TERM_HORIZON = 5      # 5天
    MEDIUM_TERM_HORIZON = 60    # 60天
    LONG_TERM_HORIZON = 120     # 120天

    ENSEMBLE_WEIGHTS = {
        'short': 0.3,
        'medium': 0.4,
        'long': 0.3
    }

    # 模型
    MODEL_DIR = 'models'
    SHORT_MODEL_FILE = 'short_term.pkl'
    MEDIUM_MODEL_FILE = 'medium_term.pkl'
    LONG_MODEL_FILE = 'long_term.pkl'

    # 日志
    LOG_DIR = 'logs'
    LOG_FILE = 'app.log'
    LOG_LEVEL = 'INFO'

    # 缓存
    CACHE_DIR = 'data/cache'
    CACHE_EXPIRE = 3600  # 1小时

    @classmethod
    def get_db_path(cls) -> str:
        """获取数据库路径"""
        return cls.DB_PATH

    @classmethod
    def get_model_path(cls, model_type: str) -> str:
        """获取模型路径"""
        return os.path.join(cls.MODEL_DIR, f'{model_type}.pkl')
```

### 5.3 logger.py

**职责**：日志管理

**核心类**：
```python
import logging

class Logger:
    """日志管理器"""

    _instance = None
    _logger = None

    @classmethod
    def get_logger(cls) -> logging.Logger:
        """获取日志实例"""
        if cls._logger is None:
            cls._setup_logger()
        return cls._logger

    @classmethod
    def _setup_logger(cls):
        """设置日志"""
        cls._logger = logging.getLogger('wealth')
        cls._logger.setLevel(Config.LOG_LEVEL)

        # 文件处理器
        os.makedirs(Config.LOG_DIR, exist_ok=True)
        file_handler = logging.FileHandler(
            os.path.join(Config.LOG_DIR, Config.LOG_FILE)
        )
        file_handler.setLevel(Config.LOG_LEVEL)

        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(Config.LOG_LEVEL)

        # 格式化
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        cls._logger.addHandler(file_handler)
        cls._logger.addHandler(console_handler)

    @classmethod
    def info(cls, message: str):
        """信息日志"""
        cls.get_logger().info(message)

    @classmethod
    def warning(cls, message: str):
        """警告日志"""
        cls.get_logger().warning(message)

    @classmethod
    def error(cls, message: str):
        """错误日志"""
        cls.get_logger().error(message)

    @classmethod
    def debug(cls, message: str):
        """调试日志"""
        cls.get_logger().debug(message)
```

### 5.4 helpers.py

**职责**：辅助函数

**核心函数**：
```python
def format_date(date: Union[str, datetime]) -> str:
    """格式化日期"""
    pass

def format_price(price: float) -> str:
    """格式化价格"""
    pass

def format_volume(volume: float) -> str:
    """格式化成交量"""
    pass

def calculate_return(start_price: float, end_price: float) -> float:
    """计算收益率"""
    pass

def action_to_chinese(action: str) -> str:
    """将动作转换为中文"""
    mapping = {'buy': '买入', 'sell': '卖出', 'hold': '持有'}
    return mapping.get(action, action)

def color_for_action(action: str) -> str:
    """获取动作对应的颜色"""
    mapping = {'buy': 'red', 'sell': 'green', 'hold': 'gray'}
    return mapping.get(action, 'gray')

def is_trading_day(date: datetime) -> bool:
    """判断是否是交易日"""
    # 排除周末和节假日
    pass

def get_trading_days(start_date: datetime, end_date: datetime) -> List[datetime]:
    """获取日期范围内的交易日"""
    pass

def retry_on_failure(func, max_retries: int = 3, delay: float = 1.0):
    """失败重试装饰器"""
    pass
```

---

## 6. 数据流和API设计

### 6.1 数据更新API

```python
class DataUpdateService:
    """数据更新服务"""

    def __init__(self, fetcher: DataFetcher, storage: StockStorage):
        self.fetcher = fetcher
        self.storage = storage
        self.logger = Logger.get_logger()

    def full_update(self, progress_callback=None) -> dict:
        """完整数据更新"""
        results = {'success': True, 'errors': []}

        try:
            # 1. 更新板块数据
            if progress_callback:
                progress_callback(10, "获取板块列表...")
            self._update_sectors()

            # 2. 更新股票基本信息
            if progress_callback:
                progress_callback(30, "获取股票信息...")
            self._update_stock_info()

            # 3. 更新历史数据
            if progress_callback:
                progress_callback(70, "获取历史数据...")
            self._update_history_data()

            # 4. 计算技术指标
            if progress_callback:
                progress_callback(90, "计算技术指标...")
            self._calculate_indicators()

            # 5. 更新龙头股
            if progress_callback:
                progress_callback(95, "更新龙头股...")
            self._update_sector_leaders()

        except Exception as e:
            self.logger.error(f"数据更新失败: {str(e)}")
            results['success'] = False
            results['errors'].append(str(e))

        return results

    def incremental_update(self, progress_callback=None) -> dict:
        """增量数据更新"""
        # 只更新最新的交易日数据
        pass
```

### 6.2 预测服务API

```python
class PredictionService:
    """预测服务"""

    def __init__(self, ensemble: EnsemblePredictor, storage: StockStorage):
        self.ensemble = ensemble
        self.storage = storage

    def predict_stock(self, symbol: str) -> dict:
        """预测单只股票"""
        result = self.ensemble.predict(symbol)

        # 保存预测结果
        prediction = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'symbol': symbol,
            'short': result['short'],
            'medium': result['medium'],
            'long': result['long'],
            'ensemble': result['ensemble']
        }

        self.storage.save_predictions([prediction])

        return prediction

    def predict_sector_leaders(self, sector_id: str) -> List[dict]:
        """预测板块龙头股"""
        leaders = self.storage.get_sector_leaders(sector_id)
        results = []

        for leader in leaders:
            prediction = self.predict_stock(leader['symbol'])
            results.append({
                'symbol': leader['symbol'],
                'name': leader.get('name'),
                'score': leader['score'],
                'prediction': prediction
            })

        return results
```

---

## 7. 错误处理

### 7.1 异常定义

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

### 7.2 错误处理策略

- 数据获取失败：记录日志，返回空数据，用户可重试
- 存储失败：事务回滚，保持数据一致性
- 预测失败：返回默认值（持有），继续其他股票
- 模型训练失败：使用旧模型，记录错误

---

## 8. 性能优化

### 8.1 数据缓存

- 数据库查询结果缓存
- API请求结果缓存
- 预测结果缓存

### 8.2 批量操作

- 批量获取数据
- 批量插入数据库
- 批量计算指标

### 8.3 异步处理

- 耗时操作使用后台线程
- 更新进度通过回调通知

---

## 9. 测试策略

### 9.1 单元测试

- 每个模块的单元测试
- 测试覆盖率目标：70%

### 9.2 集成测试

- 模块间集成测试
- 端到端流程测试

### 9.3 性能测试

- 数据更新性能测试
- 预测计算性能测试

---

## 10. 扩展性设计

### 10.1 数据源扩展

- 定义统一的数据获取接口
- 支持切换不同数据源

### 10.2 模型扩展

- 定义统一的模型接口
- 支持添加新的预测模型
- 支持模型A/B测试

### 10.3 特征扩展

- 模块化的特征提取
- 支持添加新特征

---

## 11. 安全考虑

### 11.1 数据安全

- 数据库文件权限控制
- 敏感信息不记录日志

### 11.2 API安全

- 请求频率限制
- 超时处理

### 11.3 输入验证

- 所有用户输入验证
- SQL注入防护（使用参数化查询）