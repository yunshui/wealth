# Stage 3 Prediction Layer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the prediction layer with feature engineering, three prediction models (short/medium/long term), ensemble integration, and model training using Random Forest.

**Architecture:**
- FeatureEngineer extracts features from stock data for different time horizons
- Three separate predictors (ShortTermPredictor, MediumTermPredictor, LongTermPredictor) inherit from BasePredictor
- EnsemblePredictor combines predictions with configurable weights (30%/40%/30%)
- ModelTrainer handles data preparation, training, and evaluation

**Tech Stack:**
- scikit-learn (RandomForestClassifier for predictions)
- pandas/numpy for data manipulation
- StandardScaler for feature normalization
- pickle for model persistence

---

## File Structure

### Files to Create/Modify:
- **Modify**: `prediction/base.py` - Implement BasePredictor abstract class
- **Modify**: `analysis/features.py` - Implement FeatureEngineer class
- **Modify**: `prediction/short_term.py` - Implement ShortTermPredictor
- **Modify**: `prediction/medium_term.py` - Implement MediumTermPredictor
- **Modify**: `prediction/long_term.py` - Implement LongTermPredictor
- **Modify**: `prediction/ensemble.py` - Implement EnsemblePredictor
- **Modify**: `prediction/trainer.py` - Implement ModelTrainer
- **Create**: `tests/test_features.py` - Tests for FeatureEngineer
- **Create**: `tests/test_predictors.py` - Tests for predictors
- **Create**: `tests/test_ensemble.py` - Tests for ensemble
- **Create**: `tests/test_trainer.py` - Tests for trainer

**Note**: `utils/exceptions.py` already exists with WealthException and ModelException classes.

---

## Task 1: Implement BasePredictor

**Files:**
- Modify: `prediction/base.py`
- Test: `tests/test_predictors.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_predictors.py
import pytest
import numpy as np
from prediction.base import BasePredictor
from utils.exceptions import ModelException

def test_base_predictor_is_abstract():
    """Test that BasePredictor cannot be instantiated directly"""
    with pytest.raises(TypeError):
        BasePredictor()

def test_base_predictor_methods_are_abstract():
    """Test that abstract methods are defined"""
    class TestPredictor(BasePredictor):
        def __init__(self):
            super().__init__(model_path=None)
            self.model = None

        def train(self, X, y):
            pass

        def predict(self, X):
            return np.array([1])

        def get_feature_importance(self):
            return {}

    predictor = TestPredictor()
    assert predictor.is_trained() == False
    assert predictor.get_version() == "1.0.0"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_predictors.py::test_base_predictor_is_abstract -v`
Expected: FAIL with "BasePredictor abstract methods not implemented"

- [ ] **Step 3: Write minimal implementation**

```python
# prediction/base.py
"""Base predictor module for all prediction models."""

from abc import ABC, abstractmethod
from typing import Dict, Any
import numpy as np
import pickle
import os
from utils.logger import Logger
from utils.exceptions import ModelException
from utils.config import Config

MODEL_VERSION = "1.0.0"


class BasePredictor(ABC):
    """Abstract base class for all prediction models.

    All specific predictors (short, medium, long term) inherit from this class
    and must implement the abstract methods.
    """

    def __init__(self, model_path: str = None):
        """Initialize predictor.

        Args:
            model_path: Optional path to load model from
        """
        self.model = None
        self.model_path = model_path
        self.is_loaded = False
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
            Logger.info(f"Loaded model from {model_path}")

    @abstractmethod
    def train(self, X: np.ndarray, y: np.ndarray) -> None:
        """Train the model.

        Args:
            X: Feature matrix of shape (n_samples, n_features)
            y: Target labels of shape (n_samples,)
        """
        pass

    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions.

        Args:
            X: Feature matrix of shape (n_samples, n_features)

        Returns:
            Predicted labels (0=hold, 1=buy, 2=sell)
        """
        pass

    @abstractmethod
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores.

        Returns:
            Dictionary mapping feature names to importance scores
        """
        pass

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict class probabilities.

        Args:
            X: Feature matrix of shape (n_samples, n_features)

        Returns:
            Probability array of shape (n_samples, n_classes)
        """
        if not self.is_trained():
            raise ModelException("Model not trained. Call train() first.")
        return self.model.predict_proba(X)

    def save_model(self, path: str) -> None:
        """Save model to file.

        Args:
            path: Path to save model file
        """
        if not self.is_trained():
            raise ModelException("Cannot save untrained model")

        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            pickle.dump(self.model, f)
        Logger.info(f"Model saved to {path}")

    def load_model(self, path: str) -> None:
        """Load model from file.

        Args:
            path: Path to load model file from
        """
        if not os.path.exists(path):
            raise ModelException(f"Model file not found: {path}")

        with open(path, 'rb') as f:
            self.model = pickle.load(f)
        self.is_loaded = True
        self.model_path = path
        Logger.info(f"Model loaded from {path}")

    def is_trained(self) -> bool:
        """Check if model is trained.

        Returns:
            True if model is trained, False otherwise
        """
        return self.model is not None

    def get_version(self) -> str:
        """Get model version.

        Returns:
            Version string
        """
        return MODEL_VERSION
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_predictors.py::test_base_predictor_is_abstract tests/test_predictors.py::test_base_predictor_methods_are_abstract -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add prediction/base.py tests/test_predictors.py
git commit -m "feat: implement BasePredictor abstract class"
```

---

## Task 2: Implement FeatureEngineer

