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
        # Avoid unnecessary copy - modify in place if possible
        for period in periods:
            col_name = f'ma{period}'
            df[col_name] = df['close'].rolling(window=period).mean()
        return df

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
            macd = ta.macd(df['close'], fast=fast, slow=slow, signal=signal)
            df['macd'] = macd[f'MACD_{fast}_{slow}_{signal}']
            df['macd_signal'] = macd[f'MACDs_{fast}_{slow}_{signal}']
            df['macd_hist'] = macd[f'MACDh_{fast}_{slow}_{signal}']
            return df
        except ImportError:
            Logger.warning("pandas-ta not available, using manual MACD calculation")
            return IndicatorCalculator._calculate_macd_manual(df, fast, slow, signal)

    @staticmethod
    def _calculate_macd_manual(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
        """Manual MACD calculation when pandas-ta is not available."""
        # Calculate EMAs in-place for efficiency
        ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['close'].ewm(span=slow, adjust=False).mean()

        df['macd'] = ema_fast - ema_slow
        df['macd_signal'] = df['macd'].ewm(span=signal, adjust=False).mean()
        df['macd_hist'] = df['macd'] - df['macd_signal']

        return df

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
        # Calculate RSV (Raw Stochastic Value)
        low_min = df['low'].rolling(window=k).min()
        high_max = df['high'].rolling(window=k).max()
        rsv = (df['close'] - low_min) / (high_max - low_min) * 100
        rsv = rsv.fillna(50)  # Handle NaN

        # Calculate K, D, J values in-place
        df['kdj_k'] = rsv.ewm(com=2, adjust=False).mean()
        df['kdj_d'] = df['kdj_k'].ewm(com=2, adjust=False).mean()
        df['kdj_j'] = 3 * df['kdj_k'] - 2 * df['kdj_d']

        return df

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
            for period in periods:
                col_name = f'rsi{period}'
                df[col_name] = ta.rsi(df['close'], length=period)
            return df
        except ImportError:
            Logger.warning("pandas-ta not available, using manual RSI calculation")
            return IndicatorCalculator._calculate_rsi_manual(df, periods)

    @staticmethod
    def _calculate_rsi_manual(df: pd.DataFrame, periods: List[int] = [6, 12, 24]) -> pd.DataFrame:
        """Manual RSI calculation when pandas-ta is not available."""
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=12).mean()  # Use max period for efficiency
        loss = (-delta.where(delta < 0, 0)).rolling(window=12).mean()

        for period in periods:
            rs = gain / loss
            col_name = f'rsi{period}'
            df[col_name] = 100 - (100 / (1 + rs))

        return df

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
        df['boll_middle'] = df['close'].rolling(window=period).mean()
        rolling_std = df['close'].rolling(window=period).std()
        df['boll_upper'] = df['boll_middle'] + (rolling_std * std)
        df['boll_lower'] = df['boll_middle'] - (rolling_std * std)

        return df

    @staticmethod
    def calculate_obv(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate OBV (On-Balance Volume) indicator.

        Args:
            df: DataFrame with 'close' and 'volume' columns

        Returns:
            DataFrame with OBV values
        """
        # Calculate OBV in-place for efficiency
        obv = (np.sign(df['close'].diff()) * df['volume']).fillna(0).cumsum()
        df['obv'] = obv

        return df

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

        # Calculate all indicators in-place for efficiency
        IndicatorCalculator.calculate_ma(df, [5, 10, 20, 60])
        IndicatorCalculator.calculate_macd(df)
        IndicatorCalculator.calculate_kdj(df)
        IndicatorCalculator.calculate_rsi(df, [6, 12, 24])
        IndicatorCalculator.calculate_boll(df)
        IndicatorCalculator.calculate_obv(df)

        Logger.info("Technical indicators calculated successfully")
        return df
        result = IndicatorCalculator.calculate_obv(result)

        Logger.info("Technical indicators calculated successfully")
        return result