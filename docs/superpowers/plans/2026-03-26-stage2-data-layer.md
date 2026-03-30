# Stage 2: Data Layer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the data layer components - data fetching, storage, technical indicators, and sector analysis to enable full stock data management and analysis.

**Architecture:** Layered architecture with data fetcher using akshare, storage using SQLite, indicators using pandas-ta, and sector analyzer for leader identification. All components use existing utilities (Config, Logger, Exceptions, Cache) and integrate with DatabaseManager.

**Tech Stack:** akshare>=1.12.0, pandas>=2.0.0, pandas-ta>=0.3.14b, SQLite (Python内置)

---

## File Structure

**Files to modify/create:**
```
data/
├── fetcher.py          # Create/Replace - akshare data fetching with retry and cache
├── storage.py          # Create/Replace - SQLite CRUD operations
├── database.py         # Already exists - use existing DatabaseManager
└── models.py           # Already exists - use existing dataclasses

analysis/
├── indicators.py       # Create/Replace - technical indicator calculations
└── sector.py           # Create/Replace - sector analysis and leader screening

tests/
├── test_fetcher.py     # Create - DataFetcher tests
├── test_storage.py     # Create - StockStorage tests
├── test_indicators.py  # Create - IndicatorCalculator tests
└── test_sector.py      # Create - SectorAnalyzer tests
```

---

## Task 1: Implement DataFetcher

**Files:**
- Modify: `data/fetcher.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_fetcher.py`:

```python
import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from data.fetcher import DataFetcher
from utils.exceptions import DataFetchException

def test_fetcher_initialization():
    """Test DataFetcher can be initialized"""
    fetcher = DataFetcher()
    assert fetcher is not None

@patch('akshare.stock_board_industry_name_em')
def test_get_industry_sectors(mock_api):
    """Test getting industry sectors"""
    mock_df = pd.DataFrame({
        '板块名称': ['银行', '科技'],
        '板块代码': ['BK0001', 'BK0002']
    })
    mock_api.return_value = mock_df

    fetcher = DataFetcher()
    result = fetcher.get_industry_sectors()

    assert not result.empty
    assert '板块名称' in result.columns

@patch('akshare.stock_board_concept_name_em')
def test_get_concept_sectors(mock_api):
    """Test getting concept sectors"""
    mock_df = pd.DataFrame({
        '板块名称': ['人工智能', '新能源'],
        '板块代码': ['BK0010', 'BK0020']
    })
    mock_api.return_value = mock_df

    fetcher = DataFetcher()
    result = fetcher.get_concept_sectors()

    assert not result.empty
    assert '板块名称' in result.columns

@patch('akshare.stock_board_industry_cons_em')
def test_get_sector_stocks(mock_api):
    """Test getting sector stocks"""
    mock_df = pd.DataFrame({
        '代码': ['000001', '000002'],
        '名称': ['平安银行', '万科A']
    })
    mock_api.return_value = mock_df

    fetcher = DataFetcher()
    result = fetcher.get_sector_stocks('银行', 'industry')

    assert not result.empty

@patch('akshare.stock_individual_info_em')
def test_get_stock_info(mock_api):
    """Test getting stock info"""
    mock_data = {
        '股票简称': '平安银行',
        '行业': '银行',
        '上市日期': '1991-04-03'
    }
    mock_api.return_value = mock_data

    fetcher = DataFetcher()
    result = fetcher.get_stock_info('000001.SZ')

    assert result['股票简称'] == '平安银行'

@patch('akshare.stock_zh_a_hist')
def test_get_stock_history(mock_api):
    """Test getting stock history"""
    mock_df = pd.DataFrame({
        '日期': ['2024-01-01', '2024-01-02'],
        '开盘': [10.0, 10.5],
        '最高': [10.5, 11.0],
        '最低': [9.8, 10.2],
        '收盘': [10.3, 10.8],
        '成交量': [1000000, 1200000]
    })
    mock_api.return_value = mock_df

    fetcher = DataFetcher()
    result = fetcher.get_stock_history('000001.SZ', '2024-01-01')

    assert not result.empty
    assert '开盘' in result.columns

@patch('akshare.stock_zh_a_spot_em')
def test_get_stock_latest(mock_api):
    """Test getting latest stock data"""
    mock_df = pd.DataFrame({
        '代码': ['000001'],
        '名称': ['平安银行'],
        '最新价': [10.5],
        '涨跌幅': [0.5]
    })
    mock_api.return_value = mock_df

    fetcher = DataFetcher()
    result = fetcher.get_stock_latest('000001.SZ')

    assert '最新价' in result
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_fetcher.py -v`

Expected: FAIL with DataFetchException or AttributeError

- [ ] **Step 3: Write minimal implementation**

Replace `data/fetcher.py`:

