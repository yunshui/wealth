"""Main Streamlit application."""

import streamlit as st
from utils.logger import Logger
from data.database import DatabaseManager
from data.storage import StockStorage
from ui.layout import sidebar_layout, sector_grid, footer_right
from datetime import datetime
import time

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

if "sector_data" not in st.session_state:
    st.session_state.sector_data = {}

if "last_refresh_time" not in st.session_state:
    st.session_state.last_refresh_time = 0

if "refresh_requested" not in st.session_state:
    st.session_state.refresh_requested = False


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


def fetch_sector_realtime_data(storage: StockStorage, sector_id: str):
    """Fetch real-time data for sector leaders from akshare.

    Args:
        storage: StockStorage instance
        sector_id: Sector ID

    Returns:
        Dictionary with symbol as key and latest data as value
    """
    try:
        from data.fetcher import DataFetcher

        # Get sector leaders
        leaders = storage.get_sector_leaders(sector_id)
        if not leaders:
            Logger.warning(f"No leaders found for sector {sector_id}")
            # Return empty data but also log this
            return {}

        fetcher = DataFetcher()
        realtime_data = {}

        update_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        for leader in leaders:
            symbol = leader.get('symbol', '')
            if symbol:
                try:
                    # Get latest/real-time data using spot API
                    latest_info = fetcher.get_stock_latest(symbol)

                    if latest_info:
                        # Extract data from latest info
                        open_price = float(latest_info.get('今开', 0))
                        high_price = float(latest_info.get('最高', 0))
                        low_price = float(latest_info.get('最低', 0))
                        close_price = float(latest_info.get('最新价', 0))
                        prev_close = float(latest_info.get('昨收', 0))
                        volume = float(latest_info.get('成交量', 0))
                        amount = float(latest_info.get('成交额', 0))

                        realtime_data[symbol] = {
                            'symbol': symbol,
                            'open': open_price,
                            'high': high_price,
                            'low': low_price,
                            'close': close_price,
                            'volume': volume,
                            'amount': amount,
                            'date': update_time_str,
                            'prev_close': prev_close
                        }
                except Exception as e:
                    Logger.warning(f"Failed to fetch realtime data for {symbol}: {str(e)}")
                    continue

        # Update session state
        st.session_state.sector_data = realtime_data
        st.session_state.last_refresh_time = time.time()

        return realtime_data
    except Exception as e:
        Logger.error(f"Failed to fetch sector realtime data: {str(e)}")
        return {}


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

            # Header with refresh button
            col_left, col_right = st.columns([4, 1])
            with col_left:
                st.markdown(f"<p style='color: #000000;'><strong>当前板块:</strong> {sector['sector_name']}</p>", unsafe_allow_html=True)
            with col_right:
                if st.button("🔄 刷新数据", key="refresh_sector"):
                    st.session_state.refresh_requested = True

            # Handle refresh request
            if st.session_state.refresh_requested:
                st.session_state.sector_data = {}
                st.session_state.last_refresh_time = 0
                st.session_state.refresh_requested = False
                st.rerun()

            # Auto-refresh every 5 minutes
            current_time = time.time()
            if st.session_state.last_refresh_time > 0 and current_time - st.session_state.last_refresh_time > 300:  # 5 minutes
                st.session_state.sector_data = {}
                st.session_state.last_refresh_time = 0
                st.session_state.refresh_requested = True

            # Get sector leaders
            leaders = storage.get_sector_leaders(sector_id)

            # Check if need to fetch data (do this before UI is rendered)
            if st.session_state.last_refresh_time == 0:
                with st.spinner("正在获取实时数据..."):
                    fetch_sector_realtime_data(storage, sector_id)
                # Always set refresh time to prevent infinite loops
                if st.session_state.last_refresh_time == 0:
                    st.session_state.last_refresh_time = time.time()
                st.rerun()

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
                    name = get_stock_name(storage, symbol)
                    score = leader.get('score', 0)
                    rank = leader.get('rank', 0)

                    # Use realtime data if available
                    realtime_data = st.session_state.sector_data.get(symbol, {})

                    # Create expandable card for each stock
                    with st.expander(f"{i}. {symbol} - {name} - 得分: {score:.2f} (排名: {rank})", expanded=True):
                        if realtime_data:
                            # Use realtime data
                            close_price = realtime_data.get('close', 0)
                            prev_close = realtime_data.get('prev_close', 0)

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
                                st.metric("开盘价", f"{realtime_data.get('open', 0):.2f}")

                            with col4:
                                update_date = realtime_data.get('date', '')
                                if isinstance(update_date, datetime):
                                    update_date = update_date.strftime('%Y-%m-%d %H:%M:%S')
                                st.caption(f"更新日期: {update_date}")

                            # Additional price analysis
                            st.markdown("**价位分析**")
                            price_col1, price_col2, price_col3 = st.columns(3)

                            with price_col1:
                                st.metric("最高价", f"{realtime_data.get('high', 0):.2f}")

                            with price_col2:
                                st.metric("最低价", f"{realtime_data.get('low', 0):.2f}")

                            with price_col3:
                                volume = realtime_data.get('volume', 0)
                                if volume > 100000000:
                                    vol_display = f"{volume/100000000:.2f}亿"
                                elif volume > 10000:
                                    vol_display = f"{volume/10000:.2f}万"
                                else:
                                    vol_display = f"{volume}"
                                st.metric("成交量", vol_display)

                            # Amplitude analysis
                            high_price = realtime_data.get('high', 0)
                            low_price = realtime_data.get('low', 0)
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
                            st.caption("暂无实时数据")

                            # Add button to view stock detail (even without realtime data)
                            if st.button(f"📊 查看 {symbol} 详情和预测", key=f"view_detail_no_data_{symbol}"):
                                st.session_state.selected_symbol = symbol
                                st.session_state.nav_module = "stock_detail"
                                st.rerun()

            # Display last refresh time
            if st.session_state.last_refresh_time > 0:
                refresh_time = datetime.fromtimestamp(st.session_state.last_refresh_time).strftime('%Y-%m-%d %H:%M:%S')
                st.caption(f"数据更新时间: {refresh_time} (每5分钟自动刷新)")

            if st.button("← 返回板块列表"):
                st.session_state.selected_sector = None
                st.session_state.nav_module = "home"
                st.session_state.sector_data = {}
                st.session_state.last_refresh_time = 0
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