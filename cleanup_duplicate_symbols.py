"""Clean up duplicate stock symbols in database.

This script removes stock records without .SH/.SZ suffix and keeps only
the ones with proper suffix to ensure data consistency.
"""

import sqlite3
from utils.logger import Logger

def cleanup_duplicate_symbols():
    """Clean up duplicate stock symbols (keep only ones with .SH/.SZ suffix)."""
    db_path = 'data/stock_data.db'

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Find all symbols without suffix
        cursor.execute('''
            SELECT DISTINCT symbol FROM stock_data
            WHERE symbol NOT LIKE '%.SH' AND symbol NOT LIKE '%.SZ'
        ''')
        symbols_without_suffix = [row[0] for row in cursor.fetchall()]

        if not symbols_without_suffix:
            Logger.info("No symbols without suffix found. No cleanup needed.")
            return

        Logger.info(f"Found {len(symbols_without_suffix)} symbols without suffix:")
        for symbol in symbols_without_suffix:
            Logger.info(f"  - {symbol}")

        # Count records before cleanup
        cursor.execute('SELECT COUNT(*) FROM stock_data')
        count_before = cursor.fetchone()[0]
        Logger.info(f"Total records before cleanup: {count_before}")

        # Get total records to delete
        cursor.execute('''
            SELECT COUNT(*) FROM stock_data
            WHERE symbol NOT LIKE '%.SH' AND symbol NOT LIKE '%.SZ'
        ''')
        records_to_delete = cursor.fetchone()[0]
        Logger.info(f"Records to delete: {records_to_delete}")

        # Delete records without suffix
        cursor.execute('''
            DELETE FROM stock_data
            WHERE symbol NOT LIKE '%.SH' AND symbol NOT LIKE '%.SZ'
        ''')

        # Check records after cleanup
        cursor.execute('SELECT COUNT(*) FROM stock_data')
        count_after = cursor.fetchone()[0]
        Logger.info(f"Total records after cleanup: {count_after}")
        Logger.info(f"Deleted: {count_before - count_after} records")

        conn.commit()
        conn.close()

        Logger.info("✅ Cleanup completed successfully!")

        # Verify cleanup
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) FROM stock_data
            WHERE symbol NOT LIKE '%.SH' AND symbol NOT LIKE '%.SZ'
        ''')
        remaining = cursor.fetchone()[0]

        if remaining == 0:
            Logger.info("✅ Verification: No symbols without suffix remaining")
        else:
            Logger.warning(f"⚠️ Verification: {remaining} symbols without suffix still exist")

        conn.close()

    except Exception as e:
        Logger.error(f"Cleanup failed: {str(e)}")
        raise

if __name__ == '__main__':
    cleanup_duplicate_symbols()