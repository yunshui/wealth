import pytest
from utils.config import Config


def test_config_db_path():
    """Test database path is correctly defined"""
    assert Config.DB_PATH == 'data/stock_data.db'


def test_config_data_start_date():
    """Test data start date is correctly defined"""
    assert Config.DATA_START_DATE == '2018-01-01'


def test_config_ensemble_weights():
    """Test ensemble weights sum to 1"""
    total = sum(Config.ENSEMBLE_WEIGHTS.values())
    assert abs(total - 1.0) < 0.01


def test_config_model_paths():
    """Test model paths are correctly constructed"""
    assert 'short_term' in Config.SHORT_MODEL_FILE
    assert 'medium_term' in Config.MEDIUM_MODEL_FILE
    assert 'long_term' in Config.LONG_MODEL_FILE