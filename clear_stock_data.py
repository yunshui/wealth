"""清空历史数据并重新获取的工具脚本。

注意：此操作将删除所有股票的历史数据，需要重新获取！
"""

import sqlite3
import sys

def clear_stock_data():
    """清空 stock_data 表中的所有历史数据。"""

    db_path = '/Users/yunshuiyang/Workspace/wealth/data/stock_data.db'

    print("⚠️  警告：此操作将删除所有股票的历史数据！")
    print("请在「数据更新」页面点击「更新股票数据」重新获取数据。")
    print()
    print("当前 stock_data 表中的数据情况：")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 检查数据量
    cursor.execute("SELECT COUNT(*) FROM stock_data")
    total_records = cursor.fetchone()[0]
    print(f"总记录数: {total_records}")

    cursor.execute("SELECT COUNT(DISTINCT symbol) FROM stock_data")
    total_stocks = cursor.fetchone()[0]
    print(f"股票数量: {total_stocks}")

    if total_records == 0:
        print("数据库中已无历史数据。")
        conn.close()
        return

    print()
    print("是否继续清空历史数据？")
    print("请输入 'yes' 确认，其他键取消: ", end="")

    try:
        confirm = input().strip().lower()
        if confirm != 'yes':
            print("操作已取消。")
            conn.close()
            return
    except EOFError:
        print("\n操作已取消。")
        conn.close()
        return

    print()
    print("正在清空 stock_data 表...")

    # 清空 stock_data 表
    cursor.execute("DELETE FROM stock_data")
    conn.commit()

    # 清空技术指标数据
    print("正在清空 stock_data 表（技术指标列）...")

    # 由于 SQLite 不支持 DROP COLUMN，我们重新创建表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='stock_data';")
    table_exists = cursor.fetchone()

    if table_exists:
        # 获取表结构（不包含数据）
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='stock_data';")
        create_sql = cursor.fetchone()[0]

        # 删除表
        cursor.execute("DROP TABLE stock_data;")
        conn.commit()

        # 重新创建表（不包含技术指标列，因为技术指标可以重新计算）
        cursor.execute(create_sql)
        conn.commit()

    conn.close()

    print("✅ 历史数据已清空！")
    print()
    print("请在应用中执行以下操作重新获取数据：")
    print("1. 进入「数据更新」页面")
    print("2. 点击「更新股票数据」")
    print("3. 等待数据获取完成")
    print("4. 点击「更新技术指标」重新计算指标")
    print()
    print("预计需要较长时间（约 10-30 分钟），请耐心等待。")

if __name__ == '__main__':
    clear_stock_data()