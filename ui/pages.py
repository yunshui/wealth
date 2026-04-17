"""UI page components for the application."""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

from data.storage import StockStorage
from data.database import DatabaseManager
from ui.layout import color_for_change, format_change, render_card, footer_right
from ui.charts import plot_kline_chart, plot_volume_chart, plot_indicator_chart
from ui.prediction import render_horizon_card, render_ensemble_card
from prediction.ensemble import EnsemblePredictor
from utils.logger import Logger


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
        sectors = storage.get_major_sectors()
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
    if st.button("← 返回", key="back_to_home"):
        # Return to where we came from (sector analysis or home)
        if st.session_state.selected_sector:
            st.session_state.nav_module = "analysis"
        else:
            st.session_state.nav_module = "home"
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
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("🔄 更新板块数据", use_container_width=True, key="update_sectors"):
                _update_sectors_data(storage)

        with col2:
            if st.button("🔄 更新股票数据", use_container_width=True, key="update_stocks"):
                Logger.info("========== BUTTON CLICKED: update_stocks ==========")
                _update_stocks_data(storage)

        with col3:
            if st.button("🔄 更新技术指标", use_container_width=True, key="update_indicators"):
                _update_indicators_data(storage)

        with col4:
            if st.button("🧠 训练预测模型", use_container_width=True, key="train_models"):
                _train_models(storage)
    finally:
        # Close database connection
        if db_manager:
            db_manager.close()


def _update_sectors_data(storage: StockStorage):
    """Update sectors data from config file and API, save to database.

    Args:
        storage: StockStorage instance for data operations
    """
    from data.fetcher import DataFetcher
    from analysis.indicators import IndicatorCalculator
    from analysis.sector import SectorAnalyzer
    import json
    import os
    import akshare as ak

    update_placeholder = st.empty()

    try:
        fetcher = DataFetcher()
        analyzer = SectorAnalyzer(storage)

        # Load sectors from config
        config_path = 'config/MAJOR_SECTORS.json'
        if not os.path.exists(config_path):
            update_placeholder.error("配置文件不存在")
            return

        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # Support both old and new config formats
        if 'sectors' in config:
            sectors_config = config.get('sectors', [])
            update_placeholder.info(f"正在更新 {len(sectors_config)} 个板块...")
        else:
            # Convert old format to new format
            industries = config.get('industry', [])
            concepts = config.get('concept', [])
            sectors_config = []
            for name in industries:
                sectors_config.append({'name': name, 'type': 'industry'})
            for name in concepts:
                sectors_config.append({'name': name, 'type': 'concept'})
            update_placeholder.info(f"正在更新 {len(sectors_config)} 个板块...")

        # Step 1: Clean up old sectors from database
        update_placeholder.info("正在清理旧板块数据...")
        all_sectors = storage.get_all_sectors()

        # Get connection once and reuse it
        conn = storage.db.get_connection()
        cursor = conn.cursor()

        sectors_to_delete = []
        for sector in all_sectors:
            sector_name = sector['sector_name']
            sector_type = sector['sector_type']
            # Check if sector should be kept
            keep = False
            for sector_config in sectors_config:
                if sector_config['name'] == sector_name and sector_config['type'] == sector_type:
                    keep = True
                    break

            if not keep:
                sectors_to_delete.append(sector['sector_id'])

        # Delete in batches with progress updates
        batch_size = 100
        deleted_count = 0
        total_to_delete = len(sectors_to_delete)

        for i in range(0, len(sectors_to_delete), batch_size):
            batch = sectors_to_delete[i:i + batch_size]

            # Delete sector leaders for batch
            placeholders = ', '.join(['?' for _ in batch])
            cursor.execute(f'DELETE FROM sector_leaders WHERE sector_id IN ({placeholders})', batch)

            # Delete sectors
            cursor.execute(f'DELETE FROM sectors WHERE sector_id IN ({placeholders})', batch)
            conn.commit()

            deleted_count = min(i + batch_size, total_to_delete)
            update_placeholder.info(f"正在清理旧板块数据... ({deleted_count}/{total_to_delete})")

        if total_to_delete > 0:
            update_placeholder.info(f"✅ 已清理 {total_to_delete} 个旧板块")

        # Step 2: Save sectors to database and fetch sector info from API
        update_placeholder.info("正在获取板块信息并保存...")
        saved_count = 0

        for idx, sector_config in enumerate(sectors_config):
            sector_name = sector_config['name']
            sector_type = sector_config['type']
            stocks_list = sector_config.get('stocks', [])

            # Update progress
            update_placeholder.info(f"正在处理板块 [{idx+1}/{len(sectors_config)}] {sector_name}...")

            try:
                # Get sector info from API
                sector_info_df = None
                if sector_type == 'industry':
                    try:
                        # Try to get industry sector info from akshare
                        sector_info_df = ak.stock_board_industry_name_em()
                    except:
                        pass
                else:  # concept
                    try:
                        # Try to get concept sector info from akshare
                        sector_info_df = ak.stock_board_concept_name_em()
                    except:
                        pass

                # Find matching sector in API data
                sector_id = None
                score = 0.0

                if sector_info_df is not None and not sector_info_df.empty:
                    # Try to find sector by name
                    match = sector_info_df[sector_info_df['板块名称'] == sector_name]
                    if not match.empty:
                        sector_id = match.iloc[0]['板块代码']
                        # Extract score/rating if available
                        if '涨跌幅' in match.columns:
                            score = float(match.iloc[0]['涨跌幅'])
                else:
                    # Generate sector_id from sector name if not found in API
                    sector_id = f"Sector_{sector_type}_{sector_name}"

                # Save sector to database
                if sector_id:
                    storage.save_sector({
                        'sector_id': sector_id,
                        'sector_name': sector_name,
                        'sector_type': sector_type,
                        'leader_count': len(stocks_list)
                    })
                    saved_count += 1

                    # Save sector leaders if stocks are configured
                    if stocks_list:
                        leaders_list = []
                        for stock_idx, stock_symbol in enumerate(stocks_list):
                            # Calculate a simple score based on stock position (higher for earlier stocks)
                            stock_score = 100.0 - stock_idx * 10.0
                            leaders_list.append({
                                'sector_id': sector_id,
                                'sector_name': sector_name,
                                'symbol': stock_symbol,
                                'score': stock_score,
                                'rank': stock_idx + 1,
                                'market_cap_rank': stock_idx + 1,
                                'volume_rank': stock_idx + 1
                            })
                        storage.save_sector_leaders(sector_id, leaders_list)

            except Exception as e:
                Logger.warning(f"Failed to process sector {sector_name}: {str(e)}")
                continue

        st.success(f"✅ 板块数据更新完成! 已保存 {saved_count} 个板块")

    except Exception as e:
        st.error(f"更新失败: {str(e)}")


