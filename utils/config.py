"""Configuration management module."""

import json
import os
from typing import List, Dict


class Config:
    """Application configuration."""

    # Version
    VERSION = "0.5.28"

    # Database
    DB_PATH = 'data/stock_data.db'

    # Data
    DEFAULT_DATA_START_DATE = '2025-01-01'  # Default 1 year of historical data
    DATA_UPDATE_TIME = '15:30'  # Update after market close

    # Sectors
    MAIN_SECTORS = [
        '科技', '医药', '消费', '金融', '制造',
        '能源', '材料', '公用', '地产', '交运'
    ]
    LEADER_COUNT = 20  # Top 20 leaders per sector

    # Prediction
    SHORT_TERM_HORIZON = 5      # 5 days
    MEDIUM_TERM_HORIZON = 60    # 60 days (2 months)
    LONG_TERM_HORIZON = 120     # 120 days (4 months)

    ENSEMBLE_WEIGHTS = {
        'short': 0.3,
        'medium': 0.4,
        'long': 0.3
    }

    # Models
    MODEL_DIR = 'models'
    SHORT_MODEL_FILE = 'short_term.pkl'
    MEDIUM_MODEL_FILE = 'medium_term.pkl'
    LONG_MODEL_FILE = 'long_term.pkl'

    # Logging
    LOG_DIR = 'logs'
    LOG_FILE = 'app.log'
    LOG_LEVEL = 'INFO'

    # Cache
    CACHE_DIR = 'data/cache'
    CACHE_EXPIRE = 3600  # 1 hour

    @classmethod
    def get_db_path(cls) -> str:
        """Get database file path."""
        return cls.DB_PATH

    @classmethod
    def get_data_start_date(cls) -> str:
        """Get data start date from config file.

        Returns:
            Data start date string in YYYY-MM-DD format
        """
        config_file = 'config/data_config.json'
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get('data', {}).get('start_date', cls.DEFAULT_DATA_START_DATE)
            except Exception:
                pass
        return cls.DEFAULT_DATA_START_DATE

    @classmethod
    def get_update_cache_hours(cls) -> int:
        """Get update cache hours from config file.

        Returns:
            Cache hours value (default 4 hours)
        """
        config_file = 'config/data_config.json'
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get('data', {}).get('update_cache_hours', 4)
            except Exception:
                pass
        return 4

    @classmethod
    def get_major_sectors_config(cls) -> List[Dict]:
        """Get major sectors configuration with stocks list.

        Returns:
            List of sector configurations with name, type, and stocks
        """
        config_file = 'config/MAJOR_SECTORS.json'
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get('sectors', [])
            except Exception as e:
                Logger.warning(f"Failed to load major sectors config: {str(e)}")
        return []

    @classmethod
    def get_model_path(cls, model_type: str) -> str:
        """Get model file path.

        Args:
            model_type: 'short', 'medium', or 'long'

        Returns:
            Full path to model file
        """
        import os
        model_file = f"{model_type}_term.pkl"
        return os.path.join(cls.MODEL_DIR, model_file)