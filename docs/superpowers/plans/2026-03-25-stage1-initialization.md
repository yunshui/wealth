# Stage 1: Project Initialization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Set up the project foundation including directory structure, configuration, and utility classes.

**Architecture:** Create the foundational utility layer (config, logging, helpers, exceptions, cache) that all other modules will depend on. This establishes the project structure and development environment.

**Tech Stack:** Python 3.10+, standard library (logging, os, json, datetime, pickle, time), no external dependencies yet

---

## File Structure

**New files to create:**
```
wealth/
├── requirements.txt          # Python dependencies
├── app.py                    # Main Streamlit app
├── data/
│   ├── __init__.py
│   ├── database.py           # Database manager
│   ├── models.py             # Data models
│   ├── fetcher.py            # Data fetcher (stub)
│   └── storage.py            # Data storage (stub)
├── analysis/
│   ├── __init__.py
│   ├── indicators.py         # Indicators calculator (stub)
│   ├── sector.py             # Sector analyzer (stub)
│   └── features.py           # Feature engineer (stub)
├── prediction/
│   ├── __init__.py
│   ├── base.py               # Base predictor (stub)
│   ├── short_term.py         # Short term predictor (stub)
│   ├── medium_term.py        # Medium term predictor (stub)
│   ├── long_term.py          # Long term predictor (stub)
│   ├── ensemble.py           # Ensemble predictor (stub)
│   └── trainer.py            # Model trainer (stub)
├── ui/
│   ├── __init__.py
│   ├── pages.py              # Pages (stub)
│   ├── components.py         # Components (stub)
│   ├── charts.py             # Charts (stub)
│   └── layout.py             # Layout (stub)
├── utils/
│   ├── __init__.py
│   ├── config.py             # Configuration manager
│   ├── logger.py             # Logger
│   ├── helpers.py            # Helper functions
│   ├── exceptions.py         # Custom exceptions
│   └── cache.py              # Cache manager
├── models/                   # Model files directory
├── data/                     # Database directory
│   └── cache/                # Cache directory
└── logs/                     # Logs directory
```

---

## Task 1: Create Directory Structure

**Files:**
- Create: Multiple directories

- [ ] **Step 1: Create all directories**

Run: `mkdir -p data analysis prediction ui utils models data/cache logs tests`

Expected: All directories created

- [ ] **Step 2: Create all __init__.py files**

Run: `touch data/__init__.py analysis/__init__.py prediction/__init__.py ui/__init__.py utils/__init__.py`

Expected: All __init__.py files created

- [ ] **Step 3: Verify directory structure**

Run: `tree -L 2 -I '__pycache__|*.pyc'`

Expected: Directory tree shows all modules with __init__.py

- [ ] **Step 4: Commit**

```bash
git add .
git commit -m "feat: create project directory structure"
```

---

## Task 2: Create requirements.txt

**Files:**
- Create: `requirements.txt`

- [ ] **Step 1: Write requirements.txt**

```python
# Data
akshare>=1.12.0
pandas>=2.0.0
numpy>=1.24.0
pandas-ta>=0.3.14b

# Machine Learning
scikit-learn>=1.3.0

# Visualization
plotly>=5.18.0

# UI
streamlit>=1.28.0
```

- [ ] **Step 2: Verify requirements.txt content**

Run: `cat requirements.txt`

Expected: Shows all dependencies

- [ ] **Step 3: Commit**

```bash
git add requirements.txt
git commit -m "feat: add requirements.txt"
```

---

## Task 3: Create Config Class

**Files:**
- Create: `utils/config.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_config.py`:

```python
import pytest
from utils.config import Config


def test_config_db_path():
    """Test database path is correctly defined"""
    assert Config.DB_PATH == 'data/stock_data.db'


def test_config_data_start_date():
    """Test data start date is correctly defined"""
    assert Config.DATA_START_DATE == '2018-01-01'


def test_config_ensemble_weights():
    """Test ensemble weights sum to 1"""
    total = sum(Config.ENSEMBLE_WEIGHTS.values())
    assert abs(total - 1.0) < 0.01


def test_config_model_paths():
    """Test model paths are correctly constructed"""
    assert 'short_term' in Config.SHORT_MODEL_FILE
    assert 'medium_term' in Config.MEDIUM_MODEL_FILE
    assert 'long_term' in Config.LONG_MODEL_FILE
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_config.py -v`

Expected: FAIL with "ModuleNotFoundError: No module named 'utils.config'"

- [ ] **Step 3: Write minimal implementation**

```python
"""Configuration management module."""


class Config:
    """Application configuration."""

    # Database
    DB_PATH = 'data/stock_data.db'

    # Data
    DATA_START_DATE = '2018-01-01'  # 7 years of historical data
    DATA_UPDATE_TIME = '15:30'  # Update after market close

    # Sectors
    MAIN_SECTORS = [
        '科技', '医药', '消费', '金融', '制造',
        '能源', '材料', '公用', '地产', '交运'
    ]
    LEADER_COUNT = 20  # Top 20 leaders per sector

    # Prediction
    SHORT_TERM_HORIZON = 5      # 5 days
    MEDIUM_TERM_HORIZON = 60    # 60 days (2 months)
    LONG_TERM_HORIZON = 120     # 120 days (4 months)

    ENSEMBLE_WEIGHTS = {
        'short': 0.3,
        'medium': 0.4,
        'long': 0.3
    }

    # Models
    MODEL_DIR = 'models'
    SHORT_MODEL_FILE = 'short_term.pkl'
    MEDIUM_MODEL_FILE = 'medium_term.pkl'
    LONG_MODEL_FILE = 'long_term.pkl'

    # Logging
    LOG_DIR = 'logs'
    LOG_FILE = 'app.log'
    LOG_LEVEL = 'INFO'

    # Cache
    CACHE_DIR = 'data/cache'
    CACHE_EXPIRE = 3600  # 1 hour

    @classmethod
    def get_db_path(cls) -> str:
        """Get database file path."""
        return cls.DB_PATH

    @classmethod
    def get_model_path(cls, model_type: str) -> str:
        """Get model file path.

        Args:
            model_type: 'short', 'medium', or 'long'

        Returns:
            Full path to model file
        """
        import os
        model_file = f"{model_type}_term.pkl"
        return os.path.join(cls.MODEL_DIR, model_file)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_config.py -v`

Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add utils/config.py tests/test_config.py
git commit -m "feat: add Config class with application settings"
```

---

## Task 4: Create Logger Class

**Files:**
- Create: `utils/logger.py`

- [ ] **Step 1: Write the failing test**

Add to `tests/test_config.py`:

```python
from utils.logger import Logger


