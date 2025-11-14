
import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import subprocess
import sys
from pathlib import Path
import time
import yaml
import yfinance as yf
from streamlit_autorefresh import st_autorefresh
from database import (
    get_recent_scans,
    get_top_signals,
    get_signal_stats,
    calculate_win_rates
)
from interactive_charts import create_interactive_chart
from scan_and_chart import get_clean_prices, add_indicators

# Page config
st.set_page_config(
    page_title="AI Stock Market Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Auto-refresh every 15 minutes (900000 ms) for near real-time intraday analysis
st_autorefresh(interval=900000, key="ai_stock_agent_autorefresh")

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .signal-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-size: 0.85rem;
        font-weight: bold;
        margin: 0.2rem;
    }
    .score-high { background: #ff6b6b; color: white; }
    .score-medium { background: #ffd93d; color: black; }
    .score-low { background: #6bcf7f; color: white; }
    .trend-up { color: #00d084; }
    .trend-down { color: #ff6b6b; }
    .trend-choppy { color: #ffa500; }
</style>
""", unsafe_allow_html=True)


def load_scan_results():
    """Load the latest scan results from CSV"""
    csv_path = "scan_results.csv"
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        return df
    return None


def get_last_scan_time():
    """Get the last modification time of scan results"""
    csv_path = "scan_results.csv"
    if os.path.exists(csv_path):
        timestamp = os.path.getmtime(csv_path)
        return datetime.fromtimestamp(timestamp)
    return None


def run_scan_if_stale(max_age_minutes=15):
    """Automatically run scan if data is stale (for intraday analysis)"""
    csv_path = "scan_results.csv"

    # If no results exist, run scan
    if not os.path.exists(csv_path):
        st.info("🔄 No scan data found. Running initial scan...")
        success, stdout, stderr = run_scan()
        if success:
            st.success("✅ Initial scan completed!")
        return

    # Check if data is stale
    mtime = os.path.getmtime(csv_path)
    age_minutes = (time.time() - mtime) / 60

    if age_minutes > max_age_minutes:
        st.info(f"🔄 Data is {int(age_minutes)} minutes old. Running fresh intraday scan...")
        success, stdout, stderr = run_scan()
        if success:
            st.success("✅ Intraday scan completed! Data refreshed.")
        else:
            st.warning(f"⚠️ Scan encountered an issue. Using existing data.")


def run_scan():
    """Run the stock scanning script"""
    try:
        result = subprocess.run(
            [sys.executable, "scan_and_chart.py"],
            capture_output=True,
            text=True,
            timeout=300
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def get_score_badge(score):
    """Generate HTML badge for signal score"""
    if score >= 5:
        emoji = "🔥"
        css_class = "score-high"
    elif score >= 3:
        emoji = "⭐"
        css_class = "score-medium"
    else:
        emoji = "📍"
        css_class = "score-low"

    return f'<span class="signal-badge {css_class}">{emoji} Score: {score}</span>'


def get_trend_icon(trend):
    """Get trend icon and color"""
    if trend == "UP":
        return "⬆️", "trend-up"
    elif trend == "DOWN":
        return "⬇️", "trend-down"
    else:
        return "↔️", "trend-choppy"


def display_signal_badges(row):
    """Generate signal badges for a stock"""
    badges = []

    if row.get('Consolidating'):
        badges.append('🟢 CONSOLIDATION')
    if row.get('BuyDip'):
        badges.append('📉 BUY-DIP')
    if row.get('Breakout'):
        badges.append('🚀 BREAKOUT')
    if row.get('VolSpike'):
        badges.append('📈 VOL SPIKE')

    return ' | '.join(badges) if badges else '—'


# Main UI
def main():
    # Header
    st.markdown('<div class="main-header">📊 AI Stock Market Agent</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Near real-time intraday market analysis • Auto-refreshing every 15 minutes</div>', unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.markdown("### 📊 AI Stock Agent")
        st.caption("Intelligent Market Analysis")
        st.markdown("---")

        st.subheader("⚡ Quick Actions")

        if st.button("🔄 Run New Scan", use_container_width=True, type="primary"):
            with st.spinner("Scanning markets... This may take 1-2 minutes"):
                success, stdout, stderr = run_scan()

                if success:
                    st.success("✅ Scan completed successfully!")
                    st.rerun()
                else:
                    st.error("❌ Scan failed")
                    if stderr:
                        with st.expander("Error Details"):
                            st.code(stderr)
                    st.info("💡 **Troubleshooting:**")
                    st.caption("• Check your internet connection")
                    st.caption("• Verify tickers in config.yaml")
                    st.caption("• Ensure yfinance is installed: `pip install yfinance`")
                    st.caption("• Try running manually: `python scan_and_chart.py`")

        st.markdown("---")

        # Last scan info
        last_scan = get_last_scan_time()
        if last_scan:
            st.metric("Last Scan", last_scan.strftime("%b %d, %Y"))
            st.caption(f"at {last_scan.strftime('%I:%M %p')}")
        else:
            st.warning("No scan data found")
            st.caption("Click 'Run New Scan' to start")

        st.markdown("---")

        # Settings
        st.subheader("⚙️ Settings")
        show_charts = st.checkbox("Show Charts", value=True)
        interactive_charts = st.checkbox("🎯 Interactive Charts", value=True, help="Use TradingView-style interactive charts (zoom, pan, crosshair)")
        show_only_signals = st.checkbox("Only Show Signals", value=False)
        min_score = st.slider("Minimum Score", 0, 8, 0)

        st.markdown("---")
        st.caption("Built with Python & Streamlit")
        st.caption("Powered by yfinance")

    # Auto-run scan if data is stale (intraday analysis)
    run_scan_if_stale(max_age_minutes=15)

    # Main content
    df = load_scan_results()

    if df is None:
        st.warning("⚠️ No scan results found. Run a scan to get started!")
        st.info("👈 Click 'Run New Scan' in the sidebar")
        return

    # Apply filters
    original_count = len(df)

    if show_only_signals:
        df = df[
            (df['Consolidating'] == True) |
            (df['BuyDip'] == True) |
            (df['Breakout'] == True) |
            (df['VolSpike'] == True)
        ]

    if min_score > 0:
        df = df[df['Score'] >= min_score]

    # Check if filters removed all stocks
    filtered_out = original_count - len(df)

    # Summary metrics
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Total Scanned", len(load_scan_results()))

    with col2:
        st.metric("🟢 Consolidation", int(df['Consolidating'].sum()) if not df.empty else 0)

    with col3:
        st.metric("📉 Buy-the-Dip", int(df['BuyDip'].sum()) if not df.empty else 0)

    with col4:
        st.metric("🚀 Breakout", int(df['Breakout'].sum()) if not df.empty else 0)

    with col5:
        st.metric("📈 Volume Spike", int(df['VolSpike'].sum()) if not df.empty else 0)

    st.markdown("---")

    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Signals", "📈 Charts", "📋 Full Data", "📅 History", "🎯 Performance"])

    with tab1:
        st.subheader("Top Opportunities by Signal Score")

        if df.empty:
            st.warning("⚠️ No stocks match your current filters")
            st.info(f"**{filtered_out} stocks filtered out**")
            st.markdown("**Try adjusting:**")
            st.markdown("• Lower the minimum score slider")
            st.markdown("• Disable 'Only Show Signals'")
            st.markdown("• Run a new scan to get fresh data")
        else:
            if filtered_out > 0:
                st.caption(f"Showing {len(df)} of {original_count} stocks (filtered out {filtered_out})")
            # Display each stock as a card
            for idx, row in df.iterrows():
                # Skip stocks with no signals if filter is on
                signals = display_signal_badges(row)
                if show_only_signals and signals == '—':
                    continue

                with st.container():
                    col_a, col_b, col_c = st.columns([2, 3, 2])

                    with col_a:
                        st.markdown(f"### {row['Ticker']}")
                        st.markdown(f"**${row['Close']:.2f}**")
                        st.markdown(get_score_badge(row['Score']), unsafe_allow_html=True)

                    with col_b:
                        st.markdown(f"**Signals:** {signals}")

                        trend_icon, trend_class = get_trend_icon(row['Trend'])
                        st.markdown(f'<span class="{trend_class}">Trend: {trend_icon} {row["Trend"]}</span>', unsafe_allow_html=True)

                        st.caption(f"RSI: {row['RSI']:.1f} | ADX: {row['ADX']:.1f} | BB Width: {row['BBWidth_pct']:.2f}% | ATR: {row['ATR%']:.2f}%")

                    with col_c:
                        # Technical indicators mini table
                        indicators = pd.DataFrame({
                            'Indicator': ['RSI', 'ADX', 'BB Width', 'ATR%'],
                            'Value': [
                                f"{row['RSI']:.1f}",
                                f"{row['ADX']:.1f}",
                                f"{row['BBWidth_pct']:.2f}%",
                                f"{row['ATR%']:.2f}%"
                            ]
                        })
                        st.dataframe(indicators, hide_index=True, use_container_width=True)

                    st.markdown("---")

    with tab2:
        st.subheader("Stock Charts")

        if show_charts:
            # Filter to only show charts for current filtered stocks
            filtered_tickers = df['Ticker'].tolist() if not df.empty else []

            if not filtered_tickers:
                st.warning("⚠️ No stocks to display with current filters")
                st.info("Adjust your filters in the sidebar to see charts")
            elif interactive_charts:
                # Interactive TradingView-style charts
                st.info("🎯 Interactive Charts - Zoom: scroll wheel | Pan: drag | Crosshair: hover")

                # Load config for data fetching
                cfg = yaml.safe_load(open("config.yaml", "r"))

                # Selector for which stock to view
                selected_ticker = st.selectbox(
                    "Select Stock",
                    filtered_tickers,
                    index=0 if filtered_tickers else None
                )

                if selected_ticker:
                    with st.spinner(f"Loading {selected_ticker} chart..."):
                        try:
                            # Fetch data
                            ticker_df = get_clean_prices(selected_ticker, cfg["data"]["period"], cfg["data"]["interval"])

                            if not ticker_df.empty:
                                # Add indicators
                                ticker_df = add_indicators(ticker_df, cfg)

                                # Create and display interactive chart
                                create_interactive_chart(ticker_df, selected_ticker, height=600)
                            else:
                                st.error(f"No data available for {selected_ticker}")

                        except Exception as e:
                            st.error(f"Error loading chart: {str(e)}")
                            st.info("Tip: Try using static charts if interactive charts fail to load")
            else:
                # Static PNG charts (original behavior)
                charts_dir = Path("charts")

                if not charts_dir.exists():
                    st.warning("📁 No charts directory found")
                    st.info("Charts will be created automatically when you run a scan")
                else:
                    chart_files = list(charts_dir.glob("*.png"))

                    if not chart_files:
                        st.info("📈 No charts generated yet. Run a scan to create charts.")
                    else:
                        cols_per_row = 2
                        for i in range(0, len(filtered_tickers), cols_per_row):
                            cols = st.columns(cols_per_row)

                            for j in range(cols_per_row):
                                if i + j < len(filtered_tickers):
                                    ticker = filtered_tickers[i + j]
                                    chart_path = charts_dir / f"{ticker}.png"

                                    if chart_path.exists():
                                        with cols[j]:
                                            st.markdown(f"**{ticker}**")
                                            st.image(str(chart_path), use_container_width=True)
                                    else:
                                        with cols[j]:
                                            st.warning(f"⚠️ Chart for {ticker} not found")
        else:
            st.info("📊 Chart display is disabled. Enable in sidebar settings.")

    with tab3:
        st.subheader("Complete Scan Results")

        if not df.empty:
            # Format boolean columns
            display_df = df.copy()
            bool_cols = ['Consolidating', 'BuyDip', 'Breakout', 'VolSpike']
            for col in bool_cols:
                if col in display_df.columns:
                    display_df[col] = display_df[col].apply(lambda x: '✅' if x else '—')

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )

            # Download button
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"stock_signals_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No data to display")

    with tab4:
        st.subheader("Scan History")

        try:
            # Get recent scans
            scans_df = get_recent_scans(limit=20)

            if not scans_df.empty:
                # Format scan_date
                scans_df['scan_date'] = pd.to_datetime(scans_df['scan_date']).dt.strftime('%Y-%m-%d %H:%M')

                st.dataframe(
                    scans_df,
                    column_config={
                        "scan_id": "Scan ID",
                        "scan_date": "Date & Time",
                        "total_stocks": "Total Stocks",
                        "signals_found": "Signals Found",
                        "signal_rate_pct": st.column_config.NumberColumn(
                            "Signal Rate",
                            format="%.1f%%"
                        )
                    },
                    hide_index=True,
                    use_container_width=True
                )

                st.markdown("---")

                # Show top signals from last 30 days
                st.subheader("Top Signals (Last 30 Days)")

                days_filter = st.slider("Days to show", 7, 90, 30, key="history_days")
                min_score_filter = st.slider("Minimum score", 0, 8, 2, key="history_score")

                top_signals_df = get_top_signals(days=days_filter, min_score=min_score_filter)

                if not top_signals_df.empty:
                    # Format dates
                    top_signals_df['signal_date'] = pd.to_datetime(top_signals_df['signal_date']).dt.strftime('%Y-%m-%d')

                    # Format boolean columns
                    bool_cols = ['consolidating', 'buy_dip', 'breakout', 'vol_spike']
                    for col in bool_cols:
                        if col in top_signals_df.columns:
                            top_signals_df[col] = top_signals_df[col].apply(lambda x: '✅' if x else '—')

                    st.dataframe(
                        top_signals_df,
                        column_config={
                            "ticker": "Ticker",
                            "signal_date": "Date",
                            "score": "Score",
                            "consolidating": "Consolidation",
                            "buy_dip": "Buy Dip",
                            "breakout": "Breakout",
                            "vol_spike": "Vol Spike",
                            "trend": "Trend",
                            "price_at_signal": st.column_config.NumberColumn(
                                "Price",
                                format="$%.2f"
                            ),
                            "rsi": st.column_config.NumberColumn("RSI", format="%.1f"),
                            "adx": st.column_config.NumberColumn("ADX", format="%.1f")
                        },
                        hide_index=True,
                        use_container_width=True
                    )
                else:
                    st.info(f"No signals found with score >= {min_score_filter} in the last {days_filter} days")

            else:
                st.info("📊 No scan history yet. Run a scan to start building history!")
                st.caption("Historical data will appear here after your first scan")

        except Exception as e:
            st.error(f"Error loading history: {e}")
            st.info("Make sure database is initialized. Run: `python database.py`")

    with tab5:
        st.subheader("Signal Performance Analytics")

        try:
            # Overall stats
            stats = get_signal_stats()

            st.markdown("### 📊 Overall Statistics")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Signals", stats.get('total_signals', 0))

            with col2:
                st.metric("Avg Score", stats.get('avg_score', 0))

            with col3:
                st.metric("🟢 Consolidation", stats.get('consolidation_count', 0))

            with col4:
                st.metric("🚀 Breakout", stats.get('breakout_count', 0))

            col5, col6, col7, col8 = st.columns(4)

            with col5:
                st.metric("📉 Buy-the-Dip", stats.get('buy_dip_count', 0))

            with col6:
                st.metric("📈 Volume Spike", stats.get('vol_spike_count', 0))

            st.markdown("---")

            # Win rates
            st.markdown("### 🎯 Win Rate Analysis")

            st.info("📌 **Note:** Win rate tracking requires price updates. This feature will be fully functional after implementing automated price tracking.")

            signal_type_map = {
                "All Signals": "all",
                "Consolidation": "consolidating",
                "Buy-the-Dip": "buy_dip",
                "Breakout": "breakout",
                "Volume Spike": "vol_spike"
            }

            signal_filter = st.selectbox(
                "Filter by signal type",
                list(signal_type_map.keys())
            )

            days_filter = st.slider("Days to analyze", 7, 90, 30, key="perf_days")

            win_rates = calculate_win_rates(
                signal_type=signal_type_map[signal_filter],
                days=days_filter
            )

            if win_rates['total_signals'] > 0:
                col_a, col_b, col_c = st.columns(3)

                with col_a:
                    st.metric(
                        "1-Day Win Rate",
                        f"{win_rates['win_rate_1d']}%",
                        delta=f"{win_rates['avg_return_1d']}% avg"
                    )

                with col_b:
                    st.metric(
                        "7-Day Win Rate",
                        f"{win_rates['win_rate_7d']}%",
                        delta=f"{win_rates['avg_return_7d']}% avg"
                    )

                with col_c:
                    st.metric(
                        "30-Day Win Rate",
                        f"{win_rates['win_rate_30d']}%",
                        delta=f"{win_rates['avg_return_30d']}% avg"
                    )

                st.caption(f"Based on {win_rates['total_signals']} signals from the last {days_filter} days")
            else:
                st.info(f"No {signal_filter.lower()} signals found in the last {days_filter} days")

            st.markdown("---")

            # Top tickers
            if stats.get('top_tickers'):
                st.markdown("### 🏆 Most Signaled Tickers")

                top_tickers_df = pd.DataFrame(
                    stats['top_tickers'],
                    columns=['Ticker', 'Signal Count']
                )

                st.dataframe(
                    top_tickers_df,
                    hide_index=True,
                    use_container_width=True
                )

        except Exception as e:
            st.error(f"Error loading performance data: {e}")
            st.info("Make sure database is initialized and contains scan data")

    # Footer
    st.markdown("---")
    st.caption("⚠️ This tool is for educational purposes only. Not financial advice. Always do your own research.")


if __name__ == "__main__":
    main()
