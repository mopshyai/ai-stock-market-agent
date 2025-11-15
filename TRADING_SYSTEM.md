# AI Stock Agent - Trading System

## Overview

This system converts stock signals into **real trade plans** with entry, stop loss, and take profit levels. It monitors trades in real-time and sends Telegram notifications for every step of the trade lifecycle.

## Architecture

```
Signal Generation → Trade Creation → Entry Monitoring → Exit Monitoring → Telegram Alerts
```

### Components

1. **scan_and_chart.py** - Scans stocks and generates signals
2. **signals_to_trades.py** - Converts signals to pending trades
3. **trade_monitor.py** - Monitors trades in real-time (runs continuously)
4. **trade_engine.py** - Core trade logic (entry/exit/risk management)
5. **telegram_bot.py** - Sends trade notifications

---

## How It Works

### 1. Signal to Trade Conversion

When a signal is detected (BUY-DIP, BREAKOUT, etc.), the system calculates:

- **Entry Price**: Current price or breakout level
- **Stop Loss**: Based on ATR or fixed %
- **TP1**: 1R (1x risk)
- **TP2**: 2R (2x risk)
- **Risk Amount**: Fixed $ per trade (from config)

Example trade:
```
Symbol: AAPL
Entry: $150.00
Stop Loss: $147.00  (risk = $3.00)
TP1: $153.00  (+1R)
TP2: $156.00  (+2R)
```

### 2. Trade Lifecycle

```
PENDING → OPEN → CLOSED
```

**PENDING**: Trade setup created, waiting for entry price

**OPEN**: Price hit entry level, trade is active

**CLOSED**: Stop loss or take profit hit

### 3. Exit Reasons

- **STOP**: Price hit stop loss → -1R
- **TP1**: Price hit first target → +1R
- **TP2**: Price hit second target → +2R

---

## Usage

### Step 1: Configure Risk Settings

Edit `config.yaml`:

```yaml
risk_management:
  min_signal_score: 3              # Only trade signals with score ≥ 3
  risk_per_trade_dollars: 100      # Risk $100 per trade
  stop_loss_atr_multiplier: 1.5    # Stop = ATR × 1.5
  max_daily_loss_r: 3.0            # Stop trading at -3R daily loss
  max_open_trades: 5
  max_trades_per_day: 10

trade_monitor:
  check_interval_minutes: 5        # Check trades every 5 minutes
  send_daily_summary: true
  daily_summary_hour: 16           # 4 PM
```

### Step 2: Set Telegram Credentials

```bash
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_CHAT_ID="your_chat_id"
```

### Step 3: Run the System

**Option A: Full Automation**

Terminal 1 - Run scanner:
```bash
python3 scan_and_chart.py
python3 signals_to_trades.py
```

Terminal 2 - Start trade monitor:
```bash
python3 trade_monitor.py
```

The monitor will:
- Check pending trades every 5 minutes
- Activate trades when entry price is hit
- Close trades when SL/TP is hit
- Send Telegram alerts for every event

**Option B: Manual Control**

1. Generate signals:
```bash
python3 scan_and_chart.py
```

2. Create trades (one-time):
```bash
python3 signals_to_trades.py
```

3. Check trade status:
```bash
python3 trade_engine.py
```

---

## Telegram Notifications

You'll receive messages for:

### New Trade Setup
```
📋 NEW TRADE SETUP
──────────────────────────────

AAPL @ $150.00

🎯 Entry: $150.00
🛑 Stop: $147.00
✅ TP1: $153.00 (1R)
🎯 TP2: $156.00 (2R)

📝 BUY-DIP + VOL | UP TREND | Score: 4

Waiting for entry...
```

### Entry Filled
```
▶️  TRADE ENTERED
──────────────────────────────

AAPL @ $150.20

🛑 Stop: $147.00
✅ TP1: $153.00
🎯 TP2: $156.00

Monitoring for exits...
```

### Trade Closed
```
✅ TP1 HIT
──────────────────────────────

AAPL
Entry: $150.00
Exit: $153.00

✅ +1.0R | +$95.00
```

### Daily Summary
```
📊 DAILY TRADE SUMMARY
──────────────────────────────

Trades Today: 5
Wins: 3 | Losses: 2
Win Rate: 60.0%
Avg R: +0.2R

✅ P&L: +$120.00

📂 Open: 2 | Pending: 3
```

