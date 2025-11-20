"""
MARKET MOVERS PAGE
Real-time top gainers, losers, and watchlist
"""

import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
import json
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Page config
st.set_page_config(
    page_title="Market Movers",
    page_icon="📈",
    layout="wide"
)

# Constants
WATCHLIST_FILE = "watchlist.json"
POPULAR_STOCKS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B", "JPM", "V",
    "JNJ", "UNH", "HD", "PG", "MA", "DIS", "PYPL", "ADBE", "NFLX", "CRM",
    "AMD", "INTC", "QCOM", "COST", "PEP", "KO", "MRK", "ABT", "TMO", "CSCO",
    "AVGO", "TXN", "NKE", "MCD", "WMT", "CVX", "XOM", "LLY", "DHR", "BMY",
    "ORCL", "ACN", "UPS", "NEE", "RTX", "HON", "LOW", "SPGI", "BA", "CAT"
]

# Extended list for more comprehensive scanning
EXTENDED_STOCKS = POPULAR_STOCKS + [
    "GS", "MS", "C", "WFC", "AXP", "BLK", "SCHW", "USB", "PNC", "TFC",
    "SQ", "COIN", "HOOD", "SOFI", "AFRM", "UPST", "LC", "ALLY", "DFS", "COF",
    "PLTR", "SNOW", "NET", "DDOG", "ZS", "CRWD", "OKTA", "MDB", "TEAM", "NOW",
    "SHOP", "SQ", "MELI", "SE", "BABA", "JD", "PDD", "BIDU", "NIO", "XPEV",
    "F", "GM", "RIVN", "LCID", "FSR", "RIDE", "NKLA", "GOEV", "ARVL", "WKHS",
    "ROKU", "ZM", "DOCU", "TWLO", "U", "RBLX", "ABNB", "DASH", "LYFT", "UBER"
]


def load_watchlist():
    """Load watchlist from file"""
    if os.path.exists(WATCHLIST_FILE):
        try:
            with open(WATCHLIST_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []


def save_watchlist(watchlist):
    """Save watchlist to file"""
    with open(WATCHLIST_FILE, 'w') as f:
        json.dump(watchlist, f)


@st.cache_data(ttl=60)  # Cache for 1 minute
def get_stock_data(tickers):
    """Fetch real-time stock data for multiple tickers"""
    if not tickers:
        return pd.DataFrame()

    try:
        # Download data for all tickers at once
        data = yf.download(tickers, period="2d", interval="1d", progress=False, group_by='ticker')

        results = []
        for ticker in tickers:
            try:
                if len(tickers) == 1:
                    ticker_data = data
                else:
                    ticker_data = data[ticker] if ticker in data.columns.get_level_values(0) else None

                if ticker_data is None or ticker_data.empty:
                    continue

                # Get today's and yesterday's close
                if len(ticker_data) >= 2:
                    current_price = ticker_data['Close'].iloc[-1]
                    prev_close = ticker_data['Close'].iloc[-2]
                    change = current_price - prev_close
                    change_pct = (change / prev_close) * 100
                    volume = ticker_data['Volume'].iloc[-1]

                    results.append({
                        'Ticker': ticker,
                        'Price': current_price,
                        'Change': change,
                        'Change%': change_pct,
                        'Volume': volume,
                        'PrevClose': prev_close
                    })
            except Exception as e:
                continue

        return pd.DataFrame(results)
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=60)
def get_market_movers():
    """Get top gainers and losers from extended stock list"""
    df = get_stock_data(EXTENDED_STOCKS)

    if df.empty:
        return pd.DataFrame(), pd.DataFrame()

    # Sort for gainers and losers
    gainers = df.nlargest(15, 'Change%')
    losers = df.nsmallest(15, 'Change%')

    return gainers, losers


def display_stock_table(df, title, emoji):
    """Display a styled stock table"""
    if df.empty:
        st.info(f"No {title.lower()} data available")
        return

    st.markdown(f"### {emoji} {title}")

    # Format the dataframe for display
    display_df = df.copy()
    display_df['Price'] = display_df['Price'].apply(lambda x: f"${x:.2f}")
    display_df['Change'] = display_df['Change'].apply(
        lambda x: f"+${x:.2f}" if x >= 0 else f"-${abs(x):.2f}"
    )
    display_df['Change%'] = display_df['Change%'].apply(
        lambda x: f"+{x:.2f}%" if x >= 0 else f"{x:.2f}%"
    )
    display_df['Volume'] = display_df['Volume'].apply(lambda x: f"{x/1e6:.1f}M" if x >= 1e6 else f"{x/1e3:.0f}K")

    # Select columns to display
    display_df = display_df[['Ticker', 'Price', 'Change', 'Change%', 'Volume']]

    st.dataframe(
        display_df,
        column_config={
            "Ticker": st.column_config.TextColumn("Symbol", width="small"),
            "Price": st.column_config.TextColumn("Price", width="small"),
            "Change": st.column_config.TextColumn("Change", width="small"),
            "Change%": st.column_config.TextColumn("% Change", width="small"),
            "Volume": st.column_config.TextColumn("Volume", width="small"),
        },
        hide_index=True,
        use_container_width=True
    )