**Files:**
- Modify: `analysis/features.py`
- Test: `tests/test_features.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_features.py
import pytest
import pandas as pd
import numpy as np
from analysis.features import FeatureEngineer

def test_extract_price_features():
    """Test price feature extraction"""
    df = pd.DataFrame({
        'close': [10, 11, 12, 13, 14, 15],
        'open': [9.5, 10.5, 11.5, 12.5, 13.5, 14.5]
    })
    features = FeatureEngineer.extract_price_features(df)
    assert features is not None
    assert len(features) > 0

def test_extract_volume_features():
    """Test volume feature extraction"""
    df = pd.DataFrame({
        'volume': [10000, 12000, 11000, 13000, 14000, 15000],
        'close': [10, 11, 12, 13, 14, 15]
    })
    features = FeatureEngineer.extract_volume_features(df)
    assert features is not None
    assert len(features) > 0

def test_extract_indicator_features():
    """Test indicator feature extraction"""
    df = pd.DataFrame({
        'ma5': [10.0, 10.5, 11.0, 11.5, 12.0, 12.5],
        'ma20': [9.5, 9.6, 9.7, 9.8, 9.9, 10.0],
        'macd': [0.1, 0.2, 0.3, 0.4, 0.5, 0.6],
        'rsi6': [50, 55, 60, 65, 70, 75],
        'kdj_k': [50, 55, 60, 65, 70, 75]
    })
    features = FeatureEngineer.extract_indicator_features(df)
    assert features is not None
    assert len(features) > 0

def test_extract_short_term_features():
    """Test short-term feature extraction"""
    dates = pd.date_range('2024-01-01', periods=30)
    df = pd.DataFrame({
        'date': dates.strftime('%Y-%m-%d'),
        'open': [10 + i * 0.1 for i in range(30)],
        'high': [10.5 + i * 0.1 for i in range(30)],
        'low': [9.5 + i * 0.1 for i in range(30)],
        'close': [10 + i * 0.1 for i in range(30)],
        'volume': [10000 + i * 100 for i in range(30)]
    })
    features = FeatureEngineer.extract_short_term_features(df)
    assert features is not None
    assert len(features) > 0

def test_create_labels():
    """Test label creation"""
    dates = pd.date_range('2024-01-01', periods=30)
    df = pd.DataFrame({
        'date': dates.strftime('%Y-%m-%d'),
        'close': [10 + i * 0.1 for i in range(30)]
    })
    labels = FeatureEngineer.create_labels(df, horizon=5)
    assert labels is not None
    assert len(labels) == len(df) - 5  # Last 5 days have no labels

def test_normalize_features():
    """Test feature normalization"""
    X = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]], dtype=float)
    normalized = FeatureEngineer.normalize_features(X)
    assert normalized is not None
    assert normalized.shape == X.shape
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_features.py -v`
Expected: FAIL with "FeatureEngineer methods not implemented"

- [ ] **Step 3: Write minimal implementation**

```python
# analysis/features.py
"""Feature engineering module for prediction models."""

import numpy as np
import pandas as pd
from typing import List, Tuple
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

            high_distance = (df['close'].iloc[-1] - low_252) / (high_252 - low_252)
            features.append(high_distance)

        return np.array(features)

    @staticmethod
    def extract_price_features(df: pd.DataFrame) -> List[float]:
        """Extract price-related features.

        Args:
            df: DataFrame with price columns

        Returns:
            List of price features
        """
        features = []

        if 'close' in df.columns:
            # Current price
            features.append(df['close'].iloc[-1])

            # Returns over different periods
            if len(df) > 1:
                # 1-day return
                ret_1 = (df['close'].iloc[-1] / df['close'].iloc[-2] - 1)
                features.append(ret_1)

                # 5-day return
                if len(df) > 5:
                    ret_5 = (df['close'].iloc[-1] / df['close'].iloc[-5] - 1)
                    features.append(ret_5)
                else:
                    features.append(0)

                # 10-day return
                if len(df) > 10:
                    ret_10 = (df['close'].iloc[-1] / df['close'].iloc[-10] - 1)
                    features.append(ret_10)
                else:
                    features.append(0)

            # Volatility (rolling std of returns)
            if len(df) > 10:
                returns = df['close'].pct_change().dropna()
                volatility = returns.tail(10).std()
                features.append(volatility)
            else:
                features.append(0)

        # Open/High/Low ratios
        if all(col in df.columns for col in ['open', 'high', 'low', 'close']):
            ohlc_ratio = (df['close'].iloc[-1] - df['open'].iloc[-1]) / df['open'].iloc[-1]
            features.append(ohlc_ratio)

            hl_ratio = (df['high'].iloc[-1] - df['low'].iloc[-1]) / df['low'].iloc[-1]
            features.append(hl_ratio)

        return features

    @staticmethod
    def extract_volume_features(df: pd.DataFrame) -> List[float]:
        """Extract volume-related features.

        Args:
            df: DataFrame with volume column

        Returns:
            List of volume features
        """
        features = []

        if 'volume' in df.columns:
            # Current volume
            features.append(df['volume'].iloc[-1])

            # Volume ratio vs average
            if len(df) > 10:
                avg_volume = df['volume'].tail(10).mean()
                vol_ratio = df['volume'].iloc[-1] / avg_volume if avg_volume > 0 else 1
                features.append(vol_ratio)
            else:
                features.append(1)

            # Volume trend
            if len(df) > 5:
                recent_vol = df['volume'].tail(5).mean()
                earlier_vol = df['volume'].tail(10).head(5).mean()
                vol_trend = (recent_vol - earlier_vol) / earlier_vol if earlier_vol > 0 else 0
                features.append(vol_trend)
            else:
                features.append(0)

        return features

    @staticmethod
    def extract_indicator_features(df: pd.DataFrame) -> List[float]:
        """Extract technical indicator features.

        Args:
            df: DataFrame with indicator columns

        Returns:
            List of indicator features
        """
        features = []

        # Moving averages
        ma_cols = [col for col in df.columns if col.startswith('ma')]
        for ma_col in ma_cols:
            if ma_col in df.columns and not pd.isna(df[ma_col].iloc[-1]):
                features.append(df[ma_col].iloc[-1])

        # MACD
        if 'macd' in df.columns and not pd.isna(df['macd'].iloc[-1]):
            features.append(df['macd'].iloc[-1])
        if 'macd_signal' in df.columns and not pd.isna(df['macd_signal'].iloc[-1]):
            features.append(df['macd_signal'].iloc[-1])
        if 'macd_hist' in df.columns and not pd.isna(df['macd_hist'].iloc[-1]):
            features.append(df['macd_hist'].iloc[-1])

        # KDJ
        kdj_cols = [col for col in df.columns if col.startswith('kdj_')]
        for kdj_col in kdj_cols:
            if kdj_col in df.columns and not pd.isna(df[kdj_col].iloc[-1]):
                features.append(df[kdj_col].iloc[-1])

        # RSI
        rsi_cols = [col for col in df.columns if col.startswith('rsi')]
        for rsi_col in rsi_cols:
            if rsi_col in df.columns and not pd.isna(df[rsi_col].iloc[-1]):
                features.append(df[rsi_col].iloc[-1])

        # Bollinger Bands
        boll_cols = [col for col in df.columns if col.startswith('boll_')]
        for boll_col in boll_cols:
            if boll_col in df.columns and not pd.isna(df[boll_col].iloc[-1]):
                features.append(df[boll_col].iloc[-1])

        # OBV
        if 'obv' in df.columns and not pd.isna(df['obv'].iloc[-1]):
            features.append(df['obv'].iloc[-1])

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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_features.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add analysis/features.py tests/test_features.py
git commit -m "feat: implement FeatureEngineer class"
```