---

## Database Schema

### trades table

| Field | Type | Description |
|-------|------|-------------|
| trade_id | INTEGER | Primary key |
| signal_id | INTEGER | Link to signal |
| ticker | TEXT | Stock symbol |
| status | TEXT | PENDING / OPEN / CLOSED |
| entry_price | REAL | Entry level |
| stop_loss | REAL | Stop loss level |
| tp1, tp2 | REAL | Take profit levels |
| entry_time | TIMESTAMP | When trade opened |
| exit_time | TIMESTAMP | When trade closed |
| exit_reason | TEXT | STOP / TP1 / TP2 |
| r_multiple | REAL | R-multiple result |
| pnl | REAL | Profit/loss in $ |

---

## Risk Management

### Position Sizing

The system calculates position size based on fixed risk:

```
Risk per trade: $100
Entry: $150
Stop: $147
Risk per share: $3

Position size = $100 / $3 = 33 shares
```

### Daily Loss Limit

If you lose 3R in a day (default), the system:
- Stops creating new pending trades
- Continues monitoring open trades
- Sends alert: "DAILY LOSS LIMIT HIT"

### Max Trades

- **max_open_trades**: Won't open new trades if limit reached
- **max_trades_per_day**: Won't create more than X trades per day

---

## Example Workflow

**9:30 AM** - Market open
```bash
python3 scan_and_chart.py          # Scan for signals
python3 signals_to_trades.py       # Create pending trades
```

📋 Telegram: "NEW TRADE SETUP - AAPL @ $150"

**9:45 AM** - AAPL hits $150
- Trade monitor detects entry
- Status: PENDING → OPEN

▶️  Telegram: "TRADE ENTERED - AAPL @ $150.20"

**10:30 AM** - AAPL hits TP1 at $153
- Trade monitor detects TP1
- Status: OPEN → CLOSED
- Calculates: +1.0R, +$95 P&L

✅ Telegram: "TP1 HIT - AAPL +1.0R | +$95"

**4:00 PM** - Daily summary

📊 Telegram: "DAILY SUMMARY - 5 trades, 60% win rate, +$120 P&L"

---

## Advanced Features

### Custom Stop Loss

Option 1 - ATR-based (dynamic):
```yaml
use_fixed_stop_pct: false
stop_loss_atr_multiplier: 1.5
```

Option 2 - Fixed % (static):
```yaml
use_fixed_stop_pct: true
fixed_stop_pct: 2.0  # 2% stop loss
```

### Filter Signals

Only trade high-quality signals:
```yaml
min_signal_score: 4  # Score 4+ only (very strong signals)
```

---

## Monitoring Commands

Check pending trades:
```python
from database import get_pending_trades
print(get_pending_trades())
```

Check open trades:
```python
from database import get_open_trades
print(get_open_trades())
```

Get performance summary:
```python
from database import get_trade_summary
print(get_trade_summary(days=30))
```

---

## FAQ

**Q: Can I backtest this?**
A: Yes, modify `trade_engine.py` to use historical data instead of live prices.

**Q: Does this execute real trades?**
A: No. This gives you trade plans and tracks them. You execute manually or connect to broker API.

**Q: What if I want to trade crypto?**
A: Change tickers to crypto symbols (BTC-USD, ETH-USD) and adjust timeframes.

**Q: Can I customize R-multiples?**
A: Yes, edit `calculate_trade_levels()` in `trade_engine.py` to change TP1/TP2 ratios.

**Q: How do I stop the monitor?**
A: Press `Ctrl+C` in the terminal running `trade_monitor.py`

---

## Next Steps

1. ✅ Database with trades table
2. ✅ Trade engine with entry/exit logic
3. ✅ Telegram notifications
4. ✅ Background monitoring
5. ✅ Risk management

**Coming next:**
- Web dashboard showing live trades
- Broker API integration (Alpaca, Interactive Brokers)
- Advanced position sizing (Kelly Criterion, volatility-based)
- Trade journaling and performance analytics

---

## Support

For issues or questions:
- Check logs in terminal output
- Verify Telegram credentials: `python3 telegram_bot.py`
- Test database: `python3 database.py`
