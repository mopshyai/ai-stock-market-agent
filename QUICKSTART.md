# QUICKSTART - Trading System

## 1. SETUP TELEGRAM (One-time)

**Option A - Current Session:**
```bash
source setup_telegram.sh
```

**Option B - Auto-load (Permanent):**
```bash
# Add to your shell profile
echo 'export TELEGRAM_BOT_TOKEN="7909396650:AAHRxUnSIZxWdYSCaEcZcUfQVEzZ3r8qbj0"' >> ~/.zshrc
echo 'export TELEGRAM_CHAT_ID="8201781672"' >> ~/.zshrc
source ~/.zshrc
```

**Test:**
```bash
python3 telegram_bot.py
```
You should see: ✅ Telegram bot connected successfully!

---

## 2. RUN THE SYSTEM (3 Commands)

### Step 1: Scan Stocks
```bash
source setup_telegram.sh  # If not already done
python3 scan_and_chart.py
```

This will:
- Scan TSLA, AAPL, NVDA, etc.
- Find signals (BUY-DIP, BREAKOUT, etc.)
- Save to database
- Send Telegram summary

### Step 2: Create Trades
```bash
python3 signals_to_trades.py
```

This will:
- Get signals from scan
- Calculate entry, SL, TP levels
- Create pending trades
- Send Telegram: "📋 NEW TRADE SETUP"

### Step 3: Monitor Trades
```bash
python3 trade_monitor.py
```

This will:
- Check trades every 5 minutes
- Detect entries (PENDING → OPEN)
- Detect exits (STOP/TP1/TP2)
- Send Telegram alerts for each event

**Leave this running in a terminal!**

---

## 3. ALTERNATIVE - Interactive Menu

```bash
source setup_telegram.sh
python3 run_trading_system.py
```

Choose:
- **1** → Scan
- **2** → Create trades
- **3** → Start monitor
- **4** → View summary
- **5** → View pending trades
- **6** → View open trades

---

## 4. FULL WORKFLOW EXAMPLE

**Terminal 1:**
```bash
source setup_telegram.sh

# Morning scan
python3 scan_and_chart.py

# Convert to trades
python3 signals_to_trades.py
```

**Terminal 2:**
```bash
source setup_telegram.sh

# Start monitor (leave running)
python3 trade_monitor.py
```

**What You'll See:**

1. Telegram: "🤖 AI Stock Agent Daily Scan - 11 stocks scanned, 3 signals"
2. Telegram: "📋 NEW TRADE SETUP - AAPL @ $150"
3. (Monitor detects entry)
4. Telegram: "▶️  TRADE ENTERED - AAPL @ $150.20"
5. (Monitor detects TP1 hit)
6. Telegram: "✅ TP1 HIT - AAPL +1.0R | +$95"

---

## 5. CONFIGURE RISK

Edit `config.yaml`:

```yaml
risk_management:
  min_signal_score: 3              # Only trade score 3+
  risk_per_trade_dollars: 100      # Risk $100 per trade
  max_daily_loss_r: 3.0            # Stop at -3R
  max_open_trades: 5
  max_trades_per_day: 10
```

---

## 6. TELEGRAM MESSAGE EXAMPLES

**Signal Found:**
```
🤖 AI Stock Agent Daily Scan
══════════════════════════════

📊 Scanned: 11 stocks
🟢 Consolidation: 1
📉 Buy-the-Dip: 2
🚀 Breakout: 0
📈 Volume Spike: 1

─────────────────────────────

Top Opportunities:

⭐ AAPL @ $150.00 | Score: 4
   📉 BUY-DIP | 📈 VOL SPIKE
   📊 Trend: ⬆️ UPTREND
   • RSI: 32.5 | ADX: 22.3
```

**Trade Setup Created:**
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

**Trade Entered:**
```
▶️  TRADE ENTERED
──────────────────────────────

AAPL @ $150.20

🛑 Stop: $147.00
✅ TP1: $153.00
🎯 TP2: $156.00

Monitoring for exits...
```

**TP1 Hit:**
```
✅ TP1 HIT
──────────────────────────────

AAPL
Entry: $150.00
Exit: $153.00

✅ +1.0R | +$95.00
```

**Daily Summary:**
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

## 7. CHECK STATUS

**Pending trades:**
```bash
python3 -c "from database import get_pending_trades; print(get_pending_trades())"
```

**Open trades:**
```bash
python3 -c "from database import get_open_trades; print(get_open_trades())"
```

**Summary:**
```bash
python3 -c "from database import get_trade_summary; print(get_trade_summary())"
```

---

## 8. TROUBLESHOOTING

**Telegram not working?**
```bash
python3 telegram_bot.py
```

**No signals found?**
- Check config.yaml (signals thresholds may be too strict)
- Market may be choppy (try different tickers)

**Monitor not detecting entries?**
- Price may not have hit entry level yet
- Check with: `python3 -c "from database import get_pending_trades; print(get_pending_trades())"`

**Want to change timeframes?**
Edit config.yaml:
```yaml
data:
  period: "5d"
  interval: "15m"  # Try: 5m, 15m, 30m, 1h, 1d
```

---

## DONE!

System is ready. Bas ab:
```bash
source setup_telegram.sh
python3 scan_and_chart.py
python3 signals_to_trades.py
python3 trade_monitor.py
```

Trade lifecycle Telegram pe live dikhega.
