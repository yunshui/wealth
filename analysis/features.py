"""Feature engineering module for prediction models."""

import numpy as np
import pandas as pd
from typing import List
from sklearn.preprocessing import StandardScaler
from utils.logger import Logger

# Label mapping
HOLD = 0
BUY = 1
SELL = 2

# Action mapping for consistency with storage
LABEL_TO_ACTION = {0: 'hold', 1: 'buy', 2: 'sell'}
ACTION_TO_LABEL = {'hold': 0, 'buy': 1, 'sell': 2}


class FeatureEngineer:
    """Feature engineer for extracting features from stock data.

    Extracts different sets of features for different prediction horizons:
    - Short-term (1-5 days): Recent price action, volume, indicators
    - Medium-term (1-3 months): Trends, moving averages, momentum
    - Long-term (3+ months): Value, long-term trends, fundamentals
    """

    @staticmethod
    def extract_short_term_features(df: pd.DataFrame, lookback: int = 20) -> np.ndarray:
        """Extract short-term features for 1-5 day prediction.

        Args:
            df: DataFrame with OHLCV and indicator columns
            lookback: Number of recent days to use

        Returns:
            Feature vector (if single row) or feature matrix
        """
        if df.empty or len(df) < lookback:
            Logger.warning("Insufficient data for short-term features")
            return np.zeros(1)

        # Use last `lookback` days
        recent_df = df.tail(lookback)

        features = []

        # Price features (last row values)
        features.extend(FeatureEngineer.extract_price_features(recent_df))

        # Volume features
        features.extend(FeatureEngineer.extract_volume_features(recent_df))

        # Indicator features
        features.extend(FeatureEngineer.extract_indicator_features(recent_df))

        return np.array(features)

    @staticmethod
    def extract_medium_term_features(df: pd.DataFrame, lookback: int = 120) -> np.ndarray:
        """Extract medium-term features for 1-3 month prediction.

        Args:
            df: DataFrame with OHLCV and indicator columns
            lookback: Number of recent days to use

        Returns:
            Feature vector
        """
        if df.empty or len(df) < lookback:
            Logger.warning("Insufficient data for medium-term features")
            return np.zeros(1)

        recent_df = df.tail(lookback)

        features = []

        # Price features over medium term
        features.extend(FeatureEngineer.extract_price_features(recent_df))

        # Volume features
        features.extend(FeatureEngineer.extract_volume_features(recent_df))

        # Indicator features
        features.extend(FeatureEngineer.extract_indicator_features(recent_df))

        # Medium-term specific features
        if 'close' in recent_df.columns and len(recent_df) > 20:
            # 20-day momentum
            momentum_20 = (recent_df['close'].iloc[-1] / recent_df['close'].iloc[-20] - 1)
            features.append(momentum_20)

            # 60-day momentum
            if len(recent_df) > 60:
                momentum_60 = (recent_df['close'].iloc[-1] / recent_df['close'].iloc[-60] - 1)
                features.append(momentum_60)
            else:
                features.append(0)

        return np.array(features)

    @staticmethod
    def extract_long_term_features(df: pd.DataFrame) -> np.ndarray:
        """Extract long-term features for 3+ month prediction.

        Args:
            df: DataFrame with OHLCV and indicator columns

        Returns:
            Feature vector
        """
        if df.empty or len(df) < 60:
            Logger.warning("Insufficient data for long-term features")
            return np.zeros(1)

        features = []

        # Price features
        features.extend(FeatureEngineer.extract_price_features(df))

        # Volume features
        features.extend(FeatureEngineer.extract_volume_features(df))

        # Indicator features
        features.extend(FeatureEngineer.extract_indicator_features(df))

        # Long-term specific features
        if 'close' in df.columns and len(df) > 120:
            # 120-day momentum
            momentum_120 = (df['close'].iloc[-1] / df['close'].iloc[-120] - 1)
            features.append(momentum_120)

            # Distance from 52-week high/low
            high_252 = df['close'].tail(252).max() if len(df) > 252 else df['close'].max()
            low_252 = df['close'].tail(252).min() if len(df) > 252 else df['close'].min()

            if high_252 > low_252:
                high_distance = (df['close'].iloc[-1] - low_252) / (high_252 - low_252)
            else:
                high_distance = 0.5
            features.append(high_distance)

        return np.array(features)

    @staticmethod
    def extract_price_features(df: pd.DataFrame) -> List[float]:
        """Extract price-related features.

        Args:
            df: DataFrame with price columns

        Returns:
            List of price features (always same length: 9 features)
        """
        features = []

        # Expected 9 price features
        # 1. Current price
        if 'close' in df.columns:
            features.append(float(df['close'].iloc[-1]))
        else:
            features.append(0.0)

        # 2. 1-day return
        if 'close' in df.columns and len(df) > 1:
            ret_1 = (df['close'].iloc[-1] / df['close'].iloc[-2] - 1)
            features.append(float(ret_1))
        else:
            features.append(0.0)

        # 3. 5-day return
        if 'close' in df.columns and len(df) > 5:
            ret_5 = (df['close'].iloc[-1] / df['close'].iloc[-5] - 1)
            features.append(float(ret_5))
        else:
            features.append(0.0)

        # 4. 10-day return
        if 'close' in df.columns and len(df) > 10:
            ret_10 = (df['close'].iloc[-1] / df['close'].iloc[-10] - 1)
            features.append(float(ret_10))
        else:
            features.append(0.0)

        # 5. Volatility
        if 'close' in df.columns and len(df) > 10:
            returns = df['close'].pct_change().dropna()
            volatility = returns.tail(10).std()
            features.append(float(volatility) if not pd.isna(volatility) else 0.0)
        else:
            features.append(0.0)

        # 6. OHLC ratio
        if all(col in df.columns for col in ['open', 'close']) and len(df) > 0:
            ohlc_ratio = (df['close'].iloc[-1] - df['open'].iloc[-1]) / df['open'].iloc[-1]
            features.append(float(ohlc_ratio))
        else:
            features.append(0.0)

        # 7. HL ratio
        if all(col in df.columns for col in ['high', 'low', 'close']) and len(df) > 0:
            hl_ratio = (df['high'].iloc[-1] - df['low'].iloc[-1]) / df['low'].iloc[-1]
            features.append(float(hl_ratio))
        else:
            features.append(0.0)

        # 8. Open price
        if 'open' in df.columns:
            features.append(float(df['open'].iloc[-1]))
        else:
            features.append(0.0)

        # 9. High price
        if 'high' in df.columns:
            features.append(float(df['high'].iloc[-1]))
        else:
            features.append(0.0)

        return features

    @staticmethod
    def extract_volume_features(df: pd.DataFrame) -> List[float]:
        """Extract volume-related features.

        Args:
            df: DataFrame with volume column

        Returns:
            List of volume features (always same length: 3 features)
        """
        features = []

        # 1. Current volume
        if 'volume' in df.columns:
            features.append(float(df['volume'].iloc[-1]))
        else:
            features.append(0.0)

        # 2. Volume ratio vs average
        if 'volume' in df.columns and len(df) > 10:
            avg_volume = df['volume'].tail(10).mean()
            vol_ratio = df['volume'].iloc[-1] / avg_volume if avg_volume > 0 else 1.0
            features.append(float(vol_ratio))
        else:
            features.append(1.0)

        # 3. Volume trend
        if 'volume' in df.columns and len(df) > 10:
            recent_vol = df['volume'].tail(5).mean()
            earlier_vol = df['volume'].tail(10).head(5).mean()
            vol_trend = (recent_vol - earlier_vol) / earlier_vol if earlier_vol > 0 else 0.0
            features.append(float(vol_trend))
        else:
            features.append(0.0)

        return features

    @staticmethod
    def extract_indicator_features(df: pd.DataFrame) -> List[float]:
        """Extract technical indicator features.

        Args:
            df: DataFrame with indicator columns

        Returns:
            List of indicator features (always same length)
        """
        features = []

        # Define expected indicator columns to ensure consistent feature count
        expected_indicators = [
            'ma5', 'ma10', 'ma20', 'ma60',
            'macd', 'macd_signal', 'macd_hist',
            'kdj_k', 'kdj_d', 'kdj_j',
            'rsi6', 'rsi12', 'rsi24',
            'boll_upper', 'boll_mid', 'boll_lower',
            'obv'
        ]

        # Extract each indicator, defaulting to 0 if missing or NaN
        for indicator in expected_indicators:
            if indicator in df.columns:
                val = df[indicator].iloc[-1]
                if pd.isna(val):
                    features.append(0.0)
                else:
                    features.append(float(val))
            else:
                features.append(0.0)

        return features

    @staticmethod
    def create_labels(df: pd.DataFrame, horizon: int, threshold: float = 0.03) -> np.ndarray:
        """Create labels for supervised learning.

        Args:
            df: DataFrame with 'close' column
            horizon: Number of days ahead to predict
            threshold: Return threshold for buy/sell classification

        Returns:
            Labels array (0=hold, 1=buy, 2=sell)
        """
        if 'close' not in df.columns:
            raise ValueError("DataFrame must contain 'close' column")

        labels = np.full(len(df), HOLD)

        for i in range(len(df) - horizon):
            current_price = df['close'].iloc[i]
            future_price = df['close'].iloc[i + horizon]

            if pd.isna(current_price) or pd.isna(future_price):
                labels[i] = HOLD
                continue

            return_pct = (future_price - current_price) / current_price

            if return_pct > threshold:
                labels[i] = BUY
            elif return_pct < -threshold:
                labels[i] = SELL
            else:
                labels[i] = HOLD

        # Last `horizon` rows cannot have labels
        labels[-horizon:] = HOLD

        return labels

    @staticmethod
    def normalize_features(X: np.ndarray) -> np.ndarray:
        """Normalize features using standard scaling.

        Args:
            X: Feature matrix

        Returns:
            Normalized feature matrix
        """
        if X.size == 0:
            return X

        # Handle 1D case
        if X.ndim == 1:
            X = X.reshape(1, -1)

        # Replace NaN with 0
        X = np.nan_to_num(X)

        # Standardize
        scaler = StandardScaler()
        X_normalized = scaler.fit_transform(X)

        return X_normalized