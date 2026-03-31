"""UI page components for the application."""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

from data.storage import StockStorage
from data.database import DatabaseManager
from ui.layout import color_for_change, format_change, render_card, footer
from ui.charts import plot_kline_chart, plot_volume_chart, plot_indicator_chart
from ui.prediction import render_horizon_card, render_ensemble_card
from prediction.ensemble import EnsemblePredictor


@st.cache_data(ttl=3600)
def _get_prediction_cached(symbol: str) -> Dict:
    """Cached prediction getter (creates storage inside).

    Args:
        symbol: Stock symbol

    Returns:
        Prediction dictionary
    """
    storage = StockStorage(DatabaseManager())
    predictor = EnsemblePredictor(storage)
    predictor.load_models()
    return predictor.predict(symbol)


def _get_stock_name(storage: StockStorage, symbol: str) -> str:
    """Helper function to safely get stock name.

    Args:
        storage: StockStorage instance
        symbol: Stock symbol

    Returns:
        Stock name or 'Unknown' if not found
    """
    stock_data = storage.get_stock(symbol)
    return stock_data.get('name', 'Unknown') if stock_data else 'Unknown'


def show_homepage():
    """Display homepage with sector overview."""
    st.header("🏠 首页/板块总览")

    # Load data - keep connection open for entire function
    db_manager = DatabaseManager()
    storage = StockStorage(db_manager)

    try:
        # Sector selection
        sectors = storage.get_all_sectors()
        if not sectors:
            st.warning("暂无板块数据，请先在'数据更新'页面更新板块数据")
            return

        sector_names = [s['sector_name'] for s in sectors]
        selected_sector = st.selectbox("选择板块", sector_names, key="sector_select")

        # Get selected sector
        sector = next((s for s in sectors if s['sector_name'] == selected_sector), None)
        if not sector:
            return

        # Update button
        col1, col2 = st.columns([4, 1])
        with col2:
            if st.button("🔄 更新数据", use_container_width=True, key="update_home"):
                st.info("数据更新功能将在后续完善")

        # Sector leaders
        leaders = storage.get_sector_leaders(sector['sector_id'])

        if leaders:
            render_card(
                f"{sector['sector_name']} - 龙头股列表",
                lambda: _render_leaders_table(leaders, storage),
                "🏆"
            )
        else:
            st.info("该板块暂无龙头股数据")

        # Sector trend chart placeholder
        render_card(
            f"{sector['sector_name']} - 板块趋势",
            _render_sector_trend_placeholder,
            "📈"
        )
    finally:
        # Close database connection at the very end
        db_manager.close()


def _render_leaders_table(leaders: list, storage: StockStorage):
    """Render sector leaders table with click navigation.

    Args:
        leaders: List of leader stock dictionaries
        storage: StockStorage instance for data retrieval
    """
    if not leaders:
        return st.info("暂无数据")

    # Convert to DataFrame for display
    df = pd.DataFrame(leaders)

    # Fetch stock names for display
    df['name'] = df['symbol'].apply(lambda s: _get_stock_name(storage, s))

    # Format score column
    if 'score' in df.columns:
        df['score'] = df['score'].apply(lambda x: f"{x:.2f}")

    # Reorder columns for display
    display_cols = ['symbol', 'name', 'score', 'rank']
    if 'market_cap_rank' in df.columns:
        display_cols.append('market_cap_rank')
    if 'volume_rank' in df.columns:
        display_cols.append('volume_rank')

    df_display = df[display_cols]

    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True,
        key="leaders_table",
        column_config={
            'symbol': st.column_config.TextColumn('代码'),
            'name': st.column_config.TextColumn('名称'),
            'score': st.column_config.TextColumn('综合得分'),
            'rank': st.column_config.NumberColumn('排名', format="%d"),
            'market_cap_rank': st.column_config.NumberColumn('市值排名', format="%d"),
            'volume_rank': st.column_config.NumberColumn('成交量排名', format="%d")
        },
        on_select="rerun",
        selection_mode="single-row"
    )

    # Handle row selection for navigation
    selection = st.session_state.get('leaders_table', {}).get('selection', {}).get('rows', [])
    if selection:
        selected_idx = selection[0]
        if selected_idx < len(leaders):
            selected_symbol = leaders[selected_idx].get('symbol')
            if selected_symbol:
                st.session_state.selected_symbol = selected_symbol
                st.session_state.page = "股票详情"
                st.rerun()