def test_logger_get_instance():
    """Test logger returns a singleton instance"""
    logger1 = Logger.get_logger()
    logger2 = Logger.get_logger()
    assert logger1 is logger2


def test_logger_has_handlers():
    """Test logger has file and console handlers"""
    logger = Logger.get_logger()
    assert len(logger.handlers) >= 2
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_config.py::test_logger_get_instance -v`

Expected: FAIL with "ModuleNotFoundError: No module named 'utils.logger'"

- [ ] **Step 3: Write minimal implementation**

```python
"""Logging module for the application."""

import logging
import os
from utils.config import Config


class Logger:
    """Application logger manager.

    Provides a singleton logger instance with file and console handlers.
    """

    _logger: logging.Logger = None
    _setup_complete: bool = False

    @classmethod
    def get_logger(cls) -> logging.Logger:
        """Get the logger singleton instance.

        Returns:
            Logger instance configured with file and console handlers
        """
        if cls._logger is None:
            cls._setup_logger()
        return cls._logger

    @classmethod
    def _setup_logger(cls) -> None:
        """Setup logger with file and console handlers."""
        if cls._setup_complete:
            return

        cls._logger = logging.getLogger('wealth')
        cls._logger.setLevel(Config.LOG_LEVEL)

        # Remove existing handlers to avoid duplicates
        cls._logger.handlers.clear()

        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # File handler
        os.makedirs(Config.LOG_DIR, exist_ok=True)
        log_file_path = os.path.join(Config.LOG_DIR, Config.LOG_FILE)
        file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
        file_handler.setLevel(Config.LOG_LEVEL)
        file_handler.setFormatter(formatter)
        cls._logger.addHandler(file_handler)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(Config.LOG_LEVEL)
        console_handler.setFormatter(formatter)
        cls._logger.addHandler(console_handler)

        cls._setup_complete = True

    @classmethod
    def info(cls, message: str) -> None:
        """Log an info message."""
        cls.get_logger().info(message)

    @classmethod
    def warning(cls, message: str) -> None:
        """Log a warning message."""
        cls.get_logger().warning(message)

    @classmethod
    def error(cls, message: str) -> None:
        """Log an error message."""
        cls.get_logger().error(message)

    @classmethod
    def debug(cls, message: str) -> None:
        """Log a debug message."""
        cls.get_logger().debug(message)

    @classmethod
    def exception(cls, message: str) -> None:
        """Log an exception with traceback."""
        cls.get_logger().exception(message)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_config.py::test_logger_get_instance tests/test_config.py::test_logger_has_handlers -v`

Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add utils/logger.py tests/test_config.py
git commit -m "feat: add Logger class with file and console handlers"
```

---

## Task 5: Create Helper Functions

**Files:**
- Create: `utils/helpers.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_helpers.py`:

```python
import pytest
from datetime import datetime
from utils.helpers import (
    format_date, format_price, format_volume,
    calculate_return, action_to_chinese, color_for_action
)


def test_format_date():
    """Test date formatting"""
    dt = datetime(2024, 1, 15)
    assert format_date(dt) == '2024-01-15'
    assert format_date('2024-01-15') == '2024-01-15'


def test_format_price():
    """Test price formatting"""
    assert format_price(12.3456) == '12.35'
    assert format_price(100) == '100.00'


def test_format_volume():
    """Test volume formatting"""
    assert format_volume(1000) == '1000'
    assert format_volume(10000) == '1.00万'
    assert format_volume(100000000) == '1.00亿'


def test_calculate_return():
    """Test return calculation"""
    assert calculate_return(100, 110) == 0.1
    assert calculate_return(110, 100) == -0.09090909090909091


def test_action_to_chinese():
    """Test action to Chinese conversion"""
    assert action_to_chinese('buy') == '买入'
    assert action_to_chinese('sell') == '卖出'
    assert action_to_chinese('hold') == '持有'
    assert action_to_chinese('unknown') == 'unknown'


def test_color_for_action():
    """Test color mapping for actions"""
    assert color_for_action('buy') == 'red'
    assert color_for_action('sell') == 'green'
    assert color_for_action('hold') == 'gray'
    assert color_for_action('unknown') == 'gray'
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_helpers.py -v`

Expected: FAIL with "ModuleNotFoundError: No module named 'utils.helpers'"

- [ ] **Step 3: Write minimal implementation**

