"""UI page components for the application."""

import streamlit as st
import pandas as pd
from datetime import datetime

from data.storage import StockStorage
from data.database import DatabaseManager
from ui.layout import color_for_change, format_change, render_card, footer
from ui.charts import plot_kline_chart, plot_volume_chart, plot_indicator_chart


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

    # Load data
    db_manager = None
    try:
        db_manager = DatabaseManager()
        storage = StockStorage(db_manager)
    except Exception as e:
        st.error(f"数据库连接失败: {e}")
        st.info("请先在'数据更新'页面初始化数据库")
        return
    finally:
        if db_manager:
            db_manager.close()

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


def _render_leaders_table(leaders, storage: StockStorage):
    """Render sector leaders table with click navigation."""
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
    """Display stock detail page (placeholder)."""
    st.header("📊 股票详情")
    st.info("🚀 功能开发中...")


def show_data_update():
    """Display data update interface (placeholder)."""
    st.header("🔄 数据更新")
    st.info("🚀 功能开发中...")