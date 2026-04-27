"""Main Streamlit application."""

import streamlit as st
from utils.logger import Logger
from data.database import DatabaseManager
from data.storage import StockStorage
from ui.layout import sidebar_layout, sector_grid, footer_right
from datetime import datetime, timedelta as td
import time
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="人机协同A股智能投资决策系统",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize database
db_manager = DatabaseManager()
if not db_manager.check_database_exists():
    db_manager.create_tables()
    Logger.info("Database initialized successfully")

# Initialize session state
if "nav_module" not in st.session_state:
    st.session_state.nav_module = "home"

if "selected_sector" not in st.session_state:
    st.session_state.selected_sector = None

if "selected_symbol" not in st.session_state:
    st.session_state.selected_symbol = None

if "update_sector_requested" not in st.session_state:
    st.session_state.update_sector_requested = False

if "sector_updated" not in st.session_state:
    st.session_state.sector_updated = False


def load_sectors():
    """Load major sectors from database.

    Returns:
        List of sector dictionaries
    """
    storage = StockStorage(db_manager)
    return storage.get_major_sectors()


def get_stock_name(storage: StockStorage, symbol: str) -> str:
    """Helper function to safely get stock name.

    Args:
        storage: StockStorage instance
        symbol: Stock symbol

    Returns:
        Stock name or 'Unknown' if not found
    """
    stock_data = storage.get_stock(symbol)
    return stock_data.get('name', 'Unknown') if stock_data else 'Unknown'


def get_stock_latest_data(storage: StockStorage, symbol: str) -> dict:
    """Get latest stock data from database.

    Args:
        storage: StockStorage instance
        symbol: Stock symbol

    Returns:
        Dictionary with latest stock data
    """
    try:
        # Get latest stock data from stock_data table
        latest_data = storage.get_stock_latest_data(symbol)
        if latest_data:
            return latest_data
    except Exception as e:
        Logger.warning(f"Failed to get latest data for {symbol}: {str(e)}")
    return {}