```python
"""Helper functions module."""

from datetime import datetime
from typing import Union


def format_date(date: Union[str, datetime]) -> str:
    """Format date to YYYY-MM-DD string.

    Args:
        date: Date as string or datetime object

    Returns:
        Formatted date string
    """
    if isinstance(date, str):
        return date
    return date.strftime('%Y-%m-%d')


def format_price(price: float) -> str:
    """Format price to 2 decimal places.

    Args:
        price: Price value

    Returns:
        Formatted price string
    """
    return f"{price:.2f}"


def format_volume(volume: float) -> str:
    """Format volume with units.

    Args:
        volume: Volume value

    Returns:
        Formatted volume string with unit
    """
    if volume >= 100000000:  # 亿
        return f"{volume / 100000000:.2f}亿"
    elif volume >= 10000:  # 万
        return f"{volume / 10000:.2f}万"
    else:
        return f"{volume:.0f}"


def calculate_return(start_price: float, end_price: float) -> float:
    """Calculate return rate.

    Args:
        start_price: Starting price
        end_price: Ending price

    Returns:
        Return rate (e.g., 0.1 for 10%)
    """
    if start_price == 0:
        return 0.0
    return (end_price - start_price) / start_price


def action_to_chinese(action: str) -> str:
    """Convert action to Chinese.

    Args:
        action: Action ('buy', 'sell', 'hold')

    Returns:
        Chinese text for the action
    """
    mapping = {
        'buy': '买入',
        'sell': '卖出',
        'hold': '持有'
    }
    return mapping.get(action, action)


def color_for_action(action: str) -> str:
    """Get color for an action (Chinese stock market: red = up, green = down).

    Args:
        action: Action ('buy', 'sell', 'hold')

    Returns:
        Color name
    """
    mapping = {
        'buy': 'red',
        'sell': 'green',
        'hold': 'gray'
    }
    return mapping.get(action, 'gray')
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_helpers.py -v`

Expected: PASS (7 passed)

- [ ] **Step 5: Commit**

```bash
git add utils/helpers.py tests/test_helpers.py
git commit -m "feat: add helper functions for formatting and conversion"
```

---

## Task 6: Create Custom Exception Classes

**Files:**
- Create: `utils/exceptions.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_exceptions.py`:

```python
import pytest
from utils.exceptions import (
    WealthException,
    DataFetchException,
    StorageException,
    PredictionException,
    ModelException
)


def test_wealth_exception():
    """Test base exception can be created"""
    exc = WealthException("Test error")
    assert str(exc) == "Test error"
    assert isinstance(exc, Exception)


def test_data_fetch_exception():
    """Test DataFetchException inherits from WealthException"""
    exc = DataFetchException("Fetch failed")
    assert isinstance(exc, WealthException)
    assert isinstance(exc, Exception)


def test_storage_exception():
    """Test StorageException inherits from WealthException"""
    exc = StorageException("Storage failed")
    assert isinstance(exc, WealthException)


def test_prediction_exception():
    """Test PredictionException inherits from WealthException"""
    exc = PredictionException("Prediction failed")
    assert isinstance(exc, WealthException)


def test_model_exception():
    """Test ModelException inherits from WealthException"""
    exc = ModelException("Model failed")
    assert isinstance(exc, WealthException)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_exceptions.py -v`

Expected: FAIL with "ModuleNotFoundError: No module named 'utils.exceptions'"

- [ ] **Step 3: Write minimal implementation**

```python
"""Custom exception classes for the application."""


class WealthException(Exception):
    """Base exception for the application."""

    def __init__(self, message: str, error_code: str = None):
        """Initialize exception.

        Args:
            message: Error message
            error_code: Optional error code (e.g., 'E0001')
        """
        super().__init__(message)
        self.error_code = error_code

    def __str__(self) -> str:
        if self.error_code:
            return f"[{self.error_code}] {super().__str__()}"
        return super().__str__()


class DataFetchException(WealthException):
    """Exception raised when data fetching fails."""

    def __init__(self, message: str = "Data fetch failed"):
        super().__init__(message, error_code="E0001")


class StorageException(WealthException):
    """Exception raised when data storage fails."""

    def __init__(self, message: str = "Storage operation failed"):
        super().__init__(message, error_code="E0003")


class PredictionException(WealthException):
    """Exception raised when prediction fails."""

    def __init__(self, message: str = "Prediction failed"):
        super().__init__(message, error_code="E0006")


class ModelException(WealthException):
    """Exception raised when model operation fails."""

    def __init__(self, message: str = "Model operation failed"):
        super().__init__(message, error_code="E0004")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_exceptions.py -v`

Expected: PASS (5 passed)

- [ ] **Step 5: Commit**

```bash
git add utils/exceptions.py tests/test_exceptions.py
git commit -m "feat: add custom exception classes"
```

---

## Task 7: Create Cache Manager

**Files:**
- Create: `utils/cache.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_cache.py`:

```python
import pytest
import tempfile
import os
from utils.cache import CacheManager


def test_cache_manager_creation(tmp_path):
    """Test CacheManager can be created"""
    cache_dir = tmp_path / "cache"
    cache = CacheManager(str(cache_dir))
    assert cache.cache_dir == str(cache_dir)
    assert os.path.exists(cache_dir)


def test_cache_set_and_get(tmp_path):
    """Test cache can set and get values"""
    cache_dir = tmp_path / "cache"
    cache = CacheManager(str(cache_dir))

    cache.set("test_key", {"value": 42})
    result = cache.get("test_key")

    assert result is not None
    assert result["value"] == 42


def test_cache_expire(tmp_path):
    """Test cache respects expiration time"""
    import time

    cache_dir = tmp_path / "cache"
    cache = CacheManager(str(cache_dir))

    cache.set("test_key", {"value": 42})
    # Set a very short expiration
    result = cache.get("test_key", expire=0.1)  # 0.1 seconds

    assert result is not None

    # Wait for expiration
    time.sleep(0.15)

    result = cache.get("test_key", expire=0.1)
    assert result is None


def test_cache_clear(tmp_path):
    """Test cache can be cleared"""
    cache_dir = tmp_path / "cache"
    cache = CacheManager(str(cache_dir))

    cache.set("test_key", {"value": 42})
    assert cache.get("test_key") is not None

    cache.clear("test_key")
    assert cache.get("test_key") is None


def test_cache_clear_all(tmp_path):
    """Test cache can clear all keys"""
    cache_dir = tmp_path / "cache"
    cache = CacheManager(str(cache_dir))

    cache.set("test_key1", {"value": 1})
    cache.set("test_key2", {"value": 2})

    cache.clear()  # Clear all

    assert cache.get("test_key1") is None
    assert cache.get("test_key2") is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_cache.py -v`

