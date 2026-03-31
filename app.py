"""Main Streamlit application."""

import streamlit as st
from utils.logger import Logger
from data.database import DatabaseManager
from data.storage import StockStorage
from ui.layout import header, navigation, sector_grid, footer

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


# Layer 1: Header
header()

# Layer 2: Navigation (left side)
content_col = navigation()

# Layer 3: Content based on navigation (in content column)
nav_module = st.session_state.nav_module

with content_col:
    if nav_module == "home":
        st.markdown("## 🏠 首页总览")

        # Load sectors from database
        storage = StockStorage(db_manager)
        sectors = load_sectors()

        def handle_sector_click(sector):
            """Handle sector selection."""
            st.session_state.selected_sector = sector
            st.session_state.nav_module = "analysis"
            st.session_state.subpage = "sector_detail"

        sector_grid(sectors, storage=storage, on_sector_click=handle_sector_click)

    elif nav_module == "prediction":
        st.markdown("## 🎯 智能预测")
        st.info("智能预测功能将在后续版本实现")

    elif nav_module == "analysis":
        st.markdown("## 📊 板块分析")

        if st.session_state.selected_sector:
            sector = st.session_state.selected_sector
            storage = StockStorage(db_manager)

            # Display sector info with metrics
            st.write(f"**当前板块**: {sector['sector_name']}")

            # Get sector leaders
            leaders = storage.get_sector_leaders(sector.get('sector_id', ''))
            if leaders:
                st.write(f"**龙头股数量**: {len(leaders)}")
                avg_score = sum(l.get('score', 0) for l in leaders) / len(leaders)
                st.write(f"**平均得分**: {avg_score:.2f}")

                # Display top 5 leaders
                st.markdown("### 龙头股 Top 5")
                for i, leader in enumerate(leaders[:5], 1):
                    symbol = leader.get('symbol', '')
                    score = leader.get('score', 0)
                    rank = leader.get('rank', 0)
                    st.write(f"{i}. {symbol} - 得分: {score:.2f} (排名: {rank})")

            if st.button("← 返回板块列表"):
                st.session_state.selected_sector = None
                st.session_state.nav_module = "home"
                st.rerun()
        else:
            st.info("请从首页选择一个板块")

    elif nav_module == "update":
        from ui.pages import show_data_update
        show_data_update()

    elif nav_module == "history":
        st.markdown("## 📜 历史回顾")
        from ui.pages import show_history
        show_history()

# Layer 4: Footer
footer()

# Close database connection
db_manager.close()