# AI Stock Market Agent

**AI-powered market analysis delivered to your phone. No terminal, no setup—just open the link.**

An intelligent stock scanner that detects high-probability patterns (consolidation, dips, breakouts), generates interactive charts, and sends automated daily alerts.

---

## 🚀 Try It Live (No Installation)

### [**→ Open Web App**](https://ai-stock-market-agent-mopshyai.streamlit.app) 🌐

**What you'll see:**
- Real-time signal dashboard with scores
- Interactive TradingView-style charts
- Consolidation, buy-dip, breakout, and volume spike alerts
- Historical performance tracking
- Auto-refreshes every 15 minutes

**No Python. No terminal. Just click the link.**

---

## What It Does

### 🔍 Scans Stocks for High-Probability Setups
- **Consolidation** - Low volatility → potential breakout
- **Buy-the-Dip** - Oversold conditions with support
- **Breakout** - Price breaking resistance with volume
- **Volume Spike** - Unusual trading activity

### 📊 Technical Indicators
- Bollinger Bands + BB Width
- ATR (volatility)
- ADX (trend strength)
- RSI (momentum)
- EMAs (20, 50, 200)

### 📱 Automated Alerts
- **Telegram Bot** - Signals delivered to your phone
- **Slack Webhook** - Team notifications
- Daily automation with scheduling
- Optional chart images

### 📈 Interactive Dashboard
- Color-coded signal badges
- Signal score ranking (🔥 ⭐ 📍)
- TradingView-style charts (zoom, pan, crosshair)
- Historical performance analytics
- Win rate tracking (1D, 7D, 30D)

### 💾 Data Export
- CSV export for all results
- SQLite database for history
- Works with Excel, Google Sheets, Notion

---

## 🎯 Who Is This For?

- **Swing traders** - Find setups for multi-day holds
- **Day traders** - Intraday signals with 15-min refresh
- **Investors** - Track consolidations before big moves
- **Quants** - Historical data for backtesting
- **Anyone** - Who wants AI to do the chart scanning

---

## 💻 Self-Hosting (Optional)

Want to run it locally or customize it?

### Quick Start

```bash
# Clone the repo
git clone https://github.com/mopshyai/ai-stock-market-agent.git
cd ai-stock-market-agent

# Run automated setup
./setup.sh

# Launch dashboard
source .venv/bin/activate
streamlit run dashboard.py
```

Opens at `http://localhost:8501`

### Manual Installation

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run dashboard
streamlit run dashboard.py
```

### Configuration

Edit `config.yaml` to customize:

```yaml
tickers:
  - AAPL
  - TSLA
  - NVDA
  # Add your stocks here

signals:
  consolidation:
    bb_width_mean_max: 0.06
    atr_pct_mean_max: 0.025
    adx_mean_max: 20

alerts:
  telegram:
    enabled: true
    send_charts: true
