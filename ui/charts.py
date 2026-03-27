"""Chart components using Plotly."""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Optional


def plot_kline_chart(df: pd.DataFrame, height: int = 400):
    """Plot K-line (candlestick) chart.

    Args:
        df: DataFrame with OHLCV data
        height: Chart height in pixels
    """
    if df.empty:
        st.info("暂无数据")
        return

    # Set date as index for plotting
    df_plot = df.copy()
    if 'date' in df_plot.columns:
        df_plot['date'] = pd.to_datetime(df_plot['date'])
        df_plot = df_plot.set_index('date')

    fig = go.Figure(data=[go.Candlestick(
        x=df_plot.index,
        open=df_plot['open'],
        high=df_plot['high'],
        low=df_plot['low'],
        close=df_plot['close'],
        increasing_line_color='#ef4444',  # Red for up
        decreasing_line_color='#22c55e',  # Green for down
    )])

    fig.update_layout(
        xaxis_rangeslider_visible=False,
        height=height,
        margin=dict(l=0, r=0, t=0, b=0)
    )

    st.plotly_chart(fig, use_container_width=True)


def plot_volume_chart(df: pd.DataFrame, height: int = 150):
    """Plot volume bar chart.

    Args:
        df: DataFrame with volume data
        height: Chart height in pixels
    """
    if df.empty:
        return

    # Set date as index for plotting
    df_plot = df.copy()
    if 'date' in df_plot.columns:
        df_plot['date'] = pd.to_datetime(df_plot['date'])
        df_plot = df_plot.set_index('date')

    colors = ['#ef4444' if row['close'] >= row['open'] else '#22c55e' for _, row in df_plot.iterrows()]

    fig = go.Figure(data=[go.Bar(
        x=df_plot.index,
        y=df_plot['volume'],
        marker_color=colors
    )])

    fig.update_layout(
        xaxis_rangeslider_visible=False,
        height=height,
        margin=dict(l=0, r=0, t=0, b=0)
    )

    st.plotly_chart(fig, use_container_width=True)


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

    # Set date as index for plotting
    df_plot = df.copy()
    if 'date' in df_plot.columns:
        df_plot['date'] = pd.to_datetime(df_plot['date'])
        df_plot = df_plot.set_index('date')

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
        if col in df_plot.columns:
            fig.add_trace(go.Scatter(
                x=df_plot.index,
                y=df_plot[col],
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