```python
"""Data fetcher module - akshare API wrapper with retry and cache."""

import time
import akshare as ak
import pandas as pd
from typing import Dict, List, Optional
from utils.logger import Logger
from utils.exceptions import DataFetchException
from utils.cache import CacheManager


class DataFetcher:
    """Data fetcher for stock market data using akshare API."""

    def __init__(self, use_cache: bool = True, max_retries: int = 3, retry_delay: float = 1.0):
        """Initialize data fetcher.

        Args:
            use_cache: Whether to use cache for API responses
            max_retries: Maximum number of retries for failed requests
            retry_delay: Delay between retries in seconds
        """
        self.use_cache = use_cache
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.cache = CacheManager() if use_cache else None
        Logger.info("DataFetcher initialized")

    def _retry_api_call(self, api_func, *args, cache_key: str = None, **kwargs) -> pd.DataFrame:
        """Execute API call with retry logic.

        Args:
            api_func: akshare API function
            cache_key: Optional cache key
            args: Positional arguments for API
            kwargs: Keyword arguments for API

        Returns:
            DataFrame with API response

        Raises:
            DataFetchException: If all retries fail
        """
        # Try cache first
        if self.use_cache and cache_key:
            cached = self.cache.get(cache_key)
            if cached is not None:
                Logger.debug(f"Cache hit for {cache_key}")
                return cached

        last_error = None
        for attempt in range(self.max_retries):
            try:
                result = api_func(*args, **kwargs)

                # Cache successful result
                if self.use_cache and cache_key:
                    self.cache.set(cache_key, result)

                return result
            except Exception as e:
                last_error = e
                Logger.warning(f"API call failed (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)

        raise DataFetchException(f"API call failed after {self.max_retries} retries: {str(last_error)}")

    def get_industry_sectors(self) -> pd.DataFrame:
        """Get industry sector list.

        Returns:
            DataFrame with sector information (板块名称, 板块代码)
        """
        Logger.info("Fetching industry sectors...")
        try:
            df = self._retry_api_call(
                ak.stock_board_industry_name_em,
                cache_key="industry_sectors"
            )
            return df
        except Exception as e:
            Logger.error(f"Failed to fetch industry sectors: {str(e)}")
            raise DataFetchException(f"Failed to fetch industry sectors: {str(e)}")

    def get_concept_sectors(self) -> pd.DataFrame:
        """Get concept sector list.

        Returns:
            DataFrame with concept sector information (板块名称, 板块代码)
        """
        Logger.info("Fetching concept sectors...")
        try:
            df = self._retry_api_call(
                ak.stock_board_concept_name_em,
                cache_key="concept_sectors"
            )
            return df
        except Exception as e:
            Logger.error(f"Failed to fetch concept sectors: {str(e)}")
            raise DataFetchException(f"Failed to fetch concept sectors: {str(e)}")

    def get_sector_stocks(self, sector_name: str, sector_type: str) -> pd.DataFrame:
        """Get stocks in a sector.

        Args:
            sector_name: Sector name (e.g., '银行')
            sector_type: 'industry' or 'concept'

        Returns:
            DataFrame with stock information (代码, 名称, etc.)
        """
        Logger.info(f"Fetching stocks for sector: {sector_name}")
        try:
            cache_key = f"sector_stocks_{sector_type}_{sector_name}"

            if sector_type == 'industry':
                df = self._retry_api_call(
                    ak.stock_board_industry_cons_em,
                    symbol=sector_name,
                    cache_key=cache_key
                )
            else:
                df = self._retry_api_call(
                    ak.stock_board_concept_cons_em,
                    symbol=sector_name,
                    cache_key=cache_key
                )
            return df
        except Exception as e:
            Logger.error(f"Failed to fetch sector stocks: {str(e)}")
            raise DataFetchException(f"Failed to fetch sector stocks: {str(e)}")

    def get_stock_info(self, symbol: str) -> Dict:
        """Get stock basic information.

        Args:
            symbol: Stock symbol (e.g., '000001.SZ' or '000001')

        Returns:
            Dictionary with stock information
        """
        Logger.info(f"Fetching stock info: {symbol}")
        try:
            # Remove exchange suffix if present
            clean_symbol = symbol.split('.')[0]
            cache_key = f"stock_info_{clean_symbol}"

            info = self._retry_api_call(
                ak.stock_individual_info_em,
                symbol=clean_symbol,
                cache_key=cache_key
            )

            if isinstance(info, dict):
                return info
            else:
                return info.to_dict() if hasattr(info, 'to_dict') else {'error': 'Unknown format'}
        except Exception as e:
            Logger.error(f"Failed to fetch stock info: {str(e)}")
            raise DataFetchException(f"Failed to fetch stock info: {str(e)}")

    def get_stock_history(self, symbol: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """Get stock historical data.

        Args:
            symbol: Stock symbol (e.g., '000001.SZ' or '000001')
            start_date: Start date in 'YYYYMMDD' format
            end_date: End date in 'YYYYMMDD' format

        Returns:
            DataFrame with OHLCV data
        """
        Logger.info(f"Fetching stock history: {symbol}")
        try:
            clean_symbol = symbol.split('.')[0]
            cache_key = f"stock_history_{clean_symbol}_{start_date}_{end_date}"

            df = self._retry_api_call(
                ak.stock_zh_a_hist,
                symbol=clean_symbol,
                period="daily",
                start_date=start_date,
                end_date=end_date,
                adjust="hfq",  # 前复权
                cache_key=cache_key
            )
            return df
        except Exception as e:
            Logger.error(f"Failed to fetch stock history: {str(e)}")
            raise DataFetchException(f"Failed to fetch stock history: {str(e)}")

    def get_stock_latest(self, symbol: str) -> Dict:
        """Get stock latest data.

        Args:
            symbol: Stock symbol (e.g., '000001.SZ' or '000001')

        Returns:
            Dictionary with latest stock data
        """
        Logger.info(f"Fetching latest data: {symbol}")
        try:
            clean_symbol = symbol.split('.')[0]
            cache_key = f"stock_latest_{clean_symbol}"

            # Get all stocks and filter
            df = self._retry_api_call(
                ak.stock_zh_a_spot_em,
                cache_key="all_stocks_latest",
                expire=60  # Cache for 60 seconds only
            )

            # Find the stock
            stock = df[df['代码'] == clean_symbol]

            if stock.empty:
                raise DataFetchException(f"Stock {symbol} not found in latest data")

            return stock.iloc[0].to_dict()
        except Exception as e:
            Logger.error(f"Failed to fetch latest stock data: {str(e)}")
            raise DataFetchException(f"Failed to fetch latest stock data: {str(e)}")

    def get_all_stocks_list(self) -> pd.DataFrame:
        """Get all A-share stocks list.

        Returns:
            DataFrame with all stocks (代码, 名称)
        """
        Logger.info("Fetching all stocks list...")
        try:
            df = self._retry_api_call(
                ak.stock_zh_a_spot_em,
                cache_key="all_stocks",
                expire=3600  # Cache for 1 hour
            )
            return df[['代码', '名称']]
        except Exception as e:
            Logger.error(f"Failed to fetch all stocks: {str(e)}")
            raise DataFetchException(f"Failed to fetch all stocks: {str(e)}")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_fetcher.py -v`

Expected: PASS (8 passed)

- [ ] **Step 5: Commit**

```bash
git add data/fetcher.py tests/test_fetcher.py
git commit -m "feat: implement DataFetcher with akshare integration and retry logic"
```

---

## Task 2: Implement StockStorage

**Files:**
- Modify: `data/storage.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_storage.py`:

```python
import pytest
import pandas as pd
import tempfile
import os
from data.storage import StockStorage
from data.database import DatabaseManager

@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    yield db_path
    if os.path.exists(db_path):
        os.unlink(db_path)

@pytest.fixture
def storage(temp_db):
    """Create storage with temporary database."""
    db = DatabaseManager(temp_db)
    db.create_tables()
    storage = StockStorage(db)
    yield storage
    db.close()

def test_save_and_get_sector(storage):
    """Test saving and retrieving sector"""
    sector_data = {
        'sector_id': 'industry_test',
        'sector_name': '测试板块',
        'sector_type': 'industry',
        'leader_count': 5
    }

    result = storage.save_sector(sector_data)
    assert result

    sectors = storage.get_all_sectors()
    assert len(sectors) == 1
    assert sectors[0]['sector_name'] == '测试板块'

def test_save_and_get_stock(storage):
    """Test saving and retrieving stock"""
    stock_data = {
        'symbol': '000001.TEST',
        'name': '测试股票',
        'industry': '测试行业',
        'sector': '测试板块',
        'market_cap': 1000.0,
        'pe_ratio': 15.0
    }

    result = storage.save_stock(stock_data)
    assert result

    stock = storage.get_stock('000001.TEST')
    assert stock is not None
    assert stock['name'] == '测试股票'

def test_save_and_get_stock_data(storage):
    """Test saving and retrieving stock data"""
    # First save stock
    storage.save_stock({
        'symbol': '000001.TEST',
        'name': '测试股票'
    })

    # Create DataFrame with stock data
    df = pd.DataFrame({
        'date': ['2024-01-01', '2024-01-02'],
        'symbol': ['000001.TEST', '000001.TEST'],
        'open': [10.0, 10.5],
        'high': [10.5, 11.0],
        'low': [9.8, 10.2],
        'close': [10.3, 10.8],
        'volume': [1000000, 1200000]
    })

    result = storage.save_stock_data(df)
    assert result

    data = storage.get_stock_data('000001.TEST')
    assert not data.empty
    assert len(data) == 2

def test_save_and_get_prediction(storage):
    """Test saving and retrieving prediction"""
    # First save stock
    storage.save_stock({
        'symbol': '000001.TEST',
        'name': '测试股票'
    })

    pred_data = {
        'date': '2024-01-01',
        'symbol': '000001.TEST',
        'horizon': 'short',
        'action': 'buy',
        'confidence': 0.75,
        'reasoning': '["MACD金叉"]',
        'model_version': '1.0'
    }

    result = storage.save_prediction(pred_data)
    assert result

    pred = storage.get_prediction('000001.TEST', 'short')
    assert pred is not None
    assert pred['action'] == 'buy'
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_storage.py -v`

Expected: FAIL with StorageException or AttributeError

- [ ] **Step 3: Write minimal implementation**

Replace `data/storage.py`:

