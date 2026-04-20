"""Data storage module - SQLite CRUD operations."""

import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
import json
import os
from utils.logger import Logger
from utils.exceptions import StorageException
from data.database import DatabaseManager


class StockStorage:
    """Stock data storage manager for CRUD operations."""

    def __init__(self, db_manager: DatabaseManager):
        """Initialize storage manager.

        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager
        Logger.info("StockStorage initialized")

    # ========== Sector Operations ==========

    def save_sector(self, sector_data: Dict) -> bool:
        """Save or update sector information."""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO sectors
                (sector_id, sector_name, sector_type, leader_count, updated_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                sector_data.get('sector_id'),
                sector_data.get('sector_name'),
                sector_data.get('sector_type'),
                sector_data.get('leader_count', 0),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
            conn.commit()
            return True
        except Exception as e:
            Logger.error(f"Failed to save sector: {str(e)}")
            raise StorageException(f"Failed to save sector: {str(e)}")

    def get_all_sectors(self, sector_type: str = None) -> List[Dict]:
        """Get all sectors."""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            if sector_type:
                cursor.execute('''
                    SELECT sector_id, sector_name, sector_type, leader_count
                    FROM sectors WHERE sector_type = ? ORDER BY sector_name
                ''', (sector_type,))
            else:
                cursor.execute('''
                    SELECT sector_id, sector_name, sector_type, leader_count
                    FROM sectors ORDER BY sector_name
                ''')
            rows = cursor.fetchall()
            return [
                {
                    'sector_id': row['sector_id'],
                    'sector_name': row['sector_name'],
                    'sector_type': row['sector_type'],
                    'leader_count': row['leader_count']
                }
                for row in rows
            ]
        except Exception as e:
            Logger.error(f"Failed to get sectors: {str(e)}")
            raise StorageException(f"Failed to get sectors: {str(e)}")

    def get_sector_by_id(self, sector_id: str) -> Optional[Dict]:
        """Get sector by ID.

        Args:
            sector_id: Sector ID

        Returns:
            Sector dictionary or None if not found
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT sector_id, sector_name, sector_type, leader_count
                FROM sectors WHERE sector_id = ?
            ''', (sector_id,))
            row = cursor.fetchone()
            if row:
                return {
                    'sector_id': row['sector_id'],
                    'sector_name': row['sector_name'],
                    'sector_type': row['sector_type'],
                    'leader_count': row['leader_count']
                }
            return None
        except Exception as e:
            Logger.error(f"Failed to get sector by ID: {str(e)}")
            return None

    def get_major_sectors(self, config_path: str = 'config/MAJOR_SECTORS.json') -> List[Dict]:
        """Get predefined major sectors from config file.

        Args:
            config_path: Path to major sectors config file

        Returns:
            List of sector dictionaries
        """
        try:
            # Load config file
            if not os.path.exists(config_path):
                Logger.warning(f"Major sectors config file not found at {config_path}, falling back to all sectors")
                return self.get_all_sectors()

            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # Support new config format with 'sectors' array
            if 'sectors' in config:
                sectors_config = config.get('sectors', [])
                sector_type_map = {}
                for sector_config in sectors_config:
                    sector_type_map[sector_config['name']] = sector_config['type']
            else:
                # Support old config format
                industry_sectors = config.get('industry', [])
                concept_sectors = config.get('concept', [])

                # Build sector type map
                sector_type_map = {}
                for name in industry_sectors:
                    sector_type_map[name] = 'industry'
                for name in concept_sectors:
                    sector_type_map[name] = 'concept'

            # Query matching sectors from database
            conn = self.db.get_connection()
            cursor = conn.cursor()

            # Build placeholders for SQL query
            all_sector_names = list(sector_type_map.keys())
            if not all_sector_names:
                return []

            placeholders = ', '.join(['?' for _ in all_sector_names])
            query = f'''
                SELECT sector_id, sector_name, sector_type, leader_count
                FROM sectors WHERE sector_name IN ({placeholders})
                ORDER BY sector_name
            '''
            cursor.execute(query, all_sector_names)
            rows = cursor.fetchall()

            # Return matching sectors (without type filtering)
            major_sectors = []
            for row in rows:
                sector_name = row['sector_name']
                major_sectors.append({
                    'sector_id': row['sector_id'],
                    'sector_name': row['sector_name'],
                    'sector_type': row['sector_type'],
                    'leader_count': row['leader_count']
                })

            # Log missing sectors
            found_names = {s['sector_name'] for s in major_sectors}
            for name in all_sector_names:
                if name not in found_names:
                    Logger.debug(f"Major sector '{name}' not found in database")

            Logger.info(f"Retrieved {len(major_sectors)}/{len(all_sector_names)} major sectors")
            return major_sectors

        except Exception as e:
            Logger.error(f"Failed to get major sectors: {str(e)}")
            # Fallback to all sectors on error
            Logger.info("Falling back to all sectors")
            return self.get_all_sectors()

    def get_sector(self, sector_id: str) -> Optional[Dict]:
        """Get sector by ID."""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT sector_id, sector_name, sector_type, leader_count
                FROM sectors WHERE sector_id = ?
            ''', (sector_id,))
            row = cursor.fetchone()
            if row:
                return {
                    'sector_id': row['sector_id'],
                    'sector_name': row['sector_name'],
                    'sector_type': row['sector_type'],
                    'leader_count': row['leader_count']
                }
            return None
        except Exception as e:
            Logger.error(f"Failed to get sector: {str(e)}")
            raise StorageException(f"Failed to get sector: {str(e)}")

    def get_sectors_by_name(self, sector_name: str) -> List[Dict]:
        """Get sectors by name.

        Args:
            sector_name: Sector name to search

        Returns:
            List of sector dictionaries matching the name
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT sector_id, sector_name, sector_type, leader_count
                FROM sectors WHERE sector_name = ?
            ''', (sector_name,))
            rows = cursor.fetchall()
            return [
                {
                    'sector_id': row['sector_id'],
                    'sector_name': row['sector_name'],
                    'sector_type': row['sector_type'],
                    'leader_count': row['leader_count']
                }
                for row in rows
            ]
        except Exception as e:
            Logger.error(f"Failed to get sectors by name: {str(e)}")
            raise StorageException(f"Failed to get sectors by name: {str(e)}")

    # ========== Stock Operations ==========

    def save_stock(self, stock_data: Dict) -> bool:
        """Save or update stock information."""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO stocks
                (symbol, name, industry, sector, market_cap, pe_ratio, pb_ratio, list_date, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                stock_data.get('symbol'),
                stock_data.get('name'),
                stock_data.get('industry'),
                stock_data.get('sector'),
                stock_data.get('market_cap'),
                stock_data.get('pe_ratio'),
                stock_data.get('pb_ratio'),
                stock_data.get('list_date'),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
            conn.commit()
            return True
        except Exception as e:
            Logger.error(f"Failed to save stock: {str(e)}")
            raise StorageException(f"Failed to save stock: {str(e)}")

    def get_stock(self, symbol: str) -> Optional[Dict]:
        """Get stock by symbol.

        Args:
            symbol: Stock symbol

        Returns:
            Stock dictionary or None if not found
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT symbol, name, industry, sector, market_cap, pe_ratio, pb_ratio, list_date, updated_at
                FROM stocks WHERE symbol = ?
            ''', (symbol,))
            row = cursor.fetchone()
            if row:
                return {
                    'symbol': row['symbol'],
                    'name': row['name'],
                    'industry': row['industry'],
                    'sector': row['sector'],
                    'market_cap': row['market_cap'],
                    'pe_ratio': row['pe_ratio'],
                    'pb_ratio': row['pb_ratio'],
                    'list_date': row['list_date'],
                    'updated_at': row['updated_at']
                }
            # If not found in stocks table, try to get minimal info from sector_leaders
            Logger.debug(f"Stock {symbol} not found in stocks table, checking sector_leaders")
            cursor.execute('''
                SELECT symbol, rank, score, sector_id
                FROM sector_leaders WHERE symbol = ?
            ''', (symbol,))
            leader_row = cursor.fetchone()
            if leader_row:
                # Return minimal info from sector_leaders
                return {
                    'symbol': leader_row['symbol'],
                    'name': f'股票{symbol}',  # Placeholder name
                    'industry': None,
                    'sector': None,
                    'market_cap': None,
                    'pe_ratio': None,
                    'pb_ratio': None,
                    'list_date': None,
                    'updated_at': None,
                    'from_sector_leaders': True  # Flag to indicate source
                }
            return None
        except Exception as e:
            Logger.error(f"Failed to get stock: {str(e)}")
            raise StorageException(f"Failed to get stock: {str(e)}")

    def get_stock_latest_data(self, symbol: str) -> Optional[Dict]:
        """Get latest stock data from stock_data table.

        Args:
            symbol: Stock symbol

        Returns:
            Dictionary with latest stock data or None if not found
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            # Get latest 2 records to calculate prev_close from previous day's close
            cursor.execute('''
                SELECT date, open, high, low, close, volume, amount
                FROM stock_data WHERE symbol = ? ORDER BY date DESC LIMIT 2
            ''', (symbol,))
            rows = cursor.fetchall()

            if not rows:
                return None

            # Latest data
            latest = rows[0]
            # Previous day's close (if available)
            prev_close = rows[1]['close'] if len(rows) > 1 else latest['close']

            return {
                'trade_date': latest['date'],  # Map to trade_date for compatibility
                'date': latest['date'],
                'open': latest['open'],
                'high': latest['high'],
                'low': latest['low'],
                'close': latest['close'],
                'pre_close': prev_close,  # Previous day's close
                'vol': latest['volume'],  # Map to vol for compatibility
                'volume': latest['volume'],
                'amount': latest['amount']
            }
        except Exception as e:
            Logger.warning(f"Failed to get latest data for {symbol}: {str(e)}")
            return None

    def get_stock_list(self, industry: str = None, sector: str = None) -> List[Dict]:
        """Get stock list with optional filters."""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            query = '''
                SELECT symbol, name, industry, sector, market_cap
                FROM stocks WHERE 1=1
            '''
            params = []
            if industry:
                query += ' AND industry = ?'
                params.append(industry)
            if sector:
                query += ' AND sector = ?'
                params.append(sector)
            query += ' ORDER BY market_cap DESC'
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [
                {
                    'symbol': row['symbol'],
                    'name': row['name'],
                    'industry': row['industry'],
                    'sector': row['sector'],
                    'market_cap': row['market_cap']
                }
                for row in rows
            ]
        except Exception as e:
            Logger.error(f"Failed to get stock list: {str(e)}")
            raise StorageException(f"Failed to get stock list: {str(e)}")

    # ========== Stock Data Operations ==========

    def save_stock_data(self, df: pd.DataFrame) -> bool:
        """Save stock historical data in batch."""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            columns = ['date', 'symbol', 'open', 'high', 'low', 'close', 'volume', 'amount',
                      'ma5', 'ma10', 'ma20', 'ma60', 'macd', 'macd_signal', 'macd_hist',
                      'kdj_k', 'kdj_d', 'kdj_j', 'rsi6', 'rsi12', 'rsi24',
                      'boll_upper', 'boll_middle', 'boll_lower', 'obv', 'updated_at']
            for col in columns:
                if col not in df.columns:
                    df[col] = None
            # Set updated_at to current time for all records
            df['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            data = []
            for _, row in df.iterrows():
                data.append(tuple(row.get(col) for col in columns))
            placeholders = ', '.join(['?' for _ in columns])
            query = f'''
                INSERT OR REPLACE INTO stock_data
                (date, symbol, open, high, low, close, volume, amount,
                 ma5, ma10, ma20, ma60, macd, macd_signal, macd_hist,
                 kdj_k, kdj_d, kdj_j, rsi6, rsi12, rsi24,
                 boll_upper, boll_middle, boll_lower, obv, updated_at)
                VALUES ({placeholders})
            '''
            cursor.executemany(query, data)

            # Update stocks.updated_at for affected symbols
            if 'symbol' in df.columns:
                unique_symbols = df['symbol'].unique()
                for symbol in unique_symbols:
                    cursor.execute('''
                        UPDATE stocks SET updated_at = ? WHERE symbol = ?
                    ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), symbol))

            conn.commit()
            Logger.debug(f"Saved {len(df)} stock data rows")
            return True
        except Exception as e:
            Logger.error(f"Failed to save stock data: {str(e)}")
            raise StorageException(f"Failed to save stock data: {str(e)}")

    def save_stock_data_incremental(self, df: pd.DataFrame) -> int:
        """Save stock historical data incrementally (insert only non-existing records).

        Args:
            df: DataFrame with stock data

        Returns:
            Number of new records inserted
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            columns = ['date', 'symbol', 'open', 'high', 'low', 'close', 'volume', 'amount',
                      'ma5', 'ma10', 'ma20', 'ma60', 'macd', 'macd_signal', 'macd_hist',
                      'kdj_k', 'kdj_d', 'kdj_j', 'rsi6', 'rsi12', 'rsi24',
                      'boll_upper', 'boll_middle', 'boll_lower', 'obv', 'updated_at']
            for col in columns:
                if col not in df.columns:
                    df[col] = None

            inserted_count = 0
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            for _, row in df.iterrows():
                date = row.get('date')
                symbol = row.get('symbol')

                # Check if record already exists
                cursor.execute('''
                    SELECT COUNT(*) FROM stock_data
                    WHERE symbol = ? AND date = ?
                ''', (symbol, date))
                count = cursor.fetchone()[0]

                # Only insert if not exists
                if count == 0:
                    # Add current timestamp to the row data
                    row_data = list(row.get(col) for col in columns[:-1])  # All columns except updated_at
                    row_data.append(current_time)  # Add current timestamp for updated_at
                    data = tuple(row_data)
                    placeholders = ', '.join(['?' for _ in columns])
                    query = f'''
                        INSERT INTO stock_data
                        (date, symbol, open, high, low, close, volume, amount,
                         ma5, ma10, ma20, ma60, macd, macd_signal, macd_hist,
                         kdj_k, kdj_d, kdj_j, rsi6, rsi12, rsi24,
                         boll_upper, boll_middle, boll_lower, obv, updated_at)
                        VALUES ({placeholders})
                    '''
                    cursor.execute(query, data)
                    inserted_count += 1

            # Update stocks.updated_at for affected symbols
            if inserted_count > 0 and 'symbol' in df.columns:
                unique_symbols = df['symbol'].unique()
                for symbol in unique_symbols:
                    cursor.execute('''
                        UPDATE stocks SET updated_at = ? WHERE symbol = ?
                    ''', (current_time, symbol))

            conn.commit()
            Logger.debug(f"Inserted {inserted_count} new stock data records (skipped {len(df) - inserted_count} existing)")
            return inserted_count
        except Exception as e:
            Logger.error(f"Failed to save stock data incrementally: {str(e)}")
            raise StorageException(f"Failed to save stock data incrementally: {str(e)}")

    def get_stock_data(self, symbol: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """Get stock historical data."""
        try:
            conn = self.db.get_connection()
            query = '''
                SELECT date, symbol, open, high, low, close, volume, amount,
                       ma5, ma10, ma20, ma60, macd, macd_signal, macd_hist,
                       kdj_k, kdj_d, kdj_j, rsi6, rsi12, rsi24,
                       boll_upper, boll_middle, boll_lower, obv
                FROM stock_data WHERE symbol = ?
            '''
            params = [symbol]
            if start_date:
                query += ' AND date >= ?'
                params.append(start_date)
            if end_date:
                query += ' AND date <= ?'
                params.append(end_date)
            query += ' ORDER BY date'
            df = pd.read_sql_query(query, conn, params=params)
            return df
        except Exception as e:
            Logger.error(f"Failed to get stock data: {str(e)}")
            raise StorageException(f"Failed to get stock data: {str(e)}")

    def get_latest_stock_data(self, symbol: str) -> Optional[Dict]:
        """Get latest stock data."""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT date, symbol, open, high, low, close, volume, amount
                FROM stock_data WHERE symbol = ? ORDER BY date DESC LIMIT 1
            ''', (symbol,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
        except Exception as e:
            Logger.error(f"Failed to get latest stock data: {str(e)}")
            raise StorageException(f"Failed to get latest stock data: {str(e)}")

    def has_stock_data_for_date(self, symbol: str, date: str) -> bool:
        """Check if stock data exists for a specific date.

        Args:
            symbol: Stock symbol
            date: Date in YYYY-MM-DD format

        Returns:
            True if data exists, False otherwise
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) FROM stock_data
                WHERE symbol = ? AND date = ?
            ''', (symbol, date))
            count = cursor.fetchone()[0]
            return count > 0
        except Exception as e:
            Logger.error(f"Failed to check stock data for date: {str(e)}")
            return False

    def get_stock_latest_date(self, symbol: str) -> Optional[str]:
        """Get the latest date of stock data in database.

        Args:
            symbol: Stock symbol

        Returns:
            Latest date string in YYYY-MM-DD format, or None if no data
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT MAX(date) FROM stock_data
                WHERE symbol = ?
            ''', (symbol,))
            result = cursor.fetchone()[0]
            if result:
                # Convert YYYYMMDD to YYYY-MM-DD
                if len(result) == 8 and result.isdigit():
                    return f"{result[:4]}-{result[4:6]}-{result[6:8]}"
                return result
            return None
        except Exception as e:
            Logger.error(f"Failed to get stock latest date: {str(e)}")
            return None

    # ========== Prediction Operations ==========

    def save_prediction(self, prediction_data: Dict) -> bool:
        """Save prediction result."""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO predictions
                (date, symbol, horizon, action, confidence, reasoning, model_version, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                prediction_data.get('date'),
                prediction_data.get('symbol'),
                prediction_data.get('horizon'),
                prediction_data.get('action'),
                prediction_data.get('confidence'),
                prediction_data.get('reasoning'),
                prediction_data.get('model_version'),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
            conn.commit()
            return True
        except Exception as e:
            Logger.error(f"Failed to save prediction: {str(e)}")
            raise StorageException(f"Failed to save prediction: {str(e)}")

    def get_prediction(self, symbol: str, horizon: str, date: str = None) -> Optional[Dict]:
        """Get latest prediction for stock."""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            query = '''
                SELECT id, date, symbol, horizon, action, confidence, reasoning, model_version
                FROM predictions WHERE symbol = ? AND horizon = ?
            '''
            params = [symbol, horizon]
            if date:
                query += ' AND date <= ?'
                params.append(date)
            query += ' ORDER BY date DESC LIMIT 1'
            cursor.execute(query, params)
            row = cursor.fetchone()
            if row:
                return {
                    'id': row['id'],
                    'date': row['date'],
                    'symbol': row['symbol'],
                    'horizon': row['horizon'],
                    'action': row['action'],
                    'confidence': row['confidence'],
                    'reasoning': row['reasoning'],
                    'model_version': row['model_version']
                }
            return None
        except Exception as e:
            Logger.error(f"Failed to get prediction: {str(e)}")
            raise StorageException(f"Failed to get prediction: {str(e)}")

    def get_predictions(self, symbol: str) -> List[Dict]:
        """Get all predictions for a stock."""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, date, symbol, horizon, action, confidence, reasoning, model_version
                FROM predictions WHERE symbol = ? ORDER BY date DESC, horizon
            ''', (symbol,))
            rows = cursor.fetchall()
            return [
                {
                    'id': row['id'],
                    'date': row['date'],
                    'symbol': row['symbol'],
                    'horizon': row['horizon'],
                    'action': row['action'],
                    'confidence': row['confidence'],
                    'reasoning': row['reasoning'],
                    'model_version': row['model_version']
                }
                for row in rows
            ]
        except Exception as e:
            Logger.error(f"Failed to get predictions: {str(e)}")
            raise StorageException(f"Failed to get predictions: {str(e)}")

    # ========== Sector Leaders Operations ==========

    def save_sector_leaders(self, sector_id: str, leaders: List[Dict]) -> bool:
        """Save sector leader stocks."""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM sector_leaders WHERE sector_id = ?', (sector_id,))
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            for leader in leaders:
                cursor.execute('''
                    INSERT INTO sector_leaders
                    (sector_id, sector_name, symbol, score, rank, market_cap_rank, volume_rank, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    sector_id,
                    leader.get('sector_name'),
                    leader.get('symbol'),
                    leader.get('score'),
                    leader.get('rank'),
                    leader.get('market_cap_rank'),
                    leader.get('volume_rank'),
                    timestamp
                ))
            conn.commit()
            Logger.debug(f"Saved {len(leaders)} leaders for sector {sector_id}")
            return True
        except Exception as e:
            Logger.error(f"Failed to save sector leaders: {str(e)}")
            raise StorageException(f"Failed to save sector leaders: {str(e)}")

    def get_sector_leaders(self, sector_id: str) -> List[Dict]:
        """Get sector leaders including all configured stocks.

        Args:
            sector_id: Sector ID

        Returns:
            List of leader stock dictionaries from sector_leaders table
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            # LEFT JOIN with stocks table to get all configured stocks
            cursor.execute('''
                SELECT sl.sector_id, sl.sector_name, sl.symbol, sl.score, sl.rank,
                       sl.market_cap_rank, sl.volume_rank,
                       s.name, s.industry, s.sector
                FROM sector_leaders sl
                LEFT JOIN stocks s ON sl.symbol = s.symbol
                WHERE sl.sector_id = ?
                ORDER BY sl.rank
            ''', (sector_id,))
            rows = cursor.fetchall()
            return [
                {
                    'sector_id': row['sector_id'],
                    'sector_name': row['sector_name'],
                    'symbol': row['symbol'],
                    'score': row['score'],
                    'rank': row['rank'],
                    'market_cap_rank': row['market_cap_rank'],
                    'volume_rank': row['volume_rank'],
                    # Directly use stocks.name, with placeholder fallback
                    'name': row['name'] if row['name'] else f'股票{row["symbol"]}',
                    'industry': row['industry'],
                    'sector_from_stocks': row['sector'],  # Sector from stocks table
                    'has_stock_info': row['name'] is not None  # Flag to indicate if stock info exists
                }
                for row in rows
            ]
        except Exception as e:
            Logger.error(f"Failed to get sector leaders: {str(e)}")
            raise StorageException(f"Failed to get sector leaders: {str(e)}")

    def get_sector_leaders_by_name(self, sector_name: str) -> List[Dict]:
        """Get sector leaders by sector name including all configured stocks.

        Args:
            sector_name: Sector name

        Returns:
            List of leader stock dictionaries from sector_leaders table
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            # LEFT JOIN with stocks table to get all configured stocks
            cursor.execute('''
                SELECT sl.sector_id, sl.sector_name, sl.symbol, sl.score, sl.rank,
                       sl.market_cap_rank, sl.volume_rank,
                       s.name, s.industry, s.sector
                FROM sector_leaders sl
                LEFT JOIN stocks s ON sl.symbol = s.symbol
                WHERE sl.sector_name = ?
                ORDER BY sl.rank
            ''', (sector_name,))
            rows = cursor.fetchall()
            return [
                {
                    'sector_id': row['sector_id'],
                    'sector_name': row['sector_name'],
                    'symbol': row['symbol'],
                    'score': row['score'],
                    'rank': row['rank'],
                    'market_cap_rank': row['market_cap_rank'],
                    'volume_rank': row['volume_rank'],
                    # Directly use stocks.name, with placeholder fallback
                    'name': row['name'] if row['name'] else f'股票{row["symbol"]}',
                    'industry': row['industry'],
                    'sector_from_stocks': row['sector'],  # Sector from stocks table
                    'has_stock_info': row['name'] is not None  # Flag to indicate if stock info exists
                }
                for row in rows
            ]
        except Exception as e:
            Logger.error(f"Failed to get sector leaders by name: {str(e)}")
            raise StorageException(f"Failed to get sector leaders by name: {str(e)}")