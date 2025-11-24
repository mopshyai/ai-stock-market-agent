"""
LIVE MARKET DASHBOARD
Real-time view of ALL US stocks with predictions, sorting, and filters
Auto-refreshes every 60 seconds
"""

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
import sys
from pathlib import Path
import time
import yaml

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from top_performers_scanner import get_stock_universe
from scan_and_chart import add_indicators

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

def calculate_signal_score(rsi, adx, change_pct, weekly_pct, vol_ratio):
    """Calculate signal score (1-10) based on technical indicators"""
    score = 5  # Base score

    # RSI scoring
    if 30 <= rsi <= 70:
        score += 1  # Healthy range
    if rsi < 30:
        score += 2  # Oversold - potential buy
    if rsi > 70:
        score -= 1  # Overbought

    # ADX (trend strength)
    if adx > 25:
        score += 1  # Strong trend
    if adx > 40:
        score += 1  # Very strong trend

    # Momentum
    if change_pct > 1:
        score += 1
    if weekly_pct > 3:
        score += 1

    # Volume confirmation
    if vol_ratio > 1.5:
        score += 1

    return max(1, min(10, score))


def get_action_signal(score, rsi, change_pct, weekly_pct):
    """Determine action signal based on score and indicators"""
    if score >= 8 and rsi < 65 and weekly_pct > 0:
        return 'BUY'
    elif score >= 6 and rsi < 70:
        return 'WATCH'
    elif rsi > 75:
        return 'TAKE_PROFIT'
    elif score <= 3 or (rsi > 70 and change_pct < -1):
        return 'AVOID'
    else:
        return 'HOLD'


def calculate_targets(price, atr_pct):
    """Calculate entry, stop loss, and take profit targets"""
    stop_loss = price * (1 - atr_pct * 1.5 / 100)
    tp1 = price * (1 + atr_pct * 1.5 / 100)
    tp2 = price * (1 + atr_pct * 3 / 100)
    return round(stop_loss, 2), round(tp1, 2), round(tp2, 2)


# Fallback stock list if Wikipedia fails
FALLBACK_STOCKS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK-B', 'JPM', 'V',
    'JNJ', 'UNH', 'HD', 'PG', 'MA', 'DIS', 'PYPL', 'ADBE', 'NFLX', 'CRM',
    'AMD', 'INTC', 'QCOM', 'COST', 'PEP', 'KO', 'MRK', 'ABT', 'TMO', 'CSCO',
    'AVGO', 'TXN', 'NKE', 'MCD', 'WMT', 'CVX', 'XOM', 'LLY', 'DHR', 'BMY',
    'ORCL', 'ACN', 'UPS', 'NEE', 'RTX', 'HON', 'LOW', 'SPGI', 'BA', 'CAT',
    'GS', 'MS', 'C', 'WFC', 'AXP', 'BLK', 'SCHW', 'USB', 'PNC', 'TFC',
    'PLTR', 'SNOW', 'NET', 'DDOG', 'ZS', 'CRWD', 'OKTA', 'MDB', 'TEAM', 'NOW',
    'SQ', 'COIN', 'HOOD', 'SOFI', 'AFRM', 'UBER', 'LYFT', 'ABNB', 'DASH', 'RBLX',
    'F', 'GM', 'RIVN', 'LCID', 'NIO', 'XPEV', 'LI', 'BABA', 'JD', 'PDD',
    'ROKU', 'ZM', 'DOCU', 'TWLO', 'U', 'SHOP', 'MELI', 'SE', 'SPOT', 'SQ'
]


