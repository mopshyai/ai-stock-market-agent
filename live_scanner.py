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


def calculate_potential_moves(atr_pct: float, score: float, trend: str) -> Dict:
    """
    Calculate realistic potential move ranges for different timeframes
    Based on ATR (volatility), score, and trend

    Returns dict with:
        potential_up_1h_pct, potential_down_1h_pct
        potential_up_3h_pct, potential_down_3h_pct
        potential_up_1d_pct, potential_down_1d_pct
        potential_up_7d_pct, potential_down_7d_pct
    """
    import math

    # Base daily move from ATR
    daily_move_pct = atr_pct * 100  # Convert to percentage

    # Scale for different timeframes using √time rule
    move_1h = daily_move_pct * (1 / math.sqrt(24))
    move_3h = daily_move_pct * math.sqrt(3 / 24)
    move_1d = daily_move_pct
    move_7d = daily_move_pct * math.sqrt(7)

    # Normalize score to 0-1
    score_norm = max(0, min(score, 10)) / 10.0

    # Bias up/down based on trend and score
    if trend == "UP":
        up_factor = 1.0 + 0.5 * score_norm      # More upside if high score
        down_factor = 1.0 - 0.5 * score_norm    # Less downside if high score
    elif trend == "DOWN":
        up_factor = 1.0 - 0.5 * score_norm
        down_factor = 1.0 + 0.5 * score_norm
    else:  # CHOPPY
        up_factor = down_factor = 1.0

    return {
        'potential_up_1h_pct': round(move_1h * up_factor, 2),
        'potential_down_1h_pct': round(move_1h * down_factor, 2),
        'potential_up_3h_pct': round(move_3h * up_factor, 2),
        'potential_down_3h_pct': round(move_3h * down_factor, 2),
        'potential_up_1d_pct': round(move_1d * up_factor, 2),
        'potential_down_1d_pct': round(move_1d * down_factor, 2),
        'potential_up_7d_pct': round(move_7d * up_factor, 2),
        'potential_down_7d_pct': round(move_7d * down_factor, 2),
    }


def determine_action_and_timeframe(
    score: float,
    trend: str,
    rsi: float,
    signal_flags: Dict,
    potential_up_1d: float,
    potential_down_1d: float
) -> Dict:
    """
    Determine trading action and timeframe based on setup quality

    Returns:
        action: "BUY" | "WATCH" | "AVOID" | "TAKE_PROFIT" | "TRAIL_STOP"
        timeframe_label: "scalp" | "intraday" | "swing" | "position"
        action_reason: str (clear explanation)
    """
    # Calculate risk:reward ratio
    risk_reward = potential_up_1d / potential_down_1d if potential_down_1d > 0 else 0

    # BUY conditions (strong setups)
    if score >= 8 and trend == "UP" and risk_reward > 2.0:
        return {
            'action': 'BUY',
            'timeframe_label': 'swing',
            'action_reason': f'Strong setup: Score {score}/10, uptrend, R:R {risk_reward:.2f}'
        }

    # Intraday BUY (good but not perfect)
    if 6 <= score < 8 and trend == "UP" and risk_reward > 1.5:
        return {
            'action': 'BUY',
            'timeframe_label': 'intraday',
            'action_reason': f'Good intraday setup: Score {score}/10, R:R {risk_reward:.2f}'
        }

    # WATCH conditions (forming setups)
    if 5 <= score < 6 and trend in ["UP", "CHOPPY"]:
        return {
            'action': 'WATCH',
            'timeframe_label': 'intraday',
            'action_reason': f'Setup forming—wait for confirmation. Score {score}/10'
        }

    # TAKE_PROFIT (overbought conditions)
    if rsi > 75 and trend == "UP" and signal_flags.get('Breakout'):
        return {
            'action': 'TAKE_PROFIT',
            'timeframe_label': 'swing_exit',
            'action_reason': f'Overbought (RSI {rsi:.0f})—consider profit-taking'
        }

    # TRAIL_STOP (extended move)
    if rsi > 70 and trend == "UP" and score >= 7:
        return {
            'action': 'TRAIL_STOP',
            'timeframe_label': 'swing',
            'action_reason': f'Strong but extended—trail your stop'
        }

    # AVOID (weak/risky setups)
    if score < 5:
        return {
            'action': 'AVOID',
            'timeframe_label': 'none',
            'action_reason': f'Weak setup: Score {score}/10, low probability'
        }

    # Default: WATCH
    return {
        'action': 'WATCH',
        'timeframe_label': 'intraday',
        'action_reason': f'Neutral setup—monitor for now. Score {score}/10'
    }