---

## Task 3: Implement ShortTermPredictor

**Files:**
- Modify: `prediction/short_term.py`
- Test: `tests/test_predictors.py`

- [ ] **Step 1: Write the failing test**

```python
# Add to tests/test_predictors.py
from prediction.short_term import ShortTermPredictor

def test_short_term_predictor_initialization():
    """Test ShortTermPredictor initialization"""
    predictor = ShortTermPredictor()
    assert predictor.model_type == 'random_forest'
    assert predictor.horizon == 'short'

def test_short_term_predictor_train_and_predict():
    """Test ShortTermPredictor training and prediction"""
    predictor = ShortTermPredictor()

    # Create dummy data
    X = np.random.rand(100, 20)
    y = np.random.randint(0, 3, 100)

    predictor.train(X, y)

    # Make predictions
    X_test = np.random.rand(10, 20)
    predictions = predictor.predict(X_test)

    assert len(predictions) == 10
    assert all(p in [0, 1, 2] for p in predictions)

def test_short_term_predictor_feature_importance():
    """Test getting feature importance"""
    predictor = ShortTermPredictor()

    X = np.random.rand(100, 20)
    y = np.random.randint(0, 3, 100)

    predictor.train(X, y)

    importance = predictor.get_feature_importance()
    assert importance is not None
    assert len(importance) > 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_predictors.py::test_short_term_predictor_initialization -v`
Expected: FAIL with "ShortTermPredictor not implemented"

- [ ] **Step 3: Write minimal implementation**

```python
# prediction/short_term.py
"""Short-term prediction model (1-5 days)."""

from typing import Dict, List
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

from prediction.base import BasePredictor, MODEL_VERSION
from analysis.features import FeatureEngineer, LABEL_TO_ACTION
from utils.logger import Logger


class ShortTermPredictor(BasePredictor):
    """Short-term predictor for 1-5 day predictions.

    Uses recent price action, volume, and technical indicators
    to predict short-term price movements.

    Default model: RandomForestClassifier
    Alternative models: LogisticRegression
    """

    def __init__(self, model_type: str = 'random_forest', model_path: str = None):
        """Initialize short-term predictor.

        Args:
            model_type: Type of model ('random_forest' or 'logistic')
            model_path: Optional path to load model from
        """
        super().__init__(model_path)
        self.model_type = model_type
        self.horizon = 'short'
        self._init_model()

    def _init_model(self):
        """Initialize the underlying model."""
        if self.model_type == 'random_forest':
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )
            Logger.info("Initialized Random Forest model for short-term prediction")
        elif self.model_type == 'logistic':
            self.model = LogisticRegression(
                max_iter=1000,
                random_state=42,
                n_jobs=-1
            )
            Logger.info("Initialized Logistic Regression model for short-term prediction")
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")

    def train(self, X: np.ndarray, y: np.ndarray, test_size: float = 0.2) -> Dict[str, float]:
        """Train the model.

        Args:
            X: Feature matrix
            y: Target labels (0=hold, 1=buy, 2=sell)
            test_size: Proportion of data for testing

        Returns:
            Training metrics dictionary
        """
        Logger.info(f"Training short-term model with {len(X)} samples")

        # Normalize features
        X_normalized = FeatureEngineer.normalize_features(X)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_normalized, y, test_size=test_size, random_state=42, stratify=y
        )

        # Train model
        self.model.fit(X_train, y_train)

        # Evaluate
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)

        Logger.info(f"Short-term model trained. Test accuracy: {accuracy:.3f}")

        return {
            'accuracy': accuracy,
            'train_samples': len(X_train),
            'test_samples': len(X_test)
        }

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions.

        Args:
            X: Feature matrix

        Returns:
            Predicted labels (0=hold, 1=buy, 2=sell)
        """
        if not self.is_trained():
            raise ValueError("Model not trained. Call train() first.")

        # Normalize features
        X_normalized = FeatureEngineer.normalize_features(X)

        return self.model.predict(X_normalized)

    def predict_with_confidence(self, X: np.ndarray) -> np.ndarray:
        """Make predictions with confidence scores.

        Args:
            X: Feature matrix

        Returns:
            Predicted labels (0=hold, 1=buy, 2=sell)
        """
        if not self.is_trained():
            raise ValueError("Model not trained. Call train() first.")

        # Normalize features
        X_normalized = FeatureEngineer.normalize_features(X)

        predictions = self.model.predict(X_normalized)
        proba = self.model.predict_proba(X_normalized)

        # Get confidence as max probability
        confidence = np.max(proba, axis=1)

        return predictions, confidence

    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores.

        Returns:
            Dictionary mapping feature indices to importance scores
        """
        if not self.is_trained():
            return {}

        if hasattr(self.model, 'feature_importances_'):
            importances = self.model.feature_importances_
            return {f'feature_{i}': float(imp) for i, imp in enumerate(importances)}
        else:
            Logger.warning("Model does not support feature importance")
            return {}

    def generate_reasoning(self, features: np.ndarray, prediction: int, confidence: float) -> List[str]:
        """Generate human-readable reasoning for prediction.

        Args:
            features: Feature vector
            prediction: Predicted label (0=hold, 1=buy, 2=sell)
            confidence: Confidence score

        Returns:
            List of reasoning strings
        """
        reasoning = []

        action = LABEL_TO_ACTION.get(prediction, 'hold')
        reasoning.append(f"短期预测({confidence:.1%}置信度): {action}")

        # Get feature importance for top features
        importance = self.get_feature_importance()
        if importance:
            # Sort by importance
            sorted_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)
            top_features = sorted_features[:3]

            # Add reasoning based on top features
            for feat_name, imp in top_features:
                if imp > 0.1:
                    reasoning.append(f"关键特征: {feat_name}")

        return reasoning
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_predictors.py::test_short_term_predictor_initialization tests/test_predictors.py::test_short_term_predictor_train_and_predict tests/test_predictors.py::test_short_term_predictor_feature_importance -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add prediction/short_term.py tests/test_predictors.py
git commit -m "feat: implement ShortTermPredictor"
```

