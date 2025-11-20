"""
LIVE MARKET DASHBOARD
Real-time view of ALL US stocks with predictions, sorting, and filters
Auto-refreshes every 60 seconds
"""

import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
import sys
from pathlib import Path
import time

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from top_performers_scanner import get_stock_universe

# Page config
st.set_page_config(
    page_title="Live Market Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .big-font { font-size: 24px !important; font-weight: bold; }
    .green { color: #00ff00 !important; }
    .red { color: #ff0000 !important; }
    .metric-card {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    .stDataFrame { font-size: 14px; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# DATA FETCHING
# ============================================================

@st.cache_data(ttl=60)  # Cache for 60 seconds
def fetch_all_stocks():
    """Fetch data for ALL US stocks (S&P 500 + NASDAQ-100)"""

    # Get all tickers
    tickers = get_stock_universe('all')

    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()

    # Batch download for efficiency
    batch_size = 50
    total_batches = len(tickers) // batch_size + 1

    for i in range(0, len(tickers), batch_size):
        batch = tickers[i:i+batch_size]
        batch_num = i // batch_size + 1

        status_text.text(f"Scanning batch {batch_num}/{total_batches}... ({len(results)} stocks loaded)")
        progress_bar.progress(min(i / len(tickers), 1.0))

        try:
            # Download batch data
            data = yf.download(batch, period="5d", interval="1d", progress=False, group_by='ticker')

            for ticker in batch:
                try:
                    if len(batch) == 1:
                        ticker_data = data
                    else:
                        if ticker not in data.columns.get_level_values(0):
                            continue
                        ticker_data = data[ticker]

                    if ticker_data.empty or len(ticker_data) < 2:
                        continue

                    # Calculate metrics
                    current = float(ticker_data['Close'].iloc[-1])
                    prev = float(ticker_data['Close'].iloc[-2])
                    change_pct = ((current - prev) / prev) * 100

                    # Weekly change
                    week_ago = float(ticker_data['Close'].iloc[0]) if len(ticker_data) >= 5 else prev
                    weekly_pct = ((current - week_ago) / week_ago) * 100

                    # Volume
                    volume = int(ticker_data['Volume'].iloc[-1])
                    avg_volume = int(ticker_data['Volume'].mean())
                    vol_ratio = volume / avg_volume if avg_volume > 0 else 1

                    # High/Low
                    high_52w = float(ticker_data['High'].max())
                    low_52w = float(ticker_data['Low'].min())

                    results.append({
                        'Ticker': ticker,
                        'Price': current,
                        'Change%': round(change_pct, 2),
                        'Weekly%': round(weekly_pct, 2),
                        'Volume': volume,
                        'Vol_Ratio': round(vol_ratio, 2),
                        'High': high_52w,
                        'Low': low_52w,
                        'Status': 'UP' if change_pct > 0 else 'DOWN' if change_pct < 0 else 'FLAT'
                    })

                except Exception:
                    continue

        except Exception as e:
            continue

    progress_bar.empty()
    status_text.empty()

    return pd.DataFrame(results)


@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_stock_info(ticker):
    """Get additional stock info"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            'Name': info.get('shortName', ticker),
            'Sector': info.get('sector', 'N/A'),
            'Industry': info.get('industry', 'N/A'),
            'MarketCap': info.get('marketCap', 0),
            'PE': info.get('trailingPE', 0),
            'Beta': info.get('beta', 0)
        }
    except:
        return None


# ============================================================
# MAIN APP
# ============================================================

# Header
st.title("📊 Live Market Dashboard")
st.markdown("**Real-time view of 700+ US stocks** | Auto-refreshes every 60 seconds")

# Sidebar controls
st.sidebar.header("🎛️ Filters & Controls")

# Refresh button
if st.sidebar.button("🔄 Refresh Now", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

# Auto-refresh toggle
auto_refresh = st.sidebar.checkbox("Auto-refresh (60s)", value=True)

# Filters
st.sidebar.markdown("---")
st.sidebar.subheader("📊 Filters")

# Sort options
sort_by = st.sidebar.selectbox(
    "Sort By",
    ["Change% (High to Low)", "Change% (Low to High)",
     "Weekly% (High to Low)", "Weekly% (Low to High)",
     "Volume (High to Low)", "Price (High to Low)", "Price (Low to High)"]
)

# Status filter
status_filter = st.sidebar.multiselect(
    "Status",
    ["UP", "DOWN", "FLAT"],
    default=["UP", "DOWN", "FLAT"]
)

# Min change filter
min_change = st.sidebar.slider("Min |Change%|", 0.0, 10.0, 0.0, 0.5)

# Search
search = st.sidebar.text_input("🔍 Search Ticker", "").upper()

# Number of stocks to show
num_stocks = st.sidebar.slider("Stocks to Display", 50, 500, 100, 50)

# ============================================================
# FETCH AND DISPLAY DATA
# ============================================================

# Fetch all stocks
with st.spinner("Loading market data..."):
    df = fetch_all_stocks()

if df.empty:
    st.error("Failed to fetch market data. Please try again.")
    st.stop()

# Apply filters
filtered_df = df.copy()

# Status filter
filtered_df = filtered_df[filtered_df['Status'].isin(status_filter)]

# Min change filter
filtered_df = filtered_df[filtered_df['Change%'].abs() >= min_change]

# Search filter
if search:
    filtered_df = filtered_df[filtered_df['Ticker'].str.contains(search)]

# Sort
sort_map = {
    "Change% (High to Low)": ('Change%', False),
    "Change% (Low to High)": ('Change%', True),
    "Weekly% (High to Low)": ('Weekly%', False),
    "Weekly% (Low to High)": ('Weekly%', True),
    "Volume (High to Low)": ('Volume', False),
    "Price (High to Low)": ('Price', False),
    "Price (Low to High)": ('Price', True)
}
sort_col, sort_asc = sort_map.get(sort_by, ('Change%', False))
filtered_df = filtered_df.sort_values(sort_col, ascending=sort_asc)

# Limit display
display_df = filtered_df.head(num_stocks)

# ============================================================
# MARKET OVERVIEW
# ============================================================

st.markdown("---")
st.subheader("📈 Market Overview")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    total_stocks = len(df)
    st.metric("Total Stocks", total_stocks)

with col2:
    gainers = len(df[df['Change%'] > 0])
    st.metric("Gainers", gainers, f"{(gainers/total_stocks*100):.1f}%")

with col3:
    losers = len(df[df['Change%'] < 0])
    st.metric("Losers", losers, f"{(losers/total_stocks*100):.1f}%")

with col4:
    avg_change = df['Change%'].mean()
    st.metric("Avg Change", f"{avg_change:+.2f}%")

with col5:
    st.metric("Displayed", len(display_df))

# ============================================================
# TOP MOVERS SUMMARY
# ============================================================

st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    st.subheader("🚀 Top 5 Gainers")
    top_gainers = df.nlargest(5, 'Change%')[['Ticker', 'Price', 'Change%']]
    for _, row in top_gainers.iterrows():
        st.markdown(f"**{row['Ticker']}** ${row['Price']:.2f} `+{row['Change%']:.2f}%`")

with col2:
    st.subheader("📉 Top 5 Losers")
    top_losers = df.nsmallest(5, 'Change%')[['Ticker', 'Price', 'Change%']]
    for _, row in top_losers.iterrows():
        st.markdown(f"**{row['Ticker']}** ${row['Price']:.2f} `{row['Change%']:.2f}%`")

# ============================================================
# MAIN DATA TABLE
# ============================================================

st.markdown("---")
st.subheader(f"📋 All Stocks ({len(display_df)} shown)")

# Format display
table_df = display_df.copy()
table_df['Price'] = table_df['Price'].apply(lambda x: f"${x:.2f}")
table_df['Change%'] = table_df['Change%'].apply(lambda x: f"+{x:.2f}%" if x >= 0 else f"{x:.2f}%")
table_df['Weekly%'] = table_df['Weekly%'].apply(lambda x: f"+{x:.2f}%" if x >= 0 else f"{x:.2f}%")
table_df['Volume'] = table_df['Volume'].apply(lambda x: f"{x/1e6:.1f}M" if x >= 1e6 else f"{x/1e3:.0f}K")
table_df['Vol_Ratio'] = table_df['Vol_Ratio'].apply(lambda x: f"{x:.1f}x")

# Add emoji for status
table_df[''] = table_df['Status'].apply(lambda x: '🟢' if x == 'UP' else '🔴' if x == 'DOWN' else '⚪')

# Reorder columns
table_df = table_df[['', 'Ticker', 'Price', 'Change%', 'Weekly%', 'Volume', 'Vol_Ratio']]

# Display table
st.dataframe(
    table_df,
    column_config={
        "": st.column_config.TextColumn("", width="small"),
        "Ticker": st.column_config.TextColumn("Symbol", width="small"),
        "Price": st.column_config.TextColumn("Price", width="small"),
        "Change%": st.column_config.TextColumn("Today", width="small"),
        "Weekly%": st.column_config.TextColumn("Week", width="small"),
        "Volume": st.column_config.TextColumn("Volume", width="small"),
        "Vol_Ratio": st.column_config.TextColumn("Vol Ratio", width="small"),
    },
    hide_index=True,
    use_container_width=True,
    height=600
)

# ============================================================
# STOCK DETAILS (Click to expand)
# ============================================================

st.markdown("---")
st.subheader("🔍 Stock Details")

selected_ticker = st.selectbox(
    "Select a stock for details",
    options=[""] + list(display_df['Ticker'].values),
    format_func=lambda x: "Choose a stock..." if x == "" else x
)

if selected_ticker:
    with st.spinner(f"Loading {selected_ticker} details..."):
        info = get_stock_info(selected_ticker)
        stock_data = df[df['Ticker'] == selected_ticker].iloc[0]

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"### {selected_ticker}")
            if info:
                st.write(f"**{info['Name']}**")
                st.write(f"Sector: {info['Sector']}")
                st.write(f"Industry: {info['Industry']}")

        with col2:
            st.metric("Price", f"${stock_data['Price']:.2f}")
            st.metric("Today", f"{stock_data['Change%']:+.2f}%")
            st.metric("This Week", f"{stock_data['Weekly%']:+.2f}%")

        with col3:
            if info:
                mc = info['MarketCap']
                if mc >= 1e12:
                    mc_str = f"${mc/1e12:.2f}T"
                elif mc >= 1e9:
                    mc_str = f"${mc/1e9:.2f}B"
                else:
                    mc_str = f"${mc/1e6:.2f}M"
                st.metric("Market Cap", mc_str)
                st.metric("P/E Ratio", f"{info['PE']:.2f}" if info['PE'] else "N/A")
                st.metric("Beta", f"{info['Beta']:.2f}" if info['Beta'] else "N/A")

# ============================================================
# FOOTER
# ============================================================

st.markdown("---")
st.caption(f"📊 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Scanning {len(df)} stocks")
st.caption("⚠️ Data provided for educational purposes only. Not financial advice.")

# Auto-refresh
if auto_refresh:
    time.sleep(60)
    st.rerun()