def _render_sector_trend_placeholder():
    """Render sector trend chart placeholder."""
    st.info("📈 板块趋势图表将在后续阶段实现")
    st.caption("将显示该板块的整体K线图和趋势分析")


def show_stock_detail():
    """Display stock detail page."""
    st.header("📊 股票详情")

    # Back button
    if st.button("← 返回板块总览", key="back_to_home"):
        st.session_state.page = "首页/板块总览"
        st.rerun()

    # Symbol input (or use session state from homepage)
    if "selected_symbol" not in st.session_state:
        st.session_state.selected_symbol = ""

    symbol = st.text_input(
        "股票代码",
        value=st.session_state.selected_symbol,
        placeholder="例如: 000001.SZ",
        key="stock_symbol"
    )

    if not symbol:
        st.info("请输入股票代码或从板块总览页面选择")
        return

    # Load data
    db_manager = None
    try:
        db_manager = DatabaseManager()
        storage = StockStorage(db_manager)
    except Exception as e:
        st.error(f"数据库连接失败: {e}")
        return

    try:
        # Get stock info
        stock = storage.get_stock(symbol)
        if not stock:
            st.warning(f"未找到股票: {symbol}")
            return

        # Display stock info card
        _render_stock_info_card(stock, storage)

        # Get historical data
        df = storage.get_stock_data(symbol)
        if df.empty:
            st.warning("暂无历史数据，请先更新数据")
            return

        # Time range selector
        time_range = st.selectbox(
            "时间范围",
            options=["1月", "3月", "6月", "1年", "全部"],
            key="time_range"
        )

        # Filter data based on time range
        df_filtered = _filter_by_time_range(df, time_range)

        # Charts area
        col1, col2 = st.columns([2, 1])

        with col1:
            render_card("价格走势", lambda: plot_kline_chart(df_filtered), "📈")

        with col2:
            render_card("成交量", lambda: plot_volume_chart(df_filtered), "📊")

        # Indicator selector
        indicator = st.selectbox(
            "技术指标",
            options=["MACD", "RSI", "KDJ", "BOLL"],
            key="indicator_select"
        )

        render_card(f"{indicator}指标", lambda: plot_indicator_chart(df_filtered, indicator), "📉")

        # Prediction section
        st.markdown("---")

        # Get prediction (using cached function)
        try:
            with st.spinner("正在分析预测..."):
                prediction = _get_prediction_cached(symbol)

            # Display horizon predictions in columns
            col1, col2, col3 = st.columns(3)

            with col1:
                render_horizon_card("短期预测", prediction['short'], icon="📈")

            with col2:
                render_horizon_card("中期预测", prediction['medium'], icon="📊")

            with col3:
                render_horizon_card("长期预测", prediction['long'], icon="📉")

            # Display ensemble
            render_ensemble_card(prediction)

        except FileNotFoundError:
            st.warning("⚠️ 模型文件未找到")
            st.info("请先训练模型: python prediction/trainer.py")
        except Exception as e:
            st.error(f"预测获取失败: {e}")
    finally:
        # Close database connection
        if db_manager:
            db_manager.close()