Expected: FAIL with "ModuleNotFoundError: No module named 'utils.cache'"

- [ ] **Step 3: Write minimal implementation**

```python
"""Cache management module."""

import hashlib
import os
import pickle
import time
from functools import lru_cache
from utils.config import Config
from utils.logger import Logger


class CacheManager:
    """Cache manager for storing and retrieving cached data.

    Provides file-based caching with expiration support.
    """

    def __init__(self, cache_dir: str = None):
        """Initialize cache manager.

        Args:
            cache_dir: Directory for cache files. If None, uses Config.CACHE_DIR
        """
        self.cache_dir = cache_dir or Config.CACHE_DIR
        os.makedirs(self.cache_dir, exist_ok=True)

    def get(self, key: str, expire: int = None) -> any:
        """Get cached value.

        Args:
            key: Cache key
            expire: Expiration time in seconds. If None, uses Config.CACHE_EXPIRE

        Returns:
            Cached value, or None if not found or expired
        """
        if expire is None:
            expire = Config.CACHE_EXPIRE

        cache_file = self._get_cache_file(key)
        if not os.path.exists(cache_file):
            return None

        try:
            with open(cache_file, 'rb') as f:
                data = pickle.load(f)

            if time.time() - data['timestamp'] > expire:
                os.remove(cache_file)
                return None

            return data['value']
        except (pickle.PickleError, EOFError, KeyError):
            # Corrupted cache file, remove it
            if os.path.exists(cache_file):
                os.remove(cache_file)
            return None

    def set(self, key: str, value: any) -> None:
        """Set cached value.

        Args:
            key: Cache key
            value: Value to cache
        """
        cache_file = self._get_cache_file(key)
        with open(cache_file, 'wb') as f:
            pickle.dump({
                'value': value,
                'timestamp': time.time()
            }, f)

    def clear(self, key: str = None) -> None:
        """Clear cached value.

        Args:
            key: Cache key to clear. If None, clears all cache
        """
        if key:
            cache_file = self._get_cache_file(key)
            if os.path.exists(cache_file):
                os.remove(cache_file)
        else:
            for file in os.listdir(self.cache_dir):
                if file.endswith('.cache'):
                    os.remove(os.path.join(self.cache_dir, file))

    def _get_cache_file(self, key: str) -> str:
        """Get cache file path for a key.

        Args:
            key: Cache key

        Returns:
            Cache file path
        """
        # Hash the key to create a valid filename
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{key_hash}.cache")


@lru_cache(maxsize=100)
def cached_get(cache_manager: CacheManager, key: str) -> any:
    """LRU cached version of cache get (in-memory cache).

    Args:
        cache_manager: CacheManager instance
        key: Cache key

    Returns:
        Cached value
    """
    return cache_manager.get(key)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_cache.py -v`

Expected: PASS (6 passed)

- [ ] **Step 5: Commit**

```bash
git add utils/cache.py tests/test_cache.py
git commit -m "feat: add CacheManager with file-based caching"
```

---

## Task 8: Create Data Models

**Files:**
- Create: `data/models.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_models.py`:

```python
import pytest
from data.models import Stock, StockData, Prediction, Sector, SectorLeader


def test_stock_creation():
    """Test Stock dataclass creation"""
    stock = Stock(
        symbol='000001.SZ',
        name='平安银行',
        industry='银行',
        sector='金融',
        market_cap=2345.6
    )
    assert stock.symbol == '000001.SZ'
    assert stock.name == '平安银行'
    assert stock.market_cap == 2345.6


def test_stock_data_creation():
    """Test StockData dataclass creation"""
    data = StockData(
        date='2024-01-15',
        symbol='000001.SZ',
        open=12.0,
        high=12.5,
        low=11.8,
        close=12.3,
        volume=1000000,
        ma5=12.1,
        ma10=11.9
    )
    assert data.date == '2024-01-15'
    assert data.close == 12.3
    assert data.ma5 == 12.1


def test_prediction_creation():
    """Test Prediction dataclass creation"""
    pred = Prediction(
        date='2024-01-15',
        symbol='000001.SZ',
        horizon='short',
        action='buy',
        confidence=0.78,
        reasoning=['MACD金叉', '量价配合'],
        model_version='1.0'
    )
    assert pred.horizon == 'short'
    assert pred.action == 'buy'
    assert pred.confidence == 0.78
    assert len(pred.reasoning) == 2


def test_sector_creation():
    """Test Sector dataclass creation"""
    sector = Sector(
        sector_id='industry_001',
        sector_name='银行',
        sector_type='industry'
    )
    assert sector.sector_type == 'industry'


def test_sector_leader_creation():
    """Test SectorLeader dataclass creation"""
    leader = SectorLeader(
        sector_id='industry_001',
        sector_name='银行',
        symbol='000001.SZ',
        score=0.85,
        rank=1,
        market_cap_rank=1,
        volume_rank=3
    )
    assert leader.rank == 1
    assert leader.market_cap_rank == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_models.py -v`

