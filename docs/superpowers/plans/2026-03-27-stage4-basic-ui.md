# Stage 4 Basic UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the basic UI layer with main app entry point, layout components, homepage with sector overview, chart components, and data update interface using Streamlit.

**Architecture:**
- Streamlit application with sidebar navigation and main content area
- Modular UI components (layout, pages, charts) in `ui/` directory
- Color scheme following Chinese stock market convention (red for up, green for down)
- Session state management for page navigation and user selections

**Tech Stack:**
- Streamlit for web UI
- Plotly for interactive charts
- pandas for data manipulation
- Existing backend modules for data and predictions

---

## File Structure

### Files to Create/Modify:
- **Modify**: `app.py` - Update main app to use modular components
- **Create**: `ui/__init__.py` - UI module initialization
- **Create**: `ui/layout.py` - Layout components (sidebar, main content, cards, tables)
- **Create**: `ui/pages.py` - Page components (homepage, stock detail, data update)
- **Create**: `ui/charts.py` - Chart components (K-line, volume, indicators, trends)
- **Create**: `ui/components.py` - Reusable UI components
- **Note**: Tests are optional for UI components in Streamlit

---

## Task 1: Enhance Main App Entry

**Files:**
- Modify: `app.py`

- [ ] **Step 1: Review current app.py implementation**

The current `app.py` already has:
- Page configuration with Chinese title
- Sidebar with navigation
- Session state management
- Basic page placeholders
- Database status display in data update page

- [ ] **Step 2: Import UI modules**

Add imports for new UI modules:
```python
from ui.pages import show_homepage, show_stock_detail, show_data_update
from ui.layout import footer
```

- [ ] **Step 3: Update page content to use UI modules**

Replace placeholder content with modular page functions:
```python
# Main content
if st.session_state.page == "首页/板块总览":
    show_homepage()

elif st.session_state.page == "股票详情":
    show_stock_detail()

elif st.session_state.page == "数据更新":
    show_data_update()
```

- [ ] **Step 4: Add footer component**

Add footer at the bottom:
```python
# Footer
footer()
```

- [ ] **Step 5: Run app to verify it still works**

Run: `streamlit run app.py`
Expected: App launches with same structure, no errors

- [ ] **Step 6: Commit**

```bash
git add app.py
git commit -m "refactor: update app.py to use modular UI components"
```

---

## Task 2: Implement Layout Components

**Files:**
- Create: `ui/__init__.py`
- Create: `ui/layout.py`

- [ ] **Step 1: Create UI module init**

```python
# ui/__init__.py
"""UI module for the application."""
```

- [ ] **Step 2: Create layout.py with all utility functions**

Create `ui/layout.py` with:
- `footer()` - Display footer at bottom of page
- `render_card(title, content_fn, icon=None)` - Render a content card
- `render_metric_card(title, value, delta=None, color=None)` - Render metric card
- `render_info_grid(data)` - Render grid of key-value pairs
- `color_for_change(change: float) -> str` - Return color based on change
- `format_change(change: float) -> str` - Format change percentage

- [ ] **Step 3: Implement color helper functions and render_card**

```python
def color_for_change(change: float) -> str:
    """Return delta_color value for Streamlit metric (Chinese stock market convention)."""
    if change > 0:
        return "normal"  # Streamlit's normal (red) for up
    elif change < 0:
        return "inverse"  # Streamlit's inverse (green) for down
    return "off"

def format_change(change: float) -> str:
    """Format change percentage with sign."""
    if change > 0:
        return f"+{change:.1f}%"
    elif change < 0:
        return f"{change:.1f}%"
    return "0.0%"

def render_card(title: str, content_fn, icon: str = None):
    """Render a content card with title and content.

    Args:
        title: Card title
        content_fn: Function that renders card content
        icon: Optional emoji icon for the title
    """
    title_with_icon = f"{icon} {title}" if icon else title
    st.subheader(title_with_icon)
    content_fn()
    st.divider()
```

- [ ] **Step 4: Implement footer component**

```python
def footer():
    """Display footer at bottom of page."""
    st.divider()
    st.caption("人机协同A股智能投资决策系统 v0.4.0 | 预测仅供参考，投资风险自担")
```

- [ ] **Step 5: Verify imports work**

Run: `python -c "from ui.layout import footer, color_for_change"`
Expected: No import errors

- [ ] **Step 6: Commit**

```bash
git add ui/__init__.py ui/layout.py
git commit -m "feat: implement layout components"
```

---

## Task 3: Implement Homepage (Sector Overview)

