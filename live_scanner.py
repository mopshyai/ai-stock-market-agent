#!/usr/bin/env python3
"""
LIVE MARKET SCANNER
Scans stock universe in-memory without CSV files
Used by Streamlit dashboard for real-time data
"""

import pandas as pd
import numpy as np
from typing import Literal, Optional, List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import yaml

# Import existing modules
from top_performers_scanner import get_stock_universe
from scan_and_chart import get_clean_prices, add_indicators, trend_direction
from signals_engine import evaluate_signals
from fundamentals import fetch_fundamentals, recommend_trade_action

UniverseType = Literal["popular", "sp500", "nasdaq100", "all"]


def calculate_signal_score(signal_flags: Dict, trend: str) -> int:
    """
    Calculate technical score based on signals
    Replicates logic from scan_and_chart.py
    """
    score = 0

    # Core signals (2 points each)
    if signal_flags.get('Consolidating'):
        score += 2
    if signal_flags.get('BuyDip'):
        score += 2
    if signal_flags.get('Breakout'):
        score += 2
    if signal_flags.get('VolSpike'):
        score += 2

    # Additional signals (1 point each)
    if signal_flags.get('EMABullish'):
        score += 1
    if signal_flags.get('MACDBullish'):
        score += 1
    if signal_flags.get('VWAPReclaim'):
        score += 1

    # Trend bonus
    if trend == "UP":
        score += 1

    return score


def scan_single_ticker(ticker: str, cfg: dict, include_fundamentals: bool = True) -> Optional[Dict]:
    """
    Scan a single ticker and return result dict
    Returns None if scan fails
    """
    try:
        # Fetch price data
        df = get_clean_prices(
            ticker,
            cfg["data"]["period"],
            cfg["data"]["interval"],
            cfg.get("data")
        )

        if df.empty or len(df) < 50:
            return None

        # Add indicators
        df = add_indicators(df, cfg)

        if df.empty:
            return None

        # Evaluate signals
        signal_flags = evaluate_signals(df, cfg)
        trend = trend_direction(df)

        # Technical score
        technical_score = calculate_signal_score(signal_flags, trend)

        # Get latest values
        last = df.iloc[-1]

        # Fundamentals (optional, slower)
        if include_fundamentals:
            try:
                fundamentals = fetch_fundamentals(ticker)
                fund_score = fundamentals.fundamental_score
                action_info = recommend_trade_action(technical_score, fund_score, trend)
                combined_score = action_info["total_score"]

                result = {
                    "Ticker": ticker,
                    "Score": combined_score,
                    "TechnicalScore": technical_score,
                    "FundamentalScore": fund_score,
                    "Trend": trend,
                    "BBWidth_pct": round(last["bb_width"] * 100, 2),
                    "ATR%": round(last["atr_pct"] * 100, 2),
                    "ADX": round(last["adx"], 2),
                    "RSI": round(last["rsi"], 2),
                    "Close": round(last["Close"], 2),
                    "MarketCap": fundamentals.market_cap,
                    "PERatio": fundamentals.pe_ratio,
                    "RevenueGrowthPct": fundamentals.revenue_growth_pct,
                    "ProfitMarginPct": fundamentals.profit_margin_pct,
                    "FundamentalOutlook": fundamentals.outlook,
                    "FundamentalReasons": fundamentals.reasons,
                    "Action": action_info["action"],
                    "ActionReason": action_info["reason"],
                }
            except Exception:
                # Fallback to technical only
                result = {
                    "Ticker": ticker,
                    "Score": technical_score,
                    "TechnicalScore": technical_score,
                    "FundamentalScore": 0,
                    "Trend": trend,
                    "BBWidth_pct": round(last["bb_width"] * 100, 2),
                    "ATR%": round(last["atr_pct"] * 100, 2),
                    "ADX": round(last["adx"], 2),
                    "RSI": round(last["rsi"], 2),
                    "Close": round(last["Close"], 2),
                    "MarketCap": None,
                    "PERatio": None,
                    "RevenueGrowthPct": None,
                    "ProfitMarginPct": None,
                    "FundamentalOutlook": "N/A",
                    "FundamentalReasons": "",
                    "Action": "WATCH",
                    "ActionReason": "Technical analysis only",
                }
        else:
            # Technical only (faster)
            result = {
                "Ticker": ticker,
                "Score": technical_score,
                "TechnicalScore": technical_score,
                "FundamentalScore": 0,
                "Trend": trend,
                "BBWidth_pct": round(last["bb_width"] * 100, 2),
                "ATR%": round(last["atr_pct"] * 100, 2),
                "ADX": round(last["adx"], 2),
                "RSI": round(last["rsi"], 2),
                "Close": round(last["Close"], 2),
                "MarketCap": None,
                "PERatio": None,
                "RevenueGrowthPct": None,
                "ProfitMarginPct": None,
                "FundamentalOutlook": "N/A",
                "FundamentalReasons": "",
                "Action": "WATCH",
                "ActionReason": "Technical analysis only",
            }

        # Add signal flags
        result.update(signal_flags)

        return result

    except Exception as e:
        # Silent fail for individual tickers
        return None


