"""Layout components for the application UI."""
import streamlit as st


def header():
    """Display first layer - main title."""
    st.markdown("""
        <div style='text-align: center; padding: 25px 0; background: linear-gradient(135deg, #E63946 0%, #FF6B6B 100%); border-radius: 16px; margin: 10px; box-shadow: 0 4px 20px rgba(230, 57, 70, 0.2);'>
            <h1 style='margin: 0; color: white; text-shadow: 0 2px 4px rgba(0, 0, 0, 0.15); font-size: 28px;'>📈 人机协同A股智能投资决策系统</h1>
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

    # Add custom CSS for navigation styling - 红色配色
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

        /* Button styling with left alignment - 红色 */
        div.stButton > button:first-child {
            border: none !important;
            box-shadow: none !important;
            background-color: transparent !important;
            text-align: left !important;
            padding: 12px 16px !important;
            margin: 4px 0 !important;
            border-radius: 8px !important;
            width: auto !important;
            min-width: 100% !important;
            display: inline-flex !important;
            justify-content: flex-start !important;
            align-items: center !important;
            color: #2c3e50 !important;
            font-weight: 500 !important;
            font-size: 15px !important;
        }

        /* Button content left alignment */
        div.stButton > button:first-child > div {
            display: flex !important;
            justify-content: flex-start !important;
            align-items: center !important;
            width: auto !important;
        }

        /* Hover effect - 红色高亮 */
        div.stButton > button:first-child:hover {
            background-color: rgba(230, 57, 70, 0.08) !important;
            color: #E63946 !important;
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
                # Active state - 红色
                with st.container():
                    st.markdown(f"""
                        <div style="background-color: #E63946; padding: 12px 16px; border-radius: 8px; margin: 4px 0; box-shadow: 0 2px 8px rgba(230, 57, 70, 0.15);">
                            <strong style="color: white; font-size: 15px;">{module['icon']} {module['name']}</strong>
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
    """Display third layer - sector grid with multiple rows and key metrics using tabs.

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

    # Custom CSS for sector cards - 红色配色
    st.markdown("""
        <style>
        .sector-card {
            padding: 24px;
            border-radius: 12px;
            margin: 12px 0;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
            transition: transform 0.2s, box-shadow 0.2s;
            border: 2px solid #ffe8e8;
            background: white;
        }
        .sector-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(230, 57, 70, 0.15);
            border-color: #E63946;
        }
        .sector-card-industry {
            border-left: 4px solid #E63946;
        }
        .sector-card-concept {
            border-left: 4px solid #FF6B6B;
        }
        .sector-name {
            font-size: 20px;
            font-weight: bold;
            color: #E63946;
            margin: 0 0 12px 0;
        }
        .sector-metrics {
            font-size: 14px;
            color: #666;
        }

        /* Tab styling - 红色凸显模式 */
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px;
            background-color: #f5f5f5;
            padding: 4px;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
        }
        .stTabs [data-baseweb="tab"] {
            height: 48px;
            padding: 0 24px;
            border-radius: 6px;
            background-color: white;
            color: #666;
            font-weight: 500;
            font-size: 15px;
            border: 2px solid transparent;
            transition: all 0.2s ease;
        }
        .stTabs [aria-selected="true"] {
            background-color: #E63946 !important;
            color: white !important;
            border-color: #E63946;
            font-weight: 600;
        }
        .stTabs [data-baseweb="tab"]:hover {
            background-color: rgba(230, 57, 70, 0.08);
            color: #E63946;
        }
        .stTabs [aria-selected="true"]:hover {
            background-color: #E63946 !important;
            color: white !important;
        }

        /* Button styling - 红色 */
        .stButton > button {
            background-color: #E63946;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            font-weight: 600;
            transition: all 0.2s ease;
        }
        .stButton > button:hover {
            background-color: #d62828;
            box-shadow: 0 2px 8px rgba(230, 57, 70, 0.2);
        }
        </style>
    """, unsafe_allow_html=True)

    # Use tabs to switch between industry and concept sectors
    tab1, tab2 = st.tabs(["🏭 行业板块", "💡 概念板块"])

    with tab1:
        if industry_sectors:
            cols_per_row = 3
            for i in range(0, len(industry_sectors), cols_per_row):
                cols = st.columns(cols_per_row)
                for j, sector in enumerate(industry_sectors[i:i+cols_per_row]):
                    with cols[j]:
                        sector_name = sector['sector_name']
                        sector_id = sector.get('sector_id', '')
                        button_key = f"ind_{i}_{j}"

                        # Get sector metrics
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

                        # Display colored sector card with white background and green border
                        st.markdown(f"""
                            <div class="sector-card sector-card-industry">
                                <h3 class="sector-name">{sector_name}</h3>
                                <p class="sector-metrics">
                                    🏆 龙头: {metrics.get('stocks', 0)}只 | ⭐ 均分: {metrics.get('avg_score', 0):.1f}
                                </p>
                            </div>
                        """, unsafe_allow_html=True)

                        if st.button("查看详情", key=f"btn_{button_key}", use_container_width=True):
                            if on_sector_click:
                                on_sector_click(sector)
                            st.rerun()
        else:
            st.info("暂无行业板块数据")

    with tab2:
        if concept_sectors:
            cols_per_row = 3
            for i in range(0, len(concept_sectors), cols_per_row):
                cols = st.columns(cols_per_row)
                for j, sector in enumerate(concept_sectors[i:i+cols_per_row]):
                    with cols[j]:
                        sector_name = sector['sector_name']
                        sector_id = sector.get('sector_id', '')
                        button_key = f"con_{i}_{j}"

                        # Get sector metrics
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

                        # Display colored sector card with white background and green border
                        st.markdown(f"""
                            <div class="sector-card sector-card-concept">
                                <h3 class="sector-name">{sector_name}</h3>
                                <p class="sector-metrics">
                                    🏆 龙头: {metrics.get('stocks', 0)}只 | ⭐ 均分: {metrics.get('avg_score', 0):.1f}
                                </p>
                            </div>
                        """, unsafe_allow_html=True)

                        if st.button("查看详情", key=f"btn_{button_key}", use_container_width=True):
                            if on_sector_click:
                                on_sector_click(sector)
                            st.rerun()
        else:
            st.info("暂无概念板块数据")


def footer():
    """Display fourth layer - footer at bottom of page."""
    st.markdown("""
        <div style='text-align: center; padding: 20px 0; background-color: #f5f5f5; border-radius: 12px; margin-top: 30px; border-top: 2px solid #E63946;'>
            <p style='margin: 0; color: #666; font-size: 14px;'>人机协同A股智能投资决策系统 v0.4.0 | 预测仅供参考，投资风险自担</p>
        </div>
    """, unsafe_allow_html=True)


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