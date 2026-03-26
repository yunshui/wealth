"""Main Streamlit application."""

import streamlit as st
from utils.logger import Logger
from data.database import DatabaseManager

# Page configuration
st.set_page_config(
    page_title="人机协同A股智能投资决策系统",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "首页"

if "db_initialized" not in st.session_state:
    st.session_state.db_initialized = False

# Sidebar
with st.sidebar:
    st.title("📈 人机协同A股智能投资决策系统")
    st.divider()

    # Page navigation
    page = st.radio(
        "导航",
        ["首页/板块总览", "股票详情", "数据更新"],
        index=["首页/板块总览", "股票详情", "数据更新"].index(st.session_state.page)
    )
    st.session_state.page = page

    st.divider()
    st.caption("基于7年A股历史数据预测")

# Main content
if st.session_state.page == "首页/板块总览":
    st.header("🏠 首页/板块总览")
    st.info("🚀 功能开发中...")
    st.write("""
    本页面将展示:
    - 主要板块概览
    - 板块龙头股列表
    - 实时预测建议
    """)

elif st.session_state.page == "股票详情":
    st.header("📊 股票详情")
    st.info("🚀 功能开发中...")

    # Stock symbol input
    symbol = st.text_input("股票代码", placeholder="例如: 000001.SZ")

    if symbol:
        st.write(f"正在查询: {symbol}")
        st.warning("数据查询功能将在Stage 2实现")

    st.write("""
    本页面将展示:
    - 股票基本信息
    - 历史价格走势
    - 技术指标分析
    - 短中长期预测
    - 买卖建议及理由
    """)

elif st.session_state.page == "数据更新":
    st.header("🔄 数据更新")
    st.info("🚀 功能开发中...")

    # Update buttons
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("更新板块数据", use_container_width=True):
            st.warning("板块数据更新功能将在Stage 2实现")

    with col2:
        if st.button("更新股票数据", use_container_width=True):
            st.warning("股票数据更新功能将在Stage 2实现")

    with col3:
        if st.button("训练预测模型", use_container_width=True):
            st.warning("模型训练功能将在Stage 3实现")

    # Database status
    st.divider()
    st.subheader("数据库状态")

    try:
        db = DatabaseManager()
        if db.check_database_exists():
            st.success("✅ 数据库已初始化")
            last_update = db.get_last_update_date()
            if last_update:
                st.write(f"最后更新日期: {last_update}")
            else:
                st.write("暂无数据")
        else:
            st.warning("⚠️ 数据库未初始化")
            if st.button("初始化数据库"):
                db.create_tables()
                st.success("数据库初始化成功!")
                st.rerun()
        db.close()
    except Exception as e:
        st.error(f"数据库错误: {e}")

    st.write("""
    本页面将提供:
    - 一键数据更新功能
    - 模型训练界面
    - 数据库管理
    """)

# Footer
st.divider()
st.caption("人机协同A股智能投资决策系统 v0.1.0 | 预测仅供参考，投资风险自担")