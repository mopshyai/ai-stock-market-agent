# 🚀 HOW TO SCAN ALL 700 STOCKS (Hinglish Guide)

## ⚡ QUICK ANSWER

Dashboard mein **sirf 11 stocks** dikhaaye kyunki:
- `scan_and_chart.py` sirf config.yaml ke fixed tickers scan karta hai
- Dashboard `scan_results.csv` file read karta hai

**AB SAHI SOLUTION:**

---

## 🔥 OPTION 1: SCAN ALL STOCKS (Recommended)

Yeh command chalao to **~700 stocks** scan honge aur dashboard mein dikhenge:

```bash
python3 scan_and_chart.py --all
```

**Kya hoga:**
- S&P 500 (~500 stocks) scan hoga
- NASDAQ-100 (~100 stocks) scan hoga
- Total ~700 stocks
- Time lagega: **20-30 minutes**
- Results `scan_results.csv` mein save honge
- Dashboard mein automatically dikhaai denge

**Progress dekhoge:**
```
🔥 SCANNING ALL MARKET STOCKS (~700 stocks)
⏰ This will take 20-30 minutes...

📊 Total stocks to scan: 687

✓ Progress: 50/687 stocks scanned (7%)
✓ Progress: 100/687 stocks scanned (14%)
✓ Progress: 150/687 stocks scanned (21%)
...
```

---

## 🎯 OPTION 2: FAST SCAN (Sirf top movers)

Agar jaldi results chahiye (2-3 minutes):

```bash
python3 top_performers_scanner.py --mode morning --top 50 --universe all
```

**Output:**
- `morning_picks_YYYYMMDD.csv` file banegi
- Top 50 best stocks with potential gain %
- Time: 5-10 minutes

**Results check karo:**
```bash
cat morning_picks_$(date +%Y%m%d).csv
```

---

## 📊 DASHBOARD UPDATE KAISE HOGA:

### Step 1: Full Scan Run Karo
```bash
python3 scan_and_chart.py --all
```

Wait karo 20-30 min...

### Step 2: Dashboard Refresh Karo

**Local dashboard:**
```bash
streamlit run dashboard.py
```

**Cloud dashboard:**
1. Browser refresh karo (Ctrl+R)
2. Ya "Rerun" button click karo

### Step 3: Check Results

Dashboard pe dikhaai dega:
- **Total Scanned: 687** (pehle 11 tha!)
- Top 50 stocks by score
- Signals, charts, full data

---

## ⚙️ DIFFERENCE BETWEEN TOOLS:

| Tool | Purpose | Stocks | Time | Dashboard Update? |
|------|---------|--------|------|-------------------|
| `scan_and_chart.py` | Main scanner | 11 (default) | 2 min | ✅ Yes |
| `scan_and_chart.py --all` | **Full market scan** | **~700** | **20-30 min** | **✅ Yes** |
| `top_performers_scanner.py` | Quick movers | ~700 | 5-10 min | ❌ No (separate CSV) |
| `automated_top_performers.py` | Scheduled scans | ~700 | Auto | ❌ No (separate alerts) |

---

## 🔧 SETTINGS:

### Default Scan (11 stocks) - Fast
```bash
python3 scan_and_chart.py
```

Uses `config.yaml` tickers:
```yaml
tickers:
  - TSLA
  - AAPL
  - NVDA
  - MSFT
  - AMZN
  - META
  - AMD
  - JPM
  - XOM
  - KO
  - PEP
```

### Full Market Scan (700 stocks) - Slow but Complete
```bash
python3 scan_and_chart.py --all
```

Scans:
- ALL S&P 500 stocks
- ALL NASDAQ-100 stocks
- Automatically fetches from Wikipedia

---

## 📱 OUTPUT EXAMPLES:

### After `--all` Scan:

**Terminal:**
```
=== AI STOCK AGENT SCAN RESULTS ===
Total Stocks Scanned: 687
Showing Top 50 by Score:

Ticker  Score  Trend  RSI   ADX   Close    Action
NVDA    9      UP     68.5  45.2  187.50   BUY
TSLA    8      UP     72.3  38.1  420.00   BUY
META    8      UP     65.2  42.5  608.00   WATCH
MSFT    7      UP     58.9  35.8  509.00   WATCH
... (46 more)

... (637 more stocks in CSV)
```

