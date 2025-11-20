#!/usr/bin/env python3

import os
import threading
import time
from datetime import datetime

"""
Main Runner - Runs both tweet scheduler and trade monitor in parallel
For cloud deployment (Railway, Render, etc.)
"""


def check_env_variables():
    """Check if required environment variables are set"""
    required = [
        'TELEGRAM_BOT_TOKEN',
        'TELEGRAM_CHAT_ID',
        'TWITTER_API_KEY',
        'TWITTER_API_SECRET',
        'TWITTER_ACCESS_TOKEN',
        'TWITTER_ACCESS_SECRET'
    ]

    missing = []
    for var in required:
        if not os.getenv(var):
            missing.append(var)

    if missing:
        print("❌ Missing environment variables:")
        for var in missing:
            print(f"   - {var}")
        print("\nSet these in Railway dashboard or .env file")
        return False

    print("✅ All environment variables configured")
    return True


def run_tweet_scheduler():
    """Run the automated tweet scheduler"""
    try:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting Tweet Scheduler...")

        from tweet_scheduler import AutomatedTwitterPersona

        persona = AutomatedTwitterPersona()
        persona.run_scheduler()  # This blocks

    except Exception as e:
        print(f"❌ Error in tweet scheduler: {e}")
        import traceback
        traceback.print_exc()


def run_trade_monitor():
    """Run the trade monitoring system"""
    try:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting Trade Monitor...")

        from trade_monitor import run_monitor_loop
        import yaml

        cfg = yaml.safe_load(open('config.yaml', 'r'))
        run_monitor_loop(cfg)  # This blocks

    except Exception as e:
        print(f"❌ Error in trade monitor: {e}")
        import traceback
        traceback.print_exc()


def run_interactive_bot():
    """Run the interactive Telegram bot"""
    try:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting Interactive Telegram Bot...")

        from interactive_telegram_bot import TradingAssistantBot

        bot = TradingAssistantBot()
        bot.run(in_thread=True)  # This blocks (in_thread=True to disable signal handlers)

    except Exception as e:
        print(f"❌ Error in interactive bot: {e}")
        import traceback
        traceback.print_exc()


def run_scheduled_alerts():
    """Run scheduled alerts (hourly tips, 3-hour predictions, weekly predictions)"""
    try:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting Scheduled Alerts...")

        from scheduled_alerts import run_scheduler
        run_scheduler()  # This blocks

    except Exception as e:
        print(f"❌ Error in scheduled alerts: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main entry point - runs all services in parallel"""
    print("\n" + "="*60)
    print("AI STOCK AGENT - CLOUD DEPLOYMENT")
    print("="*60)
    print("\nStarting automated systems:")
    print("  1. Tweet Scheduler (6 tweets/day)")
    print("  2. Trade Monitor (live trade alerts)")
    print("  3. Interactive Telegram Bot (chat with AI)")
    print("  4. Scheduled Alerts (hourly tips, 3h & weekly predictions)")
    print("\n" + "="*60 + "\n")

    # Check environment variables
    if not check_env_variables():
        print("\n⚠️  Please configure environment variables and restart")
        return

    # Initialize database (supports both SQLite and Postgres)
    try:
        from database import init_database
        init_database()
    except Exception as e:
        print(f"⚠️  Database init warning: {e}")

    # Create threads for parallel execution
    tweet_thread = threading.Thread(target=run_tweet_scheduler, daemon=True, name="TweetScheduler")
    trade_thread = threading.Thread(target=run_trade_monitor, daemon=True, name="TradeMonitor")
    bot_thread = threading.Thread(target=run_interactive_bot, daemon=True, name="InteractiveBot")
    alerts_thread = threading.Thread(target=run_scheduled_alerts, daemon=True, name="ScheduledAlerts")

    # Start all threads (staggered to avoid startup conflicts)
    tweet_thread.start()
    time.sleep(2)
    trade_thread.start()
    time.sleep(2)
    bot_thread.start()
    time.sleep(2)
    alerts_thread.start()

    print("\n✅ All systems running")
    print("Press Ctrl+C to stop (but on Railway, this runs forever)\n")

    # Keep main thread alive
    try:
        while True:
            time.sleep(60)

            # Health check every minute
            if not tweet_thread.is_alive():
                print("⚠️  Tweet scheduler thread died, restarting...")
                tweet_thread = threading.Thread(target=run_tweet_scheduler, daemon=True)
                tweet_thread.start()

            if not trade_thread.is_alive():
                print("⚠️  Trade monitor thread died, restarting...")
                trade_thread = threading.Thread(target=run_trade_monitor, daemon=True)
                trade_thread.start()

            if not bot_thread.is_alive():
                print("⚠️  Interactive bot thread died, restarting...")
                bot_thread = threading.Thread(target=run_interactive_bot, daemon=True)
                bot_thread.start()

            if not alerts_thread.is_alive():
                print("⚠️  Scheduled alerts thread died, restarting...")
                alerts_thread = threading.Thread(target=run_scheduled_alerts, daemon=True)
                alerts_thread.start()

    except KeyboardInterrupt:
        print("\n Shutting down...")


if __name__ == "__main__":
    main()