def _render_stock_info_card(stock: dict, storage: StockStorage):
    """Render stock basic information card.

    Args:
        stock: Stock information dictionary
        storage: StockStorage instance for data retrieval
    """
    # Get latest price and previous close
    latest = storage.get_latest_stock_data(stock['symbol'])

    if latest:
        latest_price = latest.get('close', 0)

        # Get previous day's close price for correct change calculation
        prev_close = latest.get('prev_close', 0)
        if prev_close == 0:
            # If prev_close not available, get from historical data
            df = storage.get_stock_data(stock['symbol'])
            if len(df) >= 2:
                # Sort by date and get the second-to-last row's close
                df_sorted = df.sort_values('date')
                prev_close = df_sorted.iloc[-2]['close']
            else:
                prev_close = latest_price

        change_pct = (latest_price - prev_close) / prev_close * 100 if prev_close > 0 else 0
    else:
        latest_price = 0
        change_pct = 0

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "股票代码",
            stock.get('symbol', ''),
            stock.get('name', '')
        )

    with col2:
        st.metric(
            "最新价格",
            f"{latest_price:.2f}" if latest_price else "-",
            f"{format_change(change_pct)}",
            delta_color=color_for_change(change_pct)
        )

    with col3:
        st.metric(
            "市盈率",
            f"{stock.get('pe_ratio', 0):.1f}" if stock.get('pe_ratio') else "-",
            f"PB: {stock.get('pb_ratio', 0):.1f}" if stock.get('pb_ratio') else "-"
        )


def _filter_by_time_range(df: pd.DataFrame, time_range: str) -> pd.DataFrame:
    """Filter DataFrame by time range.

    Args:
        df: DataFrame with date column
        time_range: Time range selection

    Returns:
        Filtered DataFrame
    """
    if df.empty or 'date' not in df.columns:
        return df

    df_copy = df.copy()
    df_copy['date'] = pd.to_datetime(df_copy['date'])

    # Calculate days
    ranges = {
        "1月": 30,
        "3月": 90,
        "6月": 180,
        "1年": 365
    }

    if time_range in ranges:
        days = ranges[time_range]
        cutoff_date = pd.Timestamp.now() - pd.Timedelta(days=days)
        df_copy = df_copy[df_copy['date'] >= cutoff_date]

    return df_copy


def _render_prediction_placeholder():
    """Render prediction placeholder card."""
    render_card("🎯 预测建议", lambda: st.info("""
    预测功能将在Stage 5实现，将包含：
    - 短期预测（1-5天）
    - 中期预测（1-3个月）
    - 长期预测（3个月以上）
    - 综合建议和推理依据
    """))


def show_data_update():
    """Display data update interface."""
    st.header("🔄 数据更新")

    from analysis.indicators import IndicatorCalculator
    from analysis.sector import SectorAnalyzer
    from data.fetcher import DataFetcher

    # Initialize database connection
    db_manager = None
    try:
        db_manager = DatabaseManager()
        storage = StockStorage(db_manager)
    except Exception as e:
        st.error(f"数据库连接失败: {e}")
        return

    try:
        # Database status
        if db_manager.check_database_exists():
            st.success("✅ 数据库已初始化")
            last_update = db_manager.get_last_update_date()
            if last_update:
                st.info(f"最后更新日期: {last_update}")
            else:
                st.info("暂无数据")
        else:
            st.warning("⚠️ 数据库未初始化")
            if st.button("初始化数据库", key="init_db"):
                try:
                    db_manager.create_tables()
                    st.success("数据库初始化成功!")
                    st.rerun()
                except Exception as e:
                    st.error(f"初始化失败: {e}")
            return

        # Update buttons
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🔄 更新板块数据", use_container_width=True, key="update_sectors"):
                _update_sectors_data(storage)

        with col2:
            if st.button("🔄 更新股票数据", use_container_width=True, key="update_stocks"):
                _update_stocks_data(storage)

        with col3:
            if st.button("🔄 更新技术指标", use_container_width=True, key="update_indicators"):
                _update_indicators_data(storage)
    finally:
        # Close database connection
        if db_manager:
            db_manager.close()


