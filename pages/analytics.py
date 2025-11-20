"""
ANALYTICS DASHBOARD PAGE
Advanced performance metrics and visualization for Streamlit
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from analytics_engine import (
    get_win_rate_by_signal_type,
    get_pnl_over_time,
    get_r_multiple_distribution,
    get_signal_performance_metrics,
    create_win_rate_chart,
    create_pnl_chart,
    create_r_multiple_chart,
    create_signal_score_distribution,
    get_best_performing_tickers
)

# Page config
st.set_page_config(
    page_title="StockGenie Analytics",
    page_icon="📊",
    layout="wide"
)

st.title("📊 StockGenie Analytics Dashboard")
st.markdown("*Advanced performance metrics and backtesting results*")

# Sidebar filters
st.sidebar.header("⚙️ Filters")
days_range = st.sidebar.selectbox(
    "Time Range",
    options=[7, 14, 30, 60, 90],
    index=2,
    format_func=lambda x: f"Last {x} days"
)

# Get metrics
metrics = get_signal_performance_metrics(days_range)

# Top metrics row
st.markdown("### 📈 Performance Overview")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total Signals",
        value=metrics['total_signals']
    )
    
with col2:
    st.metric(
        label="Win Rate",
        value=f"{metrics['win_rate']}%",
        delta=f"{metrics['winning_trades']}/{metrics['closed_trades']} trades" if metrics['closed_trades'] > 0 else "No trades"
    )

with col3:
    st.metric(
        label="Total P/L",
        value=f"${metrics['total_pnl']:,.2f}",
        delta=f"Avg: ${metrics['avg_pnl']:,.2f}"
    )

with col4:
    st.metric(
        label="Avg R-Multiple",
        value=f"{metrics['avg_r_multiple']:.2f}R",
        delta=f"{metrics['closed_trades']} closed"
    )

st.divider()

# Charts row 1
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🎯 Win Rate by Signal Type")
    win_rate_df = get_win_rate_by_signal_type(days_range)
    
    if len(win_rate_df) > 0:
        fig = create_win_rate_chart(win_rate_df)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No signal data available for this period")

with col2:
    st.markdown("### 📊 Signal Score Distribution")
    fig_score = create_signal_score_distribution()
    st.plotly_chart(fig_score, use_container_width=True)

st.divider()

# P/L Chart
st.markdown("### 💰 Profit & Loss Over Time")
pnl_df = get_pnl_over_time(days_range)

if len(pnl_df) > 0:
    fig_pnl = create_pnl_chart(pnl_df)
    st.plotly_chart(fig_pnl, use_container_width=True)
else:
    st.info("No closed trades yet to display P/L")

st.divider()

# R-Multiple Distribution
st.markdown("### 📐 R-Multiple Distribution")
r_mult_df = get_r_multiple_distribution()

if len(r_mult_df) > 0:
    fig_r = create_r_multiple_chart(r_mult_df)
    st.plotly_chart(fig_r, use_container_width=True)
    
    # R-Multiple table
    with st.expander("📋 Latest Trades by R-Multiple"):
        display_df = r_mult_df[['ticker', 'r_multiple', 'pnl', 'exit_reason', 'closed_at']].head(20)
        display_df['pnl'] = display_df['pnl'].apply(lambda x: f"${x:.2f}")
        display_df['r_multiple'] = display_df['r_multiple'].apply(lambda x: f"{x:.2f}R")
        st.dataframe(display_df, use_container_width=True, hide_index=True)
else:
    st.info("No closed trades yet to analyze R-multiples")

st.divider()

# Best performing tickers
st.markdown("### 🏆 Best Performing Tickers")
best_tickers = get_best_performing_tickers(days_range, 10)

if len(best_tickers) > 0:
    # Format for display
    display_tickers = best_tickers.copy()
    display_tickers['total_pnl'] = display_tickers['total_pnl'].apply(lambda x: f"${x:,.2f}")
    display_tickers['win_rate'] = display_tickers['win_rate'].apply(lambda x: f"{x}%")
    display_tickers['avg_r_multiple'] = display_tickers['avg_r_multiple'].apply(lambda x: f"{x}R")
    
    st.dataframe(
        display_tickers,
        column_config={
            "ticker": "Ticker",
            "total_trades": "Total Trades",
            "wins": "Wins",
            "total_pnl": "Total P/L",
            "avg_r_multiple": "Avg R-Multiple",
            "win_rate": "Win Rate"
        },
        hide_index=True,
        use_container_width=True
    )
else:
    st.info("No ticker data available (minimum 2 trades required)")

# Footer
st.markdown("---")
st.caption(f"📊 Analytics refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
