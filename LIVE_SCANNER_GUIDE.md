# 🔴 LIVE SCANNER - Complete Guide

## ✅ DONE - No More CSV Dependency!

Dashboard ab **directly live market data** se kaam karta hai!

---

## 🎯 WHAT CHANGED:

### Before:
```
Dashboard → scan_results.csv → scan_and_chart.py
(Sirf 11 fixed stocks)
```

### After:
```
Dashboard → live_scanner.py → API in-memory
(~700 stocks LIVE!)
```

---

## 🚀 NEW FILES CREATED:

### 1. `live_scanner.py`
Main scanner module with:
- `scan_market_live(universe, min_score, limit)` → DataFrame
- Parallel scanning using ThreadPoolExecutor
- No CSV files needed
- Returns same columns as before

### 2. Updated `dashboard.py`
New features:
- **🔴 LIVE Scanner toggle** (default ON)
- **Universe selector** (popular/sp500/nasdaq100/all)
- **Cache control** (15-minute auto-cache)
- **Fundamentals toggle** (optional)
- **Max display limit** (performance)
- **CSV fallback mode** (for debugging)

---

## 🎮 HOW TO USE:

### Option 1: Live Mode (Default)

**Start dashboard:**
```bash
streamlit run dashboard.py
```

**In sidebar you'll see:**
```
📊 Data Source
☑ 🔴 LIVE Scanner (In-Memory)

Stock Universe: [all ▼]
☐ Include Fundamentals

♻️ Clear Cache & Rescan
```

**Select universe:**
- **popular**: ~150 stocks (fastest, 1-2 min)
- **sp500**: ~500 stocks (medium, 3-5 min)
- **nasdaq100**: ~100 stocks (fast, 1-2 min)
- **all**: ~700 stocks (slowest, 5-10 min)

**First run:**
- Takes 1-10 minutes (depends on universe)
- Shows spinner: "🔴 Scanning {universe} universe live..."
- Results cached for 15 minutes

**Subsequent visits (within 15 min):**
- INSTANT! (uses cache)
- Sidebar shows: "✅ Scanned 687 stocks"

---

### Option 2: CSV Mode (Fallback)

**Uncheck LIVE Scanner:**
```
☐ 🔴 LIVE Scanner (In-Memory)
```

**Now you'll see old CSV mode:**
```
⚡ CSV Mode Actions
🔄 Run New Scan
```

Uses old flow: scan_and_chart.py → scan_results.csv

---

## 📊 DASHBOARD UI:

### Sidebar (Live Mode):
```
📊 Data Source
☑ 🔴 LIVE Scanner (In-Memory)

Stock Universe: all
☐ Include Fundamentals

♻️ Clear Cache & Rescan

✅ Scanned 687 stocks
Universe: all
Cached until: 02:45 PM

⚙️ Settings
☑ Show Charts
☑ 🎯 Interactive Charts
☐ Only Show Signals
Minimum Score: [0──────10]
Max Rows to Display: 200
```

### Main Display:
```
📊 AI Stock Market Agent
Near real-time intraday market analysis

Total Scanned: 687        ← LIVE COUNT!
🟢 Consolidation: 45
📉 Buy-the-Dip: 12
🚀 Breakout: 8
📈 Volume Spike: 23

📊 Signals | 📈 Charts | 📋 Full Data | 📅 History | 🎯 Performance
```

---

## ⚙️ SETTINGS EXPLAINED:

### Include Fundamentals
```
☐ Include Fundamentals
```

**OFF (default):** Fast, technical analysis only
- Score based on: RSI, ADX, BB, signals
- No P/E, revenue, margins
- 5-10 min for 700 stocks

**ON:** Slower, full analysis
- Fetches fundamentals from Yahoo Finance
- Includes P/E, revenue growth, profit margin
- Combined technical + fundamental score
- 15-20 min for 700 stocks

### Max Rows to Display
```
Max Rows to Display: [200]
```

Limits dashboard rendering for performance.
- Data still scanned completely
- Only top N shown in UI
- Full data in "Full Data" tab

### Minimum Score
```
Minimum Score: [0──────10]
```

Filter stocks by score:
- 0 = show all
- 5 = show only score >= 5
- 8 = show only top quality setups

---

## 🔧 TECHNICAL DETAILS:

### Caching
```python
@st.cache_data(ttl=15 * 60)  # 15 minutes
def load_scan_results_live(universe, min_score, include_fundamentals):
    ...
```

**Cache key:** `(universe, min_score, include_fundamentals)`

**What this means:**
- Changing universe → new scan
- Changing min_score after load → instant filter (same cache)
- Changing fundamentals → new scan
- After 15 min → auto-rescan

**Clear cache manually:**
```
♻️ Clear Cache & Rescan
```

### Parallel Scanning
```python
with ThreadPoolExecutor(max_workers=30) as executor:
    # Scans 30 stocks at once
```

**Speed:**
- Sequential: 700 stocks × 2 sec = 23 minutes
- Parallel (30 workers): ~5-10 minutes

