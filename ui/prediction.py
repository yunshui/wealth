"""Prediction display components for the application."""

import streamlit as st
from typing import Dict, Tuple, Optional


def _display_action(action: str, confidence: float) -> Tuple[str, str]:
    """Get display text and color for an action.

    Args:
        action: Action string ('buy', 'sell', 'hold')
        confidence: Confidence value (0-1)

    Returns:
        Tuple of (display_text, color)
    """
    action_map = {
        'buy': ('买入', '#ef4444'),
        'sell': ('卖出', '#22c55e'),
        'hold': ('持有', '#6b7280')
    }
    return action_map.get(action, ('持有', '#6b7280'))


def _confidence_bar(confidence: float) -> str:
    """Generate confidence bar HTML.

    Args:
        confidence: Confidence value (0-1)

    Returns:
        HTML string for progress bar
    """
    percent = int(confidence * 100)
    filled = '█' * int(percent / 5)
    empty = '░' * (20 - len(filled))
    return f"{filled}{empty} {percent}%"


def render_horizon_card(title: str, prediction: Dict, icon: str = None):
    """Render prediction card for a single time horizon.

    Args:
        title: Card title
        prediction: Prediction dictionary with 'action', 'confidence', 'reasoning'
        icon: Optional emoji icon
    """
    action_text, action_color = _display_action(prediction.get('action', 'hold'), prediction.get('confidence', 0))
    confidence = prediction.get('confidence', 0)

    with st.container():
        title_with_icon = f"{icon} {title}" if icon else title
        st.markdown(f"### {title_with_icon}")

        # Display action with confidence
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown(f"<h2 style='text-align: center; color: {action_color}'>{action_text}</h2>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<p style='text-align: center; color: {action_color}'>{_confidence_bar(confidence)}</p>", unsafe_allow_html=True)

        # Display reasoning
        reasoning = prediction.get('reasoning', [])
        if reasoning:
            st.markdown("**推理依据:**")
            for reason in reasoning:
                st.markdown(f"• {reason}")

        st.divider()


def render_ensemble_card(prediction: Dict):
    """Render ensemble prediction card.

    Args:
        prediction: Prediction dictionary with ensemble data
    """
    ensemble = prediction.get('ensemble', {})
    action_text, action_color = _display_action(ensemble.get('action', 'hold'), ensemble.get('confidence', 0))
    confidence = ensemble.get('confidence', 0)

    with st.container():
        st.markdown("### 🎯 综合建议")

        # Display action with confidence (larger)
        st.markdown(f"<h1 style='text-align: center; color: {action_color}'>{action_text}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: {action_color}; font-size: 1.5em;'>{_confidence_bar(confidence)}</p>", unsafe_allow_html=True)

        # Display breakdown summary
        breakdown = ensemble.get('breakdown', {})
        if breakdown:
            st.markdown("**各周期建议:**")
            for horizon in ['短期', '中期', '长期']:
                pred = prediction.get(horizon if horizon in prediction else '', {})
                if pred:
                    action = pred.get('action', 'hold')
                    conf = pred.get('confidence', 0)
                    st.caption(f"{horizon}: {action} ({int(conf*100)}%)")

        # Display reasoning
        reasoning = ensemble.get('reasoning', [])
        all_reasoning = ensemble.get('all_reasoning', [])

        if reasoning:
            st.markdown("**💡 操作提示:**")
            for reason in reasoning:
                st.markdown(reason)

        st.divider()