Expected: FAIL with "ModuleNotFoundError: No module named 'data.models'"

- [ ] **Step 3: Write minimal implementation**

```python
"""Data models for the stock prediction system."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Stock:
    """Stock basic information."""

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
    """Stock historical data with technical indicators."""

    date: str
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    amount: Optional[float] = None
    # Technical indicators
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
    """Prediction result for a stock."""

    date: str
    symbol: str
    horizon: str  # 'short', 'medium', 'long'
    action: str  # 'buy', 'sell', 'hold'
    confidence: float  # 0-1
    reasoning: List[str]
    model_version: str


@dataclass
class Sector:
    """Sector information."""

    sector_id: str
    sector_name: str
    sector_type: str  # 'industry' or 'concept'
    leader_count: int = 0


@dataclass
class SectorLeader:
    """Sector leading stock."""

    sector_id: str
    sector_name: str
    symbol: str
    score: float
    rank: int
    market_cap_rank: int
    volume_rank: int
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_models.py -v`

Expected: PASS (5 passed)

- [ ] **Step 5: Commit**

```bash
git add data/models.py tests/test_models.py
git commit -m "feat: add data models for stocks, predictions, and sectors"
```

---

## Task 9: Create Database Manager

**Files:**
- Create: `data/database.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_database.py`:

```python
import pytest
import os
import tempfile
from data.database import DatabaseManager


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    yield db_path
    os.unlink(db_path)


def test_database_manager_creation(temp_db):
    """Test DatabaseManager can be created"""
    db = DatabaseManager(db_path)
    assert db is not None
    assert db.db_path == temp_db
    db.close()


def test_database_manager_create_tables(temp_db):
    """Test tables can be created"""
    db = DatabaseManager(temp_db)
    db.create_tables()
    db.close()

    # Verify tables exist
    import sqlite3
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()

    expected_tables = ['stocks', 'sectors', 'stock_data', 'predictions', 'sector_leaders', 'model_params']
    for table in expected_tables:
        assert table in tables


def test_database_manager_check_exists(temp_db):
    """Test database existence check"""
    db = DatabaseManager(temp_db)

    # Initially should not exist
    assert not db.check_database_exists()

    # Create tables
    db.create_tables()

    # Now should exist
    assert db.check_database_exists()

    db.close()


def test_database_manager_get_connection(temp_db):
    """Test getting database connection"""
    db = DatabaseManager(temp_db)
    conn = db.get_connection()
    assert conn is not None
    conn.close()
    db.close()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_database.py -v`

Expected: FAIL with "ModuleNotFoundError: No module named 'data.database'"

- [ ] **Step 3: Write minimal implementation**

```python
"""Database manager module."""

import sqlite3
from typing import Optional
from utils.config import Config
from utils.logger import Logger


class DatabaseManager:
    """Manages SQLite database connection and table creation."""

    def __init__(self, db_path: str = None):
        """Initialize database manager.

        Args:
            db_path: Path to database file. If None, uses Config.DB_PATH
        """
        self.db_path = db_path or Config.get_db_path()
        self._conn: Optional[sqlite3.Connection] = None

    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection.

        Returns:
            SQLite connection object
        """
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def close(self) -> None:
        """Close database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    def check_database_exists(self) -> bool:
        """Check if database file exists and has tables.

        Returns:
            True if database exists with tables, False otherwise
        """
        import os
        if not os.path.exists(self.db_path):
            return False

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table'")
        count = cursor.fetchone()[0]
        return count > 0

    def create_tables(self) -> None:
        """Create all required database tables."""
        Logger.info("Creating database tables...")

        conn = self.get_connection()
        cursor = conn.cursor()

        # Create sectors table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sectors (
                sector_id TEXT PRIMARY KEY,
                sector_name TEXT NOT NULL,
                sector_type TEXT NOT NULL,
                leader_count INTEGER DEFAULT 0,
                updated_at TEXT
            )
        ''')

        # Create stocks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stocks (
                symbol TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                industry TEXT,
                sector TEXT,
                market_cap REAL,
                pe_ratio REAL,
                pb_ratio REAL,
                list_date TEXT,
                updated_at TEXT
            )
        ''')

        # Create stock_data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_data (
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
            )
        ''')

        # Create predictions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                symbol TEXT NOT NULL,
                horizon TEXT NOT NULL,
                action TEXT NOT NULL,
                confidence REAL,
                reasoning TEXT,
                model_version TEXT,
                created_at TEXT,
                FOREIGN KEY (symbol) REFERENCES stocks(symbol)
            )
        ''')

        # Create sector_leaders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sector_leaders (
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
            )
        ''')

        # Create model_params table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_params (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT NOT NULL,
                model_version TEXT NOT NULL,
                params TEXT,
                accuracy REAL,
                trained_at TEXT,
                is_active INTEGER DEFAULT 1
            )
        ''')

        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sectors_type ON sectors(sector_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_stocks_industry ON stocks(industry)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_stocks_sector ON stocks(sector)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_stock_data_date ON stock_data(date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_stock_data_symbol ON stock_data(symbol)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_stock_data_date_symbol ON stock_data(date, symbol)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_predictions_date ON predictions(date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_predictions_symbol ON predictions(symbol)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_predictions_date_symbol_horizon ON predictions(date, symbol, horizon)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sector_leaders_sector ON sector_leaders(sector_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_model_params_name ON model_params(model_name)')

        conn.commit()
        Logger.info("Database tables created successfully")

    def get_last_update_date(self) -> Optional[str]:
        """Get the last update date from stock_data.

        Returns:
            Last date string in YYYY-MM-DD format, or None if no data
        """
        if not self.check_database_exists():
            return None

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(date) FROM stock_data")
        result = cursor.fetchone()[0]
        return result
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_database.py -v`

Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add data/database.py tests/test_database.py
git commit -m "feat: add DatabaseManager with table creation"
```

---

## Task 10: Create Placeholder Modules

**Files:**
- Create: `data/fetcher.py`, `data/storage.py`, `analysis/indicators.py`, `analysis/sector.py`, `analysis/features.py`, `prediction/base.py`, `prediction/short_term.py`, `prediction/medium_term.py`, `prediction/long_term.py`, `prediction/ensemble.py`, `prediction/trainer.py`, `ui/pages.py`, `ui/components.py`, `ui/charts.py`, `ui/layout.py`

- [ ] **Step 1: Write placeholder implementations**

Create `data/fetcher.py`:

```python
"""Data fetcher module - placeholder for akshare integration."""
import pandas as pd
from utils.logger import Logger
from utils.exceptions import DataFetchException


