"""
Streamlit page that mirrors the Market AI Signals “Members Only” board with
live TradingView embeds (40 intraday charts) plus supporting info.
Run locally with: `streamlit run live_market_board.py`
"""

import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(
    page_title="Live Market Board",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    body, .stApp {
        background: radial-gradient(140% 140% at 50% 20%, #0b1c5a 0%, #0b0c12 40%, #0b0c12 100%) !important;
        color: #f5f5f5;
    }
    .page-shell {
        max-width: 1200px;
        margin: auto;
        background: rgba(12, 13, 22, 0.92);
        border: 1px solid #1f2538;
        border-radius: 16px;
        padding: 28px 24px 32px 24px;
        box-shadow: 0 16px 48px rgba(0,0,0,0.45);
    }
    .nav-buttons a {
        background: #0a0a0f;
        border: 1px solid #1f2538;
        padding: 10px 14px;
        border-radius: 10px;
        color: #dce5ff;
        font-size: 13px;
        text-decoration: none;
        margin-right: 8px;
        display: inline-block;
    }
    .hero-title {
        text-align: center;
        font-size: 34px;
        font-weight: 700;
        margin-bottom: 4px;
        color: #e9f0ff;
        letter-spacing: 0.02em;
    }
    .hero-sub {
        text-align: center;
        color: #c2c8d7;
        margin-bottom: 24px;
        font-size: 14px;
    }
    .section-text {
        color: #b2b8c7;
        font-size: 13px;
        line-height: 1.5;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def embed_tv_chart(symbol: str, height: int = 230, interval: str = "60"):
    """Embed a single TradingView advanced chart via iframe."""
    iframe = f"""
    <iframe
        title="TradingView Chart"
        allowtransparency="true"
        frameborder="0"
        scrolling="no"
        allowfullscreen="true"
        style="box-sizing:border-box;width:100%;height:{height}px;margin:0;padding:0;"
        src="https://s.tradingview.com/widgetembed/?hideideas=1&theme=dark&style=1&timezone=Etc%2FUTC&symbol={symbol}&interval={interval}&utm_source=stockgenie.local&utm_medium=widget&utm_campaign=chart">
    </iframe>
    """
    components.html(iframe, height=height + 8)


def embed_tv_iframe(src: str, height: int):
    """Render a TradingView widget iframe."""
    components.html(
        f'<iframe src="{src}" style="width:100%;height:{height}px;border:1px solid #1f2538;'
        f'border-radius:12px;" frameborder="0" allowtransparency="true" scrolling="no"></iframe>',
        height=height + 8,
    )


# --- Page shell --------------------------------------------------------------
with st.container():
    st.markdown('<div class="page-shell">', unsafe_allow_html=True)

    # Faux nav row
    st.markdown(
        """
        <div class="nav-buttons">
            <a href="#ai-signals">AI SIGNALS</a>
            <a href="#intraday">Intraday Trading</a>
            <a href="#market-news">Market News</a>
            <a href="#market-watch">Market Watch</a>
            <a href="#watchlist">Watchlist</a>
            <a href="#crypto">Crypto</a>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div id="intraday"></div>', unsafe_allow_html=True)
    st.markdown('<p class="hero-title">📉 Intraday AI Dip Buy – Live Charts (Top 40 Blue-Chip Stocks)</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="hero-sub">1H intraday charts, auto-updated from TradingView. Optimized for our AI Dip Buy signal.</p>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <p class="section-text">
        These live charts are optimized for intraday trading using the <strong>AI Dip Buy Signal</strong>
        on the <strong>1H timeframe</strong>. Each chart updates in real time directly from TradingView.
        <br><br>
        ⚠️ <strong>Educational Only – Not Financial Advice.</strong>
        Always use stop-losses and risk a small percentage of your account per trade.
        </p>
        """,
        unsafe_allow_html=True,
    )

    # Symbol universe (40)
    symbols = [
        "NASDAQ:AAPL", "NASDAQ:MSFT", "NASDAQ:NVDA", "NASDAQ:GOOGL", "NASDAQ:META",
        "NASDAQ:AMZN", "NASDAQ:TSLA", "NASDAQ:NFLX", "NASDAQ:AMD", "NASDAQ:AVGO",
        "NYSE:JPM", "NYSE:BAC", "NYSE:WFC", "NYSE:GS", "NYSE:MS",
        "NYSE:XOM", "NYSE:CVX", "NYSE:COP", "NYSE:OXY", "NASDAQ:CMCSA",
        "NYSE:VZ", "NYSE:T", "NASDAQ:PEP", "NYSE:KO", "NYSE:PG",
        "NYSE:MCD", "NASDAQ:COST", "NYSE:WMT", "NYSE:CAT", "NYSE:DE",
        "NYSE:LMT", "NYSE:BA", "NYSE:GE", "NASDAQ:PYPL", "NYSE:V",
        "NYSE:MA", "NASDAQ:NKE", "NASDAQ:QCOM", "NASDAQ:INTC", "NYSE:IBM",
    ]

    cols = st.columns(2)
    for idx, sym in enumerate(symbols):
        with cols[idx % 2]:
            st.markdown(f"**{sym}**")
            embed_tv_chart(sym)

    st.markdown(
        """
        <p class="section-text" style="margin-top:18px;">
        💡 Tip: Swap symbols to your preferred watchlist or feed the list from a backend API
        based on your latest AI signals or scanner outputs.
        </p>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <p class="section-text" style="margin-top:12px;">
        ⚠️ DISCLAIMER: Educational use only. Real-time data provided by TradingView embeds.
        Always perform your own research and manage risk when trading.
        </p>
        """,
        unsafe_allow_html=True,
    )

    # --- Market Movers (Hotlists) -------------------------------------------
    st.markdown('<div id="market-watch"></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🚦 Market Movers – Winners & Losers")
    st.markdown(
        """
        <p class="section-text">
        Live top gainers, losers and most active U.S. stocks — perfect for daily scalps.
        Data via TradingView hotlists (1D).
        </p>
        """,
        unsafe_allow_html=True,
    )

    hotlists_src = (
        "https://www.tradingview-widget.com/embed-widget/hotlists/"
        "#%7B%22colorTheme%22%3A%22dark%22%2C%22dateRange%22%3A%221D%22%2C%22exchange%22%3A%22US%22%2C"
        "%22showChart%22%3Afalse%2C%22showSymbolLogo%22%3Atrue%2C%22showFloatingTooltip%22%3Atrue%2C"
        "%22width%22%3A%22100%25%22%2C%22height%22%3A520%7D"
    )
    embed_tv_iframe(hotlists_src, height=520)

    st.markdown('</div>', unsafe_allow_html=True)
