# Dashboard Guide

Your AI Stock Agent now has a beautiful web interface powered by Streamlit.

---

## Quick Start

### 1. Install Streamlit

If you haven't already:
```bash
pip install streamlit
```

Or reinstall all dependencies:
```bash
pip install -r requirements.txt
```

### 2. Launch the Dashboard

```bash
streamlit run dashboard.py
```

The dashboard will open automatically in your browser at `http://localhost:8501`

---

## Features

### 📊 Signals Tab

**Top Opportunities View**
- Stocks ranked by Signal Score (highest first)
- Color-coded score badges:
  - 🔥 Score 5+ (High priority)
  - ⭐ Score 3-4 (Medium priority)
  - 📍 Score 1-2 (Low priority)

**Signal Types Displayed:**
- 🟢 CONSOLIDATION
- 📉 BUY-THE-DIP
- 🚀 BREAKOUT
- 📈 VOLUME SPIKE

**Trend Direction:**
- ⬆️ UPTREND (green)
- ⬇️ DOWNTREND (red)
- ↔️ CHOPPY (orange)

**Key Metrics:**
- RSI (momentum)
- ADX (trend strength)
- BB Width (volatility)
- ATR% (average true range)

---

### 📈 Charts Tab

**Visual Analysis**
- Candlestick charts for all scanned stocks
- Moving averages (20, 50)
- Volume bars
- Bollinger Bands

**Grid Layout**
- 2 charts per row
- Auto-filtered to match current signal filters
- High-resolution images saved from scans

---

### 📋 Full Data Tab

**Complete Results Table**
- All stocks and their metrics
- Sortable columns
- Downloadable as CSV
- Boolean signals shown as ✅ or —

**Export Options:**
- Download button for CSV export
- Filename includes today's date
- Compatible with Excel, Google Sheets, Notion

---

## Sidebar Controls

### ⚡ Quick Actions

**🔄 Run New Scan**
- Executes `scan_and_chart.py`
- Takes 1-2 minutes depending on market data
- Updates all data and charts
- Auto-refreshes dashboard

**Last Scan Info**
- Shows date and time of last scan
- Updates automatically after new scans

---

### ⚙️ Settings

**Show Charts**
- Toggle chart display on/off
- Useful for faster loading with many stocks

**Only Show Signals**
- Filter to show only stocks with detected signals
- Hides stocks with Score = 0

**Minimum Score Slider**
- Filter by minimum signal score (0-8)
- Quickly find highest-priority opportunities
- Example: Set to 3 to see only ⭐ and 🔥 stocks

---

## Summary Metrics (Top Row)

**5 Key Stats:**
1. **Total Scanned** - Number of stocks analyzed
2. **🟢 Consolidation** - Low volatility setups
3. **📉 Buy-the-Dip** - Oversold opportunities
4. **🚀 Breakout** - Momentum plays
5. **📈 Volume Spike** - Unusual activity

Updates in real-time based on active filters.

---

## Workflow Examples

### Daily Routine

**Morning Check (9:30 AM ET)**
1. Open dashboard: `streamlit run dashboard.py`
2. Click "Run New Scan"
3. Review top-scored opportunities
4. Check charts for visual confirmation
5. Export CSV for tracking

### Quick Filter

**Find High-Priority Breakouts**
1. Set "Minimum Score" to 4
2. Enable "Only Show Signals"
3. Look for 🚀 BREAKOUT badge
4. Check trend is ⬆️ UPTREND
5. Verify volume spike 📈

### Export Workflow

**Share with Team/Save for Later**
1. Go to "Full Data" tab
2. Apply desired filters
3. Click "📥 Download CSV"
4. File saved with date: `stock_signals_20250113.csv`
5. Open in Excel or import to Notion

---

## Keyboard Shortcuts

While dashboard is running:

- `R` - Rerun the app (refresh data)
- `C` - Clear cache
- `Ctrl+C` (terminal) - Stop the server

---

## Troubleshooting

### "No scan results found"

**Solution:**
1. Run a scan first: `python scan_and_chart.py`
2. Or click "Run New Scan" in sidebar
3. Verify `scan_results.csv` exists in project folder

### Charts not showing

**Solution:**
1. Check that `/charts` folder exists
2. Verify PNG files are present (e.g., `AAPL.png`)
3. Enable "Show Charts" in sidebar settings

### Dashboard won't start

**Solution:**
```bash
# Check Streamlit is installed
pip install streamlit --upgrade

# Verify you're in the correct directory
ls -la  # Should see dashboard.py

# Run with verbose logging
streamlit run dashboard.py --logger.level=debug
```

### Scan button doesn't work

**Solution:**
1. Verify `scan_and_chart.py` exists
2. Check Python path in terminal: `which python3`
3. Ensure all dependencies installed: `pip install -r requirements.txt`

### Slow performance

**Solution:**
1. Reduce number of tickers in `config.yaml`
2. Disable "Show Charts" in sidebar
3. Use filters to reduce displayed stocks
4. Run scan manually before opening dashboard

---

## Customization

### Change Port

Default: `http://localhost:8501`

Run on different port:
```bash
streamlit run dashboard.py --server.port 8502
```

### Remote Access

Allow access from other devices on your network:
```bash
streamlit run dashboard.py --server.address 0.0.0.0
```

Access from other device: `http://YOUR_IP:8501`

### Auto-Refresh

Add to `.streamlit/config.toml`:
```toml
[server]
runOnSave = true
```

### Theme

Streamlit auto-detects light/dark mode from browser.

Force dark mode:
```bash
streamlit run dashboard.py --theme.base dark
```

---

## Demo & Screenshots

### For Marketing

**Capture Dashboard:**
1. Set filters to show best signals
2. Take screenshot (Cmd+Shift+4 on Mac, Windows+Shift+S on Windows)
3. Use for landing page, Twitter, LinkedIn

**Record Video:**
1. Open dashboard
2. Use screen recording (QuickTime on Mac, Xbox Game Bar on Windows)
3. Show: Run Scan → View Results → Filter → Export
4. Keep under 60 seconds for social media

---

## Production Deployment

### Option 1: Streamlit Cloud (Free)

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repository
4. Deploy with one click
5. Get public URL: `https://yourapp.streamlit.app`

### Option 2: Docker

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "dashboard.py"]
```

### Option 3: VPS (DigitalOcean, AWS, etc.)

```bash
# Install dependencies
pip install -r requirements.txt

# Run with nohup
nohup streamlit run dashboard.py --server.port 8501 &

# Or use systemd service (Linux)
# See SETUP_AUTOMATION.md for systemd examples
```

---

## Next Steps

**Week 1 (Current):** ✅ Dashboard built
**Week 2:** Add database tracking (historical performance)
**Week 3:** Polish for launch (landing page, demo video)

---

## FAQ

**Q: Can I run scans from the dashboard?**
A: Yes! Click "Run New Scan" in the sidebar.

**Q: How often should I run scans?**
A: Daily at market open (9:30 AM ET) or market close (4:00 PM ET).

**Q: Can others access my dashboard?**
A: Only if you deploy it publicly or allow network access.

**Q: Does it work on mobile?**
A: Yes! Streamlit is mobile-responsive. Access via phone browser.

**Q: Can I customize the colors/layout?**
A: Yes, edit the CSS in `dashboard.py` lines 13-40.

---

**Your dashboard is production-ready for January launch!** 🚀