def _update_sectors_data(storage: StockStorage):
    """Update sectors and leaders data from key sectors in config.

    Args:
        storage: StockStorage instance for data operations
    """
    from data.fetcher import DataFetcher
    from analysis.indicators import IndicatorCalculator
    from analysis.sector import SectorAnalyzer
    import json
    import os

    update_placeholder = st.empty()

    try:
        fetcher = DataFetcher()
        analyzer = SectorAnalyzer(storage)

        # Load key sectors config
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'sectors.json')
        key_sectors = []
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                key_sectors = config.get('key_sectors', {})

        # Step 1: Get all sectors from API
        update_placeholder.info("正在获取板块列表...")
        industry_sectors = fetcher.get_industry_sectors()
        concept_sectors = fetcher.get_concept_sectors()

        # Step 2: Filter and save only key sectors
        update_placeholder.info("正在保存关键板块数据...")

        key_industry_names = key_sectors.get('industry', [])
        key_concept_names = key_sectors.get('concept', [])

        saved_industry = 0
        saved_concept = 0

        for _, sector in industry_sectors.iterrows():
            sector_name = sector['板块名称']
            if not key_industry_names or sector_name in key_industry_names:
                storage.save_sector({
                    'sector_id': sector['板块代码'],
                    'sector_name': sector_name,
                    'sector_type': 'industry'
                })
                saved_industry += 1

        for _, sector in concept_sectors.iterrows():
            sector_name = sector['板块名称']
            if not key_concept_names or sector_name in key_concept_names:
                storage.save_sector({
                    'sector_id': sector['板块代码'],
                    'sector_name': sector_name,
                    'sector_type': 'concept'
                })
                saved_concept += 1

        # Step 3: Update sector leaders for key sectors only
        update_placeholder.info("正在更新板块龙头股...")
        analyzer.update_all_sector_leaders()

        st.success(f"✅ 板块数据更新完成! 已保存 {saved_industry} 个行业板块, {saved_concept} 个概念板块")

    except Exception as e:
        st.error(f"更新失败: {str(e)}")


def _update_stocks_data(storage: StockStorage):
    """Update stock data for all sectors using parallel processing.

    Args:
        storage: StockStorage instance for data operations
    """
    from data.fetcher import DataFetcher
    from analysis.indicators import IndicatorCalculator
    from datetime import datetime, timedelta
    import json
    import os

    update_placeholder = st.empty()
    progress_placeholder = st.empty()

    try:
        fetcher = DataFetcher()
        calculator = IndicatorCalculator()

        # Load config for data retention
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'sectors.json')
        years_to_keep = 7
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                years_to_keep = config.get('data_retention', {}).get('years_to_keep', 7)

        # Get all sectors
        update_placeholder.info("正在获取板块列表...")
        sectors = storage.get_all_sectors()

        if not sectors:
            st.warning("请先更新板块数据")
            return

        # Calculate date range
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=years_to_keep*365)).strftime('%Y%m%d')

        # Thread-safe counters
        total_lock = threading.Lock()
        processed_stocks = 0
        total_sectors = len(sectors)

        # Progress tracking
        sectors_processed = 0

        def process_sector(sector: Dict) -> int:
            """Process a single sector and return count of stocks processed.

            Args:
                sector: Sector dictionary

            Returns:
                Number of stocks processed
            """
            nonlocal sectors_processed

            # Use a separate storage instance for each thread
            db = DatabaseManager()
            thread_storage = StockStorage(db)
            thread_fetcher = DataFetcher()
            thread_calculator = IndicatorCalculator()

            sector_name = sector['sector_name']
            sector_type = sector['sector_type']
            stocks_processed = 0

            try:
                # Get stocks in this sector
                stocks_df = thread_fetcher.get_sector_stocks(sector_name, sector_type)

                if stocks_df is None or stocks_df.empty:
                    return 0

                # Process each stock
                for _, stock_row in stocks_df.iterrows():
                    symbol = stock_row.get('代码', '')
                    if not symbol or len(symbol) < 6:
                        continue

                    # Format symbol
                    symbol = f"{symbol}.SH" if symbol.startswith('6') else f"{symbol}.SZ"

                    # Get stock info
                    try:
                        stock_info = thread_fetcher.get_stock_info(symbol)
                        if stock_info and not stock_info.get('error'):
                            thread_storage.save_stock({
                                'symbol': symbol,
                                'name': stock_info.get('股票简称', ''),
                                'industry': stock_info.get('所属行业', ''),
                                'sector': sector_name,
                                'market_cap': float(stock_info.get('总市值', 0) or 0),
                                'pe_ratio': float(stock_info.get('市盈率-动态', 0) or 0),
                                'pb_ratio': float(stock_info.get('市净率', 0) or 0)
                            })
                    except Exception:
                        pass

                    # Get historical data
                    try:
                        history_df = thread_fetcher.get_stock_history(symbol, start_date, end_date)

                        if history_df is not None and not history_df.empty:
                            # Calculate indicators
                            history_df = thread_calculator.calculate_all(history_df)

                            # Save data
                            thread_storage.save_stock_data(history_df)
                            stocks_processed += 1
                    except Exception:
                        pass

            except Exception as e:
                pass

            finally:
                # Update progress safely
                with total_lock:
                    nonlocal processed_stocks
                    processed_stocks += stocks_processed
                    nonlocal sectors_processed
                    sectors_processed += 1

            return stocks_processed

        # Process sectors in parallel
        max_workers = min(8, len(sectors))  # Limit to 8 concurrent workers

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            futures = {executor.submit(process_sector, sector): sector for sector in sectors}

            # Process completed tasks and update progress
            for future in as_completed(futures):
                sector = futures[future]
                try:
                    count = future.result()
                    # Update progress display
                    progress_placeholder.info(
                        f"进度: {sectors_processed}/{total_sectors} 板块, "
                        f"已处理 {processed_stocks} 只股票"
                    )
                except Exception as e:
                    pass

        st.success(f"✅ 股票数据更新完成! 共处理 {processed_stocks} 只股票")

    except Exception as e:
        st.error(f"更新失败: {str(e)}")


