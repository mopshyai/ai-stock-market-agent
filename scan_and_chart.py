
import os
import yaml
import numpy as np
import pandas as pd
from ta.trend import ADXIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import VolumeWeightedAveragePrice
import mplfinance as mpf
from utils import post_to_slack
from telegram_bot import send_telegram_alerts, is_telegram_configured
from database import init_database, store_scan_results
from market_data import fetch_price_history
from fundamentals import fetch_fundamentals, recommend_trade_action
from signals_engine import SIGNAL_DEFINITIONS, evaluate_signals

pd.options.mode.chained_assignment = None

def get_clean_prices(ticker, period, interval, data_cfg=None):
    data_cfg = data_cfg or {}
    provider = data_cfg.get("provider", "yfinance")
    df = fetch_price_history(ticker, period, interval, provider=provider, data_cfg=data_cfg)
    if df.empty:
        return df

    # Flatten multi-level columns if present
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Ensure we have the required columns
    required_cols = ["Open", "High", "Low", "Close", "Volume"]
    for col in required_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.dropna(subset=["Open", "High", "Low", "Close"], inplace=True)
    return df

def add_indicators(df, cfg):
    # Bollinger Bands
    bb = BollingerBands(close=df["Close"], window=cfg["indicators"]["bb_window"], window_dev=cfg["indicators"]["bb_dev"])
    df["bb_high"] = bb.bollinger_hband()
    df["bb_low"]  = bb.bollinger_lband()
    df["bb_width"] = (df["bb_high"] - df["bb_low"]) / df["Close"]

    # ATR
    atr = AverageTrueRange(high=df["High"], low=df["Low"], close=df["Close"], window=cfg["indicators"]["atr_window"])
    df["atr_pct"] = atr.average_true_range() / df["Close"]

    # ADX
    adx = ADXIndicator(high=df["High"], low=df["Low"], close=df["Close"], window=cfg["indicators"]["adx_window"])
    df["adx"] = adx.adx()

    # RSI
    rsi = RSIIndicator(close=df["Close"], window=cfg["indicators"]["rsi_window"])
    df["rsi"] = rsi.rsi()

    # EMAs for trend detection
    df["ema_20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["ema_50"] = df["Close"].ewm(span=50, adjust=False).mean()
    df["ema_200"] = df["Close"].ewm(span=200, adjust=False).mean()

    # Volume moving average for spike detection
    df["vol_ma_20"] = df["Volume"].rolling(window=20).mean()

    # MACD for momentum
    macd = MACD(close=df["Close"])
    df["macd"] = macd.macd()
    df["macd_signal"] = macd.macd_signal()
    df["macd_hist"] = macd.macd_diff()

    # VWAP
    vwap_window = cfg.get("signals", {}).get("vwap_reclaim", {}).get("lookback", 20)
    vwap = VolumeWeightedAveragePrice(
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        volume=df["Volume"],
        window=vwap_window
    )
    df["vwap"] = vwap.volume_weighted_average_price()

    return df

def trend_direction(df):
    """
    Classify trend based on EMA alignment
    Returns: "UP", "DOWN", or "CHOPPY"
    """
    last = df.iloc[-1]

    # Check if EMAs are valid
    if pd.isna(last["ema_20"]) or pd.isna(last["ema_50"]) or pd.isna(last["ema_200"]):
        return "CHOPPY"

    # Uptrend: EMA20 > EMA50 > EMA200
    if last["ema_20"] > last["ema_50"] > last["ema_200"]:
        return "UP"

    # Downtrend: EMA20 < EMA50 < EMA200
    if last["ema_20"] < last["ema_50"] < last["ema_200"]:
        return "DOWN"

    # Everything else is choppy
    return "CHOPPY"

def calculate_signal_score(signals: dict, trend: str) -> int:
    score = 0
    for definition in SIGNAL_DEFINITIONS:
        if signals.get(definition.key):
            score += definition.weight
    if trend == "UP":
        score += 1
    return score

def save_chart(df, ticker, outdir):
    """
    Save TradingView-style professional chart
    """
    os.makedirs(outdir, exist_ok=True)

    # TradingView-like market colors
    mc = mpf.make_marketcolors(
        up='#26a69a',        # bullish candle (teal/green)
        down='#ef5350',      # bearish candle (red)
        edge='inherit',
        wick='inherit',
        volume='in'
    )

    # Dark theme similar to TradingView
    style = mpf.make_mpf_style(
        base_mpf_style='nightclouds',
        marketcolors=mc,
        facecolor='#131722',     # chart background (TradingView dark)
        figcolor='#131722',      # outer background
        edgecolor='#2a2e39',
        gridcolor='#2a2e39',
        gridstyle=':',
        rc={
            'axes.labelcolor': '#d1d4dc',
            'xtick.color': '#787b86',
            'ytick.color': '#787b86',
            'axes.edgecolor': '#2a2e39',
        }
    )

    # Use last 150 candles for cleaner view
    df_plot = df.tail(150).copy()

    # Ensure proper datetime formatting for intraday
    if len(df_plot) > 0:
        datetime_format = '%b %d\n%H:%M' if '15m' in str(df_plot.index.freq) or len(df_plot) < 100 else '%b %d'
    else:
        datetime_format = '%b %d'

    mpf.plot(
        df_plot,
        type='candle',
        style=style,
        mav=(20, 50),          # moving averages
        volume=True,
        tight_layout=True,
        show_nontrading=False,
        datetime_format=datetime_format,
        ylabel='Price ($)',
        ylabel_lower='Volume',
        title=dict(title=f'{ticker}', color='#d1d4dc', size=14, weight='bold'),
        savefig=dict(fname=f"{outdir}/{ticker}.png", dpi=150, bbox_inches='tight'),
        scale_padding={'left': 0.05, 'top': 0.5, 'right': 0.95, 'bottom': 0.3}
    )

def main():
    # Initialize database on first run
    init_database()

    cfg = yaml.safe_load(open("config.yaml","r"))
    results = []

    # Get tickers to scan
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--all':
        # Scan ALL market stocks (S&P 500 + NASDAQ-100)
        print("🔥 SCANNING ALL MARKET STOCKS (~700 stocks)")
        print("⏰ This will take 20-30 minutes...\n")
        from top_performers_scanner import get_stock_universe
        tickers_to_scan = get_stock_universe('all')
    else:
        # Use configured tickers (default)
        tickers_to_scan = cfg["tickers"]

    print(f"📊 Total stocks to scan: {len(tickers_to_scan)}\n")

    for idx, t in enumerate(tickers_to_scan, 1):
        # Progress indicator
        if len(tickers_to_scan) > 50 and idx % 50 == 0:
            print(f"✓ Progress: {idx}/{len(tickers_to_scan)} stocks scanned ({idx*100//len(tickers_to_scan)}%)")

        try:
            df = get_clean_prices(t, cfg["data"]["period"], cfg["data"]["interval"], cfg.get("data"))
            if df.empty:
                if len(tickers_to_scan) <= 50:  # Only print for small scans
                    print(f"[NO DATA] {t}")
                continue

            df = add_indicators(df, cfg)

            # Detect all signals
            signal_flags = evaluate_signals(df, cfg)
            trend = trend_direction(df)

            # Technical score
            technical_score = calculate_signal_score(signal_flags, trend)

            # Fundamentals & combined view
            fundamentals = fetch_fundamentals(t)
            fund_score = fundamentals.fundamental_score
            action_info = recommend_trade_action(technical_score, fund_score, trend)
            combined_score = action_info["total_score"]

            last = df.iloc[-1]

            result_row = {
                "Ticker": t,
                "Score": combined_score,
                "TechnicalScore": technical_score,
                "FundamentalScore": fund_score,
                "Trend": trend,
                "BBWidth_pct": round(last["bb_width"]*100,2),
                "ATR%": round(last["atr_pct"]*100,2),
                "ADX": round(last["adx"],2),
                "RSI": round(last["rsi"],2),
                "Close": round(last["Close"],2),
                "MarketCap": fundamentals.market_cap,
                "PERatio": fundamentals.pe_ratio,
                "RevenueGrowthPct": fundamentals.revenue_growth_pct,
                "ProfitMarginPct": fundamentals.profit_margin_pct,
                "FundamentalOutlook": fundamentals.outlook,
                "FundamentalReasons": fundamentals.reasons,
                "Action": action_info["action"],
                "ActionReason": action_info["reason"],
            }

            result_row.update(signal_flags)

            results.append(result_row)

            # Only save charts for small scans (too slow for 700 stocks)
            if len(tickers_to_scan) <= 50:
                save_chart(df, t, cfg["output"]["charts_dir"])

        except Exception as e:
            if len(tickers_to_scan) <= 50:  # Only show errors for small scans
                print(f"[ERROR] {t}: {e}")

    df_out = pd.DataFrame(results)

    # Sort by signal score (highest first)
    df_out = df_out.sort_values(by="Score", ascending=False)

    df_out.to_csv(cfg["output"]["results_csv"], index=False)

    print("\n=== AI STOCK AGENT SCAN RESULTS ===")
    if len(df_out) > 50:
        # For large scans, show summary + top 50
        print(f"Total Stocks Scanned: {len(df_out)}")
        print(f"Showing Top 50 by Score:\n")
        print(df_out.head(50).to_string(index=False))
        print(f"\n... ({len(df_out) - 50} more stocks in CSV)")
    else:
        print(df_out.to_string(index=False))

    # Send Slack alert
    msg = "*AI Stock Agent Scan Complete*\n"
    for r in results[:10]:
        msg += f"{r['Ticker']}: CONS={r['Consolidating']} DIP={r['BuyDip']} RSI={r['RSI']}\n"
    post_to_slack(msg)

    # Send Telegram alerts if configured
    if is_telegram_configured(cfg):
        send_telegram_alerts(results, cfg, cfg["output"]["charts_dir"])
    else:
        print("[TELEGRAM] Skipping alerts (set TELEGRAM_BOT_TOKEN/CHAT_ID or update config to enable)")

    # Store results in database
    scan_id = store_scan_results(results)
    print(f"\n📊 Scan #{scan_id} stored in database")

if __name__ == "__main__":
    main()
