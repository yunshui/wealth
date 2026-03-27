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
