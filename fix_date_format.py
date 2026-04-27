"""
Fix date format inconsistency in stock_data table.

This script converts all dates from 'YYYY-MM-DD' format to 'YYYYMMDD' format.
"""

import sqlite3
from pathlib import Path


def fix_date_format():
    """Fix date format in stock_data table."""
    db_path = Path('data/stock_data.db')

    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        return

    print("🔧 Fixing date format in stock_data table...")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check current date format distribution
        cursor.execute('''
            SELECT SUBSTR(date, 5, 1) as sep, COUNT(*) as count
            FROM stock_data
            GROUP BY sep
        ''')
        before = cursor.fetchall()
        print("\n📊 Before fix:")
        for sep, count in before:
            format_name = 'YYYY-MM-DD' if sep == '-' else f'YYYY{sep}MMDD' if sep else 'YYYYMMDD'
            print(f"   {format_name}: {count:,} records")

        # Count records that need to be fixed
        cursor.execute("SELECT COUNT(*) FROM stock_data WHERE date LIKE '%-%'")
        to_fix = cursor.fetchone()[0]
        print(f"\n⚠️  Records to fix: {to_fix:,}")

        if to_fix == 0:
            print("\n✅ No records need to be fixed!")
            return

        # Update records: replace dashes in date
        print("\n🔄 Updating records...")
        cursor.execute("UPDATE stock_data SET date = REPLACE(date, '-', '-')")
        print(f"   Replacing '-' with empty string...")
        cursor.execute("UPDATE stock_data SET date = REPLACE(date, '-', '')")
        updated = cursor.rowcount
        print(f"   ✅ Updated {updated:,} records")

        conn.commit()

        # Verify the fix
        cursor.execute('''
            SELECT SUBSTR(date, 5, 1) as sep, COUNT(*) as count
            FROM stock_data
            GROUP BY sep
        ''')
        after = cursor.fetchall()
        print("\n📊 After fix:")
        for sep, count in after:
            format_name = 'YYYY-MM-DD' if sep == '-' else f'YYYY{sep}MMDD' if sep else 'YYYYMMDD'
            print(f"   {format_name}: {count:,} records")

        # Show sample dates
        cursor.execute("SELECT DISTINCT date FROM stock_data ORDER BY date DESC LIMIT 5")
        sample_dates = cursor.fetchall()
        print("\n📅 Sample dates (most recent):")
        for (date,) in sample_dates:
            print(f"   {date}")

        # Check for any remaining issues
        cursor.execute("SELECT COUNT(*) FROM stock_data WHERE date LIKE '%-%'")
        remaining = cursor.fetchone()[0]

        if remaining == 0:
            print("\n✅ All dates fixed! All dates are now in YYYYMMDD format.")
        else:
            print(f"\n⚠️  Warning: {remaining} records still have dashes in date field.")

    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()


if __name__ == '__main__':
    fix_date_format()