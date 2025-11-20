#!/usr/bin/env python3
"""
ANALYTICS ENGINE
Advanced analytics and performance metrics for StockGenie
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from database import get_db_connection, format_sql, DB_IS_POSTGRES


def get_win_rate_by_signal_type(days: int = 30) -> pd.DataFrame:
    """
    Calculate win rate for each signal type
    
    Returns:
        DataFrame with columns: signal_type, total_signals, winning_signals, win_rate
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = format_sql("""
        SELECT 
            CASE 
                WHEN consolidating = 1 THEN 'Consolidation'
                WHEN buy_dip = 1 THEN 'Buy-the-Dip'
                WHEN breakout = 1 THEN 'Breakout'
                WHEN vol_spike = 1 THEN 'Volume Spike'
                WHEN ema_bullish = 1 THEN 'EMA Bullish'
                WHEN macd_bullish = 1 THEN 'MACD Bullish'
                WHEN vwap_reclaim = 1 THEN 'VWAP Reclaim'
                ELSE 'Other'
            END as signal_type,
            COUNT(*) as total,
            SUM(CASE WHEN price_change_1d > 0 THEN 1 ELSE 0 END) as wins
        FROM signals
        WHERE signal_date >= date('now', '-' || ? || ' days')
        GROUP BY signal_type
        ORDER BY total DESC
    """)
    
    cursor.execute(query, (days,))
    results = cursor.fetchall()
    conn.close()
    
    df = pd.DataFrame(results, columns=['signal_type', 'total', 'wins'])
    df['win_rate'] = (df['wins'] / df['total'] * 100).round(2)
    
    return df


def get_pnl_over_time(days: int = 30) -> pd.DataFrame:
    """
    Get cumulative P/L over time from trades
    
    Returns:
        DataFrame with columns: date, daily_pnl, cumulative_pnl
    """
    conn = get_db_connection()
    
    query = format_sql("""
        SELECT 
            DATE(closed_at) as date,
            SUM(pnl) as daily_pnl
        FROM trades
        WHERE status = 'CLOSED'
        AND closed_at >= date('now', '-' || ? || ' days')
        GROUP BY DATE(closed_at)
        ORDER BY date
    """)
    
    df = pd.read_sql_query(query, conn, params=(days,))
    conn.close()
    
    if len(df) > 0:
        df['cumulative_pnl'] = df['daily_pnl'].cumsum()
    else:
        df['cumulative_pnl'] = 0
    
    return df


def get_r_multiple_distribution() -> pd.DataFrame:
    """
    Get distribution of R-multiples from closed trades
    
    Returns:
        DataFrame with R-multiple data
    """
    conn = get_db_connection()
    
    query = format_sql("""
        SELECT 
            r_multiple,
            exit_reason,
            ticker,
            pnl,
            closed_at
        FROM trades
        WHERE status = 'CLOSED'
        AND r_multiple IS NOT NULL
        ORDER BY closed_at DESC
        LIMIT 100
    """)
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    return df


