"""Layout components for the application UI."""
import streamlit as st


def header():
    """Display first layer - main title."""
    st.markdown("""
        <div style='text-align: center; padding: 20px 0;'>
            <h1 style='margin: 0; color: #1f77b4;'>📈 人机协同A股智能投资决策系统</h1>
        </div>
    """, unsafe_allow_html=True)


def navigation():
    """Display second layer - navigation module (left side)."""
    nav_modules = [
        {"id": "home", "name": "首页总览", "icon": "🏠"},
        {"id": "prediction", "name": "智能预测", "icon": "🎯"},
        {"id": "analysis", "name": "板块分析", "icon": "📊"},
        {"id": "update", "name": "数据更新", "icon": "🔄"},
        {"id": "history", "name": "历史回顾", "icon": "📜"},
    ]

    # Initialize session state for navigation
    if "nav_module" not in st.session_state:
        st.session_state.nav_module = "home"

    # Add custom CSS for navigation styling - force left alignment
    st.markdown("""
        <style>
        /* Container-level left alignment */
        div[data-testid="stVerticalBlock"] > div[data-testid="column"] {
            display: flex !important;
            flex-direction: column !important;
            align-items: flex-start !important;
        }

        /* Button container left alignment */
        div.stButton {
            display: flex !important;
            justify-content: flex-start !important;
            align-items: flex-start !important;
            width: 100% !important;
        }

        /* Button styling with left alignment */
        div.stButton > button:first-child {
            border: none !important;
            box-shadow: none !important;
            background-color: transparent !important;
            text-align: left !important;
            padding: 8px 12px !important;
            margin: 0 !important;
            border-radius: 6px !important;
            width: auto !important;
            min-width: 100% !important;
            display: inline-flex !important;
            justify-content: flex-start !important;
            align-items: center !important;
        }

        /* Button content left alignment */
        div.stButton > button:first-child > div {
            display: flex !important;
            justify-content: flex-start !important;
            align-items: center !important;
            width: auto !important;
        }

        /* Hover effect */
        div.stButton > button:first-child:hover {
            background-color: #f0f2f6 !important;
        }

        /* Remove any centering from parent elements */
        [data-testid="stVerticalBlock"] {
            align-items: flex-start !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Display navigation buttons vertically on the left
    cols = st.columns([1, 4])  # 1:4 ratio for nav:content
    with cols[0]:
        st.markdown("### 导航")
        for module in nav_modules:
            is_active = st.session_state.nav_module == module["id"]
            if is_active:
                # Active state - use container to show selected background
                with st.container():
                    st.markdown(f"""
                        <div style="background-color: #e8f4f8; padding: 8px 12px; border-radius: 6px; margin: 2px 0;">
                            <strong>{module['icon']} {module['name']}</strong>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                if st.button(f"{module['icon']} {module['name']}", key=f"nav_{module['id']}", use_container_width=True):
                    st.session_state.nav_module = module["id"]
                    st.rerun()
        st.markdown("---")
        st.caption("基于7年A股历史数据预测")

    return cols[1]  # Return content column


def sector_grid(sectors: list, storage=None, on_sector_click=None):
    """Display third layer - sector grid with multiple rows and key metrics.

    Args:
        sectors: List of sector dictionaries with 'sector_name', 'sector_type' keys
        storage: StockStorage instance for fetching sector metrics
        on_sector_click: Callback function when a sector is clicked
    """
    if not sectors:
        st.info("暂无板块数据")
        return

    # Group sectors by type
    industry_sectors = [s for s in sectors if s['sector_type'] == 'industry']
    concept_sectors = [s for s in sectors if s['sector_type'] == 'concept']

    # Display industry sectors
    if industry_sectors:
        st.markdown("### 🏭 行业板块")
        cols_per_row = 4  # Changed from 5 to 4 for more space
        for i in range(0, len(industry_sectors), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, sector in enumerate(industry_sectors[i:i+cols_per_row]):
                with cols[j]:
                    sector_name = sector['sector_name']
                    sector_id = sector.get('sector_id', '')
                    # Use sector name as fallback for unique key
                    button_key = sector_id if sector_id else f"sec_{sector_name}"

                    # Get sector metrics if storage is provided
                    metrics = {}
                    if storage and sector_id:
                        leaders = storage.get_sector_leaders(sector_id)
                        if leaders:
                            # Calculate simple metrics
                            total_stocks = len(leaders)
                            avg_score = sum(l.get('score', 0) for l in leaders) / total_stocks if total_stocks > 0 else 0
                            metrics = {
                                'stocks': total_stocks,
                                'avg_score': avg_score
                            }

                    # Display sector card with metrics
                    with st.container():
                        if st.button(sector_name, key=f"sector_{button_key}", use_container_width=True):
                            if on_sector_click:
                                on_sector_click(sector)
                            st.rerun()

                        if metrics:
                            st.caption(f"龙头: {metrics['stocks']}只 | 均分: {metrics['avg_score']:.1f}")

    # Display concept sectors
    if concept_sectors:
        st.markdown("### 💡 概念板块")
        cols_per_row = 4
        for i in range(0, len(concept_sectors), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, sector in enumerate(concept_sectors[i:i+cols_per_row]):
                with cols[j]:
                    sector_name = sector['sector_name']
                    sector_id = sector.get('sector_id', '')
                    # Use sector name as fallback for unique key
                    button_key = sector_id if sector_id else f"sec_{sector_name}"

                    # Get sector metrics if storage is provided
                    metrics = {}
                    if storage and sector_id:
                        leaders = storage.get_sector_leaders(sector_id)
                        if leaders:
                            total_stocks = len(leaders)
                            avg_score = sum(l.get('score', 0) for l in leaders) / total_stocks if total_stocks > 0 else 0
                            metrics = {
                                'stocks': total_stocks,
                                'avg_score': avg_score
                            }

                    # Display sector card with metrics
                    with st.container():
                        if st.button(sector_name, key=f"sector_{button_key}", use_container_width=True):
                            if on_sector_click:
                                on_sector_click(sector)
                            st.rerun()

                        if metrics:
                            st.caption(f"龙头: {metrics['stocks']}只 | 均分: {metrics['avg_score']:.1f}")


def footer():
    """Display fourth layer - footer at bottom of page."""
    st.markdown("---")
    st.caption("人机协同A股智能投资决策系统 v0.4.0 | 预测仅供参考，投资风险自担")


def color_for_change(change: float) -> str:
    """Return delta_color value for Streamlit metric (Chinese stock market convention).

    Args:
        change: Change percentage

    Returns:
        "normal" for positive (red in Chinese market), "inverse" for negative (green),
        or "off" for zero
    """
    if change > 0:
        return "normal"  # Streamlit's normal (red) for up
    elif change < 0:
        return "inverse"  # Streamlit's inverse (green) for down
    return "off"


def format_change(change: float) -> str:
    """Format change percentage with sign.

    Args:
        change: Change percentage

    Returns:
        Formatted string with + or - sign, e.g. "+5.2%" or "-3.1%"
    """
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