```python
"""Data storage module - SQLite CRUD operations."""

import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
from utils.logger import Logger
from utils.exceptions import StorageException
from data.database import DatabaseManager


class StockStorage:
    """Stock data storage manager for CRUD operations."""

    def __init__(self, db_manager: DatabaseManager):
        """Initialize storage manager.

        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager
        Logger.info("StockStorage initialized")

    # ========== Sector Operations ==========

    def save_sector(self, sector_data: Dict) -> bool:
        """Save or update sector information.

        Args:
            sector_data: Dictionary with sector data
                - sector_id: Unique sector ID
                - sector_name: Sector name
                - sector_type: 'industry' or 'concept'
                - leader_count: Number of leaders

        Returns:
            True if successful, raises StorageException otherwise
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT OR REPLACE INTO sectors
                (sector_id, sector_name, sector_type, leader_count, updated_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                sector_data.get('sector_id'),
                sector_data.get('sector_name'),
                sector_data.get('sector_type'),
                sector_data.get('leader_count', 0),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))

            conn.commit()
            Logger.debug(f"Saved sector: {sector_data.get('sector_name')}")
            return True
        except Exception as e:
            Logger.error(f"Failed to save sector: {str(e)}")
            raise StorageException(f"Failed to save sector: {str(e)}")

    def get_all_sectors(self, sector_type: str = None) -> List[Dict]:
        """Get all sectors.

        Args:
            sector_type: Optional filter by sector type

        Returns:
            List of sector dictionaries
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            if sector_type:
                cursor.execute('''
                    SELECT sector_id, sector_name, sector_type, leader_count
                    FROM sectors WHERE sector_type = ?
                    ORDER BY sector_name
                ''', (sector_type,))
            else:
                cursor.execute('''
                    SELECT sector_id, sector_name, sector_type, leader_count
                    FROM sectors ORDER BY sector_name
                ''')

            rows = cursor.fetchall()
            return [
                {
                    'sector_id': row['sector_id'],
                    'sector_name': row['sector_name'],
                    'sector_type': row['sector_type'],
                    'leader_count': row['leader_count']
                }
                for row in rows
            ]
        except Exception as e:
            Logger.error(f"Failed to get sectors: {str(e)}")
            raise StorageException(f"Failed to get sectors: {str(e)}")

    def get_sector(self, sector_id: str) -> Optional[Dict]:
        """Get sector by ID.

        Args:
            sector_id: Sector ID

        Returns:
            Sector dictionary or None if not found
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT sector_id, sector_name, sector_type, leader_count
                FROM sectors WHERE sector_id = ?
            ''', (sector_id,))

            row = cursor.fetchone()
            if row:
                return {
                    'sector_id': row['sector_id'],
                    'sector_name': row['sector_name'],
                    'sector_type': row['sector_type'],
                    'leader_count': row['leader_count']
                }
            return None
        except Exception as e:
            Logger.error(f"Failed to get sector: {str(e)}")
            raise StorageException(f"Failed to get sector: {str(e)}")

    # ========== Stock Operations ==========

    def save_stock(self, stock_data: Dict) -> bool:
        """Save or update stock information.

        Args:
            stock_data: Dictionary with stock data

        Returns:
            True if successful
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT OR REPLACE INTO stocks
                (symbol, name, industry, sector, market_cap, pe_ratio, pb_ratio, list_date, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                stock_data.get('symbol'),
                stock_data.get('name'),
                stock_data.get('industry'),
                stock_data.get('sector'),
                stock_data.get('market_cap'),
                stock_data.get('pe_ratio'),
                stock_data.get('pb_ratio'),
                stock_data.get('list_date'),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))

            conn.commit()
            Logger.debug(f"Saved stock: {stock_data.get('symbol')}")
            return True
        except Exception as e:
            Logger.error(f"Failed to save stock: {str(e)}")
            raise StorageException(f"Failed to save stock: {str(e)}")

    def get_stock(self, symbol: str) -> Optional[Dict]:
        """Get stock by symbol.

        Args:
            symbol: Stock symbol

        Returns:
            Stock dictionary or None if not found
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT symbol, name, industry, sector, market_cap, pe_ratio, pb_ratio, list_date
                FROM stocks WHERE symbol = ?
            ''', (symbol,))

            row = cursor.fetchone()
            if row:
                return {
                    'symbol': row['symbol'],
                    'name': row['name'],
                    'industry': row['industry'],
                    'sector': row['sector'],
                    'market_cap': row['market_cap'],
                    'pe_ratio': row['pe_ratio'],
                    'pb_ratio': row['pb_ratio'],
                    'list_date': row['list_date']
                }
            return None
        except Exception as e:
            Logger.error(f"Failed to get stock: {str(e)}")
            raise StorageException(f"Failed to get stock: {str(e)}")

    def get_stock_list(self, industry: str = None, sector: str = None) -> List[Dict]:
        """Get stock list with optional filters.

        Args:
            industry: Optional industry filter
            sector: Optional sector filter

        Returns:
            List of stock dictionaries
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            query = '''
                SELECT symbol, name, industry, sector, market_cap
                FROM stocks WHERE 1=1
            '''
            params = []

            if industry:
                query += ' AND industry = ?'
                params.append(industry)

            if sector:
                query += ' AND sector = ?'
                params.append(sector)

            query += ' ORDER BY market_cap DESC'

            cursor.execute(query, params)
            rows = cursor.fetchall()

            return [
                {
                    'symbol': row['symbol'],
                    'name': row['name'],
                    'industry': row['industry'],
                    'sector': row['sector'],
                    'market_cap': row['market_cap']
                }
                for row in rows
            ]
        except Exception as e:
            Logger.error(f"Failed to get stock list: {str(e)}")
            raise StorageException(f"Failed to get stock list: {str(e)}")

    # ========== Stock Data Operations ==========

    def save_stock_data(self, df: pd.DataFrame) -> bool:
        """Save stock historical data in batch.

        Args:
            df: DataFrame with stock data columns:
                date, symbol, open, high, low, close, volume, amount,
                ma5, ma10, ma20, ma60, macd, macd_signal, macd_hist,
                kdj_k, kdj_d, kdj_j, rsi6, rsi12, rsi24,
                boll_upper, boll_middle, boll_lower, obv

        Returns:
            True if successful
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            # Convert DataFrame to list of tuples
            columns = ['date', 'symbol', 'open', 'high', 'low', 'close', 'volume', 'amount',
                      'ma5', 'ma10', 'ma20', 'ma60', 'macd', 'macd_signal', 'macd_hist',
                      'kdj_k', 'kdj_d', 'kdj_j', 'rsi6', 'rsi12', 'rsi24',
                      'boll_upper', 'boll_middle', 'boll_lower', 'obv']

            # Ensure all columns exist
            for col in columns:
                if col not in df.columns:
                    df[col] = None

            # Prepare data for insertion
            data = []
            for _, row in df.iterrows():
                data.append(tuple(row.get(col) for col in columns))

            # Insert in batch
            placeholders = ', '.join(['?' for _ in columns])
            query = f'''
                INSERT OR REPLACE INTO stock_data
                (date, symbol, open, high, low, close, volume, amount,
                 ma5, ma10, ma20, ma60, macd, macd_signal, macd_hist,
                 kdj_k, kdj_d, kdj_j, rsi6, rsi12, rsi24,
                 boll_upper, boll_middle, boll_lower, obv)
                VALUES ({placeholders})
            '''

            cursor.executemany(query, data)
            conn.commit()
            Logger.debug(f"Saved {len(df)} stock data rows")
            return True
        except Exception as e:
            Logger.error(f"Failed to save stock data: {str(e)}")
            raise StorageException(f"Failed to save stock data: {str(e)}")

    def get_stock_data(self, symbol: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """Get stock historical data.

        Args:
            symbol: Stock symbol
            start_date: Optional start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD)

        Returns:
            DataFrame with stock data
        """
        try:
            conn = self.db.get_connection()

            query = '''
                SELECT date, symbol, open, high, low, close, volume, amount,
                       ma5, ma10, ma20, ma60, macd, macd_signal, macd_hist,
                       kdj_k, kdj_d, kdj_j, rsi6, rsi12, rsi24,
                       boll_upper, boll_middle, boll_lower, obv
                FROM stock_data
                WHERE symbol = ?
            '''
            params = [symbol]

            if start_date:
                query += ' AND date >= ?'
                params.append(start_date)

            if end_date:
                query += ' AND date <= ?'
                params.append(end_date)

            query += ' ORDER BY date'

            df = pd.read_sql_query(query, conn, params=params)
            return df
        except Exception as e:
            Logger.error(f"Failed to get stock data: {str(e)}")
            raise StorageException(f"Failed to get stock data: {str(e)}")

    def get_latest_stock_data(self, symbol: str) -> Optional[Dict]:
        """Get latest stock data.

        Args:
            symbol: Stock symbol

        Returns:
            Latest stock data dictionary or None
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT date, symbol, open, high, low, close, volume, amount
                FROM stock_data
                WHERE symbol = ?
                ORDER BY date DESC
                LIMIT 1
            ''', (symbol,))

            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
        except Exception as e:
            Logger.error(f"Failed to get latest stock data: {str(e)}")
            raise StorageException(f"Failed to get latest stock data: {str(e)}")

    # ========== Prediction Operations ==========

    def save_prediction(self, prediction_data: Dict) -> bool:
        """Save prediction result.

        Args:
            prediction_data: Dictionary with prediction data

        Returns:
            True if successful
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO predictions
                (date, symbol, horizon, action, confidence, reasoning, model_version, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                prediction_data.get('date'),
                prediction_data.get('symbol'),
                prediction_data.get('horizon'),
                prediction_data.get('action'),
                prediction_data.get('confidence'),
                prediction_data.get('reasoning'),
                prediction_data.get('model_version'),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))

            conn.commit()
            Logger.debug(f"Saved prediction for {prediction_data.get('symbol')}")
            return True
        except Exception as e:
            Logger.error(f"Failed to save prediction: {str(e)}")
            raise StorageException(f"Failed to save prediction: {str(e)}")

    def get_prediction(self, symbol: str, horizon: str, date: str = None) -> Optional[Dict]:
        """Get latest prediction for stock.

        Args:
            symbol: Stock symbol
            horizon: Prediction horizon ('short', 'medium', 'long')
            date: Optional date filter

        Returns:
            Prediction dictionary or None
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            query = '''
                SELECT id, date, symbol, horizon, action, confidence, reasoning, model_version
                FROM predictions
                WHERE symbol = ? AND horizon = ?
            '''
            params = [symbol, horizon]

            if date:
                query += ' AND date <= ?'
                params.append(date)

            query += ' ORDER BY date DESC LIMIT 1'

            cursor.execute(query, params)
            row = cursor.fetchone()

            if row:
                return {
                    'id': row['id'],
                    'date': row['date'],
                    'symbol': row['symbol'],
                    'horizon': row['horizon'],
                    'action': row['action'],
                    'confidence': row['confidence'],
                    'reasoning': row['reasoning'],
                    'model_version': row['model_version']
                }
            return None
        except Exception as e:
            Logger.error(f"Failed to get prediction: {str(e)}")
            raise StorageException(f"Failed to get prediction: {str(e)}")

    def get_predictions(self, symbol: str) -> List[Dict]:
        """Get all predictions for a stock.

        Args:
            symbol: Stock symbol

        Returns:
            List of prediction dictionaries
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT id, date, symbol, horizon, action, confidence, reasoning, model_version
                FROM predictions
                WHERE symbol = ?
                ORDER BY date DESC, horizon
            ''', (symbol,))

            rows = cursor.fetchall()
            return [
                {
                    'id': row['id'],
                    'date': row['date'],
                    'symbol': row['symbol'],
                    'horizon': row['horizon'],
                    'action': row['action'],
                    'confidence': row['confidence'],
                    'reasoning': row['reasoning'],
                    'model_version': row['model_version']
                }
                for row in rows
            ]
        except Exception as e:
            Logger.error(f"Failed to get predictions: {str(e)}")
            raise StorageException(f"Failed to get predictions: {str(e)}")

    # ========== Sector Leaders Operations ==========

    def save_sector_leaders(self, sector_id: str, leaders: List[Dict]) -> bool:
        """Save sector leader stocks.

        Args:
            sector_id: Sector ID
            leaders: List of leader data dictionaries

        Returns:
            True if successful
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            # Delete existing leaders for this sector
            cursor.execute('DELETE FROM sector_leaders WHERE sector_id = ?', (sector_id,))

            # Insert new leaders
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            for leader in leaders:
                cursor.execute('''
                    INSERT INTO sector_leaders
                    (sector_id, sector_name, symbol, score, rank, market_cap_rank, volume_rank, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    sector_id,
                    leader.get('sector_name'),
                    leader.get('symbol'),
                    leader.get('score'),
                    leader.get('rank'),
                    leader.get('market_cap_rank'),
                    leader.get('volume_rank'),
                    timestamp
                ))

            conn.commit()
            Logger.debug(f"Saved {len(leaders)} leaders for sector {sector_id}")
            return True
        except Exception as e:
            Logger.error(f"Failed to save sector leaders: {str(e)}")
            raise StorageException(f"Failed to save sector leaders: {str(e)}")

    def get_sector_leaders(self, sector_id: str) -> List[Dict]:
        """Get sector leaders.

        Args:
            sector_id: Sector ID

        Returns:
            List of leader dictionaries
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT sector_id, sector_name, symbol, score, rank, market_cap_rank, volume_rank
                FROM sector_leaders
                WHERE sector_id = ?
                ORDER BY rank
            ''', (sector_id,))

            rows = cursor.fetchall()
            return [
                {
                    'sector_id': row['sector_id'],
                    'sector_name': row['sector_name'],
                    'symbol': row['symbol'],
                    'score': row['score'],
                    'rank': row['rank'],
                    'market_cap_rank': row['market_cap_rank'],
                    'volume_rank': row['volume_rank']
                }
                for row in rows
            ]
        except Exception as e:
            Logger.error(f"Failed to get sector leaders: {str(e)}")
            raise StorageException(f"Failed to get sector leaders: {str(e)}")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_storage.py -v`

