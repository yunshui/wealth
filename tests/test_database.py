"""Tests for DatabaseManager."""

import pytest
import os
import tempfile
from data.database import DatabaseManager


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    yield db_path
    os.unlink(db_path)


def test_database_manager_creation(temp_db):
    """Test DatabaseManager can be created"""
    db = DatabaseManager(temp_db)
    assert db is not None
    assert db.db_path == temp_db
    db.close()


def test_database_manager_create_tables(temp_db):
    """Test tables can be created"""
    db = DatabaseManager(temp_db)
    db.create_tables()
    db.close()

    # Verify tables exist
    import sqlite3
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()

    expected_tables = ['stocks', 'sectors', 'stock_data', 'predictions', 'sector_leaders', 'model_params']
    for table in expected_tables:
        assert table in tables


def test_database_manager_check_exists(temp_db):
    """Test database existence check"""
    db = DatabaseManager(temp_db)

    # Initially should not exist
    assert not db.check_database_exists()

    # Create tables
    db.create_tables()

    # Now should exist
    assert db.check_database_exists()

    db.close()


def test_database_manager_get_connection(temp_db):
    """Test getting database connection"""
    db = DatabaseManager(temp_db)
    conn = db.get_connection()
    assert conn is not None
    conn.close()
    db.close()


def test_database_manager_get_last_update_date(temp_db):
    """Test getting last update date"""
    db = DatabaseManager(temp_db)

    # Initially should be None
    assert db.get_last_update_date() is None

    # Create tables
    db.create_tables()

    # Should still be None (no data yet)
    assert db.get_last_update_date() is None

    # Insert some test data
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO stocks (symbol, name)
        VALUES ('000001', '测试股票')
    ''')
    cursor.execute('''
        INSERT INTO stock_data (date, symbol, close)
        VALUES ('2024-01-01', '000001', 10.5)
    ''')
    cursor.execute('''
        INSERT INTO stock_data (date, symbol, close)
        VALUES ('2024-01-02', '000001', 11.0)
    ''')
    conn.commit()

    # Should return the max date
    last_date = db.get_last_update_date()
    assert last_date == '2024-01-02'

    db.close()