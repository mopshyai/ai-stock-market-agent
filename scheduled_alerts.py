#!/usr/bin/env python3
"""
SCHEDULED TELEGRAM ALERTS
Sends hourly tips, 3-hour predictions, and weekly predictions
Scans ALL US stocks (S&P 500 + NASDAQ-100)
"""

import os
import time
import schedule
import yaml
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Dict

# Import existing modules
from top_performers_scanner import get_stock_universe, add_indicators
from scan_and_chart import add_indicators
from telegram_bot import TelegramBot

# ============================================================
# TELEGRAM SETUP
# ============================================================

def get_bot():
    """Get Telegram bot instance"""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        print("TELEGRAM credentials not configured")
        return None

    return TelegramBot(bot_token, chat_id)


# ============================================================
# HOURLY TIPS (Every Hour)
# ============================================================

def scan_hourly_tips(top_n: int = 10) -> pd.DataFrame:
    """
    Scan ALL US stocks and find top hourly movers
    """
    print(f"\n[{datetime.now().strftime('%H:%M')}] Scanning hourly tips...")

    # Get ALL stocks (S&P 500 + NASDAQ-100)
    tickers = get_stock_universe('all')
    print(f"Scanning {len(tickers)} stocks...")

    results = []

    for ticker in tickers:
        try:
            # Get intraday data
            df = yf.download(ticker, period='1d', interval='5m', progress=False)

            if df.empty or len(df) < 12:  # Need at least 1 hour of 5min data
                continue

            current_price = df['Close'].iloc[-1]
            hour_ago_price = df['Close'].iloc[-12] if len(df) >= 12 else df['Close'].iloc[0]

            hourly_change = ((current_price - hour_ago_price) / hour_ago_price) * 100
            volume = df['Volume'].iloc[-12:].sum()

            # Only significant moves (>0.5%)
            if abs(hourly_change) >= 0.5:
                results.append({
                    'Ticker': ticker,
                    'Price': round(float(current_price), 2),
                    'Change': round(float(hourly_change), 2),
                    'Volume': int(volume),
                    'Direction': 'UP' if hourly_change > 0 else 'DOWN'
                })

        except Exception:
            continue

    if not results:
        return pd.DataFrame()

    df = pd.DataFrame(results)
    df['AbsChange'] = df['Change'].abs()
    df = df.sort_values('AbsChange', ascending=False).head(top_n)
    return df.drop('AbsChange', axis=1)


def format_hourly_tips(df: pd.DataFrame) -> str:
    """Format hourly tips for Telegram"""
    if df.empty:
        return None

    msg = f"*HOURLY STOCK TIPS*\n"
    msg += f"{datetime.now().strftime('%I:%M %p ET')}\n\n"

    gainers = df[df['Change'] > 0].head(5)
    losers = df[df['Change'] < 0].head(5)

    if not gainers.empty:
        msg += "*TOP GAINERS*\n"
        for _, row in gainers.iterrows():
            msg += f"  *{row['Ticker']}* ${row['Price']} (+{row['Change']}%)\n"
        msg += "\n"

    if not losers.empty:
        msg += "*TOP LOSERS*\n"
        for _, row in losers.iterrows():
            msg += f"  *{row['Ticker']}* ${row['Price']} ({row['Change']}%)\n"
        msg += "\n"

    msg += "_Not financial advice. DYOR._"
    return msg


def send_hourly_tips():
    """Send hourly tips to Telegram"""
    print(f"\n{'='*50}")
    print(f"HOURLY TIPS - {datetime.now().strftime('%I:%M %p')}")
    print(f"{'='*50}")

    bot = get_bot()
    if not bot:
        return

    df = scan_hourly_tips(top_n=10)
    msg = format_hourly_tips(df)

    if msg:
        bot.send_message(msg)
        print("Hourly tips sent!")
    else:
        print("No significant movers this hour")


# ============================================================
# 3-HOUR PREDICTIONS
# ============================================================