def calculate_price_levels(
    close: float,
    potential_down_1d: float,
    potential_up_1d: float,
    action: str,
    timeframe_label: str
) -> Dict:
    """
    Calculate entry, stop-loss, and take-profit levels

    Returns:
        entry_price
        stop_loss_price
        take_profit_1
        take_profit_2
    """
    entry_price = close

    # For intraday, use tighter stops
    if 'intraday' in timeframe_label:
        risk_pct = potential_down_1d * 0.6  # Tighter
        reward_pct_1 = potential_up_1d * 0.4
        reward_pct_2 = potential_up_1d * 0.8
    # For swing, use wider stops
    elif 'swing' in timeframe_label:
        risk_pct = potential_down_1d * 0.8
        reward_pct_1 = potential_up_1d * 0.5
        reward_pct_2 = potential_up_1d * 1.0
    # For position, even wider
    elif 'position' in timeframe_label:
        risk_pct = potential_down_1d * 1.0
        reward_pct_1 = potential_up_1d * 0.6
        reward_pct_2 = potential_up_1d * 1.2
    else:  # Default
        risk_pct = potential_down_1d * 0.75
        reward_pct_1 = potential_up_1d * 0.5
        reward_pct_2 = potential_up_1d * 1.0

    stop_loss_price = round(close * (1 - risk_pct / 100.0), 2)
    take_profit_1 = round(close * (1 + reward_pct_1 / 100.0), 2)
    take_profit_2 = round(close * (1 + reward_pct_2 / 100.0), 2)

    return {
        'entry_price': entry_price,
        'stop_loss_price': stop_loss_price,
        'take_profit_1': take_profit_1,
        'take_profit_2': take_profit_2,
    }


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
        close = last["Close"]
        rsi = last["rsi"]
        atr_pct = last["atr_pct"]

        # Calculate potential moves for all timeframes
        potential_moves = calculate_potential_moves(atr_pct, technical_score, trend)

        # Determine action and timeframe
        action_info_enhanced = determine_action_and_timeframe(
            score=technical_score,
            trend=trend,
            rsi=rsi,
            signal_flags=signal_flags,
            potential_up_1d=potential_moves['potential_up_1d_pct'],
            potential_down_1d=potential_moves['potential_down_1d_pct']
        )

        # Calculate price levels
        price_levels = calculate_price_levels(
            close=close,
            potential_down_1d=potential_moves['potential_down_1d_pct'],
            potential_up_1d=potential_moves['potential_up_1d_pct'],
            action=action_info_enhanced['action'],
            timeframe_label=action_info_enhanced['timeframe_label']
        )

        # Build signals string
        signals_list = []
        if signal_flags.get('Consolidating'):
            signals_list.append('CONSOLIDATION')
        if signal_flags.get('BuyDip'):
            signals_list.append('BUY_DIP')
        if signal_flags.get('Breakout'):
            signals_list.append('BREAKOUT')
        if signal_flags.get('VolSpike'):
            signals_list.append('VOL_SPIKE')
        if signal_flags.get('VWAPReclaim'):
            signals_list.append('VWAP_RECLAIM')
        if signal_flags.get('EMABullish'):
            signals_list.append('EMA_STACK')
        if signal_flags.get('MACDBullish'):
            signals_list.append('MACD_BULL')

        signals_str = ' + '.join(signals_list) if signals_list else 'None'

        # Fundamentals (optional, slower)
        if include_fundamentals:
            try:
                fundamentals = fetch_fundamentals(ticker)
                fund_score = fundamentals.fundamental_score
                combined_score = min(technical_score + fund_score, 10)  # Cap at 10

                result = {
                    # Core identification
                    "Ticker": ticker,
                    "Close": round(close, 2),
                    "Score": combined_score,
                    "TechnicalScore": technical_score,
                    "FundamentalScore": fund_score,
                    "Trend": trend,
                    "Signals": signals_str,

                    # Action & Timeframe
                    "Action": action_info_enhanced['action'],
                    "TimeframeLabel": action_info_enhanced['timeframe_label'],
                    "ActionReason": action_info_enhanced['action_reason'],

                    # Price Levels
                    "EntryPrice": price_levels['entry_price'],
                    "StopLossPrice": price_levels['stop_loss_price'],
                    "TakeProfit1": price_levels['take_profit_1'],
                    "TakeProfit2": price_levels['take_profit_2'],

                    # Potential Moves
                    "PotentialUp1h": potential_moves['potential_up_1h_pct'],
                    "PotentialDown1h": potential_moves['potential_down_1h_pct'],
                    "PotentialUp3h": potential_moves['potential_up_3h_pct'],
                    "PotentialDown3h": potential_moves['potential_down_3h_pct'],
                    "PotentialUp1d": potential_moves['potential_up_1d_pct'],
                    "PotentialDown1d": potential_moves['potential_down_1d_pct'],
                    "PotentialUp7d": potential_moves['potential_up_7d_pct'],
                    "PotentialDown7d": potential_moves['potential_down_7d_pct'],

                    # Technical Indicators
                    "RSI": round(rsi, 2),
                    "ADX": round(last["adx"], 2),
                    "BBWidth_pct": round(last["bb_width"] * 100, 2),
                    "ATR%": round(atr_pct * 100, 2),
                    "ATRValue": round(last.get("atr_pct", 0) * close, 2),

                    # Fundamentals
                    "MarketCap": fundamentals.market_cap,
                    "PERatio": fundamentals.pe_ratio,
                    "RevenueGrowthPct": fundamentals.revenue_growth_pct,
                    "ProfitMarginPct": fundamentals.profit_margin_pct,
                    "FundamentalOutlook": fundamentals.outlook,
                    "FundamentalReasons": fundamentals.reasons,

                    # Signal Flags (boolean)
                    "VWAPReclaim": signal_flags.get('VWAPReclaim', False),
                    "Breakout": signal_flags.get('Breakout', False),
                    "Consolidating": signal_flags.get('Consolidating', False),
                }
            except Exception:
                # Fallback to technical only
                result = {
                    # Core identification
                    "Ticker": ticker,
                    "Close": round(close, 2),
                    "Score": technical_score,
                    "TechnicalScore": technical_score,
                    "FundamentalScore": 0,
                    "Trend": trend,
                    "Signals": signals_str,

                    # Action & Timeframe
                    "Action": action_info_enhanced['action'],
                    "TimeframeLabel": action_info_enhanced['timeframe_label'],
                    "ActionReason": action_info_enhanced['action_reason'],

                    # Price Levels
                    "EntryPrice": price_levels['entry_price'],
                    "StopLossPrice": price_levels['stop_loss_price'],
                    "TakeProfit1": price_levels['take_profit_1'],
                    "TakeProfit2": price_levels['take_profit_2'],

                    # Potential Moves
                    "PotentialUp1h": potential_moves['potential_up_1h_pct'],
                    "PotentialDown1h": potential_moves['potential_down_1h_pct'],
                    "PotentialUp3h": potential_moves['potential_up_3h_pct'],
                    "PotentialDown3h": potential_moves['potential_down_3h_pct'],
                    "PotentialUp1d": potential_moves['potential_up_1d_pct'],
                    "PotentialDown1d": potential_moves['potential_down_1d_pct'],
                    "PotentialUp7d": potential_moves['potential_up_7d_pct'],
                    "PotentialDown7d": potential_moves['potential_down_7d_pct'],

                    # Technical Indicators
                    "RSI": round(rsi, 2),
                    "ADX": round(last["adx"], 2),
                    "BBWidth_pct": round(last["bb_width"] * 100, 2),
                    "ATR%": round(atr_pct * 100, 2),
                    "ATRValue": round(atr_pct * close, 2),

                    # Fundamentals (N/A)
                    "MarketCap": None,
                    "PERatio": None,
                    "RevenueGrowthPct": None,
                    "ProfitMarginPct": None,
                    "FundamentalOutlook": "N/A",
                    "FundamentalReasons": "",

                    # Signal Flags
                    "VWAPReclaim": signal_flags.get('VWAPReclaim', False),
                    "Breakout": signal_flags.get('Breakout', False),
                    "Consolidating": signal_flags.get('Consolidating', False),
                }
        else:
            # Technical only (faster)
            result = {
                # Core identification
                "Ticker": ticker,
                "Close": round(close, 2),
                "Score": technical_score,
                "TechnicalScore": technical_score,
                "FundamentalScore": 0,
                "Trend": trend,
                "Signals": signals_str,

                # Action & Timeframe
                "Action": action_info_enhanced['action'],
                "TimeframeLabel": action_info_enhanced['timeframe_label'],
                "ActionReason": action_info_enhanced['action_reason'],

                # Price Levels
                "EntryPrice": price_levels['entry_price'],
                "StopLossPrice": price_levels['stop_loss_price'],
                "TakeProfit1": price_levels['take_profit_1'],
                "TakeProfit2": price_levels['take_profit_2'],

                # Potential Moves
                "PotentialUp1h": potential_moves['potential_up_1h_pct'],
                "PotentialDown1h": potential_moves['potential_down_1h_pct'],
                "PotentialUp3h": potential_moves['potential_up_3h_pct'],
                "PotentialDown3h": potential_moves['potential_down_3h_pct'],
                "PotentialUp1d": potential_moves['potential_up_1d_pct'],
                "PotentialDown1d": potential_moves['potential_down_1d_pct'],
                "PotentialUp7d": potential_moves['potential_up_7d_pct'],
                "PotentialDown7d": potential_moves['potential_down_7d_pct'],

                # Technical Indicators
                "RSI": round(rsi, 2),
                "ADX": round(last["adx"], 2),
                "BBWidth_pct": round(last["bb_width"] * 100, 2),
                "ATR%": round(atr_pct * 100, 2),
                "ATRValue": round(atr_pct * close, 2),

                # Fundamentals (N/A)
                "MarketCap": None,
                "PERatio": None,
                "RevenueGrowthPct": None,
                "ProfitMarginPct": None,
                "FundamentalOutlook": "N/A",
                "FundamentalReasons": "",

                # Signal Flags
                "VWAPReclaim": signal_flags.get('VWAPReclaim', False),
                "Breakout": signal_flags.get('Breakout', False),
                "Consolidating": signal_flags.get('Consolidating', False),
            }

        # Add remaining signal flags
        result['BuyDip'] = signal_flags.get('BuyDip', False)
        result['VolSpike'] = signal_flags.get('VolSpike', False)
        result['EMABullish'] = signal_flags.get('EMABullish', False)
        result['MACDBullish'] = signal_flags.get('MACDBullish', False)

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