class DataFetcher:
    """Data fetcher for stock market data."""

    def __init__(self):
        """Initialize data fetcher."""
        Logger.warning("DataFetcher is a placeholder - implement akshare integration in Stage 2")

    def get_industry_sectors(self) -> pd.DataFrame:
        """Get industry sector list."""
        raise DataFetchException("get_industry_sectors not implemented yet")

    def get_concept_sectors(self) -> pd.DataFrame:
        """Get concept sector list."""
        raise DataFetchException("get_concept_sectors not implemented yet")

    def get_sector_stocks(self, sector_name: str, sector_type: str) -> pd.DataFrame:
        """Get sector stocks."""
        raise DataFetchException("get_sector_stocks not implemented yet")

    def get_stock_info(self, symbol: str) -> dict:
        """Get stock info."""
        raise DataFetchException("get_stock_info not implemented yet")

    def get_stock_history(self, symbol: str, start_date: str = None) -> pd.DataFrame:
        """Get stock history."""
        raise DataFetchException("get_stock_history not implemented yet")

    def get_stock_latest(self, symbol: str) -> dict:
        """Get stock latest."""
        raise DataFetchException("get_stock_latest not implemented yet")
```

Create `data/storage.py`:

```python
"""Data storage module - placeholder."""
from utils.logger import Logger
from utils.exceptions import StorageException


class StockStorage:
    """Stock data storage manager."""

    def __init__(self, db_manager):
        """Initialize storage manager."""
        self.db_manager = db_manager
        Logger.warning("StockStorage is a placeholder - implement in Stage 2")

    def save_sector(self, sector_data: dict) -> bool:
        raise StorageException("save_sector not implemented yet")

    def save_stock(self, stock_data: dict) -> bool:
        raise StorageException("save_stock not implemented yet")

    def save_stock_data(self, df) -> bool:
        raise StorageException("save_stock_data not implemented yet")

    def get_stock(self, symbol: str) -> dict:
        raise StorageException("get_stock not implemented yet")

    def get_stock_data(self, symbol: str, start_date: str = None, end_date: str = None):
        raise StorageException("get_stock_data not implemented yet")

    def save_prediction(self, prediction_data: dict) -> bool:
        raise StorageException("save_prediction not implemented yet")

    def get_prediction(self, symbol: str, horizon: str, date: str = None) -> dict:
        raise StorageException("get_prediction not implemented yet")

    def save_sector_leaders(self, sector_id: str, leaders: list) -> bool:
        raise StorageException("save_sector_leaders not implemented yet")

    def get_sector_leaders(self, sector_id: str) -> list:
        raise StorageException("get_sector_leaders not implemented yet")
```

Create `analysis/indicators.py`:

```python
"""Technical indicators module - placeholder."""
import pandas as pd
from utils.logger import Logger


