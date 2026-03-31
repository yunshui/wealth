"""Main Streamlit application."""

import streamlit as st
from utils.logger import Logger
from data.database import DatabaseManager
from data.storage import StockStorage
from ui.layout import sidebar_layout, sector_grid, footer_right

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


def load_sectors():
    """Load sectors from database.

    Returns:
        List of sector dictionaries
    """
    storage = StockStorage(db_manager)
    return storage.get_all_sectors()


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
        st.info("智能预测功能将在后续版本实现")
        footer_right()

    elif nav_module == "analysis":
        st.markdown("<h2 style='color: #000000; margin: 0;'>📊 板块分析</h2>", unsafe_allow_html=True)

        if st.session_state.selected_sector:
            sector = st.session_state.selected_sector
            storage = StockStorage(db_manager)

            # Display sector info with metrics
            st.markdown(f"<p style='color: #000000;'><strong>当前板块:</strong> {sector['sector_name']}</p>", unsafe_allow_html=True)

            # Get sector leaders
            leaders = storage.get_sector_leaders(sector.get('sector_id', ''))
            if leaders:
                st.markdown(f"<p style='color: #000000;'><strong>龙头股数量:</strong> {len(leaders)}</p>", unsafe_allow_html=True)
                avg_score = sum(l.get('score', 0) for l in leaders) / len(leaders)
                st.markdown(f"<p style='color: #000000;'><strong>平均得分:</strong> {avg_score:.2f}</p>", unsafe_allow_html=True)

                # Display top 5 leaders
                st.markdown("<h3 style='color: #000000;'>龙头股 Top 5</h3>", unsafe_allow_html=True)
                for i, leader in enumerate(leaders[:5], 1):
                    symbol = leader.get('symbol', '')
                    name = get_stock_name(storage, symbol)
                    score = leader.get('score', 0)
                    rank = leader.get('rank', 0)
                    st.markdown(f"<p style='color: #000000;'>{i}. {symbol} - {name} - 得分: {score:.2f} (排名: {rank})</p>", unsafe_allow_html=True)

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