def _update_stocks_data(storage: StockStorage):
    """Update stock data for all sectors using parallel processing from database.

    Args:
        storage: StockStorage instance for data operations
    """
    from data.fetcher import DataFetcher
    from analysis.indicators import IndicatorCalculator
    from datetime import datetime, timedelta

    Logger.info("========== _update_stocks_data: START ==========")
    Logger.info("_update_stocks_data: Starting stock data update")

    # Create progress displays
    progress_bar = st.progress(0)
    current_status = st.empty()
    completed_info = st.empty()
    remaining_info = st.empty()

    try:
        # Get all sectors from database
        current_status.info("正在获取板块列表...")
        from utils.config import Config

        # Load sectors configuration from config file
        sectors_config = Config.get_major_sectors_config()

        if not sectors_config:
            st.error("配置文件中没有板块数据，请检查 config/MAJOR_SECTORS.json")
            progress_bar.empty()
            Logger.warning("_update_stocks_data: No sectors found in config file")
            return

        Logger.info(f"_update_stocks_data: Found {len(sectors_config)} sectors in config")

        # Configuration
        years_to_keep = 7
        sector_workers = 4  # Reduced from 8 to 4
        stock_workers = 4   # Reduced from 16 to 4
        sector_timeout = 1800  # 30 minutes timeout per sector (reduced from 300 seconds)
        stock_timeout = 120   # 2 minutes timeout per stock (reduced from 60 seconds)

        # Calculate date range - get from config file
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = Config.get_data_start_date().replace('-', '')  # Convert YYYY-MM-DD to YYYYMMDD
        cache_hours = Config.get_update_cache_hours()  # Get cache hours from config

        # Thread-safe counters
        total_lock = threading.Lock()
        processed_stocks = 0
        failed_stocks = 0
        total_sectors = len(sectors_config)
        sectors_processed = 0
        completed_sectors = []

        # Thread-safe status tracking
        status_lock = threading.Lock()
        current_sector = ""
        current_stock_symbol = ""
        current_stock_name = ""
        sector_progress = 0
        sector_total = 0
        sector_started = False  # Flag to track if sector has started
        stop_ui_update = False  # Flag to stop UI updates

        Logger.info("_update_stocks_data: Starting parallel processing")

        # Create UI placeholders for real-time updates
        progress_bar = st.progress(0)
        sector_status = st.empty()  # 开始处理 X/Y 个板块...
        stock_status = st.empty()   # 处理板块 XXX，股票 XXX - XXX
        progress_status = st.empty() # 板块进度 X/Y

        # Initial display - exactly as user requested
        sector_status.info(f"开始处理 0/{total_sectors} 个板块...")
        stock_status.empty()
        progress_status.empty()

        # Process sectors sequentially to enable real-time UI updates
        for sector_idx, sector_config in enumerate(sectors_config):
            sector_name = sector_config['name']
            sector_type = sector_config['type']
            stocks_list = sector_config.get('stocks', [])

            # Update UI with current sector progress
            sector_status.info(f"开始处理 {sectors_processed}/{total_sectors} 个板块...")
            stock_status.info(f"正在处理板块 {sector_name}，共 {len(stocks_list)} 只股票...")
            progress_status.empty()

            if not stocks_list:
                Logger.warning(f"process_sector: No stocks configured for sector {sector_name}")
                sectors_processed += 1
                progress = sectors_processed / total_sectors
                progress_bar.progress(progress)
                continue

            this_sector_total = len(stocks_list)
            processed_count = 0
            failed_count = 0

            Logger.info(f"process_sector: {sector_name} starting stock processing with {len(stocks_list)} stocks")

            try:
                # Process stocks sequentially for real-time UI updates
                for stock_idx, symbol in enumerate(stocks_list):
                    # Update UI with current processing info
                    stock_name = ""
                    try:
                        db = DatabaseManager()
                        thread_storage = StockStorage(db)
                        stock_info = thread_storage.get_stock(symbol)
                        if stock_info:
                            stock_name = stock_info.get('name', '')
                    except:
                        pass

                    stock_display = f"{symbol}"
                    if stock_name:
                        stock_display += f" - {stock_name}"
                    stock_status.info(f"处理板块 {sector_name}，股票 {stock_display}")
                    progress_status.info(f"板块进度 {processed_count}/{this_sector_total}")

                    # Process stock
                    try:
                        db = DatabaseManager()
                        thread_storage = StockStorage(db)
                        thread_fetcher = DataFetcher()
                        thread_calculator = IndicatorCalculator()

                        # Process stock - check if today's data already exists
                        needs_update = True
                        from datetime import datetime as dt, date as dt_date

                        try:
                            stock_info = thread_storage.get_stock(symbol)
                            if stock_info and stock_info.get('updated_at'):
                                last_update = dt.strptime(stock_info['updated_at'], '%Y-%m-%d %H:%M:%S')
                                hours_since_update = (dt.now() - last_update).total_seconds() / 3600

                                # Check if today's data already exists in database
                                today_str = dt.now().strftime('%Y-%m-%d')
                                has_today_data = thread_storage.has_stock_data_for_date(symbol, today_str)

                                if has_today_data:
                                    # Today's data exists, skip update
                                    needs_update = False
                                elif hours_since_update < cache_hours:
                                    # Within cache time but no today data, still update
                                    needs_update = True
                        except:
                            pass

                        if needs_update:
                            # Get the latest date in database for incremental update
                            latest_date = thread_storage.get_stock_latest_date(symbol)
                            if latest_date:
                                # Convert YYYY-MM-DD to YYYYMMDD and add 1 day
                                from datetime import timedelta
                                latest_dt = dt.strptime(latest_date, '%Y-%m-%d')
                                next_date = (latest_dt + timedelta(days=1)).strftime('%Y%m%d')
                                stock_start_date = next_date
                            else:
                                # No data exists, start from config start date
                                stock_start_date = start_date

                            history_df = thread_fetcher.get_stock_history(symbol, stock_start_date, end_date)
                            if history_df is not None and not history_df.empty:
                                history_df = thread_calculator.calculate_all(history_df)
                                # Use incremental save to only insert non-existing records
                                inserted_count = thread_storage.save_stock_data_incremental(history_df)
                                if inserted_count > 0:
                                    processed_count += 1
                                else:
                                    # No new data inserted, count as cached
                                    processed_count += 1
                            else:
                                failed_count += 1
                        else:
                            processed_count += 1  # Today's data exists, count as processed

                    except Exception as e:
                        failed_count += 1
                        Logger.warning(f"Failed to process {symbol}: {str(e)}")

                # Update total counters
                with total_lock:
                    processed_stocks += processed_count
                    failed_stocks += failed_count
                    completed_sectors.append(sector_name)

                # Update sector progress
                sectors_processed += 1
                progress = sectors_processed / total_sectors
                progress_bar.progress(progress)

                Logger.info(f"Sector {sector_name} completed - processed: {processed_count}, failed: {failed_count}")

            except Exception as e:
                Logger.error(f"Error processing sector {sector_name}: {str(e)}")
                sectors_processed += 1
                progress = sectors_processed / total_sectors
                progress_bar.progress(progress)

        Logger.info(f"_update_stocks_data: Processing complete - total processed: {processed_stocks}, failed: {failed_stocks}")

        # Clear progress and status displays
        progress_bar.empty()
        sector_status.empty()
        stock_status.empty()
        progress_status.empty()

        # Display summary
        if processed_stocks > 0:
            st.success(f"✅ 股票数据更新完成! 已处理 {processed_stocks} 只股票, 失败 {failed_stocks} 只")
        elif failed_stocks > 0:
            st.warning(f"⚠️ 股票数据更新完成! 已处理 {processed_stocks} 只股票, 失败 {failed_stocks} 只")
            st.info("💡 失败原因可能是 akshare API 连接问题，请稍后重试")
        else:
            st.warning("⚠️ 没有股票被处理，请检查 akshare API 连接")

    except Exception as e:
            Logger.error(f"_update_stocks_data: Exception: {str(e)}")
            progress_bar.empty()
            sector_status.empty()
            stock_status.empty()
            progress_status.empty()
            st.error(f"更新失败: {str(e)}")