---

## Task 4: Implement MediumTermPredictor

**Files:**
- Modify: `prediction/medium_term.py`
- Test: `tests/test_predictors.py`

- [ ] **Step 1: Write the failing test**

```python
# Add to tests/test_predictors.py
from prediction.medium_term import MediumTermPredictor

def test_medium_term_predictor_initialization():
    """Test MediumTermPredictor initialization"""
    predictor = MediumTermPredictor()
    assert predictor.model_type == 'random_forest'
    assert predictor.horizon == 'medium'

def test_medium_term_predictor_train_and_predict():
    """Test MediumTermPredictor training and prediction"""
    predictor = MediumTermPredictor()

    X = np.random.rand(100, 25)
    y = np.random.randint(0, 3, 100)

    predictor.train(X, y)

    X_test = np.random.rand(10, 25)
    predictions = predictor.predict(X_test)

    assert len(predictions) == 10
    assert all(p in [0, 1, 2] for p in predictions)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_predictors.py::test_medium_term_predictor_initialization -v`
Expected: FAIL with "MediumTermPredictor not implemented"

- [ ] **Step 3: Write minimal implementation**

```python
# prediction/medium_term.py
"""Medium-term prediction model (1-3 months)."""

from typing import Dict, List
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from prediction.base import BasePredictor, MODEL_VERSION
from analysis.features import FeatureEngineer, LABEL_TO_ACTION
from utils.logger import Logger


class MediumTermPredictor(BasePredictor):
    """Medium-term predictor for 1-3 month predictions.

    Uses medium-term trends, moving averages, and momentum
    to predict medium-term price movements.

    Default model: RandomForestClassifier with deeper trees
    """

    def __init__(self, model_type: str = 'random_forest', model_path: str = None):
        """Initialize medium-term predictor.

        Args:
            model_type: Type of model ('random_forest' or 'logistic')
            model_path: Optional path to load model from
        """
        super().__init__(model_path)
        self.model_type = model_type
        self.horizon = 'medium'
        self._init_model()

    def _init_model(self):
        """Initialize the underlying model."""
        if self.model_type == 'random_forest':
            self.model = RandomForestClassifier(
                n_estimators=150,
                max_depth=15,
                min_samples_split=10,
                min_samples_leaf=4,
                random_state=42,
                n_jobs=-1
            )
            Logger.info("Initialized Random Forest model for medium-term prediction")
        elif self.model_type == 'logistic':
            self.model = LogisticRegression(
                max_iter=1000,
                random_state=42,
                n_jobs=-1
            )
            Logger.info("Initialized Logistic Regression model for medium-term prediction")
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")

    def train(self, X: np.ndarray, y: np.ndarray, test_size: float = 0.2) -> Dict[str, float]:
        """Train the model.

        Args:
            X: Feature matrix
            y: Target labels (0=hold, 1=buy, 2=sell)
            test_size: Proportion of data for testing

        Returns:
            Training metrics dictionary
        """
        Logger.info(f"Training medium-term model with {len(X)} samples")

        # Normalize features
        X_normalized = FeatureEngineer.normalize_features(X)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_normalized, y, test_size=test_size, random_state=42, stratify=y
        )

        # Train model
        self.model.fit(X_train, y_train)

        # Evaluate
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)

        Logger.info(f"Medium-term model trained. Test accuracy: {accuracy:.3f}")

        return {
            'accuracy': accuracy,
            'train_samples': len(X_train),
            'test_samples': len(X_test)
        }

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions.

        Args:
            X: Feature matrix

        Returns:
            Predicted labels (0=hold, 1=buy, 2=sell)
        """
        if not self.is_trained():
            raise ValueError("Model not trained. Call train() first.")

        # Normalize features
        X_normalized = FeatureEngineer.normalize_features(X)

        return self.model.predict(X_normalized)

    def predict_with_confidence(self, X: np.ndarray) -> tuple:
        """Make predictions with confidence scores.

        Args:
            X: Feature matrix

        Returns:
            Tuple of (predictions, confidence)
        """
        if not self.is_trained():
            raise ValueError("Model not trained. Call train() first.")

        # Normalize features
        X_normalized = FeatureEngineer.normalize_features(X)

        predictions = self.model.predict(X_normalized)
        proba = self.model.predict_proba(X_normalized)

        confidence = np.max(proba, axis=1)

        return predictions, confidence

    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores.

        Returns:
            Dictionary mapping feature indices to importance scores
        """
        if not self.is_trained():
            return {}

        if hasattr(self.model, 'feature_importances_'):
            importances = self.model.feature_importances_
            return {f'feature_{i}': float(imp) for i, imp in enumerate(importances)}
        else:
            Logger.warning("Model does not support feature importance")
            return {}

    def generate_reasoning(self, features: np.ndarray, prediction: int, confidence: float) -> List[str]:
        """Generate human-readable reasoning for prediction.

        Args:
            features: Feature vector
            prediction: Predicted label (0=hold, 1=buy, 2=sell)
            confidence: Confidence score

        Returns:
            List of reasoning strings
        """
        reasoning = []

        action = LABEL_TO_ACTION.get(prediction, 'hold')
        reasoning.append(f"中期预测({confidence:.1%}置信度): {action}")

        return reasoning
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_predictors.py::test_medium_term_predictor_initialization tests/test_predictors.py::test_medium_term_predictor_train_and_predict -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add prediction/medium_term.py tests/test_predictors.py
git commit -m "feat: implement MediumTermPredictor"
```

---

## Task 5: Implement LongTermPredictor

**Files:**
- Modify: `prediction/long_term.py`
- Test: `tests/test_predictors.py`

- [ ] **Step 1: Write the failing test**