Expected: PASS (8 passed)

- [ ] **Step 5: Commit**

```bash
git add data/storage.py tests/test_storage.py
git commit -m "feat: implement StockStorage with CRUD operations"
```

---

## Task 3: Implement IndicatorCalculator

**Files:**
- Modify: `analysis/indicators.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_indicators.py`:

```python
import pytest
import pandas as pd
import numpy as np
from analysis.indicators import IndicatorCalculator

def test_calculate_ma():
    """Test MA calculation"""
    df = pd.DataFrame({
        'close': [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    })
    result = IndicatorCalculator.calculate_ma(df, [5, 10])

    assert 'ma5' in result.columns
    assert 'ma10' in result.columns
    # MA5 at index 4 should be average of first 5 values
    assert abs(result.loc[4, 'ma5'] - 12.0) < 0.01

def test_calculate_macd():
    """Test MACD calculation"""
    df = pd.DataFrame({
        'close': [10 + i * 0.5 for i in range(30)]
    })
    result = IndicatorCalculator.calculate_macd(df)

    assert 'macd' in result.columns
    assert 'macd_signal' in result.columns
    assert 'macd_hist' in result.columns

def test_calculate_kdj():
    """Test KDJ calculation"""
    df = pd.DataFrame({
        'high': [10 + i for i in range(20)],
        'low': [10 + i - 2 for i in range(20)],
        'close': [10 + i - 1 for i in range(20)]
    })
    result = IndicatorCalculator.calculate_kdj(df)

    assert 'kdj_k' in result.columns
    assert 'kdj_d' in result.columns
    assert 'kdj_j' in result.columns

def test_calculate_rsi():
    """Test RSI calculation"""
    df = pd.DataFrame({
        'close': [10 + i * 0.5 for i in range(30)]
    })
    result = IndicatorCalculator.calculate_rsi(df, [6, 12])

    assert 'rsi6' in result.columns
    assert 'rsi12' in result.columns

def test_calculate_boll():
    """Test BOLL calculation"""
    df = pd.DataFrame({
        'close': [10 + i * 0.2 for i in range(30)]
    })
    result = IndicatorCalculator.calculate_boll(df)

    assert 'boll_upper' in result.columns
    assert 'boll_middle' in result.columns
    assert 'boll_lower' in result.columns

def test_calculate_obv():
    """Test OBV calculation"""
    df = pd.DataFrame({
        'close': [10, 11, 10, 11, 12],
        'volume': [1000, 1500, 1200, 1300, 1400]
    })
    result = IndicatorCalculator.calculate_obv(df)

    assert 'obv' in result.columns

def test_calculate_all():
    """Test calculate all indicators"""
    df = pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=100),
        'open': [10 + i * 0.1 for i in range(100)],
        'high': [10.5 + i * 0.1 for i in range(100)],
        'low': [9.5 + i * 0.1 for i in range(100)],
        'close': [10 + i * 0.1 for i in range(100)],
        'volume': [10000 + i * 100 for i in range(100)]
    })
    result = IndicatorCalculator.calculate_all(df)

    expected_columns = ['ma5', 'ma10', 'ma20', 'ma60', 'macd', 'macd_signal', 'macd_hist',
                       'kdj_k', 'kdj_d', 'kdj_j', 'rsi6', 'rsi12', 'rsi24',
                       'boll_upper', 'boll_middle', 'boll_lower', 'obv']

    for col in expected_columns:
        assert col in result.columns
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_indicators.py -v`