### Error Handling
Individual ticker failures don't crash the whole scan:
```python
def scan_single_ticker(ticker, cfg):
    try:
        # ... scan logic
        return result
    except Exception:
        return None  # Skip this ticker
```

---

## 📁 FILE STRUCTURE:

```
ai_stock_agent_fresh2/
├── live_scanner.py          ← NEW! Main scanner module
├── dashboard.py             ← UPDATED! Uses live scanner
├── scan_and_chart.py        ← Still works (batch mode)
├── top_performers_scanner.py ← Reused for get_stock_universe()
├── config.yaml              ← Same config
└── scan_results.csv         ← OPTIONAL now (not required!)
```

---

## 🎯 USE CASES:

### Intraday Trading:
```
Universe: popular
Include Fundamentals: OFF
Minimum Score: 5
Max Display: 50
```

Fast scans, frequent updates (clear cache hourly).

### Swing Trading:
```
Universe: all
Include Fundamentals: ON
Minimum Score: 3
Max Display: 200
```

Complete market coverage, quality setups.

### Quick Check:
```
Universe: nasdaq100
Include Fundamentals: OFF
Minimum Score: 7
Max Display: 20
```

Top tech movers only.

---

## 🚨 TROUBLESHOOTING:

### "Live scan failed or returned no results"

**Possible causes:**
1. Internet connection issue
2. API rate limiting
3. All stocks failed to fetch

**Solutions:**
- Check internet connection
- Wait 1 minute and clear cache
- Try smaller universe (popular instead of all)
- Check terminal for error messages

### Scan taking too long (>10 min)

**Solutions:**
- Use smaller universe (popular or nasdaq100)
- Disable fundamentals
- Check internet speed
- Reduce max_workers if CPU constrained

### Cache not clearing

**Solutions:**
1. Click "♻️ Clear Cache & Rescan"
2. Restart Streamlit (Ctrl+C and rerun)
3. Delete `.streamlit/cache` folder

### Old CSV mode showing

**Check:**
- Is "🔴 LIVE Scanner" checked?
- Is `live_scanner.py` present?
- Any import errors in terminal?

---

## 📊 PERFORMANCE COMPARISON:

| Mode | Universe | Stocks | Time | Requires |
|------|----------|--------|------|----------|
| CSV | Fixed | 11 | 2 min | scan_results.csv |
| CSV | --all flag | 700 | 20-30 min | scan_results.csv |
| **LIVE** | **popular** | **150** | **1-2 min** | **Nothing!** |
| **LIVE** | **all** | **700** | **5-10 min** | **Nothing!** |

**Live scanner is 2-3x faster** due to parallelization!

---

## 🎉 BENEFITS:

### ✅ No CSV Dependency
- Dashboard works without any CSV files
- No need to run scan_and_chart.py first
- No stale data issues

### ✅ Real-Time
- Scan live market data on-demand
- Always fresh (or 15-min cached)
- No manual scan triggers

### ✅ Flexible Universe
- Choose what to scan (popular/sp500/nasdaq100/all)
- Change anytime without config edits
- Filter by score dynamically

### ✅ Performance
- Parallel scanning (30 workers)
- Smart caching (15 min)
- Efficient memory usage

### ✅ Optional Fundamentals
- Fast mode: technical only
- Full mode: technical + fundamentals
- User choice

---

## 🔄 MIGRATION FROM OLD SYSTEM:

### Old Workflow:
```bash
# Step 1: Run scan
python3 scan_and_chart.py --all

# Step 2: Wait 20-30 min

# Step 3: Start dashboard
streamlit run dashboard.py

# Step 4: Dashboard reads scan_results.csv
```

### New Workflow:
```bash
# Just start dashboard!
streamlit run dashboard.py

# That's it! Live scanner handles everything
```

---

## 📝 DEVELOPER NOTES:

### Adding New Universes:

Edit `top_performers_scanner.py`:
```python
def get_stock_universe(mode: str) -> List[str]:
    if mode == 'my_custom_list':
        return ['AAPL', 'GOOGL', 'MSFT', ...]
```

Then use in dashboard:
```python
universe = st.selectbox(
    "Stock Universe",
    options=["popular", "sp500", "nasdaq100", "all", "my_custom_list"],
    ...
)
```

### Modifying Score Calculation:

Edit `live_scanner.py`:
```python
def calculate_signal_score(signal_flags: Dict, trend: str) -> int:
    score = 0
    # Your custom scoring logic
    return score
```

### Changing Cache Duration:

Edit `dashboard.py`:
```python
@st.cache_data(ttl=30 * 60)  # 30 minutes instead of 15
def load_scan_results_live(...):
    ...
```

---

## ✅ SUMMARY:

**Problem:** Dashboard sirf CSV pe dependent tha, 11 stocks limited

**Solution:** Live in-memory scanner with:
- ~700 stocks support
- Multiple universes
- Smart caching
- No CSV required
- Parallel processing
- Optional fundamentals

**Result:** Dashboard ab fully self-contained hai! 🎉

---

**Start using now:**
```bash
streamlit run dashboard.py
```

**Select universe → Wait 1-10 min → See 700 stocks! 🚀**
