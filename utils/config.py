"""Configuration management module."""


class Config:
    """Application configuration."""

    # Database
    DB_PATH = 'data/stock_data.db'

    # Data
    DATA_START_DATE = '2018-01-01'  # 7 years of historical data
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