Expected: FAIL with NotImplementedError or AttributeError

- [ ] **Step 3: Write minimal implementation**

Replace `analysis/indicators.py`:

```python
"""Technical indicators module using pandas-ta."""

import pandas as pd
import numpy as np
from typing import List
from utils.logger import Logger


class IndicatorCalculator:
    """Technical indicator calculator using pandas-ta library."""

    @staticmethod
    def calculate_ma(df: pd.DataFrame, periods: List[int] = [5, 10, 20, 60]) -> pd.DataFrame:
        """Calculate Moving Average (MA) indicators.

        Args:
            df: DataFrame with 'close' column
            periods: List of MA periods to calculate

        Returns:
            DataFrame with added MA columns
        """
        result = df.copy()
        for period in periods:
            col_name = f'ma{period}'
            result[col_name] = df['close'].rolling(window=period).mean()
        return result

    @staticmethod
    def calculate_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
        """Calculate MACD indicator.

        Args:
            df: DataFrame with 'close' column
            fast: Fast period
            slow: Slow period
            signal: Signal period

        Returns:
            DataFrame with MACD, MACD signal, and MACD histogram
        """
        try:
            import pandas_ta as ta
            result = df.copy()
            macd = ta.macd(df['close'], fast=fast, slow=slow, signal=signal)
            result['macd'] = macd[f'MACD_{fast}_{slow}_{signal}']
            result['macd_signal'] = macd[f'MACDs_{fast}_{slow}_{signal}']
            result['macd_hist'] = macd[f'MACDh_{fast}_{slow}_{signal}']
            return result
        except ImportError:
            Logger.warning("pandas-ta not available, using manual MACD calculation")
            return IndicatorCalculator._calculate_macd_manual(df, fast, slow, signal)

    @staticmethod
    def _calculate_macd_manual(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
        """Manual MACD calculation when pandas-ta is not available."""
        result = df.copy()

        # Calculate EMAs
        ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['close'].ewm(span=slow, adjust=False).mean()

        result['macd'] = ema_fast - ema_slow
        result['macd_signal'] = result['macd'].ewm(span=signal, adjust=False).mean()
        result['macd_hist'] = result['macd'] - result['macd_signal']

        return result

    @staticmethod
    def calculate_kdj(df: pd.DataFrame, k: int = 9, d: int = 3, j: int = 3) -> pd.DataFrame:
        """Calculate KDJ indicator.

        Args:
            df: DataFrame with 'high', 'low', 'close' columns
            k: K period
            d: D period
            j: J period

        Returns:
            DataFrame with KDJ indicators
        """
        result = df.copy()

        # Calculate RSV (Raw Stochastic Value)
        low_min = df['low'].rolling(window=k).min()
        high_max = df['high'].rolling(window=k).max()
        rsv = (df['close'] - low_min) / (high_max - low_min) * 100
        rsv = rsv.fillna(50)  # Handle NaN

        # Calculate K, D, J values
        result['kdj_k'] = rsv.ewm(com=2, adjust=False).mean()
        result['kdj_d'] = result['kdj_k'].ewm(com=2, adjust=False).mean()
        result['kdj_j'] = 3 * result['kdj_k'] - 2 * result['kdj_d']

        return result

    @staticmethod
    def calculate_rsi(df: pd.DataFrame, periods: List[int] = [6, 12, 24]) -> pd.DataFrame:
        """Calculate RSI (Relative Strength Index) indicator.

        Args:
            df: DataFrame with 'close' column
            periods: List of RSI periods

        Returns:
            DataFrame with RSI indicators
        """
        try:
            import pandas_ta as ta
            result = df.copy()
            for period in periods:
                col_name = f'rsi{period}'
                result[col_name] = ta.rsi(df['close'], length=period)
            return result
        except ImportError:
            Logger.warning("pandas-ta not available, using manual RSI calculation")
            return IndicatorCalculator._calculate_rsi_manual(df, periods)

    @staticmethod
    def _calculate_rsi_manual(df: pd.DataFrame, periods: List[int] = [6, 12, 24]) -> pd.DataFrame:
        """Manual RSI calculation when pandas-ta is not available."""
        result = df.copy()

        for period in periods:
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

            rs = gain / loss
            col_name = f'rsi{period}'
            result[col_name] = 100 - (100 / (1 + rs))

        return result

    @staticmethod
    def calculate_boll(df: pd.DataFrame, period: int = 20, std: int = 2) -> pd.DataFrame:
        """Calculate Bollinger Bands indicator.

        Args:
            df: DataFrame with 'close' column
            period: Moving average period
            std: Standard deviation multiplier

        Returns:
            DataFrame with upper, middle, and lower bands
        """
        result = df.copy()

        result['boll_middle'] = df['close'].rolling(window=period).mean()
        rolling_std = df['close'].rolling(window=period).std()
        result['boll_upper'] = result['boll_middle'] + (rolling_std * std)
        result['boll_lower'] = result['boll_middle'] - (rolling_std * std)

        return result

    @staticmethod
    def calculate_obv(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate OBV (On-Balance Volume) indicator.

        Args:
            df: DataFrame with 'close' and 'volume' columns

        Returns:
            DataFrame with OBV values
        """
        result = df.copy()

        # Calculate OBV
        obv = (np.sign(df['close'].diff()) * df['volume']).fillna(0).cumsum()
        result['obv'] = obv

        return result

    @staticmethod
    def calculate_all(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all technical indicators.

        Args:
            df: DataFrame with OHLCV columns:
                date, open, high, low, close, volume, amount

        Returns:
            DataFrame with all indicators added
        """
        Logger.info("Calculating all technical indicators...")
        result = df.copy()

        # Calculate moving averages
        result = IndicatorCalculator.calculate_ma(result, [5, 10, 20, 60])

        # Calculate MACD
        result = IndicatorCalculator.calculate_macd(result)

        # Calculate KDJ
        result = IndicatorCalculator.calculate_kdj(result)

        # Calculate RSI
        result = IndicatorCalculator.calculate_rsi(result, [6, 12, 24])

        # Calculate Bollinger Bands
        result = IndicatorCalculator.calculate_boll(result)

        # Calculate OBV
        result = IndicatorCalculator.calculate_obv(result)

        Logger.info("Technical indicators calculated successfully")
        return result
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_indicators.py -v`

