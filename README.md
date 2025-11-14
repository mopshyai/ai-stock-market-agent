
# AI Stock Market Agent

An AI-powered market analysis and signal-generation system that scans stocks, detects high-probability patterns (consolidation, dips, breakouts), generates charts, and delivers automated daily alerts straight to your phone.

---

## 📚 PRODUCT DOCUMENTATION

**🎯 [PRODUCT_SPECIFICATION.md](PRODUCT_SPECIFICATION.md)** — Complete product breakdown, technical architecture, competitive analysis, and launch strategy. **Your pitch deck, investor explanation, and Product Hunt description.**

**🚀 [ELEVATOR_PITCH.md](ELEVATOR_PITCH.md)** — Quick pitches for investors, Product Hunt, social media, and networking events.

**🌐 [LANDING_PAGE.md](LANDING_PAGE.md)** — Complete landing page copy ready for Webflow, Framer, Carrd, or WordPress.

**🎥 [DEMO_VIDEO_SCRIPT.md](DEMO_VIDEO_SCRIPT.md)** — 45-60 second demo video script for your January launch.

**📋 [PRODUCT_HUNT_COMPLETE_GUIDE.md](PRODUCT_HUNT_COMPLETE_GUIDE.md)** — Step-by-step Product Hunt launch guide.

**🔧 [TROUBLESHOOTING.md](TROUBLESHOOTING.md)** — Common issues and solutions.

**🚀 [DEPLOYMENT.md](DEPLOYMENT.md)** — Production deployment guide (cloud, VPS, Docker).

**📝 [CHANGELOG.md](CHANGELOG.md)** — Version history and release notes.

---

## FEATURES

### Core Scanning Engine
- OHLCV data via yfinance
- Technical indicators:
  - Bollinger Bands + BB Width
  - ATR (volatility)
  - ADX (trend strength)
  - RSI (momentum)
  - EMA (20, 50, 200)
- Pattern detection:
  - **Consolidation** (low volatility, potential breakout)
  - **Buy-the-Dip** (oversold conditions)
  - **Breakout** (price breaking resistance with volume)
  - **Volume Spike** (unusual trading activity)

### Automated Alerts
- **Telegram Bot Integration** - Instant signals on your phone
- **Slack Webhook Support** - Team or personal workspace alerts
- Optional chart images
- Filtered alerts (only signal-generating stocks)

### Daily Automation
- Built-in scheduler
- Auto-run at market open or custom times
- Cross-platform (macOS, Windows, Linux)
- `--run-now` mode for on-demand scanning

### Visual Analytics
- **Web Dashboard** (Streamlit UI)
  - Live signal table with color coding
  - Score badges (🔥 ⭐ 📍)
  - Trend indicators
  - Interactive filters
  - Run scans from browser
- Candlestick charts with:
  - MAs (20, 50)
  - Volume
  - Bollinger bands
- Auto-saved to `/charts`

### Data Export & Tracking
- CSV export for all results
- Works with Excel, Sheets, Notion
- **SQLite Database** - automatic historical tracking
- **Signal Score** ranking for top opportunities
- Performance analytics and win rates
- Scan history with timestamps

---

## QUICK START

### 1. Install Dependencies
```bash
python -m venv .venv
source .venv/bin/activate         # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run Your First Scan

**Option A: Command Line**
```bash
python scan_and_chart.py
```

**Option B: Web Dashboard** (Recommended)
```bash
streamlit run dashboard.py
```
Opens at `http://localhost:8501`

You'll get:
- Interactive web interface with all signals
- Console output with all signals
- Charts saved to `/charts`
- Results saved to `scan_results.csv`

---

## SETUP GUIDES

### Launch Web Dashboard
Beautiful web interface for viewing signals and running scans.

👉 **[DASHBOARD_GUIDE.md](DASHBOARD_GUIDE.md)** - Complete dashboard documentation

### Database & Historical Tracking
Automatic storage of all scans with performance analytics.

👉 **[DATABASE_GUIDE.md](DATABASE_GUIDE.md)** - Database documentation and usage

### Set Up Telegram Alerts (Recommended)
Get daily signals delivered to your phone automatically.

👉 **[SETUP_TELEGRAM.md](SETUP_TELEGRAM.md)** - Complete guide with BotFather instructions