def scan_3hour_predictions(top_n: int = 10) -> pd.DataFrame:
    """
    Scan stocks and predict next 3-hour movement
    Based on momentum, volatility, and technical setup
    """
    print(f"\n[{datetime.now().strftime('%H:%M')}] Scanning 3-hour predictions...")

    tickers = get_stock_universe('all')
    cfg = yaml.safe_load(open("config.yaml", "r"))

    results = []

    for ticker in tickers:
        try:
            # Get recent data
            df = yf.download(ticker, period='5d', interval='15m', progress=False)

            if df.empty or len(df) < 50:
                continue

            # Add indicators
            df = add_indicators(df, cfg)

            if df.empty:
                continue

            latest = df.iloc[-1]

            # Current metrics
            price = float(latest['Close'])
            rsi = float(latest['RSI'])
            adx = float(latest['ADX'])
            atr_pct = float(latest['ATR%'])

            # Calculate momentum (last 3 hours = 12 candles of 15min)
            if len(df) >= 12:
                momentum_3h = ((price - float(df['Close'].iloc[-12])) / float(df['Close'].iloc[-12])) * 100
            else:
                momentum_3h = 0

            # Prediction logic
            predicted_move = 0
            confidence = 50

            # Momentum continuation
            if momentum_3h > 1:
                predicted_move += atr_pct * 0.5
                confidence += 10
            elif momentum_3h < -1:
                predicted_move -= atr_pct * 0.5
                confidence += 10

            # RSI signals
            if rsi < 30:  # Oversold - likely bounce
                predicted_move += atr_pct * 0.8
                confidence += 15
            elif rsi > 70:  # Overbought - likely pullback
                predicted_move -= atr_pct * 0.8
                confidence += 15

            # Strong trend
            if adx > 25:
                confidence += 10
                if momentum_3h > 0:
                    predicted_move += atr_pct * 0.3
                else:
                    predicted_move -= atr_pct * 0.3

            # Cap confidence
            confidence = min(confidence, 85)

            if abs(predicted_move) >= 0.3:  # Only significant predictions
                results.append({
                    'Ticker': ticker,
                    'Price': round(price, 2),
                    'Predicted_Move': round(predicted_move, 2),
                    'Target': round(price * (1 + predicted_move/100), 2),
                    'Confidence': confidence,
                    'RSI': round(rsi, 1),
                    'Momentum_3h': round(momentum_3h, 2),
                    'Direction': 'BULLISH' if predicted_move > 0 else 'BEARISH'
                })

        except Exception:
            continue

    if not results:
        return pd.DataFrame()

    df = pd.DataFrame(results)
    df['Score'] = df['Predicted_Move'].abs() * (df['Confidence'] / 100)
    df = df.sort_values('Score', ascending=False).head(top_n)
    return df.drop('Score', axis=1)


def format_3hour_predictions(df: pd.DataFrame) -> str:
    """Format 3-hour predictions for Telegram"""
    if df.empty:
        return None

    msg = f"*3-HOUR PREDICTIONS*\n"
    msg += f"{datetime.now().strftime('%I:%M %p ET')}\n\n"

    bullish = df[df['Direction'] == 'BULLISH'].head(5)
    bearish = df[df['Direction'] == 'BEARISH'].head(5)

    if not bullish.empty:
        msg += "*BULLISH SETUPS*\n"
        for _, row in bullish.iterrows():
            msg += f"  *{row['Ticker']}* ${row['Price']}\n"
            msg += f"    Target: ${row['Target']} (+{row['Predicted_Move']}%)\n"
            msg += f"    Confidence: {row['Confidence']}%\n\n"

    if not bearish.empty:
        msg += "*BEARISH SETUPS*\n"
        for _, row in bearish.iterrows():
            msg += f"  *{row['Ticker']}* ${row['Price']}\n"
            msg += f"    Target: ${row['Target']} ({row['Predicted_Move']}%)\n"
            msg += f"    Confidence: {row['Confidence']}%\n\n"

    msg += "_Predictions based on technical analysis. Not financial advice._"
    return msg


def send_3hour_predictions():
    """Send 3-hour predictions to Telegram"""
    print(f"\n{'='*50}")
    print(f"3-HOUR PREDICTIONS - {datetime.now().strftime('%I:%M %p')}")
    print(f"{'='*50}")

    bot = get_bot()
    if not bot:
        return

    df = scan_3hour_predictions(top_n=10)
    msg = format_3hour_predictions(df)

    if msg:
        bot.send_message(msg)
        print("3-hour predictions sent!")
    else:
        print("No strong predictions found")


