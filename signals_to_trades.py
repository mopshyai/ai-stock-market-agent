
import yaml
import sqlite3
from typing import List, Dict
from database import DB_PATH
from trade_engine import signal_to_trade
from telegram_bot import notify_trade_lifecycle

"""
Signals to Trades Converter
Converts recent scan signals into pending trades
"""


def get_latest_scan_signals(min_score: int = 3) -> List[Dict]:
    """
    Get signals from the most recent scan
    Returns list of signal data suitable for trade creation
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get latest scan ID
    cursor.execute("SELECT scan_id FROM scans ORDER BY scan_date DESC LIMIT 1")
    result = cursor.fetchone()

    if not result:
        print("No scans found in database")
        conn.close()
        return []

    latest_scan_id = result[0]

    # Get signals from this scan
    query = """
        SELECT
            signal_id,
            ticker,
            score,
            consolidating,
            buy_dip,
            breakout,
            vol_spike,
            trend,
            price_at_signal,
            rsi,
            adx,
            bb_width_pct,
            atr_pct
        FROM signals
        WHERE scan_id = ? AND score >= ?
        ORDER BY score DESC
    """

    cursor.execute(query, (latest_scan_id, min_score))
    rows = cursor.fetchall()

    conn.close()

    # Convert to list of dicts
    signals = []
    for row in rows:
        signals.append({
            'signal_id': row[0],
            'Ticker': row[1],
            'Score': row[2],
            'Consolidating': bool(row[3]),
            'BuyDip': bool(row[4]),
            'Breakout': bool(row[5]),
            'VolSpike': bool(row[6]),
            'Trend': row[7],
            'Close': row[8],
            'RSI': row[9],
            'ADX': row[10],
            'BBWidth_pct': row[11],
            'ATR%': row[12]
        })

    return signals


def check_existing_trades(ticker: str) -> bool:
    """
    Check if there's already an open or pending trade for this ticker
    Returns True if trade exists
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*) FROM trades
        WHERE ticker = ? AND status IN ('PENDING', 'OPEN')
    """, (ticker,))

    count = cursor.fetchone()[0]
    conn.close()

    return count > 0


def convert_signals_to_trades(cfg: dict, send_alerts: bool = True) -> Dict:
    """
    Main function to convert latest signals to trades
    Returns summary of actions taken
    """
    print("\n" + "=" * 50)
    print("CONVERTING SIGNALS TO TRADES")
    print("=" * 50 + "\n")

    risk_cfg = cfg.get('risk_management', {})
    min_score = risk_cfg.get('min_signal_score', 3)
    max_trades = risk_cfg.get('max_trades_per_day', 10)

    # Get latest signals
    signals = get_latest_scan_signals(min_score)

    if not signals:
        print(f"No signals found with score >= {min_score}")
        return {
            'signals_found': 0,
            'trades_created': 0
        }

    print(f"Found {len(signals)} signals with score >= {min_score}")

    created_trades = []
    skipped = 0

    for signal in signals:
        # Stop if we've hit max trades
        if len(created_trades) >= max_trades:
            print(f"\n⚠️  Max trades limit reached ({max_trades})")
            break

        ticker = signal['Ticker']

        # Skip if we already have a trade for this ticker
        if check_existing_trades(ticker):
            print(f"[SKIP] {ticker} - Already have open/pending trade")
            skipped += 1
            continue

        # Create trade
        print(f"\n📋 Creating trade for {ticker} (Score: {signal['Score']})")

        trade_id = signal_to_trade(
            signal_data=signal,
            signal_id=signal['signal_id'],
            cfg=cfg
        )

        if trade_id:
            # Get trade details for notification
            from trade_engine import calculate_trade_levels

            trade_plan = calculate_trade_levels(signal, cfg)
            trade_plan['trade_id'] = trade_id

            created_trades.append(trade_plan)

            # Send Telegram notification
            if send_alerts:
                notify_trade_lifecycle('NEW', trade_plan, cfg)

    print("\n" + "=" * 50)
    print(f"✅ Created {len(created_trades)} trades")
    print(f"⏭️  Skipped {skipped} (existing trades)")
    print("=" * 50)

    return {
        'signals_found': len(signals),
        'trades_created': len(created_trades),
        'skipped': skipped,
        'trades': created_trades
    }


if __name__ == "__main__":
    # Load config
    cfg = yaml.safe_load(open("config.yaml", "r"))

    # Convert signals to trades
    result = convert_signals_to_trades(cfg)

    print(f"\n📊 Summary:")
    print(f"   Signals: {result['signals_found']}")
    print(f"   Trades Created: {result['trades_created']}")
    print(f"   Skipped: {result['skipped']}")
