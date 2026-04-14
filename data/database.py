"""Database manager module."""

import sqlite3
from typing import Optional
from utils.config import Config
from utils.logger import Logger


class DatabaseManager:
    """Manages SQLite database connection and table creation."""

    def __init__(self, db_path: str = None):
        """Initialize database manager.

        Args:
            db_path: Path to database file. If None, uses Config.DB_PATH
        """
        self.db_path = db_path or Config.get_db_path()
        self._conn: Optional[sqlite3.Connection] = None

    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection.

        Returns:
            SQLite connection object
        """
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def close(self) -> None:
        """Close database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    def check_database_exists(self) -> bool:
        """Check if database file exists and has tables.

        Returns:
            True if database exists with tables, False otherwise
        """
        import os
        if not os.path.exists(self.db_path):
            return False

        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table'")
            count = cursor.fetchone()[0]
            return count > 0
        except Exception:
            return False

    def create_tables(self) -> None:
        """Create all required database tables."""
        Logger.info("Creating database tables...")

        conn = self.get_connection()
        cursor = conn.cursor()

        # Create sectors table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sectors (
                sector_id TEXT PRIMARY KEY,
                sector_name TEXT NOT NULL,
                sector_type TEXT NOT NULL,
                leader_count INTEGER DEFAULT 0,
                updated_at TEXT
            )
        ''')

        # Create stocks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stocks (
                symbol TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                industry TEXT,
                sector TEXT,
                market_cap REAL,
                pe_ratio REAL,
                pb_ratio REAL,
                list_date TEXT,
                updated_at TEXT
            )
        ''')

        # Create stock_data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                symbol TEXT NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume REAL,
                amount REAL,
                ma5 REAL, ma10 REAL, ma20 REAL, ma60 REAL,
                macd REAL, macd_signal REAL, macd_hist REAL,
                kdj_k REAL, kdj_d REAL, kdj_j REAL,
                rsi6 REAL, rsi12 REAL, rsi24 REAL,
                boll_upper REAL, boll_middle REAL, boll_lower REAL,
                obv REAL,
                updated_at TEXT,
                FOREIGN KEY (symbol) REFERENCES stocks(symbol)
            )
        ''')

        # Add updated_at column if not exists (for existing databases)
        cursor.execute("PRAGMA table_info(stock_data)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'updated_at' not in columns:
            Logger.info("Adding updated_at column to stock_data table...")
            cursor.execute("ALTER TABLE stock_data ADD COLUMN updated_at TEXT")
            # Update existing records with current timestamp
            from datetime import datetime
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("UPDATE stock_data SET updated_at = ? WHERE updated_at IS NULL", (current_time,))
            conn.commit()
            Logger.info("Added updated_at column and updated existing records")

        # Create predictions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                symbol TEXT NOT NULL,
                horizon TEXT NOT NULL,
                action TEXT NOT NULL,
                confidence REAL,
                reasoning TEXT,
                model_version TEXT,
                created_at TEXT,
                FOREIGN KEY (symbol) REFERENCES stocks(symbol)
            )
        ''')

        # Create sector_leaders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sector_leaders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sector_id TEXT NOT NULL,
                sector_name TEXT NOT NULL,
                symbol TEXT NOT NULL,
                score REAL,
                rank INTEGER,
                market_cap_rank INTEGER,
                volume_rank INTEGER,
                updated_at TEXT,
                FOREIGN KEY (symbol) REFERENCES stocks(symbol)
            )
        ''')

        # Create model_params table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_params (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT NOT NULL,
                model_version TEXT NOT NULL,
                params TEXT,
                accuracy REAL,
                trained_at TEXT,
                is_active INTEGER DEFAULT 1
            )
        ''')

        # Create indexes for performance
        self._create_indexes(cursor)

        conn.commit()
        Logger.info("Database tables created successfully")

    def _create_indexes(self, cursor) -> None:
        """Create indexes for query performance optimization."""
        # Index on stock_data for fast symbol and date queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_stock_data_symbol_date
            ON stock_data(symbol, date)
        ''')

        # Index on stock_data for fast latest data queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_stock_data_date
            ON stock_data(date DESC)
        ''')

        # Index on stocks for fast sector queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_stocks_sector
            ON stocks(sector)
        ''')

        # Index on stocks for fast industry queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_stocks_industry
            ON stocks(industry)
        ''')

        # Index on predictions for fast lookups
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_predictions_symbol_date
            ON predictions(symbol, date)
        ''')

        # Index on sector_leaders for fast sector queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_sector_leaders_sector_id
            ON sector_leaders(sector_id)
        ''')

        # Additional indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sectors_type ON sectors(sector_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_stock_data_symbol ON stock_data(symbol)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_predictions_date ON predictions(date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_predictions_symbol ON predictions(symbol)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_predictions_date_symbol_horizon ON predictions(date, symbol, horizon)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_model_params_name ON model_params(model_name)')

    def get_last_update_date(self) -> Optional[str]:
        """Get the last update date from stock_data.

        Returns:
            Last date string in YYYY-MM-DD format, or None if no data
        """
        if not self.check_database_exists():
            return None

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(date) FROM stock_data")
        result = cursor.fetchone()[0]
        return result