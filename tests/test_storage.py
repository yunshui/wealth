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
    storage.save_stock({'symbol': '000001.TEST', 'name': '测试股票'})
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
    storage.save_stock({'symbol': '000001.TEST', 'name': '测试股票'})
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

def test_save_and_get_sector_leaders(storage):
    """Test saving and retrieving sector leaders"""
    storage.save_stock({
        'symbol': '000001.TEST',
        'name': '测试股票',
        'sector': '测试板块'
    })
    leaders = [{
        'sector_name': '测试板块',
        'symbol': '000001.TEST',
        'score': 0.85,
        'rank': 1,
        'market_cap_rank': 1,
        'volume_rank': 1
    }]
    result = storage.save_sector_leaders('industry_test', leaders)
    assert result
    retrieved = storage.get_sector_leaders('industry_test')
    assert len(retrieved) == 1
    assert retrieved[0]['symbol'] == '000001.TEST'