class IndicatorCalculator:
    """Technical indicator calculator."""

    def calculate_all(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all technical indicators."""
        Logger.warning("IndicatorCalculator is a placeholder - implement in Stage 2")
        return df
```

Create `analysis/sector.py`:

```python
"""Sector analysis module - placeholder."""
from utils.logger import Logger


class SectorAnalyzer:
    """Sector analyzer for identifying leading stocks."""

    def __init__(self, storage):
        """Initialize sector analyzer."""
        self.storage = storage
        Logger.warning("SectorAnalyzer is a placeholder - implement in Stage 2")

    def identify_leaders(self, sector_id: str, limit: int = 20) -> list:
        raise NotImplementedError

    def update_all_sector_leaders(self):
        raise NotImplementedError
```

Create `analysis/features.py`:

```python
"""Feature engineering module - placeholder."""
import numpy as np
from utils.logger import Logger


class FeatureEngineer:
    """Feature engineer for prediction models."""

    @staticmethod
    def extract_short_term_features(df, lookback: int = 20) -> np.ndarray:
        """Extract short-term features."""
        Logger.warning("FeatureEngineer is a placeholder - implement in Stage 3")
        raise NotImplementedError

    @staticmethod
    def extract_medium_term_features(df, lookback: int = 120) -> np.ndarray:
        """Extract medium-term features."""
        Logger.warning("FeatureEngineer is a placeholder - implement in Stage 3")
        raise NotImplementedError

    @staticmethod
    def extract_long_term_features(df) -> np.ndarray:
        """Extract long-term features."""
        Logger.warning("FeatureEngineer is a placeholder - implement in Stage 3")
        raise NotImplementedError

    @staticmethod
    def create_labels(df, horizon: int) -> np.ndarray:
        """Create labels for prediction."""
        Logger.warning("FeatureEngineer is a placeholder - implement in Stage 3")
        raise NotImplementedError

    @staticmethod
    def normalize_features(X: np.ndarray) -> np.ndarray:
        """Normalize features."""
        Logger.warning("FeatureEngineer is a placeholder - implement in Stage 3")
        raise NotImplementedError
```

Create `prediction/base.py`:

```python
"""Base predictor module - placeholder."""
import numpy as np
from utils.logger import Logger
from utils.exceptions import ModelException


class BasePredictor:
    """Base class for prediction models."""

    def __init__(self):
        """Initialize predictor."""
        self.model = None
        self.is_trained = False

    def train(self, X: np.ndarray, y: np.ndarray) -> None:
        """Train the model."""
        Logger.warning("BasePredictor.train is a placeholder - implement in Stage 3")
        raise ModelException("train not implemented yet")

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions."""
        Logger.warning("BasePredictor.predict is a placeholder - implement in Stage 3")
        raise ModelException("predict not implemented yet")

    def save_model(self, path: str) -> None:
        raise ModelException("save_model not implemented yet")

    def load_model(self, path: str) -> None:
        raise ModelException("load_model not implemented yet")

    def is_trained(self) -> bool:
        """Check if model is trained."""
        return self.is_trained
```

Create `prediction/short_term.py`:

```python
"""Short-term predictor module - placeholder."""
from .base import BasePredictor
from utils.logger import Logger
from utils.exceptions import ModelException


class ShortTermPredictor(BasePredictor):
    """Short-term (1-5 days) prediction model."""

    def __init__(self):
        super().__init__()
        Logger.warning("ShortTermPredictor is a placeholder - implement in Stage 3")

    def generate_reasoning(self, X, prediction, proba) -> list:
        Logger.warning("generate_reasoning is a placeholder - implement in Stage 3")
        raise ModelException("generate_reasoning not implemented yet")
```

Create `prediction/medium_term.py`:

```python
"""Medium-term predictor module - placeholder."""
from .base import BasePredictor
from utils.logger import Logger
from utils.exceptions import ModelException


class MediumTermPredictor(BasePredictor):
    """Medium-term (1-3 months) prediction model."""

    def __init__(self):
        super().__init__()
        Logger.warning("MediumTermPredictor is a placeholder - implement in Stage 3")

    def generate_reasoning(self, X, prediction, proba) -> list:
        Logger.warning("generate_reasoning is a placeholder - implement in Stage 3")
        raise ModelException("generate_reasoning not implemented yet")
```

Create `prediction/long_term.py`:

```python
"""Long-term predictor module - placeholder."""
from .base import BasePredictor
from utils.logger import Logger
from utils.exceptions import ModelException


class LongTermPredictor(BasePredictor):
    """Long-term (3+ months) prediction model."""

    def __init__(self):
        super().__init__()
        Logger.warning("LongTermPredictor is a placeholder - implement in Stage 3")

    def generate_reasoning(self, X, prediction, proba) -> list:
        Logger.warning("generate_reasoning is a placeholder - implement in Stage 3")
        raise ModelException("generate_reasoning not implemented yet")
```

Create `prediction/ensemble.py`:

```python
"""Ensemble predictor module - placeholder."""
from utils.logger import Logger


class EnsemblePredictor:
    """Ensemble predictor combining short, medium, and long-term predictions."""

    def __init__(self):
        Logger.warning("EnsemblePredictor is a placeholder - implement in Stage 3")

    def predict(self, symbol: str) -> dict:
        Logger.warning("EnsemblePredictor.predict is a placeholder - implement in Stage 3")
        raise NotImplementedError

    def batch_predict(self, symbols: list) -> dict:
        Logger.warning("EnsemblePredictor.batch_predict is a placeholder - implement in Stage 3")
        raise NotImplementedError
```

Create `prediction/trainer.py`:

```python
"""Model trainer module - placeholder."""
from utils.logger import Logger


class ModelTrainer:
    """Model trainer for prediction models."""

    def __init__(self, storage):
        """Initialize model trainer."""
        self.storage = storage
        Logger.warning("ModelTrainer is a placeholder - implement in Stage 3")

    def train_short_term_model(self) -> float:
        Logger.warning("train_short_term_model is a placeholder - implement in Stage 3")
        raise NotImplementedError

    def train_medium_term_model(self) -> float:
        Logger.warning("train_medium_term_model is a placeholder - implement in Stage 3")
        raise NotImplementedError

    def train_long_term_model(self) -> float:
        Logger.warning("train_long_term_model is a placeholder - implement in Stage 3")
        raise NotImplementedError

    def train_all_models(self) -> dict:
        Logger.warning("train_all_models is a placeholder - implement in Stage 3")
        raise NotImplementedError
```

Create `ui/pages.py`:

```python
"""UI pages module - placeholder for Streamlit pages."""
from utils.logger import Logger


def render_home_page():
    """Render home page."""
    Logger.warning("render_home_page is a placeholder - implement in Stage 4")


def render_stock_detail_page(symbol):
    """Render stock detail page."""
    Logger.warning("render_stock_detail_page is a placeholder - implement in Stage 5")
```

Create `ui/components.py`:

```python
"""UI components module - placeholder."""
from utils.logger import Logger


def render_prediction_card(prediction, title):
    """Render prediction card component."""
    Logger.warning("render_prediction_card is a placeholder - implement in Stage 4")
```

Create `ui/charts.py`:

```python
"""UI charts module - placeholder."""
from utils.logger import Logger


def create_candlestick_chart(df):
    """Create candlestick chart."""
    Logger.warning("create_candlestick_chart is a placeholder - implement in Stage 4")
    raise NotImplementedError
```

Create `ui/layout.py`:

```python
"""UI layout module - placeholder."""
from utils.logger import Logger


def render_sidebar():
    """Render sidebar layout."""
    Logger.warning("render_sidebar is a placeholder - implement in Stage 4")
```

- [ ] **Step 2: Verify all files created**

Run: `find . -name "*.py" -path "./data/*" -o -path "./analysis/*" -o -path "./prediction/*" -o -path "./ui/*" | grep -v __pycache__ | sort`

Expected: Shows all module files created

- [ ] **Step 3: Commit**

```bash
git add data/fetcher.py data/storage.py analysis/ prediction/ ui/
git commit -m "feat: add placeholder modules for Stage 2-5"
```

---

## Task 11: Create Basic Streamlit App

**Files:**
- Create: `app.py`

- [ ] **Step 1: Write basic Streamlit app**

```python
"""Main Streamlit application."""

import streamlit as st
from utils.config import Config
from utils.logger import Logger
from data.database import DatabaseManager


def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="人机协同A股智能投资决策系统",
        page_icon="📈",
        layout="wide"
    )

    st.title("📈 人机协同A股智能投资决策系统")

    # Initialize logger
    Logger.info("Application started")

    # Initialize database
    db = DatabaseManager()
    if not db.check_database_exists():
        st.warning("首次使用，请先点击下方按钮初始化数据库")
        if st.button("初始化数据库", type="primary"):
            db.create_tables()
            st.success("数据库初始化完成！")
    else:
        st.success("数据库已就绪")
        last_update = db.get_last_update_date()
        if last_update:
            st.info(f"最后更新日期: {last_update}")
        else:
            st.warning("数据库为空，请执行数据更新")

    # Sidebar
    with st.sidebar:
        st.header("功能菜单")
        if st.button("板块总览"):
            st.rerun()
        if st.button("更新数据"):
            st.warning("数据更新功能将在Stage 2实现")
        if st.button("训练模型"):
            st.warning("模型训练功能将在Stage 3实现")

    # Main content
    st.subheader("板块总览")
    st.info("板块总览功能将在Stage 4实现")

    db.close()


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Test the application**

