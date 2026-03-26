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