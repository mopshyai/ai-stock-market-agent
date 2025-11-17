#!/usr/bin/env python3
"""
TOP PERFORMERS SCANNER
Finds best performing stocks every hour and daily morning picks
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import yaml
from pathlib import Path
import sys

# Add indicators
from scan_and_chart import add_indicators, get_clean_prices
from database import get_db_connection, format_sql


# ============================================================
# STOCK UNIVERSES
# ============================================================

def get_sp500_tickers() -> List[str]:
    """Get S&P 500 stock tickers"""
    try:
        # Using Wikipedia table for S&P 500
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        tables = pd.read_html(url)
        sp500_table = tables[0]
        tickers = sp500_table['Symbol'].tolist()
        # Clean tickers (remove dots for proper yfinance format)
        tickers = [t.replace('.', '-') for t in tickers]
        return tickers
    except Exception as e:
        print(f"⚠️  Could not fetch S&P 500: {e}")
        return []


def get_nasdaq100_tickers() -> List[str]:
    """Get NASDAQ-100 stock tickers"""
    try:
        url = 'https://en.wikipedia.org/wiki/Nasdaq-100'
        tables = pd.read_html(url)
        nasdaq_table = tables[4]  # The main ticker table
        tickers = nasdaq_table['Ticker'].tolist()
        return tickers
    except Exception as e:
        print(f"⚠️  Could not fetch NASDAQ-100: {e}")
        return []


def get_top_volume_tickers(min_volume: int = 1_000_000) -> List[str]:
    """Get most actively traded stocks (high volume)"""
    # Common high-volume stocks (can be expanded with real-time data)
    popular_stocks = [
        # Mega Cap Tech
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA',

        # Large Cap Tech
        'NFLX', 'AMD', 'INTC', 'CRM', 'ORCL', 'ADBE', 'CSCO', 'AVGO',

        # Finance
        'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'BLK', 'SCHW',

        # Healthcare
        'UNH', 'JNJ', 'PFE', 'ABBV', 'LLY', 'TMO', 'MRK', 'ABT',

        # Consumer
        'WMT', 'HD', 'DIS', 'NKE', 'MCD', 'SBUX', 'TGT', 'COST',

        # Energy
        'XOM', 'CVX', 'COP', 'SLB', 'EOG', 'MPC',

        # Industrial
        'BA', 'CAT', 'GE', 'HON', 'UPS', 'RTX',

        # Volatility/Meme
        'SPY', 'QQQ', 'IWM', 'GME', 'AMC', 'PLTR', 'SOFI', 'RIVN',

        # EVs & Clean Energy
        'LCID', 'NIO', 'XPEV', 'F', 'GM', 'ENPH', 'SEDG',

        # Crypto-related
        'COIN', 'MARA', 'RIOT', 'MSTR',

        # Semiconductors
        'TSM', 'ASML', 'QCOM', 'TXN', 'AMAT', 'LRCX', 'MU',

        # Cloud/SaaS
        'SNOW', 'DDOG', 'NET', 'CRWD', 'ZS', 'OKTA', 'TEAM',
    ]
    return popular_stocks


def get_stock_universe(mode: str = 'popular') -> List[str]:
    """
    Get universe of stocks to scan

    Modes:
    - 'popular': ~150 high-volume stocks (fast)
    - 'sp500': S&P 500 stocks (~500 stocks)
    - 'nasdaq100': NASDAQ-100 stocks (~100 stocks)
    - 'all': S&P 500 + NASDAQ-100 combined
    """
    if mode == 'popular':
        return get_top_volume_tickers()
    elif mode == 'sp500':
        return get_sp500_tickers()
    elif mode == 'nasdaq100':
        return get_nasdaq100_tickers()
    elif mode == 'all':
        sp500 = get_sp500_tickers()
        nasdaq = get_nasdaq100_tickers()
        # Combine and deduplicate
        return list(set(sp500 + nasdaq))
    else:
        return get_top_volume_tickers()


# ============================================================
# HOURLY TOP MOVERS
# ============================================================

def scan_hourly_top_movers(top_n: int = 10, universe_mode: str = 'popular') -> pd.DataFrame:
    """
    Find top performing stocks in the last hour
    Returns stocks with highest % gain
    """
    print(f"\n{'='*60}")
    print(f"🔥 SCANNING HOURLY TOP MOVERS (Top {top_n})")
    print(f"{'='*60}\n")

    tickers = get_stock_universe(universe_mode)
    print(f"📊 Scanning {len(tickers)} stocks from '{universe_mode}' universe...\n")

    results = []

    for i, ticker in enumerate(tickers):
        try:
            # Get last 2 hours of data (1-minute bars)
            df = yf.download(ticker, period='1d', interval='1m', progress=False)

            if df.empty or len(df) < 60:
                continue

            # Calculate hourly performance
            current_price = df['Close'].iloc[-1]
            hour_ago_price = df['Close'].iloc[-60] if len(df) >= 60 else df['Close'].iloc[0]

            hourly_change_pct = ((current_price - hour_ago_price) / hour_ago_price) * 100

            # Get volume
            hourly_volume = df['Volume'].iloc[-60:].sum() if len(df) >= 60 else df['Volume'].sum()

            # Only include stocks with significant moves
            if abs(hourly_change_pct) >= 0.5:  # At least 0.5% move
                results.append({
                    'Ticker': ticker,
                    'Current_Price': current_price,
                    'Hourly_Change_%': round(hourly_change_pct, 2),
                    'Volume_1h': int(hourly_volume),
                    'Momentum': 'BULLISH' if hourly_change_pct > 0 else 'BEARISH'
                })

            # Progress indicator
            if (i + 1) % 20 == 0:
                print(f"✓ Scanned {i + 1}/{len(tickers)} stocks...")

        except Exception as e:
            continue

    if not results:
        print("⚠️  No significant movers found")
        return pd.DataFrame()

    # Convert to DataFrame and sort by absolute change
    df = pd.DataFrame(results)
    df['Abs_Change'] = df['Hourly_Change_%'].abs()
    df = df.sort_values('Abs_Change', ascending=False).head(top_n)
    df = df.drop('Abs_Change', axis=1)

    return df


# ============================================================
# MORNING DAILY PICKS
# ============================================================

def scan_morning_top_picks(top_n: int = 10, universe_mode: str = 'popular') -> pd.DataFrame:
    """
    Find top stock picks for the day based on:
    - Technical setup quality
    - Recent momentum
    - Volume
    - Volatility
    """
    print(f"\n{'='*60}")
    print(f"🌅 SCANNING MORNING TOP PICKS (Top {top_n})")
    print(f"{'='*60}\n")

    tickers = get_stock_universe(universe_mode)
    print(f"📊 Scanning {len(tickers)} stocks from '{universe_mode}' universe...\n")

    # Load config for indicators
    cfg = yaml.safe_load(open("config.yaml", "r"))

    results = []

    for i, ticker in enumerate(tickers):
        try:
            # Use daily data for more reliable results
            df = yf.download(ticker, period='3mo', interval='1d', progress=False)

            if df.empty or len(df) < 50:
                continue

            # Add indicators
            df = add_indicators(df, cfg)

            if df.empty:
                continue

            # Get latest values
            latest = df.iloc[-1]

            # Calculate scores
            rsi = latest['RSI']
            adx = latest['ADX']
            bb_width = latest['BBWidth_pct']
            atr_pct = latest['ATR%']

            # Calculate momentum (5-day change)
            if len(df) >= 5:
                momentum_pct = ((latest['Close'] - df['Close'].iloc[-5]) / df['Close'].iloc[-5]) * 100
            else:
                momentum_pct = 0

            # Volume spike
            avg_volume = df['Volume'].tail(20).mean()
            current_volume = latest['Volume']
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1

            # Technical setup score (0-10)
            tech_score = 0

            # RSI in buy zone (30-70)
            if 30 <= rsi <= 70:
                tech_score += 2

            # Strong trend (ADX > 15)
            if adx > 15:
                tech_score += 2

            # Consolidation (low BB width)
            if bb_width < 6:
                tech_score += 1

            # Volume spike
            if volume_ratio > 1.2:
                tech_score += 2

            # Positive momentum
            if momentum_pct > 0:
                tech_score += 2

            # Strong positive momentum
            if momentum_pct > 3:
                tech_score += 1

            # Projected potential (based on ATR and volatility)
            # Conservative estimate: 1x to 2x ATR for potential move
            potential_gain_pct = atr_pct * 1.5  # Conservative 1.5x ATR
            potential_loss_pct = atr_pct  # Stop at 1x ATR
            risk_reward = potential_gain_pct / potential_loss_pct if potential_loss_pct > 0 else 0

            # Only include stocks with decent setup (lowered threshold)
            if tech_score >= 3:
                results.append({
                    'Ticker': ticker,
                    'Score': tech_score,
                    'Current_Price': round(latest['Close'], 2),
                    'Potential_Gain_%': round(potential_gain_pct, 2),
                    'Risk_%': round(potential_loss_pct, 2),
                    'Risk_Reward': round(risk_reward, 2),
                    'RSI': round(rsi, 1),
                    'ADX': round(adx, 1),
                    'Momentum_5D_%': round(momentum_pct, 2),
                    'Volume_Ratio': round(volume_ratio, 2),
                    'Trend': latest.get('Trend', 'N/A')
                })

            # Progress indicator
            if (i + 1) % 20 == 0:
                print(f"✓ Scanned {i + 1}/{len(tickers)} stocks...")

        except Exception as e:
            continue

    if not results:
        print("⚠️  No quality setups found")
        return pd.DataFrame()

    # Convert to DataFrame and sort by score + potential
    df = pd.DataFrame(results)
    df['Combined_Score'] = df['Score'] + (df['Potential_Gain_%'] * 0.1)  # Weight potential
    df = df.sort_values('Combined_Score', ascending=False).head(top_n)
    df = df.drop('Combined_Score', axis=1)

    return df


# ============================================================
# SAVE & ALERT
# ============================================================

def save_top_performers(df: pd.DataFrame, scan_type: str):
    """Save top performers to CSV"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"top_performers_{scan_type}_{timestamp}.csv"
    df.to_csv(filename, index=False)
    print(f"\n✅ Saved to: {filename}")
    return filename