# ============================================================
# WEEKLY PREDICTIONS
# ============================================================

def scan_weekly_predictions(top_n: int = 15) -> pd.DataFrame:
    """
    Scan stocks for weekly outlook
    Based on trend, fundamentals, and technical setup
    """
    print(f"\n[{datetime.now().strftime('%H:%M')}] Scanning weekly predictions...")

    tickers = get_stock_universe('all')
    cfg = yaml.safe_load(open("config.yaml", "r"))

    results = []

    for ticker in tickers:
        try:
            # Get daily data for weekly analysis
            df = yf.download(ticker, period='3mo', interval='1d', progress=False)

            if df.empty or len(df) < 30:
                continue

            # Add indicators
            df = add_indicators(df, cfg)

            if df.empty:
                continue

            latest = df.iloc[-1]

            # Current metrics
            price = float(latest['Close'])
            rsi = float(latest['RSI'])
            adx = float(latest['ADX'])
            atr_pct = float(latest['ATR%'])

            # Weekly momentum
            week_ago = df['Close'].iloc[-5] if len(df) >= 5 else df['Close'].iloc[0]
            weekly_momentum = ((price - float(week_ago)) / float(week_ago)) * 100

            # Monthly momentum
            month_ago = df['Close'].iloc[-20] if len(df) >= 20 else df['Close'].iloc[0]
            monthly_momentum = ((price - float(month_ago)) / float(month_ago)) * 100

            # Trend determination
            ema20 = df['Close'].ewm(span=20).mean().iloc[-1]
            ema50 = df['Close'].ewm(span=50).mean().iloc[-1] if len(df) >= 50 else ema20

            trend = "NEUTRAL"
            if price > ema20 > ema50:
                trend = "UPTREND"
            elif price < ema20 < ema50:
                trend = "DOWNTREND"

            # Weekly prediction
            predicted_weekly_move = 0
            confidence = 50

            # Trend following
            if trend == "UPTREND":
                predicted_weekly_move += atr_pct * 2
                confidence += 15
            elif trend == "DOWNTREND":
                predicted_weekly_move -= atr_pct * 2
                confidence += 15

            # Momentum
            if weekly_momentum > 3:
                predicted_weekly_move += atr_pct * 1.5
                confidence += 10
            elif weekly_momentum < -3:
                predicted_weekly_move -= atr_pct * 1.5
                confidence += 10

            # Strong trend
            if adx > 25:
                confidence += 10

            # RSI extremes (potential reversals)
            if rsi < 25:
                predicted_weekly_move += atr_pct * 2
                confidence += 10
            elif rsi > 75:
                predicted_weekly_move -= atr_pct * 2
                confidence += 10

            confidence = min(confidence, 85)

            if abs(predicted_weekly_move) >= 1:
                results.append({
                    'Ticker': ticker,
                    'Price': round(price, 2),
                    'Weekly_Target': round(price * (1 + predicted_weekly_move/100), 2),
                    'Predicted_%': round(predicted_weekly_move, 2),
                    'Confidence': confidence,
                    'Trend': trend,
                    'Weekly_Mom': round(weekly_momentum, 2),
                    'Monthly_Mom': round(monthly_momentum, 2),
                    'RSI': round(rsi, 1),
                    'Outlook': 'BULLISH' if predicted_weekly_move > 0 else 'BEARISH'
                })

        except Exception:
            continue

    if not results:
        return pd.DataFrame()

    df = pd.DataFrame(results)
    df['Score'] = df['Predicted_%'].abs() * (df['Confidence'] / 100)
    df = df.sort_values('Score', ascending=False).head(top_n)
    return df.drop('Score', axis=1)