def update_sector_stocks(storage: StockStorage, sector_id: str, full_update: bool = False,
                          progress_bar=None, status_placeholder=None):
    """Update stock data for the current sector.

    Args:
        storage: StockStorage instance
        sector_id: Sector ID
        full_update: If True, fetch all data from config start date; otherwise incremental
        progress_bar: Streamlit progress bar element
        status_placeholder: Streamlit status placeholder element

    Returns:
        True if update was successful, False otherwise
    """
    from data.fetcher import DataFetcher
    from analysis.indicators import IndicatorCalculator
    from datetime import timedelta
    from utils.config import Config
    from utils.logger import Logger

    Logger.info(f"========== update_sector_stocks: START ==========")
    Logger.info(f"update_sector_stocks: sector_id={sector_id}, full_update={full_update}")

    try:
        # Get sector leaders
        leaders = storage.get_sector_leaders(sector_id)
        if not leaders:
            st.warning("该板块暂无龙头股")
            return False

        Logger.info(f"update_sector_stocks: Found {len(leaders)} leaders in sector {sector_id}")

        # Calculate date range
        end_date = datetime.now().strftime('%Y%m%d')
        cache_hours = Config.get_update_cache_hours()

        # Create progress displays if not provided
        if progress_bar is None:
            progress_bar = st.progress(0)
        if status_placeholder is None:
            status_placeholder = st.empty()

        processed_count = 0
        failed_count = 0
        total = len(leaders)

        fetcher = DataFetcher()
        calculator = IndicatorCalculator()

        for idx, leader in enumerate(leaders):
            symbol = leader.get('symbol', '')
            name = leader.get('name', symbol)

            Logger.info(f"update_sector_stocks: Processing {idx+1}/{total}: {symbol} - {name}")

            # Update status - use markdown with more prominent display
            status_placeholder.markdown(f"""
            **🔄 正在更新股票数据**

            进度: {idx+1}/{total} ({(idx+1)/total*100:.1f}%)

            当前处理: **{symbol}** - {name}
            """)

            # Update progress bar
            progress = (idx + 1) / total
            progress_bar.progress(progress)

            # Force Streamlit to render the updated progress
            time.sleep(0.2)

            try:
                # Check if stock info exists in stocks table
                stock_info = storage.get_stock(symbol)
                current_name = stock_info.get('name') if stock_info else None
                needs_name_update = (
                    not stock_info or
                    not stock_info.get('name') or
                    stock_info.get('name', '').startswith('股票') or
                    stock_info.get('name', '') == symbol
                )

                Logger.info(f"Stock {symbol}: stock_info={bool(stock_info)}, current_name='{current_name}', needs_update={needs_name_update}")

                if needs_name_update:
                    try:
                        stock_info_api = fetcher.get_stock_info(symbol)
                        new_name = None

                        Logger.info(f"Stock {symbol}: API returned type={type(stock_info_api)}")

                        # Handle DataFrame format from akshare
                        if isinstance(stock_info_api, pd.DataFrame):
                            Logger.info(f"Stock {symbol}: Processing DataFrame with {len(stock_info_api)} rows")
                            for idx, row in stock_info_api.iterrows():
                                item = row.get('item')
                                Logger.debug(f"Stock {symbol}: Row {idx}: item='{item}'")
                                if item == '股票简称':
                                    new_name = row.get('value')
                                    Logger.info(f"Stock {symbol}: Found stock name '{new_name}' at row {idx}")
                                    break

                        # Handle dict format
                        if not new_name and isinstance(stock_info_api, dict):
                            if 'value' in stock_info_api:
                                for item in stock_info_api['value']:
                                    if isinstance(item, dict) and item.get('item') == '股票简称':
                                        new_name = item.get('value')
                                        break
                            # Try to find stock name in dict directly
                            for key, value in stock_info_api.items():
                                if '名称' in key or 'name' in key.lower():
                                    new_name = value
                                    break

                        Logger.info(f"Stock {symbol}: Extracted name='{new_name}'")

                        if new_name and not new_name.startswith('股票'):
                            # Update or insert stock info in stocks table
                            conn = storage.db.get_connection()
                            cursor = conn.cursor()
                            cursor.execute('''
                                INSERT INTO stocks (symbol, name, industry, sector, updated_at)
                                VALUES (?, ?, ?, ?, ?)
                                ON CONFLICT(symbol) DO UPDATE SET
                                    name = excluded.name,
                                    updated_at = excluded.updated_at
                            ''', (symbol, new_name, stock_info.get('industry') if stock_info else None,
                                  stock_info.get('sector') if stock_info else None,
                                  datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                            conn.commit()
                            Logger.info(f"Updated stock info for {symbol}: {new_name}")
                            name = new_name  # Update display name
                        else:
                            Logger.warning(f"Stock {symbol}: No valid name found (new_name='{new_name}')")
                    except Exception as e:
                        Logger.warning(f"Failed to update stock name for {symbol}: {str(e)}")

                # Check if today's data already exists
                today_str = datetime.now().strftime('%Y-%m-%d')
                needs_update = True

                try:
                    stock_info = storage.get_stock(symbol)
                    if stock_info and stock_info.get('updated_at'):
                        last_update = datetime.strptime(stock_info['updated_at'], '%Y-%m-%d %H:%M:%S')
                        hours_since_update = (datetime.now() - last_update).total_seconds() / 3600
                        has_today_data = storage.has_stock_data_for_date(symbol, today_str)

                        if has_today_data:
                            needs_update = False
                        elif hours_since_update < cache_hours:
                            needs_update = True
                except:
                    pass

                if needs_update:
                    # Get latest date for incremental update
                    # If full_update is True, always use config start date
                    if full_update:
                        # Full update: always start from config start date
                        start_date = Config.get_data_start_date().replace('-', '')
                        Logger.info(f"{symbol}: Full update, starting from {start_date}")
                    else:
                        # Incremental update: start from latest date + 1
                        latest_date = storage.get_stock_latest_date(symbol)
                        if latest_date:
                            latest_dt = datetime.strptime(latest_date, '%Y-%m-%d')
                            next_date = (latest_dt + timedelta(days=1)).strftime('%Y%m%d')
                            start_date = next_date
                            Logger.info(f"{symbol}: Incremental update, starting from {start_date}")
                        else:
                            # No data exists, use config start date
                            start_date = Config.get_data_start_date().replace('-', '')
                            Logger.info(f"{symbol}: No data, starting from {start_date}")

                    # Fetch and save data
                    history_df = fetcher.get_stock_history(symbol, start_date, end_date)
                    if history_df is not None and not history_df.empty:
                        Logger.info(f"{symbol}: Fetched {len(history_df)} records")
                        history_df = calculator.calculate_all(history_df)
                        storage.save_stock_data_incremental(history_df)
                        processed_count += 1
                        Logger.info(f"{symbol}: Successfully saved data")
                    else:
                        failed_count += 1
                        Logger.warning(f"{symbol}: Failed to fetch data (history_df is {type(history_df)}, empty={history_df.empty if history_df is not None else 'N/A'})")
                else:
                    processed_count += 1  # Today's data exists
                    Logger.info(f"{symbol}: Skipped (today's data exists)")

            except Exception as e:
                failed_count += 1
                Logger.error(f"Failed to update {symbol}: {str(e)}")
                import traceback
                Logger.error(f"Traceback: {traceback.format_exc()}")

            # Update progress
            progress = (idx + 1) / total
            progress_bar.progress(progress)

        # Show result
        # Only clear progress displays if they were created inside this function
        if progress_bar is None:
            progress_bar.empty()
        if status_placeholder is None:
            status_placeholder.empty()

        # Only show result if placeholders were created inside this function
        if progress_bar is None and status_placeholder is None:
            if processed_count > 0:
                st.success(f"✅ 更新完成! 成功 {processed_count} 只, 失败 {failed_count} 只")
            else:
                st.warning(f"⚠️ 更新完成! 成功 {processed_count} 只, 失败 {failed_count} 只")

        Logger.info(f"update_sector_stocks: Completed - processed: {processed_count}, failed: {failed_count}")
        return True

    except Exception as e:
        Logger.error(f"update_sector_stocks: Exception: {str(e)}")
        Logger.error(f"Failed to update sector stocks: {str(e)}")
        st.error(f"更新失败: {str(e)}")
        return False


# Left sidebar with title and collapsible navigation
content_col = sidebar_layout()

# Main content area (right side)
nav_module = st.session_state.nav_module

with content_col:
    if nav_module == "home":
        st.markdown("<h2 style='color: #2c3e50; margin: 0;'>🏠 首页总览</h2>", unsafe_allow_html=True)

        # Load sectors from database
        storage = StockStorage(db_manager)
        sectors = load_sectors()

        def handle_sector_click(sector):
            """Handle sector selection."""
            st.session_state.selected_sector = sector
            st.session_state.nav_module = "analysis"
            st.session_state.subpage = "sector_detail"

        sector_grid(sectors, storage=storage, on_sector_click=handle_sector_click)

        # Footer at bottom of content area
        footer_right()

    elif nav_module == "prediction":
        st.markdown("<h2 style='color: #2c3e50; margin: 0;'>🎯 智能预测</h2>", unsafe_allow_html=True)
        st.info("💡 请从「首页总览」选择板块，然后点击龙头股查看预测")
        footer_right()

    elif nav_module == "stock_detail":
        from ui.pages import show_stock_detail
        show_stock_detail()
        footer_right()

    elif nav_module == "analysis":
        st.markdown("<h2 style='color: #000000; margin: 0;'>📊 板块分析</h2>", unsafe_allow_html=True)

        if st.session_state.selected_sector:
            sector = st.session_state.selected_sector
            storage = StockStorage(db_manager)
            sector_id = sector.get('sector_id', '')

            # Check if update is in progress
            if st.session_state.get('update_sector_in_progress', False):
                # Show update progress only
                st.markdown("---")
                st.markdown("### 📥 正在更新板块股票数据")
                st.info("💡 请稍候，正在获取股票数据...")

                progress_bar = st.progress(0)
                status_placeholder = st.empty()

                full_update = st.session_state.get('full_update_requested', False)
                st.session_state.update_sector_in_progress = False

                # Force Streamlit to render
                time.sleep(0.2)

                # Call update function
                result = update_sector_stocks(storage, sector_id, full_update=full_update,
                                               progress_bar=progress_bar, status_placeholder=status_placeholder)

                # Clear placeholders
                progress_bar.empty()
                status_placeholder.empty()

                if result:
                    st.success("✅ 板块股票数据已更新，页面将刷新...")
                    time.sleep(1)
                    # Use st.rerun() to refresh the page
                    st.rerun()
                else:
                    st.warning("⚠️ 更新失败，请稍后重试")
                    time.sleep(1)
                    st.rerun()
            else:
                # Show normal sector analysis page
                # Add full update checkbox first
                full_update = st.checkbox("全量更新（从配置起始日期重新获取）", key="full_update_sector", value=False,
                                                help="勾选后将从配置的起始日期（2015-01-01）重新获取全部历史数据，不勾选则只获取缺失的数据")

                # Header with update button
                col_left, col_right = st.columns([4, 1])
                with col_left:
                    st.markdown(f"<p style='color: #000000;'><strong>当前板块:</strong> {sector['sector_name']}</p>", unsafe_allow_html=True)
                with col_right:
                    # Save full_update value to session state before rerun
                    if st.button("🔄 更新数据", key="update_sector_stocks"):
                        st.session_state.update_sector_in_progress = True
                        st.session_state.full_update_requested = full_update
                        st.rerun()

                # Get sector leaders and display (only when not updating)
                leaders = storage.get_sector_leaders(sector_id)

                # Display message if no leaders
                if not leaders:
                    st.warning(f"⚠️ 该板块暂无龙头股数据")
                    st.info("💡 请先在「数据更新」页面点击「更新板块数据」获取龙头股")
                else:
                    st.markdown(f"<p style='color: #000000;'><strong>龙头股数量:</strong> {len(leaders)}</p>", unsafe_allow_html=True)
                    avg_score = sum(l.get('score', 0) for l in leaders) / len(leaders)
                    st.markdown(f"<p style='color: #000000;'><strong>平均得分:</strong> {avg_score:.2f}</p>", unsafe_allow_html=True)

                    # Display top 5 leaders with price and analysis
                    st.markdown("<h3 style='color: #000000;'>龙头股 Top 5</h3>", unsafe_allow_html=True)

                    for i, leader in enumerate(leaders[:5], 1):
                        symbol = leader.get('symbol', '')
                        name = leader.get('name', get_stock_name(storage, symbol))
                        score = leader.get('score', 0)
                        rank = leader.get('rank', 0)

                        # Get latest data from database
                        stock_data = get_stock_latest_data(storage, symbol)

                        # Create expandable card for each stock
                        with st.expander(f"{i}. {symbol} - {name} - 得分: {score:.2f} (排名: {rank})", expanded=True):
                            if stock_data:
                                # Use database data
                                close_price = float(stock_data.get('close', 0))
                                open_price = float(stock_data.get('open', 0))
                                high_price = float(stock_data.get('high', 0))
                                low_price = float(stock_data.get('low', 0))
                                prev_close = float(stock_data.get('pre_close', 0))
                                volume = float(stock_data.get('vol', 0))

                                # Calculate change percentage
                                if prev_close and prev_close > 0:
                                    change_pct = (close_price - prev_close) / prev_close * 100
                                else:
                                    change_pct = 0

                                col1, col2, col3, col4 = st.columns(4)

                                with col1:
                                    st.metric("最新价", f"{close_price:.2f}")

                                with col2:
                                    # Use delta_color for Chinese stock market convention (red = up)
                                    delta_color = "normal" if change_pct > 0 else ("inverse" if change_pct < 0 else "off")
                                    st.metric("涨跌幅", f"{change_pct:+.2f}%", delta=None, delta_color=delta_color)

                                with col3:
                                    st.metric("开盘价", f"{open_price:.2f}")

                                with col4:
                                    data_date = stock_data.get('trade_date', '')
                                    if data_date:
                                        st.caption(f"数据日期: {data_date}")
                                    else:
                                        st.caption("数据日期: 未知")

                                # Additional price analysis
                                st.markdown("**价位分析**")
                                price_col1, price_col2, price_col3 = st.columns(3)

                                with price_col1:
                                    st.metric("最高价", f"{high_price:.2f}")

                                with price_col2:
                                    st.metric("最低价", f"{low_price:.2f}")

                                with price_col3:
                                    if volume > 100000000:
                                        vol_display = f"{volume/100000000:.2f}亿"
                                    elif volume > 10000:
                                        vol_display = f"{volume/10000:.2f}万"
                                    else:
                                        vol_display = f"{volume}"
                                    st.metric("成交量", vol_display)

                                # Amplitude analysis
                                if low_price > 0:
                                    amplitude = (high_price - low_price) / low_price * 100
                                    st.markdown(f"**振幅**: {amplitude:+.2f}%")

                                # Add button to view stock detail with prediction
                                if st.button(f"📊 查看 {symbol} 详情和预测", key=f"view_detail_{symbol}"):
                                    st.session_state.selected_symbol = symbol
                                    st.session_state.nav_module = "stock_detail"
                                    st.rerun()
                            else:
                                # Show no data indicator
                                st.caption("暂无数据，请在「数据更新」页面更新股票数据")

                                # Add button to view stock detail (even without data)
                                if st.button(f"📊 查看 {symbol} 详情和预测", key=f"view_detail_no_data_{symbol}"):
                                    st.session_state.selected_symbol = symbol
                                    st.session_state.nav_module = "stock_detail"
                                    st.rerun()

                    if st.button("← 返回板块列表"):
                        st.session_state.selected_sector = None
                        st.session_state.nav_module = "home"
                        st.rerun()

            footer_right()
        else:
            st.info("请从首页选择一个板块")
            footer_right()

    elif nav_module == "update":
        st.markdown("<h2 style='color: #000000; margin: 0;'>🔄 数据更新</h2>", unsafe_allow_html=True)
        from ui.pages import show_data_update
        show_data_update()
        footer_right()

    elif nav_module == "history":
        st.markdown("<h2 style='color: #2c3e50; margin: 0;'>📜 历史回顾</h2>", unsafe_allow_html=True)
        from ui.pages import show_history
        show_history()
        footer_right()

# Close database connection
db_manager.close()