def display_results(df: pd.DataFrame, scan_type: str):
    """Display results in terminal"""
    if df.empty:
        print(f"\n⚠️  No {scan_type} found")
        return

    print(f"\n{'='*80}")
    print(f"📊 TOP {len(df)} {scan_type.upper()}")
    print(f"{'='*80}\n")
    print(df.to_string(index=False))
    print(f"\n{'='*80}\n")


# ============================================================
# MAIN EXECUTION
# ============================================================

def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description='Top Performers Scanner')
    parser.add_argument('--mode', type=str, default='morning',
                       choices=['hourly', 'morning', 'both'],
                       help='Scan mode: hourly movers, morning picks, or both')
    parser.add_argument('--top', type=int, default=10,
                       help='Number of top stocks to return')
    parser.add_argument('--universe', type=str, default='popular',
                       choices=['popular', 'sp500', 'nasdaq100', 'all'],
                       help='Stock universe to scan')

    args = parser.parse_args()

    print(f"\n🚀 TOP PERFORMERS SCANNER")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if args.mode in ['hourly', 'both']:
        # Hourly movers
        hourly_df = scan_hourly_top_movers(args.top, args.universe)
        display_results(hourly_df, 'hourly movers')
        if not hourly_df.empty:
            save_top_performers(hourly_df, 'hourly')

    if args.mode in ['morning', 'both']:
        # Morning picks
        morning_df = scan_morning_top_picks(args.top, args.universe)
        display_results(morning_df, 'morning picks')
        if not morning_df.empty:
            save_top_performers(morning_df, 'morning')


if __name__ == "__main__":
    main()
