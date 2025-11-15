# Quick Command Reference

## Setup (One-time)

```bash
# Set Telegram credentials
source setup_telegram.sh

# Set Twitter credentials
source setup_twitter.sh

# Test connections
python3 telegram_bot.py
python3 twitter_bot.py
```

---

## Daily Workflow

### Option A: Full AI Persona (2 Terminals)

```bash
# Terminal 1 - Automated Content (6 tweets/day at scheduled times)
source setup_twitter.sh
python3 tweet_scheduler.py

# Terminal 2 - Trade Bot (live trade alerts)
source setup_telegram.sh
source setup_twitter.sh
python3 trade_monitor.py
```

### Option B: Manual Trading Only

```bash
# Setup credentials first
source setup_telegram.sh
source setup_twitter.sh

# 1. Scan stocks
python3 scan_and_chart.py

# 2. Create trades
python3 signals_to_trades.py

# 3. Monitor trades (leave running - posts to Telegram + Twitter)
python3 trade_monitor.py
```

### Option C: Interactive Menu

```bash
python3 run_trading_system.py
```

---

## Individual Commands

| Command | What It Does |
|---------|--------------|
| `python3 scan_and_chart.py` | Scan stocks for signals |
| `python3 signals_to_trades.py` | Convert signals → trades |
| `python3 trade_monitor.py` | Monitor trades (runs forever) |
| `python3 tweet_scheduler.py` | 6 auto tweets/day (market + AI) |
| `python3 tweet_scheduler.py test` | Post test tweets NOW |
| `python3 content_engine.py` | Test content generation |
| `python3 trade_engine.py` | One-time trade check |
| `python3 telegram_bot.py` | Test Telegram connection |
| `python3 twitter_bot.py` | Test Twitter connection |
| `python3 database.py` | Initialize database |
| `python3 run_trading_system.py` | Interactive menu |

---

## Quick Checks

```bash
# View pending trades
python3 -c "from database import get_pending_trades; print(get_pending_trades())"

# View open trades
python3 -c "from database import get_open_trades; print(get_open_trades())"

# View summary
python3 -c "from database import get_trade_summary; print(get_trade_summary())"
```

---

## Configuration Files

| File | Purpose |
|------|---------|
| `config.yaml` | Risk settings, signal thresholds |
| `setup_telegram.sh` | Telegram credentials |
| `.env` | Alternative credential storage |

---

## Telegram Credentials

```bash
# Set for current session
export TELEGRAM_BOT_TOKEN="7909396650:AAHRxUnSIZxWdYSCaEcZcUfQVEzZ3r8qbj0"
export TELEGRAM_CHAT_ID="8201781672"

# Or use setup script
source setup_telegram.sh

# Make permanent (add to ~/.zshrc or ~/.bashrc)
echo 'export TELEGRAM_BOT_TOKEN="7909396650:AAHRxUnSIZxWdYSCaEcZcUfQVEzZ3r8qbj0"' >> ~/.zshrc
echo 'export TELEGRAM_CHAT_ID="8201781672"' >> ~/.zshrc
```

---

## Risk Management (config.yaml)

```yaml
risk_management:
  min_signal_score: 3              # Min score to trade
  risk_per_trade_dollars: 100      # $ risk per trade
  max_daily_loss_r: 3.0            # Stop at -3R
  max_open_trades: 5
  max_trades_per_day: 10
```

---

## Trade States

```
PENDING  →  Entry price not hit yet
OPEN     →  Trade active, monitoring exits
CLOSED   →  Hit SL or TP
```

---

## Exit Reasons

```
STOP  →  Stop loss hit (-1R)
TP1   →  First target hit (+1R)
TP2   →  Second target hit (+2R)
```

---

## Full Documentation

- **AI_PERSONA_COMPLETE.md** - Automated Twitter persona (6 tweets/day)
- **QUICKSTART.md** - Step-by-step trading setup
- **TRADING_SYSTEM.md** - Full system explanation
- **TWITTER_SETUP.md** - Twitter/X bot setup & permissions
- **README.md** - Project overview