def display_watchlist_table(watchlist):
    """Display watchlist with real-time data"""
    if not watchlist:
        st.info("Your watchlist is empty. Add stocks using the sidebar.")
        return

    df = get_stock_data(watchlist)

    if df.empty:
        st.warning("Could not fetch data for watchlist stocks")
        return

    st.markdown("### 👁️ Your Watchlist")

    # Format the dataframe
    display_df = df.copy()
    display_df['Price'] = display_df['Price'].apply(lambda x: f"${x:.2f}")
    display_df['Change'] = display_df['Change'].apply(
        lambda x: f"+${x:.2f}" if x >= 0 else f"-${abs(x):.2f}"
    )
    display_df['Change%'] = display_df['Change%'].apply(
        lambda x: f"+{x:.2f}%" if x >= 0 else f"{x:.2f}%"
    )
    display_df['Volume'] = display_df['Volume'].apply(lambda x: f"{x/1e6:.1f}M" if x >= 1e6 else f"{x/1e3:.0f}K")

    # Add color coding
    for idx, row in df.iterrows():
        if row['Change%'] >= 0:
            display_df.loc[idx, 'Status'] = '🟢'
        else:
            display_df.loc[idx, 'Status'] = '🔴'

    display_df = display_df[['Status', 'Ticker', 'Price', 'Change', 'Change%', 'Volume']]

    st.dataframe(
        display_df,
        column_config={
            "Status": st.column_config.TextColumn("", width="small"),
            "Ticker": st.column_config.TextColumn("Symbol", width="small"),
            "Price": st.column_config.TextColumn("Price", width="small"),
            "Change": st.column_config.TextColumn("Change", width="small"),
            "Change%": st.column_config.TextColumn("% Change", width="small"),
            "Volume": st.column_config.TextColumn("Volume", width="small"),
        },
        hide_index=True,
        use_container_width=True
    )


# Main app
st.title("📈 Market Movers")
st.markdown("*Real-time top gainers, losers, and your personal watchlist*")

# Sidebar for watchlist management
st.sidebar.header("📋 Manage Watchlist")

# Load current watchlist
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = load_watchlist()

# Add to watchlist
new_ticker = st.sidebar.text_input("Add Stock Symbol", placeholder="e.g., AAPL").upper().strip()
if st.sidebar.button("➕ Add to Watchlist"):
    if new_ticker:
        if new_ticker not in st.session_state.watchlist:
            st.session_state.watchlist.append(new_ticker)
            save_watchlist(st.session_state.watchlist)
            st.sidebar.success(f"Added {new_ticker}")
            st.rerun()
        else:
            st.sidebar.warning(f"{new_ticker} already in watchlist")

# Remove from watchlist
if st.session_state.watchlist:
    remove_ticker = st.sidebar.selectbox(
        "Remove Stock",
        options=[""] + st.session_state.watchlist,
        format_func=lambda x: "Select to remove..." if x == "" else x
    )
    if remove_ticker and st.sidebar.button("🗑️ Remove"):
        st.session_state.watchlist.remove(remove_ticker)
        save_watchlist(st.session_state.watchlist)
        st.sidebar.success(f"Removed {remove_ticker}")
        st.rerun()

# Quick add popular stocks
st.sidebar.markdown("---")
st.sidebar.markdown("**Quick Add Popular:**")
quick_add_cols = st.sidebar.columns(3)
popular_quick = ["AAPL", "MSFT", "GOOGL", "NVDA", "TSLA", "AMZN"]
for i, ticker in enumerate(popular_quick):
    col = quick_add_cols[i % 3]
    if col.button(ticker, key=f"quick_{ticker}"):
        if ticker not in st.session_state.watchlist:
            st.session_state.watchlist.append(ticker)
            save_watchlist(st.session_state.watchlist)
            st.rerun()

# Refresh button
st.sidebar.markdown("---")
if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

# Main content tabs
tab1, tab2, tab3 = st.tabs(["🚀 Top Gainers", "📉 Top Losers", "👁️ Watchlist"])

# Get market movers
with st.spinner("Fetching market data..."):
    gainers, losers = get_market_movers()

with tab1:
    display_stock_table(gainers, "Top Gainers Today", "🚀")

    if not gainers.empty:
        # Show summary stats
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            best = gainers.iloc[0]
            st.metric("🥇 Best Performer", best['Ticker'], f"+{best['Change%']:.2f}%")
        with col2:
            avg_gain = gainers['Change%'].mean()
            st.metric("📊 Avg Gain (Top 15)", f"+{avg_gain:.2f}%")
        with col3:
            total_volume = gainers['Volume'].sum()
            st.metric("📈 Total Volume", f"{total_volume/1e9:.2f}B")

with tab2:
    display_stock_table(losers, "Top Losers Today", "📉")

    if not losers.empty:
        # Show summary stats
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            worst = losers.iloc[0]
            st.metric("📉 Worst Performer", worst['Ticker'], f"{worst['Change%']:.2f}%")
        with col2:
            avg_loss = losers['Change%'].mean()
            st.metric("📊 Avg Loss (Top 15)", f"{avg_loss:.2f}%")
        with col3:
            total_volume = losers['Volume'].sum()
            st.metric("📈 Total Volume", f"{total_volume/1e9:.2f}B")

with tab3:
    display_watchlist_table(st.session_state.watchlist)

    if st.session_state.watchlist:
        st.markdown("---")
        # Summary of watchlist performance
        df = get_stock_data(st.session_state.watchlist)
        if not df.empty:
            col1, col2, col3 = st.columns(3)
            with col1:
                gainers_count = len(df[df['Change%'] > 0])
                st.metric("🟢 Up Today", gainers_count)
            with col2:
                losers_count = len(df[df['Change%'] < 0])
                st.metric("🔴 Down Today", losers_count)
            with col3:
                avg_change = df['Change%'].mean()
                st.metric("📊 Avg Change", f"{avg_change:+.2f}%")

# Footer
st.markdown("---")
st.caption(f"📈 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Data refreshes every 60 seconds")
st.caption("⚠️ Data provided for educational purposes only. Not financial advice.")