**Files:**
- Create: `ui/pages.py`

- [ ] **Step 1: Create pages.py with homepage function**

Create `ui/pages.py` with:
- `show_homepage()` - Main homepage with sector overview

- [ ] **Step 2: Implement homepage structure**

```python
from utils.logger import Logger
from data.storage import StockStorage
from data.database import DatabaseManager
from ui.layout import color_for_change, format_change, render_card, footer

def show_homepage():
    """Display homepage with sector overview."""
    st.header("🏠 首页/板块总览")

    # Load data
    try:
        storage = StockStorage(DatabaseManager())
    except Exception as e:
        st.error(f"数据库连接失败: {e}")
        st.info("请先在'数据更新'页面初始化数据库")
        return

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
            lambda: _render_leaders_table(leaders),
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
```

- [ ] **Step 3: Implement leaders table with navigation**

```python
def _render_leaders_table(leaders):
    """Render sector leaders table with click navigation."""
    if not leaders:
        return st.info("暂无数据")

    # Convert to DataFrame for display
    import pandas as pd

    df = pd.DataFrame(leaders)

    # Add formatted columns if needed
    df = df.copy()

    # Format score column
    if 'score' in df.columns:
        df['score'] = df['score'].apply(lambda x: f"{x:.2f}")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
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
    if st.session_state.get('dataframe/_render_leaders_table/selection/rows'):
        selected_rows = st.session_state['dataframe/_render_leaders_table/selection/rows']
        if selected_rows:
            selected_idx = selected_rows[0]
            if selected_idx < len(leaders):
                selected_symbol = leaders[selected_idx].get('symbol')
                if selected_symbol:
                    st.session_state.selected_symbol = selected_symbol
                    st.session_state.page = "股票详情"
                    st.rerun()
```

- [ ] **Step 4: Implement sector trend placeholder**

```python
def _render_sector_trend_placeholder():
    """Render sector trend chart placeholder."""
    st.info("📈 板块趋势图表将在后续阶段实现")
    st.caption("将显示该板块的整体K线图和趋势分析")
```

- [ ] **Step 5: Verify imports work**

Run: `python -c "from ui.pages import show_homepage"`
Expected: No import errors

- [ ] **Step 6: Commit**

```bash
git add ui/pages.py
git commit -m "feat: implement homepage with sector overview"
```

---

## Task 4: Implement Chart Components

**Files:**
- Create: `ui/charts.py`

- [ ] **Step 1: Create charts.py with plotly imports**

```python
"""Chart components using Plotly."""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Optional
```

- [ ] **Step 2: Implement K-line chart function**

```python
def plot_kline_chart(df: pd.DataFrame, height: int = 400):
    """Plot K-line (candlestick) chart.

    Args:
        df: DataFrame with OHLCV data
        height: Chart height in pixels
    """
    if df.empty:
        st.info("暂无数据")
        return

    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        increasing_line_color='#ef4444',  # Red for up
        decreasing_line_color='#22c55e',  # Green for down
    )])

    fig.update_layout(
        xaxis_rangeslider_visible=False,
        height=height,
        margin=dict(l=0, r=0, t=0, b=0)
    )

    st.plotly_chart(fig, use_container_width=True)
```

- [ ] **Step 3: Implement volume chart function**

```python
def plot_volume_chart(df: pd.DataFrame, height: int = 150):
    """Plot volume bar chart.

    Args:
        df: DataFrame with volume data
        height: Chart height in pixels
    """
    if df.empty:
        return

    colors = ['#ef4444' if row['close'] >= row['open'] else '#22c55e' for _, row in df.iterrows()]

    fig = go.Figure(data=[go.Bar(
        x=df.index,
        y=df['volume'],
        marker_color=colors
    )])

    fig.update_layout(
        xaxis_rangeslider_visible=False,
        height=height,
        margin=dict(l=0, r=0, t=0, b=0)
    )

    st.plotly_chart(fig, use_container_width=True)
```

- [ ] **Step 4: Implement indicator chart function with BOLL support**

