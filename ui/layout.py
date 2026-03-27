"""Layout components for the application UI."""
import streamlit as st


def footer():
    """Display footer at bottom of page."""
    st.divider()
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