def _update_indicators_data(storage: StockStorage):
    """Update technical indicators for configured stocks from config file.

    Args:
        storage: StockStorage instance for data operations
    """
    from analysis.indicators import IndicatorCalculator
    from data.fetcher import DataFetcher
    from utils.config import Config
    import json
    from datetime import datetime
    from datetime import timedelta

    update_placeholder = st.empty()
    progress_placeholder = st.empty()

    try:
        # Load sectors configuration from config file
        update_placeholder.info("正在读取配置文件...")
        sectors_config = Config.get_major_sectors_config()

        if not sectors_config:
            st.warning("配置文件中没有板块数据，请检查 config/MAJOR_SECTORS.json")
            return

        # Collect all unique stocks from config
        stock_symbols = set()
        for sector_config in sectors_config:
            stocks = sector_config.get('stocks', [])
            stock_symbols.update(stocks)

        # Convert to list of stock dictionaries (all from config, regardless of DB state)
        stocks_list = []
        for symbol in stock_symbols:
            stock_info = {
                'symbol': symbol,
                'name': f'股票{symbol}',
                'industry': None,
                'sector': None,
                'market_cap': None
            }
            stocks_list.append(stock_info)

        if not stocks_list:
            st.warning("配置文件中没有股票数据")
            return

        update_placeholder.info(f"正在更新 {len(stocks_list)} 只配置股票的技术指标...")

        # Thread-safe counters
        total_lock = threading.Lock()
        processed_count = 0
        failed_count = 0
        total = len(stocks_list)

        # Get date range from config
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = Config.get_data_start_date().replace('-', '')

        # Create shared fetcher instance to avoid multiple baostock connections
        shared_fetcher = DataFetcher()

        def process_stock(stock: Dict) -> Dict:
            """Process a single stock and return result.

            Args:
                stock: Stock dictionary

            Returns:
                Result dictionary with status and info
            """
            nonlocal processed_count
            nonlocal failed_count

            # Use a separate storage instance for each thread
            db = DatabaseManager()
            thread_storage = StockStorage(db)
            thread_calculator = IndicatorCalculator()

            # Use shared fetcher instance
            thread_fetcher = shared_fetcher

            result = {
                'symbol': stock['symbol'],
                'success': False,
                'rows_processed': 0,
                'error': None
            }

            try:
                Logger.info(f"开始处理股票: {stock['symbol']}")

                # Get latest date in database for incremental update
                latest_date = thread_storage.get_stock_latest_date(stock['symbol'])
                if latest_date:
                    # Convert YYYY-MM-DD to YYYYMMDD and add 1 day
                    latest_dt = datetime.strptime(latest_date, '%Y-%m-%d')
                    next_date = (latest_dt + timedelta(days=1)).strftime('%Y%m%d')
                    stock_start_date = next_date
                    Logger.debug(f"{stock['symbol']}: 最新日期 {latest_date}, 从 {next_date} 开始获取")
                else:
                    # No data exists, start from config start date
                    stock_start_date = start_date
                    Logger.debug(f"{stock['symbol']}: 无历史数据，从 {start_date} 开始获取")

                # Fetch data from akshare
                history_df = thread_fetcher.get_stock_history(stock['symbol'], stock_start_date, end_date)

                if history_df is not None and not history_df.empty:
                    Logger.info(f"{stock['symbol']}: 获取到 {len(history_df)} 条数据")

                    # Calculate indicators
                    df_with_indicators = thread_calculator.calculate_all(history_df)

                    # Save updated data with current timestamp
                    inserted_count = thread_storage.save_stock_data_incremental(df_with_indicators)

                    if inserted_count > 0:
                        result['success'] = True
                        result['rows_processed'] = inserted_count
                        Logger.info(f"{stock['symbol']}: 成功插入 {inserted_count} 条新数据")
                    else:
                        # No new data but stock exists
                        result['success'] = True
                        result['rows_processed'] = 0
                        Logger.info(f"{stock['symbol']}: 无新数据插入（数据已存在）")
                elif history_df is None:
                    error_msg = 'API返回None（可能网络连接问题或股票代码无效）'
                    result['error'] = error_msg
                    Logger.warning(f"{stock['symbol']}: {error_msg}")
                else:
                    error_msg = f'获取数据为空（起始日期: {stock_start_date}, 结束日期: {end_date}）'
                    result['error'] = error_msg
                    Logger.warning(f"{stock['symbol']}: {error_msg}")

            except Exception as e:
                result['error'] = str(e)
                Logger.error(f"{stock['symbol']}: 处理失败 - {str(e)}")

            finally:
                # Update progress safely
                with total_lock:
                    processed_count += 1
                    if not result['success']:
                        failed_count += 1

            return result

        # Process stocks sequentially for better error handling and progress updates
        max_workers = 2  # Reduce to 2 to avoid API rate limiting and connection issues

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            futures = {executor.submit(process_stock, stock): stock for stock in stocks_list}

            # Process completed tasks and update progress
            for future in as_completed(futures):
                stock = futures[future]
                try:
                    result = future.result()
                    # Update progress display
                    if result['success']:
                        progress_placeholder.info(f"进度: {processed_count}/{total} 只股票 (成功: {processed_count - failed_count}, 失败: {failed_count})")
                    else:
                        progress_placeholder.warning(f"进度: {processed_count}/{total} 只股票 (成功: {processed_count - failed_count}, 失败: {failed_count}) - {stock['symbol']}: {result.get('error', '未知错误')}")
                except Exception as e:
                    progress_placeholder.error(f"进度: {processed_count}/{total} 只股票 - {stock['symbol']}: 处理异常: {str(e)}")

        if failed_count == 0:
            st.success(f"✅ 技术指标更新完成! 共处理 {processed_count} 只股票")
        else:
            st.warning(f"⚠️ 技术指标更新完成! 共处理 {processed_count} 只股票, 失败 {failed_count} 只")

    except Exception as e:
        st.error(f"更新失败: {str(e)}")


