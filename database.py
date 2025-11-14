
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple

"""
Database module for AI Stock Market Agent
Stores scan results, tracks historical performance, and calculates signal win rates
"""

DB_PATH = "stock_agent.db"


def init_database():
    """Initialize database schema"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Scans table - stores metadata about each scan
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            scan_id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_date TIMESTAMP NOT NULL,
            total_stocks INTEGER NOT NULL,
            signals_found INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Signals table - stores individual stock signals
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS signals (
            signal_id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_id INTEGER NOT NULL,
            ticker TEXT NOT NULL,
            signal_date DATE NOT NULL,
            score INTEGER NOT NULL,
            consolidating BOOLEAN,
            buy_dip BOOLEAN,
            breakout BOOLEAN,
            vol_spike BOOLEAN,
            trend TEXT,
            price_at_signal REAL NOT NULL,
            rsi REAL,
            adx REAL,
            bb_width_pct REAL,
            atr_pct REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (scan_id) REFERENCES scans(scan_id)
        )
    """)

    # Price tracking - stores price movements after signals
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS price_tracking (
            tracking_id INTEGER PRIMARY KEY AUTOINCREMENT,
            signal_id INTEGER NOT NULL,
            ticker TEXT NOT NULL,
            days_after INTEGER NOT NULL,
            price REAL NOT NULL,
            price_change_pct REAL NOT NULL,
            tracked_date DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (signal_id) REFERENCES signals(signal_id)
        )
    """)

    # Create indexes for faster queries
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_signals_ticker ON signals(ticker)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_signals_date ON signals(signal_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tracking_signal ON price_tracking(signal_id)")

    conn.commit()
    conn.close()
    print(f"✅ Database initialized at {DB_PATH}")


def store_scan_results(results: List[Dict]) -> int:
    """
    Store scan results in database
    Returns scan_id
    """
    if not results:
        return -1

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Count signals
    signals_count = sum(
        1 for r in results
        if r.get('Consolidating') or r.get('BuyDip') or r.get('Breakout') or r.get('VolSpike')
    )

    # Insert scan record
    scan_date = datetime.now()
    cursor.execute("""
        INSERT INTO scans (scan_date, total_stocks, signals_found)
        VALUES (?, ?, ?)
    """, (scan_date, len(results), signals_count))

    scan_id = cursor.lastrowid

    # Insert individual signals
    for result in results:
        cursor.execute("""
            INSERT INTO signals (
                scan_id, ticker, signal_date, score,
                consolidating, buy_dip, breakout, vol_spike, trend,
                price_at_signal, rsi, adx, bb_width_pct, atr_pct
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            scan_id,
            result.get('Ticker'),
            scan_date.date(),
            result.get('Score', 0),
            result.get('Consolidating', False),
            result.get('BuyDip', False),
            result.get('Breakout', False),
            result.get('VolSpike', False),
            result.get('Trend', 'CHOPPY'),
            result.get('Close', 0.0),
            result.get('RSI'),
            result.get('ADX'),
            result.get('BBWidth_pct'),
            result.get('ATR%')
        ))

    conn.commit()
    conn.close()

    print(f"✅ Stored scan {scan_id}: {len(results)} stocks, {signals_count} signals")
    return scan_id


def get_recent_scans(limit: int = 10) -> pd.DataFrame:
    """Get recent scan summary"""
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT
            scan_id,
            scan_date,
            total_stocks,
            signals_found,
            ROUND(CAST(signals_found AS FLOAT) / total_stocks * 100, 1) as signal_rate_pct
        FROM scans
        ORDER BY scan_date DESC
        LIMIT ?
    """
    df = pd.read_sql_query(query, conn, params=(limit,))
    conn.close()
    return df


def get_signals_by_date_range(start_date: str, end_date: str) -> pd.DataFrame:
    """Get all signals within a date range"""
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT
            s.signal_id,
            s.ticker,
            s.signal_date,
            s.score,
            s.consolidating,
            s.buy_dip,
            s.breakout,
            s.vol_spike,
            s.trend,
            s.price_at_signal,
            s.rsi,
            s.adx
        FROM signals s
        WHERE s.signal_date BETWEEN ? AND ?
        ORDER BY s.signal_date DESC, s.score DESC
    """
    df = pd.read_sql_query(query, conn, params=(start_date, end_date))
    conn.close()
    return df


def get_top_signals(days: int = 30, min_score: int = 3) -> pd.DataFrame:
    """Get top-scoring signals from recent days"""
    conn = sqlite3.connect(DB_PATH)
    cutoff_date = (datetime.now() - timedelta(days=days)).date()

    query = """
        SELECT
            ticker,
            signal_date,
            score,
            consolidating,
            buy_dip,
            breakout,
            vol_spike,
            trend,
            price_at_signal,
            rsi,
            adx
        FROM signals
        WHERE signal_date >= ? AND score >= ?
        ORDER BY score DESC, signal_date DESC
        LIMIT 50
    """
    df = pd.read_sql_query(query, conn, params=(cutoff_date, min_score))
    conn.close()
    return df