**Dashboard:**
- Total Scanned: **687**
- Automatically shows all results
- Sorted by score

---

## ⏱️ TIME ESTIMATES:

| Stocks | Default Scan | --all Flag |
|--------|--------------|------------|
| 11 | 2 min | N/A |
| 100 | N/A | 5 min |
| 500 | N/A | 15 min |
| 700 | N/A | 20-30 min |

**Speed depends on:**
- Internet connection
- Market hours (faster during market hours)
- API rate limits

---

## 🚀 AUTOMATION:

### Option A: Scheduled Full Scan

Roz subah 7:45 AM pe full scan:

**1. Create cron job:**
```bash
crontab -e
```

**2. Add line:**
```
45 7 * * * cd /path/to/ai_stock_agent && python3 scan_and_chart.py --all
```

Dashboard automatically update hoga har din!

### Option B: Quick Morning Picks

Agar full scan slow hai, use quick scanner:

```bash
# Morning picks (fast)
python3 automated_top_performers.py
```

Yeh automatic har ghante chalega + morning picks bhejega.

---

## 💡 BEST PRACTICES:

### For Intraday Trading:
```bash
# Quick hourly scans
python3 top_performers_scanner.py --mode hourly --top 20 --universe all
```

### For Swing Trading:
```bash
# Full scan once a day
python3 scan_and_chart.py --all
```

### For Dashboard Viewers:
```bash
# Full scan in morning, then check dashboard
python3 scan_and_chart.py --all
streamlit run dashboard.py
```

---

## 🔥 RECOMMENDED WORKFLOW:

**Morning Routine (Before 9:30 AM):**
```bash
# 1. Full market scan
python3 scan_and_chart.py --all

# 2. Start dashboard
streamlit run dashboard.py

# 3. Start trade monitor
python3 trade_monitor.py
```

**During Market Hours:**
- Dashboard auto-refreshes every 15 min
- Check Telegram for hourly movers
- Monitor trades

**After Market Close:**
- Review `scan_results.csv`
- Check trade performance
- Plan next day

---

## 📊 FILE LOCATIONS:

| File | Content | Used By |
|------|---------|---------|
| `scan_results.csv` | Main scan results (11 or 700 stocks) | **Dashboard** |
| `morning_picks_*.csv` | Top movers from quick scanner | Manual review |
| `hourly_movers_*.csv` | Hourly top movers | Manual review |
| `stock_agent.db` | Database (all scans + trades) | Dashboard history |

---

## ⚠️ IMPORTANT NOTES:

1. **Charts disabled for 700 stocks** - Too slow, sirf CSV results
2. **Error messages hidden** - Clean output for large scans
3. **Progress shown** - Har 50 stocks pe update
4. **Top 50 displayed** - Terminal mein, but CSV mein sab hai
5. **Database updated** - All 700 stocks stored

---

## 🎯 QUICK COMMANDS:

```bash
# Default scan (fast, 11 stocks)
python3 scan_and_chart.py

# Full market scan (slow, 700 stocks)
python3 scan_and_chart.py --all

# View results
cat scan_results.csv | head -50

# Count stocks scanned
wc -l scan_results.csv

# View dashboard
streamlit run dashboard.py

# Check database
sqlite3 stock_agent.db "SELECT COUNT(*) FROM signals;"
```

---

## ✅ SUMMARY:

**Problem:** Dashboard sirf 11 stocks dikha raha tha

**Solution:**
```bash
python3 scan_and_chart.py --all
```

**Result:** Dashboard mein ~700 stocks dikhenge!

**Time:** 20-30 minutes

**Output:**
- `scan_results.csv` updated
- Dashboard automatically shows all
- Database updated
- Top 50 in terminal

---

**Ab jaake test karo:**
```bash
python3 scan_and_chart.py --all
```

**Phir dashboard check karo - 700 stocks dikhenge! 🎉**