```python
# Add to tests/test_predictors.py
from prediction.long_term import LongTermPredictor

def test_long_term_predictor_initialization():
    """Test LongTermPredictor initialization"""
    predictor = LongTermPredictor()
    assert predictor.model_type == 'random_forest'
    assert predictor.horizon == 'long'

def test_long_term_predictor_train_and_predict():
    """Test LongTermPredictor training and prediction"""
    predictor = LongTermPredictor()

    X = np.random.rand(100, 30)
    y = np.random.randint(0, 3, 100)

    predictor.train(X, y)

    X_test = np.random.rand(10, 30)
    predictions = predictor.predict(X_test)

    assert len(predictions) == 10
    assert all(p in [0, 1, 2] for p in predictions)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_predictors.py::test_long_term_predictor_initialization -v`
Expected: FAIL with "LongTermPredictor not implemented"

- [ ] **Step 3: Write minimal implementation**

```python
# prediction/long_term.py
"""Long-term prediction model (3+ months)."""

from typing import Dict, List
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from prediction.base import BasePredictor, MODEL_VERSION
from analysis.features import FeatureEngineer, LABEL_TO_ACTION
from utils.logger import Logger


class LongTermPredictor(BasePredictor):
    """Long-term predictor for 3+ month predictions.

    Uses long-term trends, value indicators, and fundamentals
    to predict long-term price movements.

    Default model: RandomForestClassifier with deeper trees
    """

    def __init__(self, model_type: str = 'random_forest', model_path: str = None):
        """Initialize long-term predictor.

        Args:
            model_type: Type of model ('random_forest' or 'logistic')
            model_path: Optional path to load model from
        """
        super().__init__(model_path)
        self.model_type = model_type
        self.horizon = 'long'
        self._init_model()

    def _init_model(self):
        """Initialize the underlying model."""
        if self.model_type == 'random_forest':
            self.model = RandomForestClassifier(
                n_estimators=200,
                max_depth=20,
                min_samples_split=10,
                min_samples_leaf=4,
                random_state=42,
                n_jobs=-1
            )
            Logger.info("Initialized Random Forest model for long-term prediction")
        elif self.model_type == 'logistic':
            self.model = LogisticRegression(
                max_iter=1000,
                random_state=42,
                n_jobs=-1
            )
            Logger.info("Initialized Logistic Regression model for long-term prediction")
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")

    def train(self, X: np.ndarray, y: np.ndarray, test_size: float = 0.2) -> Dict[str, float]:
        """Train the model.

        Args:
            X: Feature matrix
            y: Target labels (0=hold, 1=buy, 2=sell)
            test_size: Proportion of data for testing

        Returns:
            Training metrics dictionary
        """
        Logger.info(f"Training long-term model with {len(X)} samples")

        # Normalize features
        X_normalized = FeatureEngineer.normalize_features(X)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_normalized, y, test_size=test_size, random_state=42, stratify=y
        )

        # Train model
        self.model.fit(X_train, y_train)

        # Evaluate
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)

        Logger.info(f"Long-term model trained. Test accuracy: {accuracy:.3f}")

        return {
            'accuracy': accuracy,
            'train_samples': len(X_train),
            'test_samples': len(X_test)
        }

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions.

        Args:
            X: Feature matrix

        Returns:
            Predicted labels (0=hold, 1=buy, 2=sell)
        """
        if not self.is_trained():
            raise ValueError("Model not trained. Call train() first.")

        # Normalize features
        X_normalized = FeatureEngineer.normalize_features(X)

        return self.model.predict(X_normalized)

    def predict_with_confidence(self, X: np.ndarray) -> tuple:
        """Make predictions with confidence scores.

        Args:
            X: Feature matrix

        Returns:
            Tuple of (predictions, confidence)
        """
        if not self.is_trained():
            raise ValueError("Model not trained. Call train() first.")

        # Normalize features
        X_normalized = FeatureEngineer.normalize_features(X)

        predictions = self.model.predict(X_normalized)
        proba = self.model.predict_proba(X_normalized)

        confidence = np.max(proba, axis=1)

        return predictions, confidence

    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores.

        Returns:
            Dictionary mapping feature indices to importance scores
        """
        if not self.is_trained():
            return {}

        if hasattr(self.model, 'feature_importances_'):
            importances = self.model.feature_importances_
            return {f'feature_{i}': float(imp) for i, imp in enumerate(importances)}
        else:
            Logger.warning("Model does not support feature importance")
            return {}

    def generate_reasoning(self, features: np.ndarray, prediction: int, confidence: float) -> List[str]:
        """Generate human-readable reasoning for prediction.

        Args:
            features: Feature vector
            prediction: Predicted label (0=hold, 1=buy, 2=sell)
            confidence: Confidence score

        Returns:
            List of reasoning strings
        """
        reasoning = []

        action = LABEL_TO_ACTION.get(prediction, 'hold')
        reasoning.append(f"长期预测({confidence:.1%}置信度): {action}")

        return reasoning
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_predictors.py::test_long_term_predictor_initialization tests/test_predictors.py::test_long_term_predictor_train_and_predict -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add prediction/long_term.py tests/test_predictors.py
git commit -m "feat: implement LongTermPredictor"
```

---

## Task 6: Implement EnsemblePredictor

**Files:**
- Modify: `prediction/ensemble.py`
- Test: `tests/test_ensemble.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_ensemble.py
import pytest
import pandas as pd
import numpy as np
import tempfile
from prediction.ensemble import EnsemblePredictor
from data.storage import StockStorage
from data.database import DatabaseManager

@pytest.fixture
def temp_storage():
    """Create temporary storage for testing"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    db = DatabaseManager(db_path)
    db.create_tables()
    storage = StockStorage(db)

    # Add test data with indicators
    dates = pd.date_range('2024-01-01', periods=200)
    df = pd.DataFrame({
        'date': dates.strftime('%Y-%m-%d'),
        'symbol': 'TEST',
        'open': [10 + i * 0.05 for i in range(200)],
        'high': [10.5 + i * 0.05 for i in range(200)],
        'low': [9.5 + i * 0.05 for i in range(200)],
        'close': [10 + i * 0.05 for i in range(200)],
        'volume': [10000 + i * 100 for i in range(200)]
    })
    storage.save_stock({'symbol': 'TEST', 'name': '测试股票'})
    storage.save_stock_data(df)

    yield storage
    db.close()

def test_ensemble_predictor_initialization(temp_storage):
    """Test EnsemblePredictor initialization"""
    predictor = EnsemblePredictor(temp_storage)
    assert predictor.storage is not None
    assert predictor.short_predictor is not None
    assert predictor.medium_predictor is not None
    assert predictor.long_predictor is not None

def test_ensemble_predictor_predict(temp_storage):
    """Test ensemble predict method"""
    predictor = EnsemblePredictor(temp_storage)

    # Train each predictor
    for p in [predictor.short_predictor, predictor.medium_predictor, predictor.long_predictor]:
        X = np.random.rand(100, 20)
        y = np.random.randint(0, 3, 100)
        p.train(X, y)

    # Make prediction
    result = predictor.predict('TEST')

    assert 'short' in result
    assert 'medium' in result
    assert 'long' in result
    assert 'ensemble' in result
    assert 'action' in result['ensemble']
    assert 'confidence' in result['ensemble']
    assert result['symbol'] == 'TEST'
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_ensemble.py::test_ensemble_predictor_initialization -v`
Expected: FAIL with "EnsemblePredictor not implemented"