Run: `streamlit run app.py`

Expected: Streamlit launches and shows the basic app

- [ ] **Step 3: Commit**

```bash
git add app.py
git commit -m "feat: add basic Streamlit application with database initialization"
```

---

## Task 12: Final Verification and Documentation

**Files:**
- Modify: `README.md`, `CLAUDE.md`

- [ ] **Step 1: Create README.md**

```markdown
# 人机协同A股智能投资决策系统

基于7年A股历史数据，通过AI模型对板块龙头股进行短中长期预测，为个人投资者提供买卖操作建议。

## 安装

```bash
pip install -r requirements.txt
```

## 运行

```bash
streamlit run app.py
```

## 项目结构

- `data/` - 数据层：数据获取、存储、模型管理
- `analysis/` - 分析层：技术指标计算、板块分析、特征工程
- `prediction/` - 预测层：预测模型、模型训练、集成预测
- `ui/` - 界面层：界面组件、页面布局、图表展示
- `utils/` - 工具层：配置管理、日志、辅助函数、异常、缓存

## 文档

详细文档请查看 `docs/` 目录：
- `PRD.md` - 产品需求文档
- `APP_FLOW.md` - 应用流程文档
- `TECH_STACK.md` - 技术栈文档
- `FRONTEND_GUIDELINES.md` - 前端设计指南
- `BACKEND_STRUCTURE.md` - 后端结构文档
- `IMPLEMENTATION_PLAN.md` - 实现计划

## 进度

- ✅ Stage 1: 项目初始化
- ⏳ Stage 2: 数据层实现
- ⏳ Stage 3: 预测层实现
- ⏳ Stage 4: 基础UI实现
- ⏳ Stage 5: 详情页实现
- ⏳ Stage 6: 集成测试和优化
```

- [ ] **Step 2: Update CLAUDE.md with Stage 1 info**

Add to CLAUDE.md:

```markdown
## Stage 1 Implementation Status

**Completed:**
- ✅ Project directory structure
- ✅ requirements.txt with dependencies
- ✅ Config class (utils/config.py)
- ✅ Logger class (utils/logger.py)
- ✅ Helper functions (utils/helpers.py)
- ✅ Custom exceptions (utils/exceptions.py)
- ✅ Cache manager (utils/cache.py)
- ✅ Data models (data/models.py)
- ✅ DatabaseManager (data/database.py)
- ✅ Placeholder modules for future stages
- ✅ Basic Streamlit app (app.py)

**Next:** Stage 2 - Data layer implementation (akshare integration, indicators, sector analysis)
```

- [ ] **Step 3: Verify all tests pass**

Run: `pytest tests/ -v`

Expected: All tests pass

- [ ] **Step 4: Final commit**

```bash
git add README.md CLAUDE.md
git commit -m "docs: add README and update CLAUDE.md for Stage 1"
```

---

## Verification Checklist

After completing all tasks:

- [ ] All directory structure is in place
- [ ] All `__init__.py` files exist
- [ ] All tests pass: `pytest tests/ -v`
- [ ] Streamlit app runs without errors: `streamlit run app.py`
- [ ] Database tables are created correctly
- [ ] All placeholder modules use custom exceptions
- [ ] README.md is complete
- [ ] Git history shows clean, incremental commits
- [ ] All commits follow conventional commit format