# Database Guide

Your AI Stock Agent now tracks historical performance with an SQLite database.

---

## Overview

The database automatically stores every scan, enabling:
- Historical signal tracking
- Performance analytics
- Win rate calculations
- Top-performing signal identification
- Trend analysis over time

---

## Database Schema

### Tables

**1. `scans`** - Scan metadata
```sql
- scan_id (PRIMARY KEY)
- scan_date (TIMESTAMP)
- total_stocks (INTEGER)
- signals_found (INTEGER)
- created_at (TIMESTAMP)
```

**2. `signals`** - Individual stock signals
```sql
- signal_id (PRIMARY KEY)
- scan_id (FOREIGN KEY)
- ticker (TEXT)
- signal_date (DATE)
- score (INTEGER)
- consolidating (BOOLEAN)
- buy_dip (BOOLEAN)
- breakout (BOOLEAN)
- vol_spike (BOOLEAN)
- trend (TEXT)
- price_at_signal (REAL)
- rsi, adx, bb_width_pct, atr_pct (REAL)
- created_at (TIMESTAMP)
```

**3. `price_tracking`** - Price movements after signals
```sql
- tracking_id (PRIMARY KEY)
- signal_id (FOREIGN KEY)
- ticker (TEXT)
- days_after (INTEGER)
- price (REAL)
- price_change_pct (REAL)
- tracked_date (DATE)
- created_at (TIMESTAMP)
```

---

## Automatic Storage

Every time you run `scan_and_chart.py`, results are automatically saved to the database:

```bash
python scan_and_chart.py
```

Output:
```
✅ Stored scan 1: 11 stocks, 2 signals
📊 Scan #1 stored in database
```

---

## Database Location

**File:** `stock_agent.db` (SQLite database)
**Location:** Project root directory

To view the file:
```bash
ls -lh stock_agent.db
```

---

## Initialization

The database is automatically initialized on first use. To manually initialize:

```bash
python database.py
```

Output:
```
Initializing AI Stock Agent database...
✅ Database initialized at stock_agent.db
✅ Database ready!
📁 Location: /path/to/stock_agent.db
```

---

## Viewing Data

### Option 1: Dashboard (Recommended)

```bash
streamlit run dashboard.py
```

Navigate to:
- **📅 History tab** - View all scans and top signals
- **🎯 Performance tab** - Analytics and win rates

### Option 2: Command Line (SQLite)

```bash
sqlite3 stock_agent.db
```

Query examples:
```sql
-- View all scans
SELECT * FROM scans ORDER BY scan_date DESC;

-- View signals from last scan
SELECT ticker, score, price_at_signal, trend
FROM signals
WHERE scan_id = (SELECT MAX(scan_id) FROM scans);

-- Count signals by type
SELECT
    SUM(CASE WHEN consolidating = 1 THEN 1 ELSE 0 END) as consolidation,
    SUM(CASE WHEN buy_dip = 1 THEN 1 ELSE 0 END) as buy_dip,
    SUM(CASE WHEN breakout = 1 THEN 1 ELSE 0 END) as breakout,
    SUM(CASE WHEN vol_spike = 1 THEN 1 ELSE 0 END) as vol_spike
FROM signals;
```

### Option 3: Python Script

```python
from database import get_recent_scans, get_top_signals, get_signal_stats

# Get last 10 scans
scans = get_recent_scans(limit=10)
print(scans)

# Get top signals from last 30 days
signals = get_top_signals(days=30, min_score=3)
print(signals)

# Get statistics
stats = get_signal_stats()
print(f"Total signals: {stats['total_signals']}")
print(f"Average score: {stats['avg_score']}")
```

---

## Features

### 1. Scan History

Track all your scans:
- Date and time of scan
- Number of stocks analyzed
- Number of signals detected
- Signal rate percentage

**Access:** Dashboard → History tab

### 2. Top Signals

View highest-scoring signals from any time period:
- Filter by days (7, 30, 90)
- Filter by minimum score
- See all signal types and indicators
- Track prices at signal time

**Access:** Dashboard → History tab → "Top Signals" section

### 3. Performance Analytics

Overall statistics:
- Total signals generated
- Average signal score
- Breakdown by signal type (CONS, DIP, BREAKOUT, VOL)
- Most frequently signaled tickers

**Access:** Dashboard → Performance tab

### 4. Win Rate Tracking (Future Feature)

Track signal success rates:
- 1-day, 7-day, 30-day performance
- Price change percentages
- Filter by signal type
- Calculate average returns

**Note:** Requires automated price updates (Week 3 feature)

---

## Database Functions

### Storing Data

```python
from database import store_scan_results

results = [
    {'Ticker': 'AAPL', 'Score': 5, 'Close': 175.50, ...},
    {'Ticker': 'TSLA', 'Score': 3, 'Close': 250.00, ...}
]

scan_id = store_scan_results(results)
print(f"Stored as scan #{scan_id}")
```

### Querying Data