- [ ] **Step 3: Write minimal implementation**

```python
# prediction/ensemble.py
"""Ensemble prediction module integrating three time horizons."""

from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
from datetime import datetime

from prediction.short_term import ShortTermPredictor
from prediction.medium_term import MediumTermPredictor
from prediction.long_term import LongTermPredictor
from analysis.features import FeatureEngineer, LABEL_TO_ACTION
from data.storage import StockStorage
from utils.logger import Logger
from utils.config import Config


# Default ensemble weights
DEFAULT_WEIGHTS = {
    'short': 0.3,
    'medium': 0.4,
    'long': 0.3
}


class EnsemblePredictor:
    """Ensemble predictor integrating short, medium, and long-term predictions.

    Combines predictions from three horizons using configurable weights.
    Generates a comprehensive recommendation with reasoning for each horizon.

    This class acts as a prediction service, fetching data from storage
    and returning comprehensive predictions.
    """

    def __init__(self, storage: StockStorage, weights: Dict[str, float] = None):
        """Initialize ensemble predictor.

        Args:
            storage: StockStorage instance for fetching data
            weights: Dictionary of weights for each horizon (short, medium, long)
                    Default: {'short': 0.3, 'medium': 0.4, 'long': 0.3}
        """
        self.storage = storage
        self.weights = weights or DEFAULT_WEIGHTS

        # Validate weights
        total = sum(self.weights.values())
        if abs(total - 1.0) > 0.01:
            Logger.warning(f"Ensemble weights sum to {total:.2f}, normalizing")
            self.weights = {k: v / total for k, v in self.weights.items()}

        # Initialize predictors
        self.short_predictor = ShortTermPredictor()
        self.medium_predictor = MediumTermPredictor()
        self.long_predictor = LongTermPredictor()

        Logger.info("EnsemblePredictor initialized")

    def load_models(self, model_dir: str = 'models'):
        """Load all pretrained models.

        Args:
            model_dir: Directory containing model files
        """
        import os

        try:
            self.short_predictor.load_model(os.path.join(model_dir, 'short_term.pkl'))
            Logger.info("Loaded short-term model")
        except Exception as e:
            Logger.warning(f"Failed to load short-term model: {e}")

        try:
            self.medium_predictor.load_model(os.path.join(model_dir, 'medium_term.pkl'))
            Logger.info("Loaded medium-term model")
        except Exception as e:
            Logger.warning(f"Failed to load medium-term model: {e}")

        try:
            self.long_predictor.load_model(os.path.join(model_dir, 'long_term.pkl'))
            Logger.info("Loaded long-term model")
        except Exception as e:
            Logger.warning(f"Failed to load long-term model: {e}")

    def predict(self, symbol: str) -> Dict:
        """Make prediction for a stock.

        Args:
            symbol: Stock symbol

        Returns:
            Prediction dictionary with all horizons and ensemble
        """
        # Get stock data from storage
        df = self.storage.get_stock_data(symbol)

        if df.empty:
            Logger.warning(f"No data available for {symbol}")
            return self._empty_prediction(symbol)

        # Calculate indicators
        from analysis.indicators import IndicatorCalculator
        df = IndicatorCalculator.calculate_all(df)

        # Extract features for each horizon
        X_short = FeatureEngineer.extract_short_term_features(df, lookback=20)
        X_medium = FeatureEngineer.extract_medium_term_features(df, lookback=120)
        X_long = FeatureEngineer.extract_long_term_features(df)

        # Reshape if needed (single sample)
        if X_short.ndim == 1:
            X_short = X_short.reshape(1, -1)
        if X_medium.ndim == 1:
            X_medium = X_medium.reshape(1, -1)
        if X_long.ndim == 1:
            X_long = X_long.reshape(1, -1)

        return self._make_prediction(X_short, X_medium, X_long, symbol)

    def _empty_prediction(self, symbol: str) -> Dict:
        """Return empty prediction when no data available.

        Args:
            symbol: Stock symbol

        Returns:
            Empty prediction dictionary
        """
        return {
            'symbol': symbol,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'short': {'action': 'hold', 'confidence': 0.0, 'reasoning': ['无数据']},
            'medium': {'action': 'hold', 'confidence': 0.0, 'reasoning': ['无数据']},
            'long': {'action': 'hold', 'confidence': 0.0, 'reasoning': ['无数据']},
            'ensemble': {'action': 'hold', 'confidence': 0.0, 'breakdown': {}, 'reasoning': ['无数据']}
        }

    def _make_prediction(self, X_short: np.ndarray, X_medium: np.ndarray,
                         X_long: np.ndarray, symbol: str) -> Dict:
        """Internal method to make predictions.

        Args:
            X_short: Short-term features
            X_medium: Medium-term features
            X_long: Long-term features
            symbol: Stock symbol

        Returns:
            Prediction dictionary
        """
        result = {
            'symbol': symbol,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'short': self._predict_horizon(self.short_predictor, X_short, 'short'),
            'medium': self._predict_horizon(self.medium_predictor, X_medium, 'medium'),
            'long': self._predict_horizon(self.long_predictor, X_long, 'long')
        }

        # Generate ensemble
        result['ensemble'] = self._ensemble_predictions(result)

        return result

    def _predict_horizon(self, predictor, X: np.ndarray, horizon: str) -> Dict:
        """Make prediction for a specific horizon.

        Args:
            predictor: The predictor instance
            X: Features
            horizon: Horizon name ('short', 'medium', 'long')

        Returns:
            Prediction dictionary for this horizon
        """
        if not predictor.is_trained():
            # Return default prediction if model not trained
            return {
                'action': 'hold',
                'confidence': 0.5,
                'reasoning': ['模型未训练，使用默认预测']
            }

        predictions, confidence = predictor.predict_with_confidence(X)

        prediction = int(predictions[0])
        confidence = float(confidence[0])

        # Generate reasoning
        reasoning = predictor.generate_reasoning(X, prediction, confidence)

        return {
            'action': LABEL_TO_ACTION.get(prediction, 'hold'),
            'confidence': confidence,
            'reasoning': reasoning
        }

    def _ensemble_predictions(self, predictions: Dict) -> Dict:
        """Ensemble predictions from all horizons.

        Args:
            predictions: Dictionary with predictions for each horizon

        Returns:
            Ensemble prediction
        """
        # Calculate weighted scores for each action
        action_scores = {'buy': 0.0, 'sell': 0.0, 'hold': 0.0}

        # Get predictions
        short_pred = predictions['short']
        medium_pred = predictions['medium']
        long_pred = predictions['long']

        # Weight by horizon
        action_scores[short_pred['action']] += short_pred['confidence'] * self.weights['short']
        action_scores[medium_pred['action']] += medium_pred['confidence'] * self.weights['medium']
        action_scores[long_pred['action']] += long_pred['confidence'] * self.weights['long']

        # Select action with highest score
        ensemble_action = max(action_scores, key=action_scores.get)
        ensemble_confidence = action_scores[ensemble_action]

        # Generate reasoning
        reasoning = []
        if short_pred['action'] == ensemble_action:
            reasoning.append(f"短期建议{short_pred['action']}")
        if medium_pred['action'] == ensemble_action:
            reasoning.append(f"中期建议{medium_pred['action']}")
        if long_pred['action'] == ensemble_action:
            reasoning.append(f"长期建议{long_pred['action']}")

        # Combine all reasoning
        all_reasoning = []
        all_reasoning.extend(short_pred['reasoning'])
        all_reasoning.extend(medium_pred['reasoning'])
        all_reasoning.extend(long_pred['reasoning'])

        return {
            'action': ensemble_action,
            'confidence': ensemble_confidence,
            'breakdown': action_scores,
            'reasoning': reasoning,
            'all_reasoning': all_reasoning
        }

    def batch_predict(self, symbols: List[str]) -> Dict[str, Dict]:
        """Make predictions for multiple stocks.

        Args:
            symbols: List of stock symbols

        Returns:
            Dictionary mapping symbols to predictions
        """
        results = {}

        for symbol in symbols:
            try:
                # Make prediction using self.storage
                prediction = self.predict(symbol)
                results[symbol] = prediction

            except Exception as e:
                Logger.error(f"Failed to predict {symbol}: {str(e)}")

        return results
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_ensemble.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add prediction/ensemble.py tests/test_ensemble.py
git commit -m "feat: implement EnsemblePredictor"
```

