"""
Database module for AI Stock Market Agent - Postgres Edition
Supports both SQLite (local) and PostgreSQL (production)
"""

import os
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from contextlib import contextmanager

# Database configuration
DB_TYPE = os.getenv("DB_TYPE", "sqlite")  # "sqlite" or "postgres"
DB_PATH = "stock_agent.db"  # SQLite path
DATABASE_URL = os.getenv("DATABASE_URL")  # Postgres connection string

SIGNAL_COLUMNS = [
    'Consolidating',
    'BuyDip',
    'Breakout',
    'VolSpike',
    'EMABullish',
    'MACDBullish',
    'VWAPReclaim',
]

# Try to import psycopg2 for Postgres support
try:
    import psycopg2
    import psycopg2.extras
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    if DB_TYPE == "postgres":
        print("⚠️  psycopg2 not installed. Install with: pip install psycopg2-binary")


@contextmanager
def get_connection():
    """Get database connection (SQLite or Postgres based on environment)"""
    if DB_TYPE == "postgres" and DATABASE_URL and POSTGRES_AVAILABLE:
        # Use Postgres
        conn = psycopg2.connect(DATABASE_URL)
        try:
            yield conn
        finally:
            conn.close()
    else:
        # Use SQLite
        conn = sqlite3.connect(DB_PATH)
        try:
            yield conn
        finally:
            conn.close()


def execute_query(query: str, params: tuple = None, fetch: str = None):
    """Execute a query on the current database"""
    with get_connection() as conn:
        cursor = conn.cursor()

        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        if fetch == "one":
            result = cursor.fetchone()
        elif fetch == "all":
            result = cursor.fetchall()
        else:
            result = None

        conn.commit()
        return result