```

---

## 📚 Documentation

### Deployment
| Guide | Description |
|-------|-------------|
| **[DEPLOY_SAAS.md](docs/deployment/DEPLOY_SAAS.md)** | Deploy as hosted web app on Streamlit Cloud |
| **[GITHUB_DEPLOY.md](docs/deployment/GITHUB_DEPLOY.md)** | Step-by-step GitHub deployment |
| **[DEPLOYMENT_CHECKLIST.md](docs/deployment/DEPLOYMENT_CHECKLIST.md)** | Pre/post-deployment verification |

### User Guides
| Guide | Description |
|-------|-------------|
| **[DASHBOARD_GUIDE.md](docs/guides/DASHBOARD_GUIDE.md)** | Complete dashboard documentation |
| **[DATABASE_GUIDE.md](docs/guides/DATABASE_GUIDE.md)** | Database setup and usage |
| **[SETUP_TELEGRAM.md](docs/guides/SETUP_TELEGRAM.md)** | Telegram bot configuration |
| **[SETUP_AUTOMATION.md](docs/guides/SETUP_AUTOMATION.md)** | Daily automation scheduling |
| **[TROUBLESHOOTING.md](docs/guides/TROUBLESHOOTING.md)** | Common issues and solutions |

### Marketing
| Guide | Description |
|-------|-------------|
| **[PRODUCT_SPECIFICATION.md](docs/marketing/PRODUCT_SPECIFICATION.md)** | Full product breakdown |
| **[PRODUCT_HUNT_COMPLETE_GUIDE.md](docs/marketing/PRODUCT_HUNT_COMPLETE_GUIDE.md)** | Product Hunt launch guide |
| **[ELEVATOR_PITCH.md](docs/marketing/ELEVATOR_PITCH.md)** | Quick pitches for investors |
| **[LANDING_PAGE.md](docs/marketing/LANDING_PAGE.md)** | Website copy |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│   Web Dashboard (Streamlit)        │  ← You interact here
├─────────────────────────────────────┤
│   scan_and_chart.py                 │  ← Core scanning engine
│   - Fetches OHLCV data (yfinance)   │
│   - Calculates indicators           │
│   - Detects patterns                │
│   - Generates charts                │
├─────────────────────────────────────┤
│   database.py                       │  ← Persistent storage
│   - SQLite (v1)                     │
│   - Postgres (v2 upgrade)           │
│   - Historical tracking             │
│   - Performance analytics           │
├─────────────────────────────────────┤
│   telegram_bot.py / scheduler.py    │  ← Optional automation
└─────────────────────────────────────┘
```

**Data Flow:**
1. Dashboard triggers scan
2. Engine fetches market data (yfinance)
3. Calculates indicators + detects patterns
4. Saves to database
5. Updates dashboard UI
6. (Optional) Sends Telegram alert

---

## 🚢 Deployment Options

### Option 1: Streamlit Cloud (Recommended for SaaS)
- **Cost:** FREE
- **Setup time:** 5 minutes
- **URL:** `https://yourapp.streamlit.app`
- **Guide:** [DEPLOY_SAAS.md](docs/deployment/DEPLOY_SAAS.md)

### Option 2: Docker + VPS
- **Cost:** $5-10/month (DigitalOcean, Linode)
- **Control:** Full control over infrastructure
- **Guide:** See [DEPLOY_SAAS.md](docs/deployment/DEPLOY_SAAS.md) for alternatives

### Option 3: AWS / GCP / Azure
- **Cost:** ~$10-50/month (depends on usage)
- **Scalability:** Auto-scaling, load balancing
- **Guide:** See [DEPLOY_SAAS.md](docs/deployment/DEPLOY_SAAS.md) for cloud options

---

## 📊 Example Output

### Web Dashboard
```
📊 AI Stock Market Agent
Near real-time intraday market analysis • Auto-refreshing every 15 minutes

Total Scanned: 11  |  🟢 Consolidation: 2  |  📉 Buy-Dip: 1  |  🚀 Breakout: 1  |  📈 Vol Spike: 0

AAPL
$178.50
🔥 Score: 6

Signals: 🟢 CONSOLIDATION | 🚀 BREAKOUT
Trend: ⬆️ UP
RSI: 52.3 | ADX: 18.5 | BB Width: 3.21% | ATR: 1.85%
```

### Telegram Alert
```
🤖 AI Stock Agent Daily Scan
==============================

📊 Scanned: 11 stocks
🔔 Consolidation Setups: 2
📉 Buy-the-Dip Setups: 1

*AAPL* @ $178.50
   🟢 CONSOLIDATION detected
   🔥 Score: 6
   • RSI: 52.3
   • ADX: 18.5
   • BB Width: 3.21%

[Chart image attached]
```

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Python 3.9+ |
| **Web Framework** | Streamlit |
| **Data Source** | yfinance (Yahoo Finance) |
| **Technical Analysis** | pandas, numpy, ta |
| **Charts** | mplfinance, streamlit-lightweight-charts |
| **Database** | SQLite (v1) → Postgres (v2) |
| **Scheduling** | schedule, pytz |
| **Alerts** | Telegram Bot API, Slack Webhooks |
| **Deployment** | Streamlit Cloud / Docker |

---

## 🗓️ Roadmap