---

## Task 7: Implement ModelTrainer

**Files:**
- Modify: `prediction/trainer.py`
- Test: `tests/test_trainer.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_trainer.py
import pytest
import pandas as pd
import numpy as np
import tempfile
from prediction.trainer import ModelTrainer
from data.storage import StockStorage
from data.database import DatabaseManager

@pytest.fixture
def temp_storage():
    """Create temporary storage for testing"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    db = DatabaseManager(db_path)
    db.create_tables()
    storage = StockStorage(db)

    # Add test data
    dates = pd.date_range('2024-01-01', periods=200)
    df = pd.DataFrame({
        'date': dates.strftime('%Y-%m-%d'),
        'symbol': 'TEST',
        'open': [10 + i * 0.05 for i in range(200)],
        'high': [10.5 + i * 0.05 for i in range(200)],
        'low': [9.5 + i * 0.05 for i in range(200)],
        'close': [10 + i * 0.05 for i in range(200)],
        'volume': [10000 + i * 100 for i in range(200)]
    })
    storage.save_stock({'symbol': 'TEST', 'name': '测试股票'})
    storage.save_stock_data(df)

    yield storage
    db.close()

def test_model_trainer_initialization(temp_storage):
    """Test ModelTrainer initialization"""
    trainer = ModelTrainer(temp_storage)
    assert trainer.storage is not None
    assert trainer.short_predictor is not None
    assert trainer.medium_predictor is not None
    assert trainer.long_predictor is not None

def test_prepare_training_data(temp_storage):
    """Test training data preparation"""
    trainer = ModelTrainer(temp_storage)
    X, y = trainer.prepare_training_data('short', horizon=5)

    assert X is not None
    assert y is not None
    assert len(X) > 0
    assert len(X) == len(y)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_trainer.py::test_model_trainer_initialization -v`
Expected: FAIL with "ModelTrainer not implemented"

- [ ] **Step 3: Write minimal implementation**

