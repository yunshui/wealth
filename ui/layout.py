"""Layout components for the application UI."""
import streamlit as st


def header():
    """Display first layer - main title."""
    st.markdown("""
        <div style='text-align: center; padding: 25px 0; background: linear-gradient(135deg, #4A90E2 0%, #87CEEB 100%); border-radius: 16px; margin: 10px; box-shadow: 0 4px 20px rgba(74, 144, 226, 0.3);'>
            <h1 style='margin: 0; color: white; text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2); font-size: 28px;'>📈 人机协同A股智能投资决策系统</h1>
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

    # Add custom CSS for navigation styling - 天空蓝配色
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

        /* Button styling with left alignment - 天空蓝 */
        div.stButton > button:first-child {
            border: none !important;
            box-shadow: none !important;
            background-color: transparent !important;
            text-align: left !important;
            padding: 12px 16px !important;
            margin: 4px 0 !important;
            border-radius: 10px !important;
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

        /* Hover effect - 天空蓝高亮 */
        div.stButton > button:first-child:hover {
            background-color: rgba(74, 144, 226, 0.12) !important;
            color: #4A90E2 !important;
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
                # Active state - 天空蓝凸显模式
                with st.container():
                    st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #4A90E2 0%, #87CEEB 100%); padding: 12px 16px; border-radius: 10px; margin: 4px 0; box-shadow: 0 4px 12px rgba(74, 144, 226, 0.3);">
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

    # Custom CSS for sector cards - 天空蓝配色
    st.markdown("""
        <style>
        .sector-card {
            padding: 24px;
            border-radius: 16px;
            margin: 12px 0;
            box-shadow: 0 8px 24px rgba(74, 144, 226, 0.2);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        .sector-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 32px rgba(74, 144, 226, 0.3);
        }
        .sector-card-industry {
            background: linear-gradient(135deg, #4A90E2 0%, #6BB9F0 100%);
        }
        .sector-card-concept {
            background: linear-gradient(135deg, #87CEEB 0%, #B0E0E6 100%);
        }
        .sector-card::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.1), transparent);
            pointer-events: none;
        }
        .sector-name {
            font-size: 20px;
            font-weight: bold;
            color: white;
            margin: 0 0 12px 0;
            text-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
            position: relative;
            z-index: 1;
        }
        .sector-metrics {
            font-size: 15px;
            color: rgba(255, 255, 255, 0.95);
            text-shadow: 0 1px 3px rgba(0, 0, 0, 0.12);
            position: relative;
            z-index: 1;
        }

        /* Tab styling - 天空蓝凸显模式 */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: rgba(74, 144, 226, 0.08);
            padding: 6px;
            border-radius: 12px;
            border: 2px solid rgba(74, 144, 226, 0.2);
        }
        .stTabs [data-baseweb="tab"] {
            height: 52px;
            padding: 0 24px;
            border-radius: 10px;
            background-color: transparent;
            color: #2c3e50;
            font-weight: 600;
            font-size: 16px;
            border: 2px solid transparent;
            transition: all 0.2s ease;
        }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #4A90E2 0%, #6BB9F0 100%) !important;
            color: white !important;
            border-color: transparent;
            box-shadow: 0 4px 12px rgba(74, 144, 226, 0.3);
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
        }
        .stTabs [data-baseweb="tab"]:hover {
            background-color: rgba(74, 144, 226, 0.12);
            color: #4A90E2;
        }
        .stTabs [aria-selected="true"]:hover {
            background: linear-gradient(135deg, #4A90E2 0%, #6BB9F0 100%) !important;
            color: white !important;
        }

        /* Button styling - 天空蓝 */
        .stButton > button {
            background: linear-gradient(135deg, #4A90E2 0%, #6BB9F0 100%);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 10px;
            font-weight: 600;
            transition: all 0.2s ease;
            box-shadow: 0 4px 12px rgba(74, 144, 226, 0.2);
            position: relative;
            z-index: 1;
        }
        .stButton > button:hover {
            background: linear-gradient(135deg, #3A7BC8 0%, #5BA8E0 100%);
            box-shadow: 0 6px 16px rgba(74, 144, 226, 0.35);
            transform: translateY(-1px);
        }
        .stButton > button:active {
            transform: translateY(0);
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

                        # Display colored sector card
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

                        # Display colored sector card
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
        <div style='text-align: center; padding: 20px 0; background: linear-gradient(135deg, rgba(74, 144, 226, 0.08) 0%, rgba(135, 206, 235, 0.08) 100%); border-radius: 12px; margin-top: 30px;'>
            <p style='margin: 0; color: #4A90E2; font-weight: 600;'>人机协同A股智能投资决策系统 v0.4.0 | 预测仅供参考，投资风险自担</p>
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