@st.cache_data(ttl=60)  # Cache for 60 seconds
def fetch_all_stocks():
    """Fetch data for ALL US stocks with predictions and signals"""

    # Load config
    try:
        config_path = Path(__file__).parent.parent / "config.yaml"
        cfg = yaml.safe_load(open(config_path, "r"))
    except:
        cfg = {}

    # Get all tickers with fallback
    try:
        tickers = get_stock_universe('all')
        if not tickers or len(tickers) < 50:
            st.warning("Using fallback stock list")
            tickers = FALLBACK_STOCKS
    except Exception as e:
        st.warning(f"Using fallback stock list: {e}")
        tickers = FALLBACK_STOCKS

    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()

    total = len(tickers)

    for i, ticker in enumerate(tickers):
        if i % 10 == 0:
            status_text.text(f"Analyzing {ticker}... ({i}/{total} stocks)")
            progress_bar.progress(min(i / total, 1.0))

        try:
            # Download more data for technical analysis
            ticker_data = yf.download(ticker, period="1mo", interval="1d", progress=False)

            if ticker_data.empty or len(ticker_data) < 10:
                continue

            # Flatten columns if needed
            if isinstance(ticker_data.columns, pd.MultiIndex):
                ticker_data.columns = ticker_data.columns.get_level_values(0)

            # Add technical indicators
            try:
                ticker_data = add_indicators(ticker_data, cfg)
            except:
                # Basic indicators if add_indicators fails
                ticker_data['RSI'] = 50
                ticker_data['ADX'] = 20
                ticker_data['ATR%'] = 2

            if ticker_data.empty:
                continue

            latest = ticker_data.iloc[-1]

            # Basic metrics
            current = float(latest['Close'])
            prev = float(ticker_data['Close'].iloc[-2])
            change_pct = ((current - prev) / prev) * 100

            # Weekly change
            week_ago = float(ticker_data['Close'].iloc[-5]) if len(ticker_data) >= 5 else prev
            weekly_pct = ((current - week_ago) / week_ago) * 100

            # Volume
            volume = int(latest['Volume'])
            avg_volume = int(ticker_data['Volume'].tail(20).mean())
            vol_ratio = volume / avg_volume if avg_volume > 0 else 1

            # Technical indicators
            rsi = float(latest.get('RSI', 50))
            adx = float(latest.get('ADX', 20))
            atr_pct = float(latest.get('ATR%', 2))

            # Calculate score and signal
            score = calculate_signal_score(rsi, adx, change_pct, weekly_pct, vol_ratio)
            action = get_action_signal(score, rsi, change_pct, weekly_pct)

            # Calculate targets
            stop, tp1, tp2 = calculate_targets(current, atr_pct)

            # Prediction
            if score >= 7 and weekly_pct > 0:
                prediction = f"+{atr_pct * 1.5:.1f}%"
                outlook = 'BULLISH'
            elif score <= 4 or rsi > 70:
                prediction = f"-{atr_pct:.1f}%"
                outlook = 'BEARISH'
            else:
                prediction = f"±{atr_pct * 0.5:.1f}%"
                outlook = 'NEUTRAL'

            results.append({
                'Ticker': ticker,
                'Price': current,
                'Change%': round(change_pct, 2),
                'Weekly%': round(weekly_pct, 2),
                'Volume': volume,
                'Vol_Ratio': round(vol_ratio, 2),
                'RSI': round(rsi, 1),
                'ADX': round(adx, 1),
                'Score': score,
                'Action': action,
                'Prediction': prediction,
                'Outlook': outlook,
                'Stop': stop,
                'TP1': tp1,
                'TP2': tp2,
                'Status': 'UP' if change_pct > 0 else 'DOWN' if change_pct < 0 else 'FLAT'
            })

        except Exception:
            continue

    progress_bar.empty()
    status_text.empty()

    if not results:
        st.error("No stocks loaded. Check your internet connection.")
        return pd.DataFrame()

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
    ["Score (High to Low)", "Score (Low to High)",
     "Change% (High to Low)", "Change% (Low to High)",
     "Weekly% (High to Low)", "Weekly% (Low to High)",
     "Volume (High to Low)", "Price (High to Low)", "Price (Low to High)"]
)

# Action filter
action_filter = st.sidebar.multiselect(
    "Action Signal",
    ["BUY", "WATCH", "HOLD", "TAKE_PROFIT", "AVOID"],
    default=["BUY", "WATCH", "HOLD"]
)

# Status filter
status_filter = st.sidebar.multiselect(
    "Price Status",
    ["UP", "DOWN", "FLAT"],
    default=["UP", "DOWN", "FLAT"]
)

# Min score filter
min_score = st.sidebar.slider("Min Score", 1, 10, 1)

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

# Action filter
filtered_df = filtered_df[filtered_df['Action'].isin(action_filter)]

# Status filter
filtered_df = filtered_df[filtered_df['Status'].isin(status_filter)]

# Min score filter
filtered_df = filtered_df[filtered_df['Score'] >= min_score]

# Min change filter
filtered_df = filtered_df[filtered_df['Change%'].abs() >= min_change]

# Search filter
if search:
    filtered_df = filtered_df[filtered_df['Ticker'].str.contains(search)]

# Sort
sort_map = {
    "Score (High to Low)": ('Score', False),
    "Score (Low to High)": ('Score', True),
    "Change% (High to Low)": ('Change%', False),
    "Change% (Low to High)": ('Change%', True),
    "Weekly% (High to Low)": ('Weekly%', False),
    "Weekly% (Low to High)": ('Weekly%', True),
    "Volume (High to Low)": ('Volume', False),
    "Price (High to Low)": ('Price', False),
    "Price (Low to High)": ('Price', True)
}
sort_col, sort_asc = sort_map.get(sort_by, ('Score', False))
filtered_df = filtered_df.sort_values(sort_col, ascending=sort_asc)

# Limit display
display_df = filtered_df.head(num_stocks)

# ============================================================
# MARKET OVERVIEW
# ============================================================

st.markdown("---")
st.subheader("📈 Market Overview")

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    total_stocks = len(df)
    st.metric("Total Stocks", total_stocks)

with col2:
    buy_signals = len(df[df['Action'] == 'BUY'])
    st.metric("🟢 BUY Signals", buy_signals)

with col3:
    watch_signals = len(df[df['Action'] == 'WATCH'])
    st.metric("👀 WATCH", watch_signals)

with col4:
    gainers = len(df[df['Change%'] > 0])
    st.metric("📈 Gainers", gainers)

