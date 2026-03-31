"""Layout components for the application UI."""
import streamlit as st


def header():
    """Display first layer - main title."""
    st.markdown("""
        <div style='text-align: center; padding: 20px 0; background: linear-gradient(135deg, #C8102E 0%, #E63946 100%); border-radius: 12px; margin: 10px;'>
            <h1 style='margin: 0; color: white; text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);'>📈 人机协同A股智能投资决策系统</h1>
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

    # Add custom CSS for navigation styling - 招商证券配色
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

        /* Button styling with left alignment - 招商证券红色 */
        div.stButton > button:first-child {
            border: none !important;
            box-shadow: none !important;
            background-color: transparent !important;
            text-align: left !important;
            padding: 10px 14px !important;
            margin: 4px 0 !important;
            border-radius: 8px !important;
            width: auto !important;
            min-width: 100% !important;
            display: inline-flex !important;
            justify-content: flex-start !important;
            align-items: center !important;
            color: #333 !important;
            font-weight: 500 !important;
        }

        /* Button content left alignment */
        div.stButton > button:first-child > div {
            display: flex !important;
            justify-content: flex-start !important;
            align-items: center !important;
            width: auto !important;
        }

        /* Hover effect - 招商证券红色高亮 */
        div.stButton > button:first-child:hover {
            background-color: rgba(200, 16, 46, 0.1) !important;
            color: #C8102E !important;
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
                # Active state - use CMS Securities red color
                with st.container():
                    st.markdown(f"""
                        <div style="background-color: #C8102E; padding: 10px 14px; border-radius: 8px; margin: 4px 0;">
                            <strong style="color: white;">{module['icon']} {module['name']}</strong>
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

    # Custom CSS for sector cards -招商证券配色方案
    st.markdown("""
        <style>
        .sector-card {
            padding: 20px;
            border-radius: 12px;
            margin: 10px 0;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .sector-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
        }
        .sector-card-industry {
            background: linear-gradient(135deg, #C8102E 0%, #E63946 100%);
        }
        .sector-card-concept {
            background: linear-gradient(135deg, #FFA500 0%, #FFB84D 100%);
        }
        .sector-name {
            font-size: 18px;
            font-weight: bold;
            color: white;
            margin: 0 0 10px 0;
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
        }
        .sector-metrics {
            font-size: 14px;
            color: rgba(255, 255, 255, 0.95);
            text-shadow: 0 1px 1px rgba(0, 0, 0, 0.15);
        }

        /* Tab styling - 招商证券配色 */
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            padding: 0 20px;
            border-radius: 6px;
            background-color: transparent;
            color: #666;
            font-weight: 600;
            font-size: 15px;
            border: 2px solid transparent;
        }
        .stTabs [aria-selected="true"] {
            background-color: #C8102E !important;
            color: white !important;
            border-color: #C8102E;
        }
        .stTabs [data-baseweb="tab"]:hover {
            background-color: rgba(200, 16, 46, 0.1);
            color: #C8102E;
        }
        .stTabs [aria-selected="true"]:hover {
            background-color: #C8102E !important;
            color: white !important;
        }

        /* Button styling */
        .stButton > button {
            background-color: #C8102E;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: 600;
            transition: background-color 0.2s;
        }
        .stButton > button:hover {
            background-color: #A50C26;
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