def get_signal_performance_metrics(days: int = 30) -> Dict:
    """
    Get comprehensive performance metrics
    
    Returns:
        Dict with various performance metrics
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Total signals
    cursor.execute(format_sql("""
        SELECT COUNT(*) FROM signals
        WHERE signal_date >= date('now', '-' || ? || ' days')
    """), (days,))
    total_signals = cursor.fetchone()[0]
    
    # Trades summary
    cursor.execute(format_sql("""
        SELECT 
            COUNT(*) as total_trades,
            SUM(CASE WHEN status = 'CLOSED' THEN 1 ELSE 0 END) as closed_trades,
            SUM(CASE WHEN status = 'OPEN' THEN 1 ELSE 0 END) as open_trades,
            SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
            AVG(CASE WHEN status = 'CLOSED' THEN pnl ELSE NULL END) as avg_pnl,
            SUM(CASE WHEN status = 'CLOSED' THEN pnl ELSE 0 END) as total_pnl,
            AVG(CASE WHEN status = 'CLOSED' THEN r_multiple ELSE NULL END) as avg_r_multiple
        FROM trades
        WHERE created_at >= datetime('now', '-' || ? || ' days')
    """), (days,))
    
    trade_stats = cursor.fetchone()
    conn.close()
    
    metrics = {
        'total_signals': total_signals,
        'total_trades': trade_stats[0] or 0,
        'closed_trades': trade_stats[1] or 0,
        'open_trades': trade_stats[2] or 0,
        'winning_trades': trade_stats[3] or 0,
        'avg_pnl': round(trade_stats[4] or 0, 2),
        'total_pnl': round(trade_stats[5] or 0, 2),
        'avg_r_multiple': round(trade_stats[6] or 0, 2),
    }
    
    # Calculate win rate
    if metrics['closed_trades'] > 0:
        metrics['win_rate'] = round((metrics['winning_trades'] / metrics['closed_trades']) * 100, 2)
    else:
        metrics['win_rate'] = 0.0
    
    return metrics


def create_win_rate_chart(df: pd.DataFrame) -> go.Figure:
    """
    Create a bar chart showing win rates by signal type
    """
    fig = go.Figure(data=[
        go.Bar(
            x=df['signal_type'],
            y=df['win_rate'],
            text=df['win_rate'].apply(lambda x: f"{x}%"),
            textposition='outside',
            marker_color='#667eea',
            hovertemplate='%{x}<br>Win Rate: %{y}%<br>Total: %{customdata}<extra></extra>',
            customdata=df['total']
        )
    ])
    
    fig.update_layout(
        title='Win Rate by Signal Type',
        xaxis_title='Signal Type',
        yaxis_title='Win Rate (%)',
        template='plotly_dark',
        height=400,
        showlegend=False
    )
    
    return fig


def create_pnl_chart(df: pd.DataFrame) -> go.Figure:
    """
    Create cumulative P/L chart
    """
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Daily P/L', 'Cumulative P/L'),
        vertical_spacing=0.15
    )
    
    # Daily P/L
    colors = ['green' if val > 0 else 'red' for val in df['daily_pnl']]
    fig.add_trace(
        go.Bar(
            x=df['date'],
            y=df['daily_pnl'],
            marker_color=colors,
            name='Daily P/L',
            showlegend=False
        ),
        row=1, col=1
    )
    
    # Cumulative P/L
    fig.add_trace(
        go.Scatter(
            x=df['date'],
            y=df['cumulative_pnl'],
            mode='lines+markers',
            line=dict(color='#667eea', width=3),
            marker=dict(size=6),
            name='Cumulative P/L',
            showlegend=False
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        template='plotly_dark',
        height=600,
        showlegend=False
    )
    
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="P/L ($)", row=1, col=1)
    fig.update_yaxes(title_text="Cumulative P/L ($)", row=2, col=1)
    
    return fig


def create_r_multiple_chart(df: pd.DataFrame) -> go.Figure:
    """
    Create R-multiple distribution histogram
    """
    fig = go.Figure(data=[
        go.Histogram(
            x=df['r_multiple'],
            nbinsx=20,
            marker_color='#667eea',
            opacity=0.7,
            name='R-Multiple Distribution'
        )
    ])
    
    # Add vertical line at 0
    fig.add_vline(x=0, line_dash="dash", line_color="red", annotation_text="Break-even")
    
    # Add mean line
    mean_r = df['r_multiple'].mean()
    fig.add_vline(
        x=mean_r, 
        line_dash="dash", 
        line_color="green",
        annotation_text=f"Mean: {mean_r:.2f}R"
    )
    
    fig.update_layout(
        title='R-Multiple Distribution',
        xaxis_title='R-Multiple',
        yaxis_title='Count',
        template='plotly_dark',
        height=400,
        showlegend=False
    )
    
    return fig


def create_signal_score_distribution() -> go.Figure:
    """
    Create distribution of signal scores
    """
    conn = get_db_connection()
    
    query = format_sql("""
        SELECT score, COUNT(*) as count
        FROM signals
        WHERE signal_date >= date('now', '-30 days')
        GROUP BY score
        ORDER BY score
    """)
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    fig = go.Figure(data=[
        go.Bar(
            x=df['score'],
            y=df['count'],
            marker_color='#764ba2',
            text=df['count'],
            textposition='outside'
        )
    ])
    
    fig.update_layout(
        title='Signal Score Distribution (Last 30 Days)',
        xaxis_title='Signal Score',
        yaxis_title='Count',
        template='plotly_dark',
        height=400,
        showlegend=False
    )
    
    return fig


def get_best_performing_tickers(days: int = 30, limit: int = 10) -> pd.DataFrame:
    """
    Get top performing tickers by total P/L
    """
    conn = get_db_connection()
    
    query = format_sql("""
        SELECT 
            ticker,
            COUNT(*) as total_trades,
            SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins,
            SUM(pnl) as total_pnl,
            AVG(r_multiple) as avg_r_multiple
        FROM trades
        WHERE status = 'CLOSED'
        AND closed_at >= datetime('now', '-' || ? || ' days')
        GROUP BY ticker
        HAVING total_trades >= 2
        ORDER BY total_pnl DESC
        LIMIT ?
    """)
    
    df = pd.read_sql_query(query, conn, params=(days, limit))
    conn.close()
    
    if len(df) > 0:
        df['win_rate'] = (df['wins'] / df['total_trades'] * 100).round(2)
        df['total_pnl'] = df['total_pnl'].round(2)
        df['avg_r_multiple'] = df['avg_r_multiple'].round(2)
    
    return df


if __name__ == "__main__":
    print("🚀 Testing Analytics Engine\n")
    
    # Test win rates
    print("📊 Win Rates by Signal Type:")
    win_rates = get_win_rate_by_signal_type(30)
    print(win_rates)
    print()
    
    # Test metrics
    print("📈 Performance Metrics (30 days):")
    metrics = get_signal_performance_metrics(30)
    for key, value in metrics.items():
        print(f"  {key}: {value}")
    print()
    
    # Test best performers
    print("🏆 Best Performing Tickers:")
    best = get_best_performing_tickers(30, 5)
    print(best)
