#!/usr/bin/env python3
"""
AUTOMATED TOP PERFORMERS SCHEDULER
Runs hourly scans and morning picks automatically
Sends alerts via Telegram
"""

import os
import sys
import time
import schedule
from datetime import datetime
import pandas as pd
import yaml

# Import scanner
from top_performers_scanner import scan_hourly_top_movers, scan_morning_top_picks

# Import telegram notifications
try:
    from telegram_bot import send_telegram_message
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    print("⚠️  Telegram bot not available")


# ============================================================
# TELEGRAM ALERTS
# ============================================================

def format_hourly_alert(df: pd.DataFrame) -> str:
    """Format hourly movers for Telegram"""
    if df.empty:
        return "⚠️ No significant hourly movers found"

    msg = "🔥 *HOURLY TOP MOVERS*\n"
    msg += f"⏰ {datetime.now().strftime('%I:%M %p')}\n\n"

    for idx, row in df.iterrows():
        emoji = "📈" if row['Hourly_Change_%'] > 0 else "📉"
        msg += f"{emoji} *{row['Ticker']}*: ${row['Current_Price']:.2f}\n"
        msg += f"   Change: *{row['Hourly_Change_%']:+.2f}%*\n"
        msg += f"   Volume: {row['Volume_1h']:,.0f}\n"
        msg += f"   {row['Momentum']}\n\n"

    return msg


def format_morning_alert(df: pd.DataFrame) -> str:
    """Format morning picks for Telegram"""
    if df.empty:
        return "⚠️ No quality morning setups found"

    msg = "🌅 *MORNING TOP PICKS*\n"
    msg += f"📅 {datetime.now().strftime('%B %d, %Y')}\n\n"

    for idx, row in df.iterrows():
        msg += f"⭐ *{row['Ticker']}* (Score: {row['Score']}/10)\n"
        msg += f"   Price: ${row['Current_Price']:.2f}\n"
        msg += f"   Potential: *+{row['Potential_Gain_%']:.2f}%*\n"
        msg += f"   Risk: -{row['Risk_%']:.2f}%\n"
        msg += f"   R:R = {row['Risk_Reward']:.2f}\n"
        msg += f"   RSI: {row['RSI']:.1f} | ADX: {row['ADX']:.1f}\n"
        msg += f"   Momentum: {row['Momentum_5D_%']:+.2f}%\n\n"

    msg += "⚠️ _Not financial advice. Always DYOR._"
    return msg


def send_telegram_alert(message: str):
    """Send Telegram alert"""
    if not TELEGRAM_AVAILABLE:
        print("⚠️  Telegram not configured")
        return

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        print("⚠️  Telegram credentials missing")
        return

    try:
        send_telegram_message(message, bot_token, chat_id, parse_mode='Markdown')
        print("✅ Telegram alert sent")
    except Exception as e:
        print(f"❌ Telegram alert failed: {e}")


# ============================================================
# SCHEDULED JOBS
# ============================================================

def hourly_scan_job():
    """Run hourly top movers scan"""
    print(f"\n{'='*60}")
    print(f"⏰ HOURLY SCAN TRIGGERED")
    print(f"   Time: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}")
    print(f"{'='*60}\n")

    try:
        # Scan top 10 movers
        df = scan_hourly_top_movers(top_n=10, universe_mode='popular')

        if not df.empty:
            # Save to CSV
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            filename = f"hourly_movers_{timestamp}.csv"
            df.to_csv(filename, index=False)
            print(f"✅ Saved: {filename}")

            # Send Telegram alert
            alert_msg = format_hourly_alert(df)
            send_telegram_alert(alert_msg)

            # Print results
            print(f"\n📊 TOP 10 HOURLY MOVERS:\n")
            print(df.to_string(index=False))
        else:
            print("⚠️  No significant movers this hour")

    except Exception as e:
        print(f"❌ Hourly scan failed: {e}")


def morning_scan_job():
    """Run morning top picks scan"""
    print(f"\n{'='*60}")
    print(f"🌅 MORNING SCAN TRIGGERED")
    print(f"   Time: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}")
    print(f"{'='*60}\n")

    try:
        # Scan top 10 picks
        df = scan_morning_top_picks(top_n=10, universe_mode='popular')

        if not df.empty:
            # Save to CSV
            timestamp = datetime.now().strftime("%Y%m%d")
            filename = f"morning_picks_{timestamp}.csv"
            df.to_csv(filename, index=False)
            print(f"✅ Saved: {filename}")

            # Send Telegram alert
            alert_msg = format_morning_alert(df)
            send_telegram_alert(alert_msg)

            # Print results
            print(f"\n📊 TOP 10 MORNING PICKS:\n")
            print(df.to_string(index=False))
        else:
            print("⚠️  No quality setups found")

    except Exception as e:
        print(f"❌ Morning scan failed: {e}")


# ============================================================
# SCHEDULER CONFIGURATION
# ============================================================

def setup_scheduler(config: dict):
    """Setup scheduled jobs based on config"""
    hourly_enabled = config.get('hourly_scans', {}).get('enabled', True)
    morning_enabled = config.get('morning_scans', {}).get('enabled', True)

    # Hourly scans (every hour during market hours)
    if hourly_enabled:
        market_hours = config.get('hourly_scans', {}).get('market_hours', ['09:30', '10:30', '11:30', '12:30', '13:30', '14:30', '15:30'])

        for hour in market_hours:
            schedule.every().day.at(hour).do(hourly_scan_job)
            print(f"✅ Scheduled hourly scan at {hour}")

    # Morning scan (before market open)
    if morning_enabled:
        morning_time = config.get('morning_scans', {}).get('time', '08:00')
        schedule.every().day.at(morning_time).do(morning_scan_job)
        print(f"✅ Scheduled morning scan at {morning_time}")


def main():
    """Main scheduler loop"""
    print(f"\n{'='*60}")
    print("🤖 AUTOMATED TOP PERFORMERS SCHEDULER")
    print(f"{'='*60}\n")

    # Load config
    try:
        cfg = yaml.safe_load(open("config.yaml", "r"))
        scan_config = cfg.get('top_performers_scan', {
            'hourly_scans': {
                'enabled': True,
                'market_hours': ['09:30', '10:30', '11:30', '12:30', '13:30', '14:30', '15:30']
            },
            'morning_scans': {
                'enabled': True,
                'time': '08:00'
            }
        })
    except Exception as e:
        print(f"⚠️  Could not load config: {e}")
        scan_config = {
            'hourly_scans': {'enabled': True, 'market_hours': ['09:30', '10:30', '11:30', '12:30', '13:30', '14:30', '15:30']},
            'morning_scans': {'enabled': True, 'time': '08:00'}
        }

    # Setup scheduler
    setup_scheduler(scan_config)

    print(f"\n⏰ Scheduler started at {datetime.now().strftime('%Y-%m-%d %I:%M %p')}")
    print("Press Ctrl+C to stop\n")

    # Run initial scan immediately (optional)
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--now', action='store_true', help='Run morning scan immediately')
    args = parser.parse_args()

    if args.now:
        print("Running immediate morning scan...\n")
        morning_scan_job()

    # Main loop
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\n\n⏹️  Scheduler stopped")


if __name__ == "__main__":
    main()