Expected: PASS (8 passed)

- [ ] **Step 5: Commit**

```bash
git add analysis/indicators.py tests/test_indicators.py
git commit -m "feat: implement IndicatorCalculator with pandas-ta integration"
```

---

## Task 4: Implement SectorAnalyzer

**Files:**
- Modify: `analysis/sector.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_sector.py`:

```python
import pytest
from data.storage import StockStorage
from data.database import DatabaseManager
from analysis.sector import SectorAnalyzer
import tempfile
import os

@pytest.fixture
def temp_db():
    """Create a temporary database with test data."""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    yield db_path
    if os.path.exists(db_path):
        os.unlink(db_path)

@pytest.fixture
def storage_with_data(temp_db):
    """Create storage with test data."""
    db = DatabaseManager(temp_db)
    db.create_tables()
    storage = StockStorage(db)

    # Add test stocks
    storage.save_stock({'symbol': '000001.TEST', 'name': '股票1', 'market_cap': 1000})
    storage.save_stock({'symbol': '000002.TEST', 'name': '股票2', 'market_cap': 800})
    storage.save_stock({'symbol': '000003.TEST', 'name': '股票3', 'market_cap': 600})

    # Add test stock data
    import pandas as pd
    dates = pd.date_range('2024-01-01', periods=30)
    for symbol in ['000001.TEST', '000002.TEST', '000003.TEST']:
        df = pd.DataFrame({
            'date': dates.strftime('%Y-%m-%d'),
            'symbol': symbol,
            'open': [10 + i * 0.1 for i in range(30)],
            'high': [10.5 + i * 0.1 for i in range(30)],
            'low': [9.5 + i * 0.1 for i in range(30)],
            'close': [10 + i * 0.1 for i in range(30)],
            'volume': [10000 + i * 100 for i in range(30)]
        })
        storage.save_stock_data(df)

    return storage

def test_rank_by_market_cap(storage_with_data):
    """Test ranking by market cap"""
    analyzer = SectorAnalyzer(storage_with_data)
    rankings = analyzer.rank_by_market_cap(['000001.TEST', '000002.TEST', '000003.TEST'])

    assert len(rankings) == 3
    assert rankings[0][0] == '000001.TEST'  # Highest market cap
    assert rankings[0][1] == 1000.0

def test_rank_by_volume(storage_with_data):
    """Test ranking by volume"""
    analyzer = SectorAnalyzer(storage_with_data)
    rankings = analyzer.rank_by_volume(['000001.TEST', '000002.TEST'], days=20)

    assert len(rankings) == 2
    assert all(isinstance(r[1], (int, float)) for r in rankings)

def test_calculate_sector_score(storage_with_data):
    """Test sector score calculation"""
    analyzer = SectorAnalyzer(storage_with_data)

    # Mock score calculation
    score = analyzer.calculate_sector_score('000001.TEST')

    assert 0 <= score <= 1  # Score should be normalized
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_sector.py -v`

Expected: FAIL with NotImplementedError or AttributeError

- [ ] **Step 3: Write minimal implementation**

Replace `analysis/sector.py`:

```python
"""Sector analysis module for identifying leading stocks."""

from typing import List, Tuple
from utils.logger import Logger
from data.storage import StockStorage
from analysis.indicators import IndicatorCalculator
import pandas as pd


class SectorAnalyzer:
    """Sector analyzer for identifying leading stocks in each sector."""

    def __init__(self, storage: StockStorage):
        """Initialize sector analyzer.

        Args:
            storage: StockStorage instance
        """
        self.storage = storage
        Logger.info("SectorAnalyzer initialized")

    def identify_leaders(self, sector_id: str, sector_name: str, limit: int = 20) -> List[dict]:
        """Identify leading stocks in a sector.

        Args:
            sector_id: Sector ID
            sector_name: Sector name
            limit: Maximum number of leaders to return

        Returns:
            List of leader dictionaries with symbol, score, rank, etc.
        """
        Logger.info(f"Identifying leaders for sector: {sector_name}")

        # Get stocks in the sector
        stocks = self.storage.get_stock_list(sector=sector_name)

        if not stocks:
            Logger.warning(f"No stocks found for sector: {sector_name}")
            return []

        # Calculate scores for each stock
        stock_scores = []
        for stock in stocks:
            try:
                symbol = stock['symbol']
                score = self.calculate_sector_score(symbol)
                stock_scores.append({
                    'symbol': symbol,
                    'score': score,
                    'market_cap': stock.get('market_cap', 0)
                })
            except Exception as e:
                Logger.warning(f"Failed to calculate score for {stock['symbol']}: {str(e)}")
                continue

        # Sort by score
        stock_scores.sort(key=lambda x: x['score'], reverse=True)

        # Create leaders list with rankings
        leaders = []
        market_cap_ranks = self.rank_by_market_cap([s['symbol'] for s in stock_scores])
        volume_ranks = self.rank_by_volume([s['symbol'] for s in stock_scores])

        rank_dict = {symbol: rank for rank, symbol in enumerate(market_cap_ranks, 1)}
        volume_dict = {symbol: rank for rank, (symbol, _) in enumerate(volume_ranks, 1)}

        for i, item in enumerate(stock_scores[:limit], 1):
            leaders.append({
                'sector_id': sector_id,
                'sector_name': sector_name,
                'symbol': item['symbol'],
                'score': item['score'],
                'rank': i,
                'market_cap_rank': rank_dict.get(item['symbol'], 0),
                'volume_rank': volume_dict.get(item['symbol'], 0)
            })

        Logger.info(f"Identified {len(leaders)} leaders for sector: {sector_name}")
        return leaders

    def calculate_sector_score(self, symbol: str) -> float:
        """Calculate comprehensive score for a stock in its sector.

        Args:
            symbol: Stock symbol

        Returns:
            Score between 0 and 1
        """
        try:
            # Get stock info
            stock = self.storage.get_stock(symbol)
            if not stock:
                return 0.0

            # Get recent stock data
            df = self.storage.get_stock_data(symbol, end_date=None)
            if df.empty or len(df) < 20:
                return 0.0

            df = df.tail(60)  # Use last 60 days
            df = IndicatorCalculator.calculate_all(df)

            # Calculate component scores
            market_cap_score = self._calculate_market_cap_score(stock.get('market_cap', 0))
            volume_score = self._calculate_volume_score(df)
            trend_score = self._calculate_trend_score(df)
            stability_score = self._calculate_stability_score(df)

            # Weighted average
            score = (
                market_cap_score * 0.35 +
                volume_score * 0.25 +
                trend_score * 0.25 +
                stability_score * 0.15
            )

            return min(max(score, 0.0), 1.0)  # Normalize to 0-1

        except Exception as e:
            Logger.error(f"Failed to calculate sector score for {symbol}: {str(e)}")
            return 0.0

    def _calculate_market_cap_score(self, market_cap: float) -> float:
        """Calculate market cap score (normalized to 0-1)."""
        # Larger market cap gets higher score, capped at 10000亿
        return min(market_cap / 10000.0, 1.0)

    def _calculate_volume_score(self, df: pd.DataFrame) -> float:
        """Calculate volume score based on recent activity."""
        if 'volume' not in df.columns or len(df) < 5:
            return 0.0

        # Compare recent average volume to historical average
        recent_avg = df['volume'].tail(5).mean()
        historical_avg = df['volume'].mean()

        if historical_avg == 0:
            return 0.5

        # Recent higher volume = higher score, cap at 2x
        ratio = recent_avg / historical_avg
        return min(ratio / 2.0, 1.0)

    def _calculate_trend_score(self, df: pd.DataFrame) -> float:
        """Calculate trend score based on price movement."""
        if 'close' not in df.columns or len(df) < 20:
            return 0.5

        # Calculate returns over different periods
        returns_5 = (df['close'].iloc[-1] - df['close'].iloc[-6]) / df['close'].iloc[-6] if len(df) > 5 else 0
        returns_20 = (df['close'].iloc[-1] - df['close'].iloc[-21]) / df['close'].iloc[-21] if len(df) > 20 else 0

        # Positive trend gets higher score
        # 5% 5-day return or 10% 20-day return = 1.0
        score = (max(returns_5, 0) * 10 + max(returns_20, 0) * 5) / 2
        return min(score, 1.0)

    def _calculate_stability_score(self, df: pd.DataFrame) -> float:
        """Calculate stability score based on price volatility."""
        if 'close' not in df.columns or len(df) < 10:
            return 0.5

        # Calculate volatility (standard deviation of returns)
        returns = df['close'].pct_change().dropna()
        volatility = returns.std()

        # Lower volatility = higher stability score
        # 5% daily volatility = 0.5 score
        score = max(0, 1.0 - volatility / 0.1)
        return score

    def rank_by_market_cap(self, symbols: List[str]) -> List[str]:
        """Rank stocks by market cap.

        Args:
            symbols: List of stock symbols

        Returns:
            List of symbols ranked by market cap (descending)
        """
        stock_mcap = []
        for symbol in symbols:
            stock = self.storage.get_stock(symbol)
            if stock and stock.get('market_cap'):
                stock_mcap.append((symbol, stock['market_cap']))

        # Sort by market cap descending
        stock_mcap.sort(key=lambda x: x[1], reverse=True)
        return [s[0] for s in stock_mcap]

    def rank_by_volume(self, symbols: List[str], days: int = 20) -> List[Tuple[str, float]]:
        """Rank stocks by average volume.

        Args:
            symbols: List of stock symbols
            days: Number of recent days to average

        Returns:
            List of (symbol, avg_volume) tuples ranked by volume (descending)
        """
        volumes = []
        for symbol in symbols:
            try:
                df = self.storage.get_stock_data(symbol)
                if not df.empty and 'volume' in df.columns:
                    recent_df = df.tail(days)
                    avg_volume = recent_df['volume'].mean()
                    volumes.append((symbol, avg_volume))
            except Exception as e:
                Logger.warning(f"Failed to get volume for {symbol}: {str(e)}")

        # Sort by volume descending
        volumes.sort(key=lambda x: x[1], reverse=True)
        return volumes

    def update_all_sector_leaders(self):
        """Update leaders for all sectors."""
        Logger.info("Updating all sector leaders...")

        # Get all sectors
        sectors = self.storage.get_all_sectors()

        total_updated = 0
        for sector in sectors:
            try:
                leaders = self.identify_leaders(
                    sector['sector_id'],
                    sector['sector_name']
                )

                if leaders:
                    self.storage.save_sector_leaders(sector['sector_id'], leaders)
                    total_updated += 1

            except Exception as e:
                Logger.error(f"Failed to update leaders for {sector['sector_name']}: {str(e)}")

        Logger.info(f"Updated leaders for {total_updated}/{len(sectors)} sectors")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_sector.py -v`

Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add analysis/sector.py tests/test_sector.py
git commit -m "feat: implement SectorAnalyzer with leader identification"
```

---

## Verification Steps

After completing all tasks:

1. **Run all tests**:
   ```bash
   pytest tests/ -v
   ```
   Expected: 70+ tests passing (48 from Stage 1 + new tests)

2. **Verify module imports**:
   ```python
   python -c "from data.fetcher import DataFetcher; from data.storage import StockStorage; from analysis.indicators import IndicatorCalculator; from analysis.sector import SectorAnalyzer; print('All imports successful')"
   ```

3. **Test data fetching** (requires network):
   ```python
   from data.fetcher import DataFetcher
   fetcher = DataFetcher()
   df = fetcher.get_industry_sectors()
   print(f"Fetched {len(df)} industry sectors")
   ```

4. **Test database operations**:
   ```python
   from data.database import DatabaseManager
   from data.storage import StockStorage
   db = DatabaseManager()
   db.create_tables()
   storage = StockStorage(db)
   print("Database initialized successfully")
   ```

5. **Test indicator calculation**:
   ```python
   import pandas as pd
   from analysis.indicators import IndicatorCalculator
   df = pd.DataFrame({'close': [10+i*0.5 for i in range(30)]})
   result = IndicatorCalculator.calculate_all(df)
   print(f"Calculated {len([c for c in result.columns if c not in df.columns])} indicators")
   ```

---

## Integration Notes

**Dependencies on existing code:**
- Uses `Config` from `utils/config` for configuration
- Uses `Logger` from `utils/logger` for logging
- Uses `DataFetchException` and `StorageException` from `utils/exceptions`
- Uses `CacheManager` from `utils/cache` for API response caching
- Uses `DatabaseManager` from `data/database` (already implemented)

**Data flow:**
```
DataFetcher (akshare) → StockStorage (SQLite) → IndicatorCalculator (pandas-ta) → SectorAnalyzer
```

**Next Stage:** Stage 3 will implement feature engineering and prediction models using the data layer completed in this stage.