def _train_models(storage: StockStorage):
    """Train prediction models using configured stocks.

    Args:
        storage: StockStorage instance for fetching training data
    """
    from prediction.trainer import ModelTrainer
    from datetime import datetime
    import json
    import os
    import pandas as pd
    from utils.config import Config

    # Load configured stocks from config file
    sectors_config = Config.get_major_sectors_config()

    if not sectors_config:
        st.warning("配置文件中没有板块数据，请检查 config/MAJOR_SECTORS.json")
        return

    # Collect all unique stocks from config
    stock_symbols = set()
    for sector_config in sectors_config:
        stocks = sector_config.get('stocks', [])
        stock_symbols.update(stocks)

    # Convert to list of stock dictionaries
    stocks = []
    for symbol in stock_symbols:
        # Check if stock has data in stock_data table
        try:
            df = storage.get_stock_data(symbol)
            if not df.empty:
                # Create stock dictionary with minimal required fields
                stock_info = {
                    'symbol': symbol,
                    'name': f'股票{symbol}',  # Placeholder name
                    'industry': None,
                    'sector': None,
                    'market_cap': None
                }
                stocks.append(stock_info)
        except Exception:
            pass

    if not stocks:
        st.error("❌ 数据库中没有股票数据，请先更新板块数据")
        return

    # Check data availability - sample a few stocks
    total_stocks = len(stocks)
    st.info(f"📊 检测到 {total_stocks} 只配置股票，检查历史数据...")

    # Sample check: test first 5 stocks
    sample_stocks = stocks[:min(5, len(stocks))]
    data_available = False
    max_data_length = 0

    for stock in sample_stocks:
        try:
            df = storage.get_stock_data(stock['symbol'])
            if not df.empty:
                data_available = True
                max_data_length = max(max_data_length, len(df))
        except Exception:
            pass

    if not data_available:
        st.error("❌ 数据库中没有历史交易数据")
        st.markdown("""
        **请按以下步骤操作：**

        1. 点击 **"🔄 更新板块数据"** 获取板块列表
        2. 点击 **"🔄 更新股票数据"** 获取历史交易数据（首次可能需要较长时间）
        3. 等待数据更新完成后，再点击 **"🧠 训练预测模型"**

        **注意：** 首次更新股票数据需要从 akshare API 获取历史数据，
        涉及配置的股票，请耐心等待。
        """)
        return

    st.info(f"✅ 历史数据检查通过，样本股票最多有 {max_data_length} 条记录")

    # Create model directory
    model_dir = 'models'
    os.makedirs(model_dir, exist_ok=True)

    # Initialize trainer
    try:
        trainer = ModelTrainer(storage, model_dir)
    except Exception as e:
        st.error(f"❌ 初始化训练器失败: {str(e)}")
        return

    # Training progress
    progress_placeholder = st.empty()
    log_placeholder = st.empty()

    # Train each model
    model_names = {
        'short': '短期预测模型',
        'medium': '中期预测模型',
        'long': '长期预测模型'
    }

    results = {}

    for horizon, name in model_names.items():
        progress_placeholder.info(f"⏳ 正在训练 {name}...")
        log_placeholder.empty()

        try:
            # Get available stocks for this horizon
            symbols = [s['symbol'] for s in stocks]

            # Train model
            if horizon == 'short':
                metrics = trainer.train_short_term_model(symbols)
            elif horizon == 'medium':
                metrics = trainer.train_medium_term_model(symbols)
            else:
                metrics = trainer.train_long_term_model(symbols)

            results[horizon] = metrics

            # Display result
            if 'error' in metrics:
                st.warning(f"⚠️ {name} 训练失败: {metrics['error']}")
                log_placeholder.info(
                    f"💡 可能原因：\n"
                    f"  • 数据不足（短期需要至少25天，中期需要至少180天，长期需要至少372天）\n"
                    f"  • 没有足够的买/卖信号样本（阈值3%）\n"
                    f"  • 请先点击「🔄 更新股票数据」获取足够的历史数据"
                )
            else:
                accuracy = metrics.get('accuracy', 0)
                samples = metrics.get('samples', 0)
                st.success(f"✅ {name} 训练完成! 准确率: {accuracy*100:.1f}%, 样本数: {samples}")

        except Exception as e:
            st.error(f"❌ {name} 训练失败: {str(e)}")
            results[horizon] = {'error': str(e)}

    # Save model info
    model_info = {}
    for horizon, name in model_names.items():
        if horizon in results and 'error' not in results[horizon]:
            model_info[name] = {
                'accuracy': results[horizon].get('accuracy', 0),
                'samples': results[horizon].get('samples', 0),
                'train_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

    if model_info:
        model_info_file = os.path.join(model_dir, 'model_info.json')
        with open(model_info_file, 'w') as f:
            json.dump(model_info, f, indent=2)

    # Summary
    st.markdown("---")

    if model_info:
        st.success("🎉 所有模型训练完成!")
        st.info("💡 现在可以在股票详情页查看预测结果")
    else:
        st.warning("⚠️ 所有模型训练失败，请检查历史数据是否充足")


def show_history():
    """Display history review page."""
    st.info("🚀 历史回顾功能将在后续实现")