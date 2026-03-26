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
    assert len(labels) == len(df)  # All rows have labels
    # Last 5 rows should be HOLD (0)
    assert all(labels[-5:] == 0)

def test_normalize_features():
    """Test feature normalization"""
    X = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]], dtype=float)
    normalized = FeatureEngineer.normalize_features(X)
    assert normalized is not None
    assert normalized.shape == X.shape