```python
from database import (
    get_recent_scans,
    get_signals_by_date_range,
    get_top_signals,
    get_signal_stats,
    calculate_win_rates
)

# Recent scans
scans = get_recent_scans(limit=5)

# Signals in date range
signals = get_signals_by_date_range('2025-01-01', '2025-01-31')

# Top signals
top = get_top_signals(days=30, min_score=4)

# Statistics
stats = get_signal_stats()

# Win rates (requires price tracking)
win_rates = calculate_win_rates(signal_type='breakout', days=30)
```

---

## Data Retention

### Current Behavior
- All scans are stored permanently
- No automatic deletion
- Database grows over time

### Managing Database Size

**Check size:**
```bash
ls -lh stock_agent.db
```

**Clear old data (SQLite):**
```sql
-- Delete scans older than 90 days
DELETE FROM scans WHERE scan_date < date('now', '-90 days');

-- Delete orphaned signals
DELETE FROM signals WHERE scan_id NOT IN (SELECT scan_id FROM scans);

-- Vacuum to reclaim space
VACUUM;
```

**Backup database:**
```bash
cp stock_agent.db stock_agent_backup_$(date +%Y%m%d).db
```

---

## Export Data

### CSV Export (Dashboard)

1. Open dashboard: `streamlit run dashboard.py`
2. Go to "Full Data" tab
3. Click "📥 Download CSV"

### SQL Export

```bash
sqlite3 stock_agent.db
.mode csv
.output signals_export.csv
SELECT * FROM signals;
.quit
```

### Excel Export (Python)

```python
import pandas as pd
from database import get_top_signals

df = get_top_signals(days=90, min_score=2)
df.to_excel('signals.xlsx', index=False)
```

---

## Troubleshooting

### "Database is locked"

**Cause:** Another process is using the database
**Solution:**
```bash
# Check for running processes
ps aux | grep python

# Kill if needed
pkill -f streamlit
pkill -f scan_and_chart
```

### "No such table"

**Cause:** Database not initialized
**Solution:**
```bash
python database.py
```

### "No data in History tab"

**Cause:** No scans stored yet
**Solution:**
```bash
python scan_and_chart.py
```

### "Error loading performance data"

**Cause:** Database query failed
**Solution:**
1. Check database exists: `ls stock_agent.db`
2. Verify schema: `python database.py`
3. Check dashboard logs in terminal

---

## Advanced Usage

### Custom Queries

Create your own analytics:

```python
import sqlite3
import pandas as pd

conn = sqlite3.connect('stock_agent.db')

# Average score by trend direction
query = """
    SELECT trend, AVG(score) as avg_score, COUNT(*) as count
    FROM signals
    GROUP BY trend
    ORDER BY avg_score DESC
"""

df = pd.read_sql_query(query, conn)
print(df)

conn.close()
```

### Automated Reports

Generate weekly reports:

```python
from database import get_top_signals
from datetime import datetime

signals = get_top_signals(days=7, min_score=3)

report = f"""
Weekly Signal Report - {datetime.now().strftime('%Y-%m-%d')}
================================================
Top Signals: {len(signals)}

{signals[['ticker', 'score', 'trend', 'price_at_signal']].to_string()}
"""

with open(f"report_{datetime.now().strftime('%Y%m%d')}.txt", 'w') as f:
    f.write(report)
```

---

## Week 3 Feature: Price Tracking

Coming soon - automatic price updates for win rate calculation:

**Planned features:**
- Daily price updates for active signals
- Automatic win/loss calculation
- Performance charts and trends
- Signal type comparison
- Best/worst performing patterns

**Implementation:**
```python
# Future feature
from database import update_price_tracking
import yfinance as yf

ticker = "AAPL"
current_price = yf.Ticker(ticker).info['currentPrice']
update_price_tracking(ticker, current_price)
```

---

## Database Maintenance

### Optimize Performance

```sql
-- Rebuild indexes
REINDEX;

-- Analyze query performance
ANALYZE;

-- Vacuum database
VACUUM;
```

### Weekly Maintenance Script

```bash
#!/bin/bash
# weekly_maintenance.sh

# Backup
cp stock_agent.db "backups/stock_agent_$(date +%Y%m%d).db"

# Optimize
sqlite3 stock_agent.db "VACUUM; ANALYZE;"

echo "✅ Database maintenance complete"
```

---

## Migration & Portability

### Moving to Another Machine

```bash
# Copy these files
- stock_agent.db (database)
- config.yaml (settings)
- charts/ (chart images)

# On new machine
pip install -r requirements.txt
python database.py  # Verify schema
streamlit run dashboard.py
```

### Merging Databases

```python
import sqlite3

# Attach second database
conn = sqlite3.connect('stock_agent.db')
conn.execute("ATTACH DATABASE 'other_stock_agent.db' AS other")

# Copy data
conn.execute("INSERT INTO scans SELECT * FROM other.scans")
conn.execute("INSERT INTO signals SELECT * FROM other.signals")

conn.commit()
conn.close()
```

---

**Your database is now tracking every scan automatically!**

Next: Week 3 → Landing page, demo video, and launch preparation
