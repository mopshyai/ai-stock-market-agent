
import time
import yaml
from datetime import datetime
from trade_engine import (
    check_pending_entries,
    monitor_open_trades,
    check_daily_risk_limit,
    get_trade_summary
)
from telegram_bot import notify_trade_lifecycle

"""
Trade Monitor - Continuous background process to monitor trade lifecycle
"""


def run_monitor_loop(cfg: dict):
    """
    Main monitoring loop
    Runs continuously and checks trades every N minutes
    """
    monitor_cfg = cfg.get('trade_monitor', {})
    check_interval_seconds = monitor_cfg.get('check_interval_minutes', 5) * 60
    send_daily_summary = monitor_cfg.get('send_daily_summary', True)
    summary_sent_today = False
    weekly_summary_sent_this_week = False

    print("🤖 TRADE MONITOR STARTED")
    print(f"⏰ Check interval: {check_interval_seconds // 60} minutes")
    print("=" * 50)

    while True:
        try:
            current_time = datetime.now()
            print(f"\n[{current_time.strftime('%H:%M:%S')}] Running monitor cycle...")

            # Check daily risk limit
            can_trade, daily_r = check_daily_risk_limit(cfg)

            if not can_trade:
                print(f"⚠️  DAILY LOSS LIMIT HIT: {daily_r:.2f}R")
                print("🛑 New entries disabled")
            else:
                # Check for new entries (pending → open)
                new_entries = check_pending_entries(cfg)

                if new_entries:
                    print(f"▶️  {len(new_entries)} trade(s) entered")

                    # Send alerts for each entry
                    for entry in new_entries:
                        notify_trade_lifecycle('ENTRY', entry, cfg)

            # Monitor open trades for exits
            closed_trades = monitor_open_trades(cfg)

            if closed_trades:
                print(f"🔔 {len(closed_trades)} trade(s) closed")

                # Send alerts for each exit
                for trade in closed_trades:
                    notify_trade_lifecycle('EXIT', trade, cfg)

            # Send daily summary (once per day at configured time)
            if send_daily_summary:
                summary_hour = monitor_cfg.get('daily_summary_hour', 16)  # 4 PM default

                if current_time.hour == summary_hour and not summary_sent_today:
                    summary = get_trade_summary(days=1)
                    notify_trade_lifecycle('DAILY_SUMMARY', summary, cfg)
                    summary_sent_today = True
                    print(f"📊 Daily summary sent")

                    # Send weekly summary on Friday (weekday 4)
                    if current_time.weekday() == 4 and not weekly_summary_sent_this_week:
                        weekly = get_trade_summary(days=7)
                        notify_trade_lifecycle('WEEKLY_SUMMARY', weekly, cfg)
                        weekly_summary_sent_this_week = True
                        print(f"📈 Weekly summary sent")

                # Reset daily flag at midnight
                if current_time.hour == 0:
                    summary_sent_today = False

                # Reset weekly flag on Sunday
                if current_time.weekday() == 6:  # Sunday
                    weekly_summary_sent_this_week = False

            print(f"✅ Monitor cycle complete. Next check in {check_interval_seconds // 60} min")

        except KeyboardInterrupt:
            print("\n🛑 Monitor stopped by user")
            break

        except Exception as e:
            print(f"❌ ERROR in monitor cycle: {e}")
            print("Continuing...")

        # Wait before next check
        time.sleep(check_interval_seconds)


if __name__ == "__main__":
    # Load config
    cfg = yaml.safe_load(open("config.yaml", "r"))

    print("\n" + "=" * 50)
    print("AI STOCK AGENT - TRADE MONITOR")
    print("=" * 50)
    print("\nThis process will continuously monitor:")
    print("  • Pending trades for entry")
    print("  • Open trades for SL/TP hits")
    print("  • Daily risk limits")
    print("\nPress Ctrl+C to stop\n")
    print("=" * 50 + "\n")

    # Start monitoring loop
    run_monitor_loop(cfg)
