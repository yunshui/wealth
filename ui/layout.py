"""Layout components for the application UI."""
import streamlit as st
import streamlit.components.v1 as components


def sidebar_layout():
    """Display left sidebar with title and collapsible navigation.

    Returns:
        content_col: The right content column
    """
    # Initialize session state for navigation
    if "nav_module" not in st.session_state:
        st.session_state.nav_module = "home"

    # Initialize session state for sidebar collapsed state
    if "sidebar_collapsed" not in st.session_state:
        st.session_state.sidebar_collapsed = False

    nav_modules = [
        {"id": "home", "name": "首页总览", "icon": "🏠"},
        {"id": "prediction", "name": "智能预测", "icon": "🎯"},
        {"id": "analysis", "name": "板块分析", "icon": "📊"},
        {"id": "update", "name": "数据更新", "icon": "🔄"},
        {"id": "history", "name": "历史回顾", "icon": "📜"},
    ]

    # Add custom CSS for sidebar styling - 淡蓝色配色
    st.markdown("""
        <style>
        /* Global background - 白色 */
        .stApp {
            background-color: #ffffff !important;
        }

        /* Main content background */
        [data-testid="stMainBlockContainer"] {
            background-color: #ffffff !important;
        }

        /* Sidebar container styling */
        .sidebar-container {
            background-color: #fafafa;
            border-right: none;
            padding: 20px;
            min-height: 100vh;
        }

        /* Navigation button styling */
        .nav-btn {
            background-color: transparent;
            color: #2c3e50;
            border: none;
            padding: 12px 16px;
            border-radius: 8px;
            margin: 4px 0;
            width: 100%;
            text-align: left;
            cursor: pointer;
            font-size: 15px;
            font-weight: 500;
            transition: all 0.2s ease;
        }
        .nav-btn:hover {
            background-color: rgba(160, 216, 239, 0.15);
            color: #5BA3C8;
        }
        .nav-btn.active {
            background-color: #A0D8EF;
            color: #2c3e50;
            box-shadow: 0 2px 8px rgba(160, 216, 239, 0.3);
            text-align: center;
        }

        /* Streamlit button styling for navigation */
        .stButton button {
            background-color: transparent !important;
            color: #2c3e50 !important;
            border: none !important;
            padding: 12px 16px !important;
            border-radius: 8px !important;
            margin: 4px 0 !important;
            width: 100% !important;
            text-align: left !important;
            font-size: 15px !important;
            font-weight: 500 !important;
            transition: all 0.2s ease !important;
            justify-content: flex-start !important;
        }
        .stButton button:hover {
            background-color: rgba(160, 216, 239, 0.15) !important;
            color: #5BA3C8 !important;
        }

        /* Toggle button styling */
        .toggle-button-floating {
            background-color: #A0D8EF !important;
            color: #2c3e50 !important;
            border: none;
            padding: 8px 12px;
            border-radius: 0 6px 6px 0;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: all 0.2s ease;
            z-index: 10000;
            box-shadow: 2px 0 8px rgba(160, 216, 239, 0.3);
        }
        .toggle-button-floating:hover {
            background-color: #8FD4E8 !important;
        }

        /* Override Streamlit's default button styling in sidebar */
        [data-testid="stSidebar"] .stButton button,
        [data-testid="column"] .stButton button {
            background-color: transparent !important;
            color: #2c3e50 !important;
            border: none !important;
        }
        [data-testid="stSidebar"] .stButton button:hover,
        [data-testid="column"] .stButton button:hover {
            background-color: rgba(160, 216, 239, 0.15) !important;
            color: #5BA3C8 !important;
        }

        /* Footer styling for right side */
        .footer-right {
            background-color: #f5f5f5;
            padding: 16px 20px;
            border-radius: 8px;
            margin-top: 30px;
            border-top: 2px solid #A0D8EF;
            text-align: right;
        }
        .footer-right p {
            margin: 0;
            color: #666;
            font-size: 13px;
        }
        </style>
    """, unsafe_allow_html=True)

    # Create left sidebar, divider, and right content
    sidebar_width = 1 if not st.session_state.sidebar_collapsed else 0.2
    divider_width = 0.05
    cols = st.columns([sidebar_width, divider_width, 4])

    with cols[0]:  # Left sidebar
        # System title at top of sidebar
        st.markdown(f"""
            <div style='text-align: center; padding: 16px 0; margin-bottom: 12px;'>
                <h2 style='margin: 0; color: #333; font-size: 20px; font-weight: 600;'>📈 人机协同A股<br>智能投资决策系统</h2>
            </div>
        """, unsafe_allow_html=True)

        # Navigation buttons
        if not st.session_state.sidebar_collapsed:
            for module in nav_modules:
                is_active = st.session_state.nav_module == module["id"]
                btn_style = "nav-btn active" if is_active else "nav-btn"

                if is_active:
                    st.markdown(f"""
                        <div class="{btn_style}">
                            <strong>{module['icon']} {module['name']}</strong>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    if st.button(f"{module['icon']} {module['name']}", key=f"nav_{module['id']}", use_container_width=True):
                        st.session_state.nav_module = module["id"]
                        st.rerun()

            st.markdown("---")
            st.caption("基于7年A股历史数据预测")
        else:
            # Collapsed state - show icons only
            for module in nav_modules:
                is_active = st.session_state.nav_module == module["id"]
                btn_style = "nav-btn active" if is_active else "nav-btn"

                if is_active:
                    st.markdown(f"""
                        <div class="{btn_style}" style="text-align: center; padding: 8px;">
                            <strong>{module['icon']}</strong>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    if st.button(module['icon'], key=f"nav_{module['id']}", use_container_width=True):
                        st.session_state.nav_module = module["id"]
                        st.rerun()

    with cols[1]:  # Divider with toggle button
        # Custom CSS for toggle button on left edge
        st.markdown("""
            <style>
            /* Toggle button positioned on left edge */
            .toggle-button-floating {
                position: fixed;
                left: 0;
                top: 50%;
                transform: translateY(-50%);
                background-color: #A0D8EF;
                color: #2c3e50;
                border: none;
                padding: 8px 12px;
                border-radius: 0 6px 6px 0;
                cursor: pointer;
                font-size: 16px;
                font-weight: 600;
                transition: all 0.2s ease;
                z-index: 10000;
                box-shadow: 2px 0 8px rgba(160, 216, 239, 0.3);
            }
            .toggle-button-floating:hover {
                background-color: #8FD4E8;
            }

            /* Vertical line */
            .v-divider {
                position: absolute;
                width: 2px;
                height: 100vh;
                background-color: #D0E8F5;
                left: 50%;
                top: 0;
                transform: translateX(-50%);
                z-index: 0;
            }
            </style>
        """, unsafe_allow_html=True)

        # Vertical line
        st.markdown("<div class='v-divider'></div>", unsafe_allow_html=True)

        # Hidden button to handle toggle (the visible one is positioned via CSS)
        toggle_text = "<<" if not st.session_state.sidebar_collapsed else ">>"
        st.markdown(f"""
            <button class='toggle-button-floating' onclick="
                const btn = document.querySelector('button[key=\"toggle_sidebar\"]');
                if (btn) btn.click();
            ">{toggle_text}</button>
        """, unsafe_allow_html=True)

        if st.button(toggle_text, key="toggle_sidebar"):
            st.session_state.sidebar_collapsed = not st.session_state.sidebar_collapsed
            st.rerun()

    return cols[2]  # Return right content column


def sector_grid(sectors: list, storage=None, on_sector_click=None):
    """Display sector grid with tabs.

    Args:
        sectors: List of sector dictionaries
        storage: StockStorage instance
        on_sector_click: Callback function
    """
    if not sectors:
        st.info("暂无板块数据")
        return

    industry_sectors = [s for s in sectors if s['sector_type'] == 'industry']
    concept_sectors = [s for s in sectors if s['sector_type'] == 'concept']

    # Custom CSS for sector grid - 淡蓝色配色
    st.markdown("""
        <style>
        /* Tab styling - 淡蓝色凸显模式 */
        .stTabs [data-baseweb="tab-list"] {
            display: flex !important;
            flex-direction: row !important;
            gap: 4px;
            background-color: #F0F8FF;
            padding: 4px;
            border-radius: 8px;
            border: 1px solid #D0E8F5;
            margin-bottom: 20px;
        }
        .stTabs [data-baseweb="tab"] {
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            min-width: 120px !important;
            height: 48px;
            padding: 0 24px;
            border-radius: 6px;
            background-color: white;
            color: #666;
            font-weight: 500;
            font-size: 15px;
            border: 2px solid transparent;
            transition: all 0.2s ease;
            flex-shrink: 0;
        }
        .stTabs [aria-selected="true"] {
            background-color: #A0D8EF !important;
            color: #2c3e50 !important;
            border-color: #A0D8EF;
            font-weight: 600;
        }
        .stTabs [data-baseweb="tab"]:hover {
            background-color: rgba(160, 216, 239, 0.15);
            color: #5BA3C8;
        }
        .stTabs [aria-selected="true"]:hover {
            background-color: #A0D8EF !important;
            color: #2c3e50 !important;
        }

        /* Sector button styling */
        .stButton > button {
            background-color: #A0D8EF;
            color: #2c3e50;
            border: none;
            padding: 16px 20px;
            border-radius: 6px;
            font-weight: 600;
            width: 100%;
            transition: all 0.2s ease;
            box-shadow: 0 2px 8px rgba(160, 216, 239, 0.2);
        }
        .stButton > button:hover {
            background-color: #8FD4E8;
            box-shadow: 0 2px 8px rgba(160, 216, 239, 0.4);
        }
        </style>
    """, unsafe_allow_html=True)

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

                        if st.button(f"**{sector_name}**  \n🏆 龙头: {metrics.get('stocks', 0)}只 | ⭐ 均分: {metrics.get('avg_score', 0):.1f}",
                                   key=f"ind_{i}_{j}", use_container_width=True):
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

                        if st.button(f"**{sector_name}**  \n🏆 龙头: {metrics.get('stocks', 0)}只 | ⭐ 均分: {metrics.get('avg_score', 0):.1f}",
                                   key=f"con_{i}_{j}", use_container_width=True):
                            if on_sector_click:
                                on_sector_click(sector)
                            st.rerun()
        else:
            st.info("暂无概念板块数据")


def footer_right():
    """Display footer at right side bottom."""
    st.markdown("""
        <div style='text-align: center; padding: 20px 0; margin-top: 30px;'>
            <p style='margin: 0; color: #666; font-size: 14px;'>人机协同A股智能投资决策系统 v0.4.0 | 预测仅供参考，投资风险自担</p>
        </div>
    """, unsafe_allow_html=True)


def color_for_change(change: float) -> str:
    """Return delta_color value for Streamlit metric (Chinese stock market convention)."""
    if change > 0:
        return "normal"
    elif change < 0:
        return "inverse"
    return "off"


def format_change(change: float) -> str:
    """Format change percentage with sign."""
    if change > 0:
        return f"+{change:.1f}%"
    elif change < 0:
        return f"{change:.1f}%"
    return "0.0%"


def render_card(title: str, content_fn, icon: str = None):
    """Render a content card with title and content."""
    title_with_icon = f"{icon} {title}" if icon else title
    st.subheader(title_with_icon)
    content_fn()
    st.divider()