```python
# prediction/trainer.py
"""Model trainer for training all prediction models."""

from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import os

from prediction.short_term import ShortTermPredictor
from prediction.medium_term import MediumTermPredictor
from prediction.long_term import LongTermPredictor
from analysis.features import FeatureEngineer
from analysis.indicators import IndicatorCalculator
from data.storage import StockStorage
from utils.logger import Logger
from utils.config import Config


class ModelTrainer:
    """Model trainer for training all prediction models.

    Handles data preparation, training, and evaluation
    for short, medium, and long-term predictors.
    """

    def __init__(self, storage: StockStorage, model_dir: str = 'models'):
        """Initialize model trainer.

        Args:
            storage: StockStorage instance for fetching data
            model_dir: Directory to save trained models
        """
        self.storage = storage
        self.model_dir = model_dir

        # Initialize predictors
        self.short_predictor = ShortTermPredictor()
        self.medium_predictor = MediumTermPredictor()
        self.long_predictor = LongTermPredictor()

        Logger.info("ModelTrainer initialized")

    def prepare_training_data(self, horizon: str, symbols: List[str] = None,
                             lookback: int = None, label_horizon: int = None) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare training data for a specific horizon.

        Args:
            horizon: Prediction horizon ('short', 'medium', 'long')
            symbols: List of stock symbols to use (None for all stocks)
            lookback: Number of days to look back for features
            label_horizon: Number of days ahead for labels

        Returns:
            Tuple of (features, labels)
        """
        # Default parameters
        if horizon == 'short':
            lookback = lookback or 20
            label_horizon = label_horizon or 5
        elif horizon == 'medium':
            lookback = lookback or 120
            label_horizon = label_horizon or 60
        else:  # long
            lookback = lookback or 252
            label_horizon = label_horizon or 120

        Logger.info(f"Preparing training data for {horizon} horizon")

        # Get stock list
        if symbols is None:
            stocks = self.storage.get_stock_list()
        else:
            stocks = [{'symbol': s} for s in symbols]

        if not stocks:
            Logger.warning("No stocks found for training")
            return np.array([]), np.array([])

        X_list = []
        y_list = []

        for stock in stocks:
            symbol = stock['symbol']
            try:
                # Get stock data
                df = self.storage.get_stock_data(symbol)

                if df.empty or len(df) < lookback + label_horizon:
                    continue

                # Calculate indicators
                df = IndicatorCalculator.calculate_all(df)

                # Extract features
                if horizon == 'short':
                    features = FeatureEngineer.extract_short_term_features(df, lookback)
                elif horizon == 'medium':
                    features = FeatureEngineer.extract_medium_term_features(df, lookback)
                else:
                    features = FeatureEngineer.extract_long_term_features(df)

                # Create labels
                labels = FeatureEngineer.create_labels(df, label_horizon)

                # Only use samples with valid labels
                valid_indices = labels[lookback:] != 0  # Exclude HOLD labels

                if np.sum(valid_indices) > 0:
                    X_list.append(features[lookback:][valid_indices])
                    y_list.append(labels[lookback:][valid_indices])

            except Exception as e:
                Logger.warning(f"Failed to prepare data for {symbol}: {str(e)}")
                continue

        if not X_list:
            Logger.warning("No valid training samples found")
            return np.array([]), np.array([])

        # Combine all samples
        X = np.vstack(X_list)
        y = np.hstack(y_list)

        Logger.info(f"Prepared {len(X)} training samples for {horizon} horizon")

        return X, y

    def train_short_term_model(self, symbols: List[str] = None) -> Dict[str, float]:
        """Train short-term model.

        Args:
            symbols: List of stock symbols to use (None for all stocks)

        Returns:
            Training metrics
        """
        Logger.info("Training short-term model")

        # Prepare data
        X, y = self.prepare_training_data('short', symbols)

        if len(X) == 0:
            Logger.error("No training data available")
            return {'error': 'No training data available'}

        # Train model
        metrics = self.short_predictor.train(X, y, test_size=0.2)

        # Save model
        model_path = os.path.join(self.model_dir, 'short_term.pkl')
        self.short_predictor.save_model(model_path)

        return metrics

    def train_medium_term_model(self, symbols: List[str] = None) -> Dict[str, float]:
        """Train medium-term model.

        Args:
            symbols: List of stock symbols to use (None for all stocks)

        Returns:
            Training metrics
        """
        Logger.info("Training medium-term model")

        # Prepare data
        X, y = self.prepare_training_data('medium', symbols)

        if len(X) == 0:
            Logger.error("No training data available")
            return {'error': 'No training data available'}

        # Train model
        metrics = self.medium_predictor.train(X, y, test_size=0.2)

        # Save model
        model_path = os.path.join(self.model_dir, 'medium_term.pkl')
        self.medium_predictor.save_model(model_path)

        return metrics

    def train_long_term_model(self, symbols: List[str] = None) -> Dict[str, float]:
        """Train long-term model.

        Args:
            symbols: List of stock symbols to use (None for all stocks)

        Returns:
            Training metrics
        """
        Logger.info("Training long-term model")

        # Prepare data
        X, y = self.prepare_training_data('long', symbols)

        if len(X) == 0:
            Logger.error("No training data available")
            return {'error': 'No training data available'}

        # Train model
        metrics = self.long_predictor.train(X, y, test_size=0.2)

        # Save model
        model_path = os.path.join(self.model_dir, 'long_term.pkl')
        self.long_predictor.save_model(model_path)

        return metrics

    def train_all_models(self, symbols: List[str] = None) -> Dict[str, Dict[str, float]]:
        """Train all models.

        Args:
            symbols: List of stock symbols to use (None for all stocks)

        Returns:
            Dictionary of metrics for each model
        """
        Logger.info("Training all models")

        # Create model directory
        os.makedirs(self.model_dir, exist_ok=True)

        results = {
            'short': self.train_short_term_model(symbols),
            'medium': self.train_medium_term_model(symbols),
            'long': self.train_long_term_model(symbols)
        }

        Logger.info("All models trained successfully")
        return results

    def evaluate_model(self, predictor, X_test: np.ndarray, y_test: np.ndarray) -> Dict:
        """Evaluate a model.

        Args:
            predictor: The predictor to evaluate
            X_test: Test features
            y_test: Test labels

        Returns:
            Evaluation metrics
        """
        y_pred = predictor.predict(X_test)

        return {
            'accuracy': accuracy_score(y_test, y_pred),
            'classification_report': classification_report(y_test, y_pred, zero_division=0),
            'confusion_matrix': confusion_matrix(y_test, y_pred)
        }

    def load_models(self) -> bool:
        """Load all trained models.

        Returns:
            True if all models loaded successfully
        """
        try:
            self.short_predictor.load_model(os.path.join(self.model_dir, 'short_term.pkl'))
            self.medium_predictor.load_model(os.path.join(self.model_dir, 'medium_term.pkl'))
            self.long_predictor.load_model(os.path.join(self.model_dir, 'long_term.pkl'))
            Logger.info("All models loaded successfully")
            return True
        except Exception as e:
            Logger.error(f"Failed to load models: {str(e)}")
            return False
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_trainer.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add prediction/trainer.py tests/test_trainer.py
git commit -m "feat: implement ModelTrainer"
```

---

## Final Verification

After completing all tasks:

- [ ] **Run all tests**: `pytest tests/ -v`
- [ ] **Verify all pass**: Expect 100+ tests passing
- [ ] **Check coverage**: `pytest --cov=. tests/`
- [ ] **Update PROGRESS.md**: Mark Stage 3 complete
- [ ] **Final commit**: `git add PROGRESS.md && git commit -m "docs: update PROGRESS.md with Stage 3 completion"`