```python
def plot_indicator_chart(df: pd.DataFrame, indicator: str, height: int = 200):
    """Plot technical indicator chart.

    Args:
        df: DataFrame with indicator data
        indicator: Indicator name (MACD, KDJ, RSI, BOLL, etc.)
        height: Chart height in pixels
    """
    if df.empty:
        st.info("暂无数据")
        return

    # Map indicator column names
    if indicator == 'MACD':
        y_cols = ['macd', 'macd_signal', 'macd_hist']
        colors = ['#3b82f6', '#f59e0b', '#ef4444']
    elif indicator == 'RSI':
        y_cols = ['rsi6', 'rsi12', 'rsi24']
        colors = ['#3b82f6', '#f59e0b', '#ef4444']
    elif indicator == 'KDJ':
        y_cols = ['kdj_k', 'kdj_d', 'kdj_j']
        colors = ['#3b82f6', '#f59e0b', '#ef4444']
    elif indicator == 'BOLL':
        # BOLL requires special handling with upper/middle/lower bands
        y_cols = ['boll_upper', 'boll_middle', 'boll_lower']
        colors = ['#ef4444', '#3b82f6', '#22c55e']
    else:
        st.warning(f"不支持的指标: {indicator}")
        return

    fig = go.Figure()

    for i, col in enumerate(y_cols):
        if col in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df[col],
                mode='lines',
                name=col,
                line=dict(color=colors[i])
            ))

    fig.update_layout(
        xaxis_rangeslider_visible=False,
        height=height,
        hovermode='x unified',
        margin=dict(l=0, r=0, t=30, b=0),
        legend=dict(orientation="h", yanchor="bottom")
    )

    st.plotly_chart(fig, use_container_width=True)
```

- [ ] **Step 5: Implement sector trend chart placeholder**

```python
def plot_sector_trend_chart(df: pd.DataFrame, height: int = 400):
    """Plot sector trend line chart.

    Args:
        df: DataFrame with close price data
        height: Chart height in pixels
    """
    if df.empty or 'close' not in df.columns:
        st.info("暂无数据")
        return

    fig = go.Figure(data=[go.Scatter(
        x=df.index,
        y=df['close'],
        mode='lines',
        name='价格',
        line=dict(color='#3b82f6', width=2)
    )])

    fig.update_layout(
        xaxis_rangeslider_visible=False,
        height=height,
        margin=dict(l=0, r=0, t=0, b=0)
    )

    st.plotly_chart(fig, use_container_width=True)
```

- [ ] **Step 6: Verify imports work**

Run: `python -c "from ui.charts import plot_kline_chart, plot_volume_chart"`
Expected: No import errors

- [ ] **Step 7: Commit**

```bash
git add ui/charts.py
git commit -m "feat: implement chart components with Plotly"
```

---

## Task 5: Enhance Stock Detail Page

**Files:**
- Modify: `ui/pages.py`

- [ ] **Step 1: Update show_stock_detail function with navigation**

Replace placeholder with actual implementation:

```python
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
    try:
        storage = StockStorage(DatabaseManager())
    except Exception as e:
        st.error(f"数据库连接失败: {e}")
        return

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

    # Prediction placeholder
    _render_prediction_placeholder()
```

- [ ] **Step 2: Implement stock info card**

```python
def _render_stock_info_card(stock: dict, storage: StockStorage):
    """Render stock basic information card."""
    # Get latest price
    latest = storage.get_latest_stock_data(stock['symbol'])

    if latest:
        latest_price = latest.get('close', 0)
        prev_price = latest.get('open', latest_price)
        change_pct = (latest_price - prev_price) / prev_price * 100 if prev_price > 0 else 0
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
```

- [ ] **Step 3: Implement time range filter**

```python
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
```

- [ ] **Step 4: Implement prediction placeholder**

```python
def _render_prediction_placeholder():
    """Render prediction placeholder card."""
    render_card("🎯 预测建议", lambda: st.info("""
    预测功能将在Stage 5实现，将包含：
    - 短期预测（1-5天）
    - 中期预测（1-3个月）
    - 长期预测（3个月以上）
    - 综合建议和推理依据
    """))
```

- [ ] **Step 5: Commit**

```bash
git add ui/pages.py
git commit -m "feat: enhance stock detail page with charts"
```

---

## Task 6: Implement Data Update Interface

**Files:**
- Modify: `ui/pages.py`

- [ ] **Step 1: Add update_progress function**

```python
def update_progress(step: int, total: int, message: str, placeholder):
    """Update progress bar and status.

    Args:
        step: Current step number
        total: Total steps
        message: Current step description
        placeholder: Streamlit empty placeholder for updates
    """
    progress = step / total
    placeholder.progress(progress)
    placeholder.write(f"{message} ({step}/{total})")
```

- [ ] **Step 2: Update show_data_update function with full update flow**