### ✅ Completed (v1.0)
- Core scanning engine with 4 signal types
- Web dashboard with interactive charts
- Historical database + performance tracking
- Telegram & Slack alerts
- Daily automation
- SaaS deployment ready

### 🚧 Coming Soon (v2.0)
- [ ] Multi-user accounts (auth)
- [ ] Custom tickers per user
- [ ] Email + SMS alerts
- [ ] Backtesting engine
- [ ] Multi-timeframe analysis (1D + 4H + 1H)
- [ ] MACD / Supertrend indicators
- [ ] Real-time WebSocket alerts
- [ ] Mobile app (React Native)

### 💰 Future (v3.0)
- [ ] Premium data sources (Alpha Vantage, Polygon)
- [ ] Options flow analysis
- [ ] AI-generated trade commentary
- [ ] Portfolio tracking
- [ ] Community features (share signals)

---

## 📈 Performance

### Speed
- Scan 10 stocks: ~10-15 seconds
- Generate charts: ~5 seconds
- Dashboard load: <2 seconds

### Accuracy
- Signal detection: Rule-based (100% consistent)
- Win rate tracking: In development
- False positive rate: Varies by signal type

### Scalability
- Current: 10-50 stocks (free tier)
- Upgrade: 100-500 stocks (requires caching + paid tier)
- Enterprise: 1000+ stocks (requires Postgres + distributed processing)

---

## 🔒 Security & Disclaimer

### Security
- ✅ No user data collected (v1)
- ✅ Secrets stored in environment variables
- ✅ HTTPS by default (Streamlit Cloud)
- ✅ XSRF protection enabled
- ⚠️ No authentication yet (single-tenant)

### Disclaimer

**This tool is for educational and analytical purposes only.**

- ❌ NOT financial advice
- ❌ NOT investment recommendations
- ❌ Past performance ≠ future results
- ✅ Always do your own research
- ✅ Trade at your own risk

---

## 🤝 Contributing

### Local Development

```bash
# Fork the repo
git clone https://github.com/mopshyai/ai-stock-market-agent.git
cd ai-stock-market-agent

# Create feature branch
git checkout -b feature/your-feature

# Make changes
# ... edit code ...

# Test locally
streamlit run dashboard.py

# Commit and push
git add .
git commit -m "Add your feature"
git push origin feature/your-feature

# Open pull request on GitHub
```

### Areas for Contribution
- New signal types (MACD crossover, Supertrend, etc.)
- Additional data sources (Finnhub, IEX Cloud)
- UI/UX improvements
- Performance optimizations
- Documentation
- Bug fixes

---

## 📜 License

MIT License - See [LICENSE](LICENSE) for details.

**TL;DR:** Use freely, modify, distribute. No warranty. Not financial advice.

---

## 🌟 Star History

If you find this useful, give it a star on GitHub! ⭐

---

## 📧 Contact

- **GitHub Issues:** [Report bugs / Request features](https://github.com/mopshyai/ai-stock-market-agent/issues)
- **Discussions:** [Ask questions / Share ideas](https://github.com/mopshyai/ai-stock-market-agent/discussions)

---

## 🙏 Acknowledgments

- **yfinance** - Free market data
- **Streamlit** - Amazing web framework
- **pandas/numpy** - Data processing backbone
- **Technical Analysis library (ta)** - Indicator calculations
- **mplfinance** - Beautiful candlestick charts

---

**Built with Python | Powered by yfinance | Delivered via Streamlit** 🚀

---

## Quick Links

- **[Try Live App](https://ai-stock-market-agent-mopshyai.streamlit.app)** 🌐
- **[GitHub Repository](https://github.com/mopshyai/ai-stock-market-agent)** ⭐
- **[Deploy Your Own](docs/deployment/DEPLOY_SAAS.md)** 🚀
- **[Product Specification](docs/marketing/PRODUCT_SPECIFICATION.md)** 📋
- **[Launch Guide](docs/marketing/PRODUCT_HUNT_COMPLETE_GUIDE.md)** 📣
- **[Troubleshooting](docs/guides/TROUBLESHOOTING.md)** 🔧
