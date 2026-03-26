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