def init_database():
    """Initialize database schema (works for both SQLite and Postgres)"""
    with get_connection() as conn:
        cursor = conn.cursor()

        # Adjust syntax for Postgres vs SQLite
        if DB_TYPE == "postgres":
            serial_type = "SERIAL"
            autoincrement = ""
            timestamp_default = "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
            boolean_type = "BOOLEAN"
        else:
            serial_type = "INTEGER"
            autoincrement = "AUTOINCREMENT"
            timestamp_default = "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
            boolean_type = "BOOLEAN"

        # Scans table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS scans (
                scan_id {serial_type} PRIMARY KEY {autoincrement},
                scan_date TIMESTAMP NOT NULL,
                total_stocks INTEGER NOT NULL,
                signals_found INTEGER NOT NULL,
                created_at {timestamp_default}
            )
        """)

        # Signals table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS signals (
                signal_id {serial_type} PRIMARY KEY {autoincrement},
                scan_id INTEGER NOT NULL,
                ticker TEXT NOT NULL,
                signal_date DATE NOT NULL,
                score INTEGER NOT NULL,
                technical_score INTEGER,
                consolidating {boolean_type},
                buy_dip {boolean_type},
                breakout {boolean_type},
                vol_spike {boolean_type},
                ema_bullish {boolean_type},
                macd_bullish {boolean_type},
                vwap_reclaim {boolean_type},
                trend TEXT,
                price_at_signal REAL NOT NULL,
                rsi REAL,
                adx REAL,
                bb_width_pct REAL,
                atr_pct REAL,
                fundamental_score INTEGER,
                market_cap REAL,
                pe_ratio REAL,
                revenue_growth_pct REAL,
                profit_margin_pct REAL,
                action TEXT,
                action_reason TEXT,
                fundamental_outlook TEXT,
                fundamental_reasons TEXT,
                created_at {timestamp_default},
                FOREIGN KEY (scan_id) REFERENCES scans(scan_id)
            )
        """)

        # Price tracking table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS price_tracking (
                tracking_id {serial_type} PRIMARY KEY {autoincrement},
                signal_id INTEGER NOT NULL,
                ticker TEXT NOT NULL,
                days_after INTEGER NOT NULL,
                price REAL NOT NULL,
                price_change_pct REAL NOT NULL,
                tracked_date DATE NOT NULL,
                created_at {timestamp_default},
                FOREIGN KEY (signal_id) REFERENCES signals(signal_id)
            )
        """)

        # Trades table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS trades (
                trade_id {serial_type} PRIMARY KEY {autoincrement},
                signal_id INTEGER,
                ticker TEXT NOT NULL,
                side TEXT DEFAULT 'BUY',
                status TEXT NOT NULL,
                entry_price REAL NOT NULL,
                stop_loss REAL NOT NULL,
                tp1 REAL NOT NULL,
                tp2 REAL NOT NULL,
                current_price REAL,
                entry_time TIMESTAMP,
                exit_time TIMESTAMP,
                exit_reason TEXT,
                risk_amount REAL,
                r_multiple REAL,
                pnl REAL,
                notes TEXT,
                created_at {timestamp_default},
                updated_at {timestamp_default},
                FOREIGN KEY (signal_id) REFERENCES signals(signal_id)
            )
        """)

        # Create indexes
        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_signals_ticker ON signals(ticker)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_signals_date ON signals(signal_date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tracking_signal ON price_tracking(signal_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_ticker ON trades(ticker)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_status ON trades(status)")
        except Exception as e:
            print(f"Note: Some indexes may already exist: {e}")

        conn.commit()

    db_info = f"{DB_TYPE.upper()}"
    if DB_TYPE == "postgres":
        db_info += f" (Railway)"
    else:
        db_info += f" at {DB_PATH}"

    print(f"✅ Database initialized ({db_info})")


def store_scan_results(results: List[Dict]) -> int:
    """Store scan results in database"""
    if not results:
        return -1

    with get_connection() as conn:
        cursor = conn.cursor()

        # Count signals
        signals_count = sum(
            1 for r in results
            if any(r.get(col) for col in SIGNAL_COLUMNS)
        )

        # Insert scan record
        scan_date = datetime.now()
        cursor.execute("""
            INSERT INTO scans (scan_date, total_stocks, signals_found)
            VALUES (%s, %s, %s) RETURNING scan_id
        """ if DB_TYPE == "postgres" else """
            INSERT INTO scans (scan_date, total_stocks, signals_found)
            VALUES (?, ?, ?)
        """, (scan_date, len(results), signals_count))

        if DB_TYPE == "postgres":
            scan_id = cursor.fetchone()[0]
        else:
            scan_id = cursor.lastrowid

        # Insert individual signals
        for result in results:
            placeholder = "%s" if DB_TYPE == "postgres" else "?"
            cursor.execute(f"""
                INSERT INTO signals (
                    scan_id, ticker, signal_date, score, technical_score,
                    consolidating, buy_dip, breakout, vol_spike, ema_bullish, macd_bullish, vwap_reclaim, trend,
                    price_at_signal, rsi, adx, bb_width_pct, atr_pct,
                    fundamental_score, market_cap, pe_ratio, revenue_growth_pct,
                    profit_margin_pct, action, action_reason, fundamental_outlook,
                    fundamental_reasons
                ) VALUES ({','.join([placeholder]*27)})
            """, (
                scan_id,
                result.get('Ticker'),
                scan_date.date(),
                result.get('Score', 0),
                result.get('TechnicalScore'),
                result.get('Consolidating', False),
                result.get('BuyDip', False),
                result.get('Breakout', False),
                result.get('VolSpike', False),
                result.get('EMABullish', False),
                result.get('MACDBullish', False),
                result.get('VWAPReclaim', False),
                result.get('Trend', 'CHOPPY'),
                result.get('Close', 0.0),
                result.get('RSI'),
                result.get('ADX'),
                result.get('BBWidth_pct'),
                result.get('ATR%'),
                result.get('FundamentalScore'),
                result.get('MarketCap'),
                result.get('PERatio'),
                result.get('RevenueGrowthPct'),
                result.get('ProfitMarginPct'),
                result.get('Action'),
                result.get('ActionReason'),
                result.get('FundamentalOutlook'),
                result.get('FundamentalReasons'),
            ))

        conn.commit()

    print(f"✅ Stored scan {scan_id}: {len(results)} stocks, {signals_count} signals")
    return scan_id


def get_recent_scans(limit: int = 10) -> pd.DataFrame:
    """Get recent scan summary"""
    with get_connection() as conn:
        query = """
            SELECT
                scan_id,
                scan_date,
                total_stocks,
                signals_found,
                ROUND(CAST(signals_found AS FLOAT) / total_stocks * 100, 1) as signal_rate_pct
            FROM scans
            ORDER BY scan_date DESC
            LIMIT %s
        """ if DB_TYPE == "postgres" else """
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
    return df


def create_trade(signal_id: int, ticker: str, entry_price: float,
                 stop_loss: float, tp1: float, tp2: float,
                 risk_amount: float = None, notes: str = None) -> int:
    """Create a new pending trade from a signal"""
    with get_connection() as conn:
        cursor = conn.cursor()

        placeholder = "%s" if DB_TYPE == "postgres" else "?"
        cursor.execute(f"""
            INSERT INTO trades (
                signal_id, ticker, status, entry_price, stop_loss, tp1, tp2, risk_amount, notes
            ) VALUES ({','.join([placeholder]*9)})
            {"RETURNING trade_id" if DB_TYPE == "postgres" else ""}
        """, (signal_id, ticker, 'PENDING', entry_price, stop_loss, tp1, tp2, risk_amount, notes))

        if DB_TYPE == "postgres":
            trade_id = cursor.fetchone()[0]
        else:
            trade_id = cursor.lastrowid

        conn.commit()

    print(f"✅ Created trade {trade_id}: {ticker} PENDING @ {entry_price}")
    return trade_id


def get_open_trades() -> pd.DataFrame:
    """Get all open trades"""
    with get_connection() as conn:
        query = """
            SELECT
                trade_id, ticker, entry_price, stop_loss, tp1, tp2,
                current_price, entry_time, risk_amount, notes
            FROM trades
            WHERE status = 'OPEN'
            ORDER BY entry_time DESC
        """
        df = pd.read_sql_query(query, conn)
    return df


def get_pending_trades() -> pd.DataFrame:
    """Get all pending trades"""
    with get_connection() as conn:
        query = """
            SELECT
                trade_id, ticker, entry_price, stop_loss, tp1, tp2,
                risk_amount, created_at, notes
            FROM trades
            WHERE status = 'PENDING'
            ORDER BY created_at DESC
        """
        df = pd.read_sql_query(query, conn)
    return df


if __name__ == "__main__":
    # Initialize database when run directly
    print("Initializing AI Stock Agent database...")
    print(f"Database type: {DB_TYPE}")
    if DB_TYPE == "postgres" and DATABASE_URL:
        print(f"Postgres URL: {DATABASE_URL[:30]}...")

    init_database()
    print("\n✅ Database ready!")
    if DB_TYPE == "sqlite":
        print(f"📁 Location: {Path(DB_PATH).absolute()}")
