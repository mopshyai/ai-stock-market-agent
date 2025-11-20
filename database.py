import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple

import pandas as pd

DB_PATH = "stock_agent.db"
DATABASE_URL = os.getenv("DATABASE_URL")
DB_IS_POSTGRES = bool(DATABASE_URL)

if DB_IS_POSTGRES:
    import psycopg2
    from psycopg2 import sql
else:
    psycopg2 = None

SIGNAL_COLUMNS = [
    'Consolidating',
    'BuyDip',
    'Breakout',
    'VolSpike',
    'EMABullish',
    'MACDBullish',
    'VWAPReclaim',
]


def get_db_connection():
    """Return a DB connection to Postgres (if configured) or SQLite."""
    if DB_IS_POSTGRES:
        return psycopg2.connect(DATABASE_URL)
    return sqlite3.connect(DB_PATH)


def format_sql(query: str) -> str:
    """Convert SQLite-style placeholders to Postgres-style when needed."""
    if DB_IS_POSTGRES:
        return query.replace("?", "%s")
    return query


def ensure_column(cursor, table: str, column: str, definition: str):
    """Add a column to a table if it does not exist."""
    if DB_IS_POSTGRES:
        cursor.execute("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = %s AND column_name = %s
        """, (table, column))
        if not cursor.fetchone():
            cursor.execute(
                sql.SQL("ALTER TABLE {} ADD COLUMN {} {}").format(
                    sql.Identifier(table),
                    sql.Identifier(column),
                    sql.SQL(definition)
                )
            )
    else:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = {row[1] for row in cursor.fetchall()}
        if column not in columns:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def init_database():
    """Initialize or migrate database schema."""
    conn = get_db_connection()
    cursor = conn.cursor()

    if DB_IS_POSTGRES:
        scans_table = """
            CREATE TABLE IF NOT EXISTS scans (
                scan_id SERIAL PRIMARY KEY,
                scan_date TIMESTAMP NOT NULL,
                total_stocks INTEGER NOT NULL,
                signals_found INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        signals_table = """
            CREATE TABLE IF NOT EXISTS signals (
                signal_id SERIAL PRIMARY KEY,
                scan_id INTEGER NOT NULL,
                ticker TEXT NOT NULL,
                signal_date DATE NOT NULL,
                score INTEGER NOT NULL,
                technical_score INTEGER,
                consolidating BOOLEAN,
                buy_dip BOOLEAN,
                breakout BOOLEAN,
                vol_spike BOOLEAN,
                ema_bullish BOOLEAN,
                macd_bullish BOOLEAN,
                vwap_reclaim BOOLEAN,
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (scan_id) REFERENCES scans(scan_id)
            )
        """
        price_tracking_table = """
            CREATE TABLE IF NOT EXISTS price_tracking (
                tracking_id SERIAL PRIMARY KEY,
                signal_id INTEGER NOT NULL,
                ticker TEXT NOT NULL,
                days_after INTEGER NOT NULL,
                price REAL NOT NULL,
                price_change_pct REAL NOT NULL,
                tracked_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (signal_id) REFERENCES signals(signal_id)
            )
        """
        trades_table = """
            CREATE TABLE IF NOT EXISTS trades (
                trade_id SERIAL PRIMARY KEY,
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (signal_id) REFERENCES signals(signal_id)
            )
        """
    else:
        scans_table = """
            CREATE TABLE IF NOT EXISTS scans (
                scan_id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_date TIMESTAMP NOT NULL,
                total_stocks INTEGER NOT NULL,
                signals_found INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        signals_table = """
            CREATE TABLE IF NOT EXISTS signals (
                signal_id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_id INTEGER NOT NULL,
                ticker TEXT NOT NULL,
                signal_date DATE NOT NULL,
                score INTEGER NOT NULL,
                technical_score INTEGER,
                consolidating BOOLEAN,
                buy_dip BOOLEAN,
                breakout BOOLEAN,
                vol_spike BOOLEAN,
                ema_bullish BOOLEAN,
                macd_bullish BOOLEAN,
                vwap_reclaim BOOLEAN,
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (scan_id) REFERENCES scans(scan_id)
            )
        """
        price_tracking_table = """
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
        """
        trades_table = """
            CREATE TABLE IF NOT EXISTS trades (
                trade_id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (signal_id) REFERENCES signals(signal_id)
            )
        """

    cursor.execute(scans_table)
    cursor.execute(signals_table)
    ensure_column(cursor, "signals", "technical_score", "INTEGER")
    ensure_column(cursor, "signals", "fundamental_score", "INTEGER")
    ensure_column(cursor, "signals", "market_cap", "REAL")
    ensure_column(cursor, "signals", "pe_ratio", "REAL")
    ensure_column(cursor, "signals", "revenue_growth_pct", "REAL")
    ensure_column(cursor, "signals", "profit_margin_pct", "REAL")
    ensure_column(cursor, "signals", "action", "TEXT")
    ensure_column(cursor, "signals", "action_reason", "TEXT")
    ensure_column(cursor, "signals", "fundamental_outlook", "TEXT")
    ensure_column(cursor, "signals", "fundamental_reasons", "TEXT")
    ensure_column(cursor, "signals", "ema_bullish", "BOOLEAN")
    ensure_column(cursor, "signals", "macd_bullish", "BOOLEAN")
    ensure_column(cursor, "signals", "vwap_reclaim", "BOOLEAN")

    cursor.execute(price_tracking_table)
    cursor.execute(trades_table)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_signals_ticker ON signals(ticker)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_signals_date ON signals(signal_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tracking_signal ON price_tracking(signal_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_ticker ON trades(ticker)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_status ON trades(status)")

    conn.commit()
    conn.close()
    print(f"✅ Database initialized at {DATABASE_URL if DB_IS_POSTGRES else DB_PATH}")


def store_scan_results(results: List[Dict]) -> int:
    """Persist scan results and return the scan_id."""
    if not results:
        return -1

    conn = get_db_connection()
    cursor = conn.cursor()

    signals_count = sum(
        1 for r in results
        if any(r.get(col) for col in SIGNAL_COLUMNS)
    )

    scan_date = datetime.now()
    insert_scan_sql = """
        INSERT INTO scans (scan_date, total_stocks, signals_found)
        VALUES (?, ?, ?)
    """
    if DB_IS_POSTGRES:
        cursor.execute(format_sql(insert_scan_sql) + " RETURNING scan_id", (scan_date, len(results), signals_count))
        scan_id = cursor.fetchone()[0]
    else:
        cursor.execute(insert_scan_sql, (scan_date, len(results), signals_count))
        scan_id = cursor.lastrowid

    insert_signal_sql = """
        INSERT INTO signals (
            scan_id, ticker, signal_date, score, technical_score,
            consolidating, buy_dip, breakout, vol_spike, ema_bullish, macd_bullish, vwap_reclaim, trend,
            price_at_signal, rsi, adx, bb_width_pct, atr_pct,
            fundamental_score, market_cap, pe_ratio, revenue_growth_pct,
            profit_margin_pct, action, action_reason, fundamental_outlook,
            fundamental_reasons
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    for result in results:
        cursor.execute(format_sql(insert_signal_sql), (
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
    conn.close()

    print(f"✅ Stored scan {scan_id}: {len(results)} stocks, {signals_count} signals")
    return scan_id


def _read_dataframe(query: str, params: Tuple = None) -> pd.DataFrame:
    conn = get_db_connection()
    try:
        formatted = format_sql(query)
        if not params:
            df = pd.read_sql_query(formatted, conn)
        else:
            df = pd.read_sql_query(formatted, conn, params=params)
    finally:
        conn.close()
    return df


def get_recent_scans(limit: int = 10) -> pd.DataFrame:
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
    return _read_dataframe(query, (limit,))


def get_signals_by_date_range(start_date: str, end_date: str) -> pd.DataFrame:
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
    return _read_dataframe(query, (start_date, end_date))


def get_top_signals(days: int = 30, min_score: int = 3) -> pd.DataFrame:
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
    return _read_dataframe(query, (cutoff_date, min_score))


def get_signal_stats() -> Dict:
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM signals")
    total_signals = cursor.fetchone()[0]

    stats = {'total_signals': total_signals}

    cursor.execute("SELECT COUNT(*) FROM signals WHERE consolidating = 1")
    stats['consolidation_count'] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM signals WHERE buy_dip = 1")
    stats['buy_dip_count'] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM signals WHERE breakout = 1")
    stats['breakout_count'] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM signals WHERE vol_spike = 1")
    stats['vol_spike_count'] = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(score) FROM signals")
    avg_score = cursor.fetchone()[0]
    stats['avg_score'] = round(avg_score, 2) if avg_score else 0

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
    conn = get_db_connection()
    cursor = conn.cursor()

    cutoff_date = (datetime.now() - timedelta(days=30)).date()
    cursor.execute(format_sql("""
        SELECT signal_id, signal_date, price_at_signal
        FROM signals
        WHERE ticker = ? AND signal_date >= ?
    """), (ticker, cutoff_date))

    signals = cursor.fetchall()

    for signal_id, signal_date_str, price_at_signal in signals:
        signal_date = datetime.strptime(signal_date_str, '%Y-%m-%d').date()
        days_after = (datetime.now().date() - signal_date).days

        if days_after > 0 and price_at_signal > 0:
            price_change_pct = ((current_price - price_at_signal) / price_at_signal) * 100

            cursor.execute(format_sql("""
                SELECT tracking_id FROM price_tracking
                WHERE signal_id = ? AND days_after = ?
            """), (signal_id, days_after))

            existing = cursor.fetchone()

            if existing:
                cursor.execute(format_sql("""
                    UPDATE price_tracking
                    SET price = ?, price_change_pct = ?, tracked_date = ?
                    WHERE tracking_id = ?
                """), (current_price, price_change_pct, datetime.now().date(), existing[0]))
            else:
                cursor.execute(format_sql("""
                    INSERT INTO price_tracking (signal_id, ticker, days_after, price, price_change_pct, tracked_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                """), (signal_id, ticker, days_after, current_price, price_change_pct, datetime.now().date()))

    conn.commit()
    conn.close()


def get_signal_performance(signal_type: str = 'all', days: int = 30) -> pd.DataFrame:
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
    if DB_IS_POSTGRES:
        query = query.replace("date('now', '-{days} days')".format(days=days),
                              f"(CURRENT_DATE - INTERVAL '{days} days')")

    return _read_dataframe(query, ())


def calculate_win_rates(signal_type: str = 'all', days: int = 30) -> Dict:
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


def create_trade(signal_id: int, ticker: str, entry_price: float,
                 stop_loss: float, tp1: float, tp2: float,
                 risk_amount: float = None, notes: str = None) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()

    insert_sql = """
        INSERT INTO trades (
            signal_id, ticker, status, entry_price, stop_loss, tp1, tp2, risk_amount, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    params = (signal_id, ticker, 'PENDING', entry_price, stop_loss, tp1, tp2, risk_amount, notes)

    if DB_IS_POSTGRES:
        cursor.execute(format_sql(insert_sql) + " RETURNING trade_id", params)
        trade_id = cursor.fetchone()[0]
    else:
        cursor.execute(insert_sql, params)
        trade_id = cursor.lastrowid

    conn.commit()
    conn.close()

    print(f"✅ Created trade {trade_id}: {ticker} PENDING @ {entry_price}")
    return trade_id


def get_pending_trades() -> pd.DataFrame:
    query = """
        SELECT
            trade_id, ticker, entry_price, stop_loss, tp1, tp2,
            risk_amount, created_at, notes
        FROM trades
        WHERE status = 'PENDING'
        ORDER BY created_at DESC
    """
    return _read_dataframe(query, ())


def get_open_trades() -> pd.DataFrame:
    query = """
        SELECT
            trade_id, ticker, entry_price, stop_loss, tp1, tp2,
            current_price, entry_time, risk_amount, notes
        FROM trades
        WHERE status = 'OPEN'
        ORDER BY entry_time DESC
    """
    return _read_dataframe(query, ())


def update_trade_status(trade_id: int, status: str, current_price: float = None) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()

    update_fields = ["status = ?", "updated_at = CURRENT_TIMESTAMP"]
    params = [status]

    if current_price is not None:
        update_fields.append("current_price = ?")
        params.append(current_price)

    if status == 'OPEN':
        update_fields.append("entry_time = CURRENT_TIMESTAMP")

    params.append(trade_id)
    query = f"UPDATE trades SET {', '.join(update_fields)} WHERE trade_id = ?"

    cursor.execute(format_sql(query), tuple(params))
    conn.commit()
    conn.close()


def close_trade(trade_id: int, exit_price: float, exit_reason: str) -> Dict:
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(format_sql("""
        SELECT ticker, entry_price, stop_loss, tp1, tp2, risk_amount
        FROM trades
        WHERE trade_id = ?
    """), (trade_id,))

    row = cursor.fetchone()
    if not row:
        conn.close()
        return None

    ticker, entry_price, stop_loss, tp1, tp2, risk_amount = row

    risk_per_share = entry_price - stop_loss
    profit_per_share = exit_price - entry_price

    if risk_per_share > 0:
        r_multiple = profit_per_share / risk_per_share
    else:
        r_multiple = 0

    if risk_amount and risk_per_share > 0:
        shares = risk_amount / risk_per_share
        pnl = shares * profit_per_share
    else:
        pnl = 0

    cursor.execute(format_sql("""
        UPDATE trades
        SET status = 'CLOSED',
            current_price = ?,
            exit_time = CURRENT_TIMESTAMP,
            exit_reason = ?,
            r_multiple = ?,
            pnl = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE trade_id = ?
    """), (exit_price, exit_reason, r_multiple, pnl, trade_id))

    conn.commit()
    conn.close()

    result = {
        'trade_id': trade_id,
        'ticker': ticker,
        'entry_price': entry_price,
        'exit_price': exit_price,
        'exit_reason': exit_reason,
        'r_multiple': round(r_multiple, 2),
        'pnl': round(pnl, 2) if pnl else 0
    }

    print(f"✅ Closed trade {trade_id}: {ticker} @ {exit_price} | {exit_reason} | {r_multiple:.2f}R")
    return result


def get_trade_summary(days: int = 30) -> Dict:
    conn = get_db_connection()
    cursor = conn.cursor()

    cutoff_date = (datetime.now() - timedelta(days=days)).date()

    cursor.execute(format_sql("""
        SELECT COUNT(*) FROM trades
        WHERE DATE(created_at) >= ?
    """), (cutoff_date,))
    total = cursor.fetchone()[0]

    cursor.execute(format_sql("""
        SELECT
            COUNT(*) as closed_count,
            SUM(CASE WHEN r_multiple > 0 THEN 1 ELSE 0 END) as wins,
            AVG(r_multiple) as avg_r,
            SUM(pnl) as total_pnl
        FROM trades
        WHERE status = 'CLOSED' AND DATE(exit_time) >= ?
    """), (cutoff_date,))
    row = cursor.fetchone()
    closed_count, wins, avg_r, total_pnl = row

    cursor.execute("SELECT COUNT(*) FROM trades WHERE status = 'OPEN'")
    open_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM trades WHERE status = 'PENDING'")
    pending_count = cursor.fetchone()[0]

    conn.close()

    win_rate = (wins / closed_count * 100) if closed_count else 0

    return {
        'total_trades': total,
        'open': open_count,
        'pending': pending_count,
        'closed': closed_count or 0,
        'wins': wins or 0,
        'win_rate': round(win_rate, 1),
        'avg_r': round(avg_r, 2) if avg_r else 0,
        'total_pnl': round(total_pnl, 2) if total_pnl else 0
    }


if __name__ == "__main__":
    print("Initializing AI Stock Agent database...")
    init_database()
    print("\n✅ Database ready!")
    location = DATABASE_URL if DB_IS_POSTGRES else Path(DB_PATH).absolute()
    print(f"📁 Location: {location}")