def format_weekly_predictions(df: pd.DataFrame) -> str:
    """Format weekly predictions for Telegram"""
    if df.empty:
        return None

    msg = f"*WEEKLY STOCK PREDICTIONS*\n"
    msg += f"Week of {datetime.now().strftime('%B %d, %Y')}\n\n"

    bullish = df[df['Outlook'] == 'BULLISH'].head(7)
    bearish = df[df['Outlook'] == 'BEARISH'].head(5)

    if not bullish.empty:
        msg += "*BULLISH OUTLOOK*\n\n"
        for _, row in bullish.iterrows():
            emoji = "" if row['Trend'] == 'UPTREND' else ""
            msg += f"{emoji} *{row['Ticker']}* @ ${row['Price']}\n"
            msg += f"    Target: ${row['Weekly_Target']} (+{row['Predicted_%']}%)\n"
            msg += f"    Trend: {row['Trend']} | Conf: {row['Confidence']}%\n"
            msg += f"    Week: {row['Weekly_Mom']:+.1f}% | Month: {row['Monthly_Mom']:+.1f}%\n\n"

    if not bearish.empty:
        msg += "*BEARISH OUTLOOK*\n\n"
        for _, row in bearish.iterrows():
            msg += f"  *{row['Ticker']}* @ ${row['Price']}\n"
            msg += f"    Target: ${row['Weekly_Target']} ({row['Predicted_%']}%)\n"
            msg += f"    Trend: {row['Trend']} | Conf: {row['Confidence']}%\n\n"

    msg += "_Weekly outlook based on technical & momentum analysis._\n"
    msg += "_Not financial advice. Always do your own research._"
    return msg


def send_weekly_predictions():
    """Send weekly predictions to Telegram"""
    print(f"\n{'='*50}")
    print(f"WEEKLY PREDICTIONS - {datetime.now().strftime('%B %d, %Y')}")
    print(f"{'='*50}")

    bot = get_bot()
    if not bot:
        return

    df = scan_weekly_predictions(top_n=15)
    msg = format_weekly_predictions(df)

    if msg:
        bot.send_message(msg)
        print("Weekly predictions sent!")
    else:
        print("No strong weekly predictions found")


# ============================================================
# SCHEDULER
# ============================================================

def setup_schedule():
    """Setup all scheduled jobs"""

    # Hourly tips (every hour during market hours: 9:30 AM - 4:00 PM ET)
    hourly_times = ['09:30', '10:30', '11:30', '12:30', '13:30', '14:30', '15:30']
    for t in hourly_times:
        schedule.every().monday.at(t).do(send_hourly_tips)
        schedule.every().tuesday.at(t).do(send_hourly_tips)
        schedule.every().wednesday.at(t).do(send_hourly_tips)
        schedule.every().thursday.at(t).do(send_hourly_tips)
        schedule.every().friday.at(t).do(send_hourly_tips)
    print(f"Scheduled hourly tips at: {', '.join(hourly_times)}")

    # 3-hour predictions (9:30, 12:30, 15:30)
    prediction_times = ['09:30', '12:30', '15:30']
    for t in prediction_times:
        schedule.every().monday.at(t).do(send_3hour_predictions)
        schedule.every().tuesday.at(t).do(send_3hour_predictions)
        schedule.every().wednesday.at(t).do(send_3hour_predictions)
        schedule.every().thursday.at(t).do(send_3hour_predictions)
        schedule.every().friday.at(t).do(send_3hour_predictions)
    print(f"Scheduled 3-hour predictions at: {', '.join(prediction_times)}")

    # Weekly predictions (Monday 8:00 AM)
    schedule.every().monday.at('08:00').do(send_weekly_predictions)
    print("Scheduled weekly predictions: Monday 8:00 AM")


def run_scheduler():
    """Run the scheduler loop"""
    print(f"\n{'='*60}")
    print("SCHEDULED ALERTS SYSTEM")
    print(f"{'='*60}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    setup_schedule()

    print(f"\nScheduler running... (Press Ctrl+C to stop)\n")

    while True:
        schedule.run_pending()
        time.sleep(60)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--test', type=str, choices=['hourly', '3hour', 'weekly', 'all'],
                       help='Test specific alert type')
    args = parser.parse_args()

    if args.test:
        if args.test == 'hourly' or args.test == 'all':
            send_hourly_tips()
        if args.test == '3hour' or args.test == 'all':
            send_3hour_predictions()
        if args.test == 'weekly' or args.test == 'all':
            send_weekly_predictions()
    else:
        run_scheduler()
