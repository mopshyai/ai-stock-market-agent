#!/usr/bin/env python3

import os
import sys
import subprocess
import yaml

"""
AI Stock Agent Trading System - Quick Start
"""

BANNER = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║       AI STOCK AGENT - TRADING SYSTEM                     ║
║                                                           ║
║  Signal → Trade → Entry → Exit → Telegram Alerts         ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
"""

MENU = """
Choose an option:

1. 🔍 Scan for signals (scan_and_chart.py)
2. 📋 Convert signals to trades (signals_to_trades.py)
3. 🤖 Start trade monitor (continuous monitoring)
4. 📊 View trade summary
5. 📈 View pending trades
6. 🔓 View open trades
7. ⚙️  Configure risk settings
8. 🧪 Test Telegram connection
9. 📖 View trading system guide

0. Exit

"""


def check_telegram_configured():
    """Check if Telegram credentials are set"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    if not token or not chat_id:
        print("\n⚠️  WARNING: Telegram not configured!")
        print("\nSet credentials:")
        print('  export TELEGRAM_BOT_TOKEN="your_token"')
        print('  export TELEGRAM_CHAT_ID="your_chat_id"')
        print("\nOr run option 8 to test connection\n")
        return False
    return True


def run_scan():
    """Run stock scanner"""
    print("\n🔍 Running stock scanner...\n")
    subprocess.run(['python3', 'scan_and_chart.py'])
    print("\n✅ Scan complete!")


def convert_signals():
    """Convert signals to trades"""
    print("\n📋 Converting signals to trades...\n")
    subprocess.run(['python3', 'signals_to_trades.py'])


def start_monitor():
    """Start trade monitor"""
    print("\n🤖 Starting trade monitor...")
    print("Press Ctrl+C to stop\n")
    try:
        subprocess.run(['python3', 'trade_monitor.py'])
    except KeyboardInterrupt:
        print("\n\n🛑 Monitor stopped\n")


def view_summary():
    """View trade summary"""
    from database_postgres import get_trade_summary

    print("\n📊 TRADE SUMMARY (Last 30 days)")
    print("═" * 50)

    summary = get_trade_summary(days=30)

    print(f"\nTotal Trades: {summary['total_trades']}")
    print(f"  • Open: {summary['open']}")
    print(f"  • Pending: {summary['pending']}")
    print(f"  • Closed: {summary['closed']}")

    if summary['closed'] > 0:
        print(f"\n  • Wins: {summary['wins']}")
        print(f"  • Win Rate: {summary['win_rate']}%")
        print(f"  • Avg R: {summary['avg_r']}R")
        print(f"  • Total P&L: ${summary['total_pnl']:.2f}")

    print()


def view_pending():
    """View pending trades"""
    from database_postgres import get_pending_trades

    print("\n📋 PENDING TRADES")
    print("═" * 50)

    df = get_pending_trades()

    if df.empty:
        print("\nNo pending trades.\n")
    else:
        print(f"\n{len(df)} pending trade(s):\n")
        for _, trade in df.iterrows():
            print(f"  {trade['ticker']}")
            print(f"    Entry: ${trade['entry_price']:.2f}")
            print(f"    Stop: ${trade['stop_loss']:.2f}")
            print(f"    TP1: ${trade['tp1']:.2f} | TP2: ${trade['tp2']:.2f}")
            print(f"    Created: {trade['created_at']}")
            print()


def view_open():
    """View open trades"""
    from database_postgres import get_open_trades

    print("\n🔓 OPEN TRADES")
    print("═" * 50)

    df = get_open_trades()

    if df.empty:
        print("\nNo open trades.\n")
    else:
        print(f"\n{len(df)} open trade(s):\n")
        for _, trade in df.iterrows():
            print(f"  {trade['ticker']}")
            print(f"    Entry: ${trade['entry_price']:.2f}")
            print(f"    Current: ${trade['current_price']:.2f}")
            print(f"    Stop: ${trade['stop_loss']:.2f}")
            print(f"    TP1: ${trade['tp1']:.2f} | TP2: ${trade['tp2']:.2f}")
            print(f"    Opened: {trade['entry_time']}")
            print()


def configure_risk():
    """Show risk configuration"""
    cfg = yaml.safe_load(open("config.yaml", "r"))
    risk = cfg.get('risk_management', {})

    print("\n⚙️  RISK CONFIGURATION")
    print("═" * 50)
    print(f"\nMin Signal Score: {risk.get('min_signal_score', 3)}")
    print(f"Risk per Trade: ${risk.get('risk_per_trade_dollars', 100)}")
    print(f"Max Daily Loss: {risk.get('max_daily_loss_r', 3.0)}R")
    print(f"Max Open Trades: {risk.get('max_open_trades', 5)}")
    print(f"Max Trades/Day: {risk.get('max_trades_per_day', 10)}")

    if risk.get('use_fixed_stop_pct'):
        print(f"Stop Loss: {risk.get('fixed_stop_pct', 2.0)}% (fixed)")
    else:
        print(f"Stop Loss: ATR × {risk.get('stop_loss_atr_multiplier', 1.5)}")

    print("\nEdit config.yaml to change settings\n")


def test_telegram():
    """Test Telegram connection"""
    print("\n🧪 Testing Telegram connection...\n")
    subprocess.run(['python3', 'telegram_bot.py'])


def view_guide():
    """View trading system guide"""
    print("\n📖 Opening TRADING_SYSTEM.md...\n")

    if os.path.exists("TRADING_SYSTEM.md"):
        # Try to open with default viewer
        if sys.platform == "darwin":
            subprocess.run(['open', 'TRADING_SYSTEM.md'])
        elif sys.platform == "linux":
            subprocess.run(['xdg-open', 'TRADING_SYSTEM.md'])
        else:
            print("Read TRADING_SYSTEM.md for full documentation")
    else:
        print("TRADING_SYSTEM.md not found")


def main():
    """Main menu loop"""
    print(BANNER)

    # Check Telegram on startup
    check_telegram_configured()

    while True:
        print(MENU)

        try:
            choice = input("Enter choice (0-9): ").strip()

            if choice == '1':
                run_scan()
            elif choice == '2':
                convert_signals()
            elif choice == '3':
                start_monitor()
            elif choice == '4':
                view_summary()
            elif choice == '5':
                view_pending()
            elif choice == '6':
                view_open()
            elif choice == '7':
                configure_risk()
            elif choice == '8':
                test_telegram()
            elif choice == '9':
                view_guide()
            elif choice == '0':
                print("\n👋 Goodbye!\n")
                break
            else:
                print("\n❌ Invalid choice. Try again.\n")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    main()