```python
def show_data_update():
    """Display data update interface."""
    st.header("🔄 数据更新")

    from analysis.indicators import IndicatorCalculator
    from analysis.sector import SectorAnalyzer
    from utils.logger import Logger
    from data.fetcher import DataFetcher

    # Initialize database connection
    try:
        storage = StockStorage(DatabaseManager())
    except Exception as e:
        st.error(f"数据库连接失败: {e}")
        return

    # Database status
    db = DatabaseManager()
    if db.check_database_exists():
        st.success("✅ 数据库已初始化")
        last_update = db.get_last_update_date()
        if last_update:
            st.info(f"最后更新日期: {last_update}")
        else:
            st.info("暂无数据")
    else:
        st.warning("⚠️ 数据库未初始化")
        if st.button("初始化数据库", key="init_db"):
            try:
                db.create_tables()
                st.success("数据库初始化成功!")
                st.rerun()
            except Exception as e:
                st.error(f"初始化失败: {e}")
        db.close()
        return
    db.close()

    # Update buttons
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔄 更新板块数据", use_container_width=True, key="update_sectors"):
            _update_sectors_data(storage)

    with col2:
        if st.button("🔄 更新股票数据", use_container_width=True, key="update_stocks"):
            st.info("股票数据更新功能将在后续完善")

    with col3:
        if st.button("🔄 更新技术指标", use_container_width=True, key="update_indicators"):
            _update_indicators_data(storage)
```

- [ ] **Step 3: Implement sectors data update**

```python
def _update_sectors_data(storage: StockStorage):
    """Update sectors and leaders data."""
    from data.fetcher import DataFetcher
    from analysis.indicators import IndicatorCalculator
    from analysis.sector import SectorAnalyzer

    update_placeholder = st.empty()

    try:
        fetcher = DataFetcher()
        analyzer = SectorAnalyzer(storage)

        # Step 1: Get sectors
        update_placeholder.info("正在获取板块列表...")
        industry_sectors = fetcher.get_industry_sectors()
        concept_sectors = fetcher.get_concept_sectors()

        # Step 2: Save sectors
        update_placeholder.info("正在保存板块数据...")
        for _, sector in industry_sectors.iterrows():
            storage.save_sector({
                'sector_id': sector['行业'],
                'sector_name': sector['行业名称'],
                'sector_type': 'industry'
            })

        for _, sector in concept_sectors.iterrows():
            storage.save_sector({
                'sector_id': sector['概念'],
                'sector_name': sector['概念名称'],
                'sector_type': 'concept'
            })

        # Step 3: Update sector leaders
        update_placeholder.info("正在更新板块龙头股...")
        analyzer.update_all_sector_leaders()

        st.success("✅ 板块数据更新完成!")

    except Exception as e:
        Logger.error(f"板块数据更新失败: {str(e)}")
        st.error(f"更新失败: {str(e)}")
```

- [ ] **Step 4: Implement indicators data update**

```python
def _update_indicators_data(storage: StockStorage):
    """Update technical indicators for all stocks."""
    from analysis.indicators import IndicatorCalculator
    from utils.logger import Logger

    update_placeholder = st.empty()

    try:
        # Get all stocks
        update_placeholder.info("正在获取股票列表...")
        stocks = storage.get_stock_list()

        if not stocks:
            st.warning("暂无股票数据，请先更新板块和股票数据")
            return

        calculator = IndicatorCalculator()
        total = len(stocks)

        for idx, stock in enumerate(stocks, 1):
            update_placeholder.info(f"正在计算指标: {stock['name']} ({idx}/{total})")

            # Get historical data
            df = storage.get_stock_data(stock['symbol'])

            if not df.empty:
                # Calculate indicators
                df_with_indicators = calculator.calculate_all(df)

                # Save updated data
                for _, row in df_with_indicators.iterrows():
                    storage.save_stock_data(row.to_dict())

        st.success(f"✅ 技术指标更新完成! 共处理 {total} 只股票")

    except Exception as e:
        Logger.error(f"技术指标更新失败: {str(e)}")
        st.error(f"更新失败: {str(e)}")
```

- [ ] **Step 5: Commit**

```bash
git add ui/pages.py
git commit -m "feat: implement data update interface"
```

---

## Final Verification

After completing all tasks:

- [ ] **Run the application**: `streamlit run app.py`
- [ ] **Verify each page loads correctly**:
  - Homepage displays and sector selection works
  - Stock detail page displays with placeholder prediction
  - Data update page displays status and update buttons
- [ ] **Verify charts render**: Check that K-line chart and volume chart work
- [ ] **Update PROGRESS.md**: Mark Stage 4 completion
- [ ] **Final commit**: `git add PROGRESS.md && git commit -m "docs: update PROGRESS.md with Stage 4 completion"`