import pytest
import pandas as pd
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
    assert rankings[0] == '000001.TEST'  # Highest market cap
    # Verify rankings are in descending market cap order
    assert rankings == ['000001.TEST', '000002.TEST', '000003.TEST']

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