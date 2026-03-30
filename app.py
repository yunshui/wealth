"""Main Streamlit application."""

import streamlit as st
from utils.logger import Logger
from data.database import DatabaseManager
from ui.pages import show_homepage, show_stock_detail, show_data_update, show_history
from ui.layout import footer

# Page configuration
st.set_page_config(
    page_title="人机协同A股智能投资决策系统",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "首页/板块总览"

if "db_initialized" not in st.session_state:
    st.session_state.db_initialized = False

# Sidebar
with st.sidebar:
    st.title("📈 人机协同A股智能投资决策系统")
    st.divider()

    # Page navigation
    page = st.radio(
        "导航",
        ["首页/板块总览", "股票详情", "数据更新", "历史回顾"],
        index=["首页/板块总览", "股票详情", "数据更新", "历史回顾"].index(st.session_state.page)
    )
    st.session_state.page = page

    st.divider()
    st.caption("基于7年A股历史数据预测")

# Main content
if st.session_state.page == "首页/板块总览":
    show_homepage()

elif st.session_state.page == "股票详情":
    show_stock_detail()

elif st.session_state.page == "数据更新":
    show_data_update()

elif st.session_state.page == "历史回顾":
    show_history()

# Footer
footer()