### Set Up Daily Automation
Run scans automatically every day at market open.

👉 **[SETUP_AUTOMATION.md](SETUP_AUTOMATION.md)** - Scheduling for Mac, Windows, Linux

---

## CONFIGURATION

Edit `config.yaml` to customize:

### Tickers
```yaml
tickers:
  - TSLA
  - AAPL
  - NVDA
  # Add more...
```

### Signal Thresholds
```yaml
signals:
  consolidation:
    bb_width_mean_max: 0.06    # Max BB width for consolidation
    atr_pct_mean_max: 0.025    # Max ATR % for low volatility
    adx_mean_max: 20           # Max ADX for weak trend
    lookback: 20               # Days to analyze
  buy_the_dip:
    rsi_max: 35                # RSI threshold for oversold
    close_below_lower_bb: true # Must be below lower BB
```

### Alert Settings
```yaml
alerts:
  telegram:
    enabled: true              # Turn on/off
    send_charts: true          # Include chart images
    only_signal_stocks: true   # Filter to signals only
```

---

## USAGE EXAMPLES

### Launch Dashboard (Recommended)
```bash
streamlit run dashboard.py
```
Opens web UI at `http://localhost:8501`

### Manual Scan
```bash
python scan_and_chart.py
```

### Test Telegram Connection
```bash
python telegram_bot.py
```

### Run Scheduler (Daily Automation)
```bash
# Run at 9:30 AM ET daily
python scheduler.py --time 09:30 --timezone US/Eastern

# Run immediately (one-time)
python scheduler.py --run-now
```

---

## PROJECT STRUCTURE

```
ai_stock_agent_fresh2/
├── dashboard.py           # Web UI (Streamlit)
├── scan_and_chart.py      # Main scanning engine
├── database.py            # SQLite database operations
├── telegram_bot.py        # Telegram alert system
├── scheduler.py           # Daily automation
├── utils.py               # Slack webhook helper
├── config.yaml            # Configuration file
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── DASHBOARD_GUIDE.md     # Dashboard documentation
├── DATABASE_GUIDE.md      # Database documentation
├── SETUP_TELEGRAM.md      # Telegram setup guide
├── SETUP_AUTOMATION.md    # Automation setup guide
├── charts/                # Generated chart images
├── scan_results.csv       # Latest scan results
└── stock_agent.db         # SQLite database (auto-created)
```

---

## WHAT YOU'LL RECEIVE

### Console Output
```
=== AI STOCK AGENT SCAN RESULTS ===
Ticker  Consolidating  BuyDip  BBWidth_pct  ATR%  ADX   RSI    Close
AAPL    True          False   3.21         1.85  18.5  52.3   178.50
NVDA    False         True    5.42         2.31  25.7  32.1   495.20
```

### Telegram Message
```
🤖 AI Stock Agent Daily Scan
==============================

📊 Scanned: 11 stocks
🔔 Consolidation Setups: 2
📉 Buy-the-Dip Setups: 1

*AAPL* @ $178.50
   🟢 CONSOLIDATION detected
   • RSI: 52.3
   • ADX: 18.5
   • BB Width: 3.21%
   • ATR: 1.85%
```

Plus individual chart images for each signal.

---

## REQUIREMENTS

- Python 3.8+
- Internet connection (for market data)
- Telegram account (optional, for alerts)

---

## ROADMAP

**✅ Completed:**
- Core scanning engine with 4 signal types
- Web dashboard (Streamlit)
- Historical database + performance tracking
- Telegram & Slack alerts
- Daily automation

**🚧 In Progress (Week 3):**
- Landing page
- Demo video
- Price tracking for win rates

**📅 Future:**
- Multi-timeframe analysis (1D + 4H + 1H)
- MACD / Supertrend indicators
- Backtesting engine
- Real-time alerts (WebSocket)
- Mobile app

---

## DISCLAIMER

This tool is for educational and analytical purposes only.
It is not financial advice. Always perform independent research before trading.

---

## SUPPORT

Having issues? Check:
1. `SETUP_TELEGRAM.md` for Telegram setup
2. `SETUP_AUTOMATION.md` for scheduling help
3. Verify environment variables are set
4. Check log files for errors

---

**Built with Python | Powered by yfinance | Delivered via Telegram**
