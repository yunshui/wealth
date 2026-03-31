"""Test script to verify parallel data update functionality."""

import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from data.storage import StockStorage
from data.database import DatabaseManager
from data.fetcher import DataFetcher
from analysis.indicators import IndicatorCalculator


def test_parallel_update():
    """Test parallel update functionality with timing."""
    print("=== 并行数据更新测试 ===\n")

    db_manager = DatabaseManager()
    storage = StockStorage(db_manager)
    fetcher = DataFetcher()
    calculator = IndicatorCalculator()

    # Get a few sectors to test with (limit to 3 for quick testing)
    print("获取板块列表...")
    sectors = storage.get_all_sectors()[:3]

    if not sectors:
        print("没有板块数据，请先运行应用并更新板块数据")
        return

    print(f"将测试 {len(sectors)} 个板块的并行更新\n")

    # Test 1: Serial processing
    print("测试 1: 串行处理...")
    start_time = time.time()

    serial_count = 0
    for sector in sectors:
        try:
            stocks_df = fetcher.get_sector_stocks(sector['sector_name'], sector['sector_type'])
            if stocks_df is not None and not stocks_df.empty:
                serial_count += len(stocks_df)
        except Exception as e:
            pass

    serial_time = time.time() - start_time
    print(f"串行处理完成: {serial_count} 只股票, 耗时: {serial_time:.2f} 秒\n")

    # Test 2: Parallel processing
    print("测试 2: 并行处理 (4线程)...")

    def process_sector(sector):
        """Process a single sector."""
        db = DatabaseManager()
        thread_fetcher = DataFetcher()

        try:
            stocks_df = thread_fetcher.get_sector_stocks(sector['sector_name'], sector['sector_type'])
            return len(stocks_df) if stocks_df is not None and not stocks_df.empty else 0
        except Exception:
            return 0

    start_time = time.time()
    parallel_count = 0

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(process_sector, sector): sector for sector in sectors}
        for future in as_completed(futures):
            parallel_count += future.result()

    parallel_time = time.time() - start_time
    print(f"并行处理完成: {parallel_count} 只股票, 耗时: {parallel_time:.2f} 秒\n")

    # Results
    print("=== 测试结果 ===")
    print(f"串行耗时: {serial_time:.2f} 秒")
    print(f"并行耗时: {parallel_time:.2f} 秒")
    if parallel_time > 0:
        speedup = serial_time / parallel_time
        print(f"加速比: {speedup:.2f}x")
    print(f"处理股票数: 串行={serial_count}, 并行={parallel_count}")

    db_manager.close()


def test_thread_safety():
    """Test thread safety of counter updates."""
    print("\n=== 线程安全测试 ===\n")

    # Shared counter without lock
    unsafe_counter = 0
    lock = threading.Lock()

    def increment_unsafe():
        nonlocal unsafe_counter
        for _ in range(1000):
            unsafe_counter += 1

    def increment_safe():
        nonlocal unsafe_counter
        with lock:
            for _ in range(1000):
                unsafe_counter += 1

    # Test unsafe increment
    unsafe_counter = 0
    threads = []
    for _ in range(10):
        t = threading.Thread(target=increment_unsafe)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print(f"不加锁的计数器结果: {unsafe_counter} (预期: 10000)")

    # Test safe increment
    unsafe_counter = 0
    threads = []
    for _ in range(10):
        t = threading.Thread(target=increment_safe)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print(f"加锁的计数器结果: {unsafe_counter} (预期: 10000)")


if __name__ == "__main__":
    test_parallel_update()
    test_thread_safety()