with col5:
    losers = len(df[df['Change%'] < 0])
    st.metric("📉 Losers", losers)

with col6:
    avg_score = df['Score'].mean()
    st.metric("Avg Score", f"{avg_score:.1f}/10")

# ============================================================
# TOP SIGNALS SUMMARY
# ============================================================

st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("🟢 Top BUY Signals")
    buy_stocks = df[df['Action'] == 'BUY'].nlargest(5, 'Score')
    if not buy_stocks.empty:
        for _, row in buy_stocks.iterrows():
            st.markdown(f"**{row['Ticker']}** Score: {row['Score']}/10")
            st.caption(f"${row['Price']:.2f} | Target: ${row['TP1']:.2f} | Stop: ${row['Stop']:.2f}")
    else:
        st.info("No BUY signals currently")

with col2:
    st.subheader("🚀 Top Gainers")
    top_gainers = df.nlargest(5, 'Change%')
    for _, row in top_gainers.iterrows():
        action_emoji = "🟢" if row['Action'] == 'BUY' else "👀" if row['Action'] == 'WATCH' else "⚪"
        st.markdown(f"{action_emoji} **{row['Ticker']}** `+{row['Change%']:.2f}%`")

with col3:
    st.subheader("📉 Top Losers")
    top_losers = df.nsmallest(5, 'Change%')
    for _, row in top_losers.iterrows():
        st.markdown(f"**{row['Ticker']}** ${row['Price']:.2f} `{row['Change%']:.2f}%`")

# ============================================================
# MAIN DATA TABLE
# ============================================================

st.markdown("---")
st.subheader(f"📋 All Stocks with Signals ({len(display_df)} shown)")

# Format display
table_df = display_df.copy()
table_df['Price'] = table_df['Price'].apply(lambda x: f"${x:.2f}")
table_df['Change%'] = table_df['Change%'].apply(lambda x: f"+{x:.2f}%" if x >= 0 else f"{x:.2f}%")
table_df['Weekly%'] = table_df['Weekly%'].apply(lambda x: f"+{x:.2f}%" if x >= 0 else f"{x:.2f}%")
table_df['Volume'] = table_df['Volume'].apply(lambda x: f"{x/1e6:.1f}M" if x >= 1e6 else f"{x/1e3:.0f}K")
table_df['Stop'] = table_df['Stop'].apply(lambda x: f"${x:.2f}")
table_df['TP1'] = table_df['TP1'].apply(lambda x: f"${x:.2f}")

# Add emoji for action
action_emoji = {
    'BUY': '🟢 BUY',
    'WATCH': '👀 WATCH',
    'HOLD': '⚪ HOLD',
    'TAKE_PROFIT': '💰 TP',
    'AVOID': '🔴 AVOID'
}
table_df['Signal'] = table_df['Action'].map(action_emoji)

# Score with visual
table_df['Score'] = table_df['Score'].apply(lambda x: f"{'⭐' * min(x//2, 5)} {x}/10")

# Reorder columns
table_df = table_df[['Ticker', 'Price', 'Change%', 'Score', 'Signal', 'Prediction', 'Stop', 'TP1', 'RSI']]

# Display table
st.dataframe(
    table_df,
    column_config={
        "Ticker": st.column_config.TextColumn("Symbol", width="small"),
        "Price": st.column_config.TextColumn("Price", width="small"),
        "Change%": st.column_config.TextColumn("Today", width="small"),
        "Score": st.column_config.TextColumn("Score", width="medium"),
        "Signal": st.column_config.TextColumn("Action", width="small"),
        "Prediction": st.column_config.TextColumn("Predict", width="small"),
        "Stop": st.column_config.TextColumn("Stop Loss", width="small"),
        "TP1": st.column_config.TextColumn("Target", width="small"),
        "RSI": st.column_config.NumberColumn("RSI", width="small", format="%.1f"),
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

        col1, col2, col3, col4 = st.columns(4)

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
            # Signal info
            action = stock_data['Action']
            action_colors = {'BUY': '🟢', 'WATCH': '👀', 'HOLD': '⚪', 'TAKE_PROFIT': '💰', 'AVOID': '🔴'}
            st.markdown(f"### {action_colors.get(action, '')} {action}")
            st.metric("Score", f"{stock_data['Score']}/10")
            st.metric("Prediction", stock_data['Prediction'])
            st.write(f"RSI: {stock_data['RSI']:.1f} | ADX: {stock_data['ADX']:.1f}")

        with col4:
            # Trade levels
            st.markdown("### 📊 Trade Levels")
            st.write(f"**Entry:** ${stock_data['Price']:.2f}")
            st.write(f"**Stop Loss:** ${stock_data['Stop']:.2f}")
            st.write(f"**Target 1:** ${stock_data['TP1']:.2f}")
            st.write(f"**Target 2:** ${stock_data['TP2']:.2f}")

            # Risk/Reward
            risk = stock_data['Price'] - stock_data['Stop']
            reward = stock_data['TP1'] - stock_data['Price']
            rr = reward / risk if risk > 0 else 0
            st.write(f"**R:R** = {rr:.2f}")

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
