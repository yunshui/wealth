import pytest
import pandas as pd
import numpy as np
import tempfile
from prediction.ensemble import EnsemblePredictor
from data.storage import StockStorage
from data.database import DatabaseManager
from analysis.features import FeatureEngineer
from analysis.indicators import IndicatorCalculator

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

    # Get data to determine feature count for each horizon
    df = temp_storage.get_stock_data('TEST')
    df = IndicatorCalculator.calculate_all(df)
    
    X_short = FeatureEngineer.extract_short_term_features(df, lookback=20)
    X_medium = FeatureEngineer.extract_medium_term_features(df, lookback=120)
    X_long = FeatureEngineer.extract_long_term_features(df)

    # Train each predictor with correct feature count
    X_train_short = np.random.rand(100, len(X_short))
    y_train = np.random.randint(0, 3, 100)
    predictor.short_predictor.train(X_train_short, y_train)

    X_train_medium = np.random.rand(100, len(X_medium))
    predictor.medium_predictor.train(X_train_medium, y_train)

    X_train_long = np.random.rand(100, len(X_long))
    predictor.long_predictor.train(X_train_long, y_train)

    # Make prediction
    result = predictor.predict('TEST')

    assert 'short' in result
    assert 'medium' in result
    assert 'long' in result
    assert 'ensemble' in result
    assert 'action' in result['ensemble']
    assert 'confidence' in result['ensemble']
    assert result['symbol'] == 'TEST'