def scan_market_live(
    universe: UniverseType = "all",
    min_score: Optional[float] = None,
    limit: Optional[int] = None,
    max_workers: int = 20,
    include_fundamentals: bool = False,  # Disabled by default for speed
    progress_callback = None,
) -> pd.DataFrame:
    """
    Scan the requested stock universe live (no CSV) and return a DataFrame
    with all signals, scores and metrics required by the dashboard.

    Args:
        universe: Stock universe to scan ('popular', 'sp500', 'nasdaq100', 'all')
        min_score: Minimum score filter (None = no filter)
        limit: Max number of results to return (None = all)
        max_workers: Number of parallel workers for scanning
        include_fundamentals: Whether to fetch fundamental data (slower)
        progress_callback: Optional callback function(current, total) for progress updates

    Returns:
        DataFrame with columns:
        - Ticker, Score, TechnicalScore, FundamentalScore
        - Trend, BBWidth_pct, ATR%, ADX, RSI, Close
        - MarketCap, PERatio, RevenueGrowthPct, ProfitMarginPct
        - FundamentalOutlook, FundamentalReasons
        - Action, ActionReason
        - Consolidating, BuyDip, Breakout, VolSpike
        - EMABullish, MACDBullish, VWAPReclaim
    """
    # Load config
    try:
        cfg = yaml.safe_load(open("config.yaml", "r"))
    except Exception as e:
        raise RuntimeError(f"Failed to load config.yaml: {e}")

    # Get tickers for universe
    tickers = get_stock_universe(universe)
    total_tickers = len(tickers)

    if total_tickers == 0:
        return pd.DataFrame()

    # Scan tickers in parallel
    results = []
    completed = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_ticker = {
            executor.submit(scan_single_ticker, ticker, cfg, include_fundamentals): ticker
            for ticker in tickers
        }

        # Process completed tasks
        for future in as_completed(future_to_ticker):
            completed += 1

            # Progress callback
            if progress_callback:
                progress_callback(completed, total_tickers)

            result = future.result()
            if result is not None:
                results.append(result)

    # Convert to DataFrame
    if not results:
        return pd.DataFrame()

    df = pd.DataFrame(results)

    # Apply minimum score filter
    if min_score is not None:
        df = df[df["Score"] >= min_score]

    # Sort by score (descending)
    df = df.sort_values("Score", ascending=False)

    # Apply limit
    if limit is not None:
        df = df.head(limit)

    # Reset index
    df = df.reset_index(drop=True)

    return df


def scan_market_live_with_status(
    universe: UniverseType = "all",
    min_score: Optional[float] = None,
    limit: Optional[int] = None,
    max_workers: int = 20,
    include_fundamentals: bool = False,
):
    """
    Wrapper around scan_market_live that yields progress updates

    Yields:
        - ('progress', current, total) during scanning
        - ('complete', df) when done
    """
    # Load config
    cfg = yaml.safe_load(open("config.yaml", "r"))
    tickers = get_stock_universe(universe)
    total_tickers = len(tickers)

    if total_tickers == 0:
        yield ('complete', pd.DataFrame())
        return

    results = []
    completed = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_ticker = {
            executor.submit(scan_single_ticker, ticker, cfg, include_fundamentals): ticker
            for ticker in tickers
        }

        for future in as_completed(future_to_ticker):
            completed += 1

            # Yield progress
            yield ('progress', completed, total_tickers)

            result = future.result()
            if result is not None:
                results.append(result)

    # Build DataFrame
    if not results:
        yield ('complete', pd.DataFrame())
        return

    df = pd.DataFrame(results)

    if min_score is not None:
        df = df[df["Score"] >= min_score]

    df = df.sort_values("Score", ascending=False)

    if limit is not None:
        df = df.head(limit)

    df = df.reset_index(drop=True)

    yield ('complete', df)


# Test function
if __name__ == "__main__":
    print("🚀 Testing Live Scanner\n")

    # Test with popular universe (fast)
    print("Testing 'popular' universe...")
    df = scan_market_live(
        universe="popular",
        min_score=3,
        limit=20,
        max_workers=20,
        include_fundamentals=False,
    )

    print(f"\n✅ Scanned {len(df)} stocks")
    print(f"Columns: {list(df.columns)}")
    print("\nTop 10 Results:")
    print(df[['Ticker', 'Score', 'Trend', 'RSI', 'ADX', 'Close']].head(10))