def _update_indicators_data(storage: StockStorage):
    """Update technical indicators for all stocks using parallel processing.

    Args:
        storage: StockStorage instance for data operations
    """
    from analysis.indicators import IndicatorCalculator

    update_placeholder = st.empty()
    progress_placeholder = st.empty()

    try:
        # Get all stocks
        update_placeholder.info("正在获取股票列表...")
        stocks = storage.get_stock_list()

        if not stocks:
            st.warning("暂无股票数据，请先更新板块和股票数据")
            return

        # Thread-safe counters
        total_lock = threading.Lock()
        processed_count = 0
        total = len(stocks)

        def process_stock(stock: Dict) -> int:
            """Process a single stock and return count of rows updated.

            Args:
                stock: Stock dictionary

            Returns:
                Number of rows processed
            """
            nonlocal processed_count

            # Use a separate storage instance for each thread
            db = DatabaseManager()
            thread_storage = StockStorage(db)
            thread_calculator = IndicatorCalculator()

            rows_processed = 0

            try:
                # Get historical data
                df = thread_storage.get_stock_data(stock['symbol'])

                if not df.empty:
                    # Calculate indicators
                    df_with_indicators = thread_calculator.calculate_all(df)

                    # Save updated data
                    for _, row in df_with_indicators.iterrows():
                        thread_storage.save_stock_data(row.to_dict())
                        rows_processed += 1

            except Exception:
                pass

            finally:
                # Update progress safely
                with total_lock:
                    nonlocal processed_count
                    processed_count += 1

            return rows_processed

        # Process stocks in parallel
        max_workers = min(16, total)  # Limit to 16 concurrent workers

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            futures = {executor.submit(process_stock, stock): stock for stock in stocks}

            # Process completed tasks and update progress
            for future in as_completed(futures):
                stock = futures[future]
                try:
                    future.result()
                    # Update progress display
                    progress_placeholder.info(f"进度: {processed_count}/{total} 只股票")
                except Exception:
                    pass

        st.success(f"✅ 技术指标更新完成! 共处理 {processed_count} 只股票")

    except Exception as e:
        st.error(f"更新失败: {str(e)}")


def show_history():
    """Display history review page."""
    st.header("📜 历史预测回顾")
    st.info("🚀 历史回顾功能将在后续实现")
    st.write("""
    本页面将展示:
    - 预测准确率统计
    - 准确率趋势图
    - 历史预测记录
    """)