def get_signal_stats() -> Dict:
    """Get overall signal statistics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    stats = {}

    # Total signals
    cursor.execute("SELECT COUNT(*) FROM signals")
    stats['total_signals'] = cursor.fetchone()[0]

    # Signals by type
    cursor.execute("SELECT COUNT(*) FROM signals WHERE consolidating = 1")
    stats['consolidation_count'] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM signals WHERE buy_dip = 1")
    stats['buy_dip_count'] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM signals WHERE breakout = 1")
    stats['breakout_count'] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM signals WHERE vol_spike = 1")
    stats['vol_spike_count'] = cursor.fetchone()[0]

    # Average score
    cursor.execute("SELECT AVG(score) FROM signals")
    avg_score = cursor.fetchone()[0]
    stats['avg_score'] = round(avg_score, 2) if avg_score else 0

    # Top tickers
    cursor.execute("""
        SELECT ticker, COUNT(*) as signal_count
        FROM signals
        GROUP BY ticker
        ORDER BY signal_count DESC
        LIMIT 10
    """)
    stats['top_tickers'] = cursor.fetchall()

    conn.close()
    return stats


def update_price_tracking(ticker: str, current_price: float) -> None:
    """
    Update price tracking for all active signals of a ticker
    Tracks price movement 1, 3, 7, 14, 30 days after signal
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get active signals for this ticker (last 30 days)
    cutoff_date = (datetime.now() - timedelta(days=30)).date()
    cursor.execute("""
        SELECT signal_id, signal_date, price_at_signal
        FROM signals
        WHERE ticker = ? AND signal_date >= ?
    """, (ticker, cutoff_date))

    signals = cursor.fetchall()

    for signal_id, signal_date_str, price_at_signal in signals:
        signal_date = datetime.strptime(signal_date_str, '%Y-%m-%d').date()
        days_after = (datetime.now().date() - signal_date).days

        if days_after > 0 and price_at_signal > 0:
            price_change_pct = ((current_price - price_at_signal) / price_at_signal) * 100

            # Check if we already have tracking for this day
            cursor.execute("""
                SELECT tracking_id FROM price_tracking
                WHERE signal_id = ? AND days_after = ?
            """, (signal_id, days_after))

            existing = cursor.fetchone()

            if existing:
                # Update existing record
                cursor.execute("""
                    UPDATE price_tracking
                    SET price = ?, price_change_pct = ?, tracked_date = ?
                    WHERE tracking_id = ?
                """, (current_price, price_change_pct, datetime.now().date(), existing[0]))
            else:
                # Insert new tracking record
                cursor.execute("""
                    INSERT INTO price_tracking (signal_id, ticker, days_after, price, price_change_pct, tracked_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (signal_id, ticker, days_after, current_price, price_change_pct, datetime.now().date()))

    conn.commit()
    conn.close()


def get_signal_performance(signal_type: str = 'all', days: int = 30) -> pd.DataFrame:
    """
    Calculate win rates for signals
    signal_type: 'consolidating', 'buy_dip', 'breakout', 'vol_spike', or 'all'
    """
    conn = sqlite3.connect(DB_PATH)

    # Build WHERE clause based on signal type
    if signal_type == 'consolidating':
        signal_filter = "AND s.consolidating = 1"
    elif signal_type == 'buy_dip':
        signal_filter = "AND s.buy_dip = 1"
    elif signal_type == 'breakout':
        signal_filter = "AND s.breakout = 1"
    elif signal_type == 'vol_spike':
        signal_filter = "AND s.vol_spike = 1"
    else:
        signal_filter = ""

    query = f"""
        SELECT
            s.ticker,
            s.signal_date,
            s.score,
            s.price_at_signal,
            MAX(CASE WHEN pt.days_after = 1 THEN pt.price_change_pct END) as day1_change,
            MAX(CASE WHEN pt.days_after = 3 THEN pt.price_change_pct END) as day3_change,
            MAX(CASE WHEN pt.days_after = 7 THEN pt.price_change_pct END) as day7_change,
            MAX(CASE WHEN pt.days_after = 14 THEN pt.price_change_pct END) as day14_change,
            MAX(CASE WHEN pt.days_after = 30 THEN pt.price_change_pct END) as day30_change
        FROM signals s
        LEFT JOIN price_tracking pt ON s.signal_id = pt.signal_id
        WHERE s.signal_date >= date('now', '-{days} days') {signal_filter}
        GROUP BY s.signal_id
        ORDER BY s.signal_date DESC
    """

    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def calculate_win_rates(signal_type: str = 'all', days: int = 30) -> Dict:
    """
    Calculate win rate statistics
    Win = price increased after signal
    """
    df = get_signal_performance(signal_type, days)

    if df.empty:
        return {
            'total_signals': 0,
            'win_rate_1d': 0,
            'win_rate_7d': 0,
            'win_rate_30d': 0,
            'avg_return_1d': 0,
            'avg_return_7d': 0,
            'avg_return_30d': 0
        }

    stats = {
        'total_signals': len(df)
    }

    for period, col in [('1d', 'day1_change'), ('7d', 'day7_change'), ('30d', 'day30_change')]:
        valid_data = df[col].dropna()
        if len(valid_data) > 0:
            wins = (valid_data > 0).sum()
            stats[f'win_rate_{period}'] = round((wins / len(valid_data)) * 100, 1)
            stats[f'avg_return_{period}'] = round(valid_data.mean(), 2)
        else:
            stats[f'win_rate_{period}'] = 0
            stats[f'avg_return_{period}'] = 0

    return stats


if __name__ == "__main__":
    # Initialize database when run directly
    print("Initializing AI Stock Agent database...")
    init_database()
    print("\n✅ Database ready!")
    print(f"📁 Location: {Path(DB_PATH).absolute()}")
