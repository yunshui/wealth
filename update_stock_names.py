"""Batch update stock names to stocks table."""

import sqlite3
import json
import akshare as ak
import pandas as pd

def update_stock_names():
    """Update stock names for all configured stocks."""

    # Connect to database
    db_path = '/Users/yunshuiyang/Workspace/wealth/data/stock_data.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Load configured stocks
    with open('config/MAJOR_SECTORS.json', 'r', encoding='utf-8') as f:
        config = json.load(f)

    # Collect all unique stocks
    configured_stocks = set()
    for sector in config['sectors']:
        for stock in sector.get('stocks', []):
            configured_stocks.add(stock)

    print(f"Total configured stocks: {len(configured_stocks)}")
    print("Updating stock names...")

    updated_count = 0
    failed_count = 0

    for symbol in sorted(configured_stocks):
        try:
            # Get stock name from API
            clean_symbol = symbol.split('.')[0]
            stock_info = ak.stock_individual_info_em(symbol=clean_symbol)
            new_name = None

            # Handle DataFrame format from akshare
            if isinstance(stock_info, pd.DataFrame):
                for idx, row in stock_info.iterrows():
                    if row.get('item') == '股票简称':
                        new_name = row.get('value')
                        break

            if new_name and not new_name.startswith('股票'):
                # Insert or update stocks table
                cursor.execute('''
                    INSERT OR REPLACE INTO stocks (symbol, name, updated_at)
                    VALUES (?, ?, datetime('now'))
                ''', (symbol, new_name))
                updated_count += 1
                print(f"✓ {symbol}: {new_name}")
            else:
                print(f"✗ {symbol}: No valid name found")
                failed_count += 1

        except Exception as e:
            print(f"✗ {symbol}: Error - {str(e)}")
            failed_count += 1

    conn.commit()
    conn.close()

    print(f"\nSummary: {updated_count} updated, {failed_count} failed")

if __name__ == '__main__':
    update_stock_names()