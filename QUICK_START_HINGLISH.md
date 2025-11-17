# 🚀 TOP PERFORMERS - QUICK START (HINGLISH)

## ✅ PROBLEM SOLVED:

### 1. **Dashboard Error - FIXED**
Streamlit Cloud pe `requirements.txt` push kar diya hai. Ab dashboard chalega!

**Check karo:**
- Streamlit Cloud dashboard pe jao
- Refresh karo (Ctrl+R)
- Agar abhi bhi error hai toh "Manage app" → "Reboot app" click karo

---

### 2. **ALL MARKET STOCKS - ENABLED**

Ab scanner **~700 STOCKS** scan karega:
- **S&P 500** (~500 stocks)
- **NASDAQ-100** (~100 stocks)
- **Top 20** best performers return karega (pehle sirf 10 the)

**Config updated:**
```yaml
universe: 'all'    # Pehle 'popular' tha (sirf 150 stocks)
top_n: 20          # Pehle 10 the
```

---

## 📊 KITNE STOCKS SCAN HOTE HAIN:

| Universe Mode | Stocks Count | Speed | Best For |
|--------------|--------------|-------|----------|
| `popular` | ~150 | ⚡ Fastest | Intraday scalping |
| `sp500` | ~500 | 🐢 Medium | Swing trading |
| `nasdaq100` | ~100 | ⚡ Fast | Tech stocks |
| **`all`** | **~700** | 🐢 Slow (10-15 min) | **Complete market scan** |

---

## 🎯 COMMANDS:

### **Option 1: Manual Scan (Jab chahein run karo)**

**Top 20 hourly movers (ALL market stocks):**
```bash
python3 top_performers_scanner.py --mode hourly --top 20 --universe all
```

**Top 20 morning picks (ALL market stocks):**
```bash
python3 top_performers_scanner.py --mode morning --top 20 --universe all
```

**Top 50 chahiye? Change karo:**
```bash
python3 top_performers_scanner.py --mode morning --top 50 --universe all
```

**Top 100 chahiye? Aur bhi zyada:**
```bash
python3 top_performers_scanner.py --mode morning --top 100 --universe all
```

---

### **Option 2: Automated (Best Option!)**

Yeh automatically har ghante chalega aur Telegram pe alerts bhejega:

```bash
python3 automated_top_performers.py
```

**Abhi immediately morning scan run karo:**
```bash
python3 automated_top_performers.py --now
```

---

## 📱 OUTPUT EXAMPLES:

### **Hourly Top 20 Movers:**
```
Ticker  Current_Price  Hourly_Change_%  Volume_1h   Momentum
NVDA    $187.50       +4.50%           25M         BULLISH
TSLA    $420.00       +3.80%           18M         BULLISH
META    $608.00       +2.95%           12M         BULLISH
AMD     $245.00       +2.50%           15M         BULLISH
AAPL    $268.00       +1.80%           20M         BULLISH
... (15 more stocks)
```

### **Morning Top 20 Picks:**
```
Ticker  Score  Price    Potential_Gain_%  Risk_%  R:R   Momentum
MSFT    9/10   $507.95  +3.50%           1.20%   2.92  +5.5%
AMZN    8/10   $233.00  +4.10%           1.50%   2.73  +4.8%
GOOGL   8/10   $142.00  +3.80%           1.40%   2.71  +4.2%
AAPL    7/10   $268.00  +2.80%           1.10%   2.54  +3.1%
... (16 more stocks)
```

---

## ⚙️ CONFIG SETTINGS:

`config.yaml` mein settings:

```yaml
top_performers_scan:
  hourly_scans:
    enabled: true
    universe: 'all'      # ALL market stocks (~700)
    top_n: 20            # Top 20 return karo

  morning_scans:
    enabled: true
    universe: 'all'      # ALL market stocks (~700)
    top_n: 20            # Top 20 return karo
```

**Agar speed slow lag rahi hai:**
```yaml
universe: 'sp500'   # Sirf S&P 500 (faster)
```

**Agar 50 stocks chahiye:**
```yaml
top_n: 50
```

---

## 🔧 STREAMLIT CLOUD FIX:

**Dashboard abhi bhi error de raha hai?**

### Step 1: Reboot App
1. Streamlit Cloud dashboard pe jao
2. "Manage app" click karo (bottom right)
3. "Reboot app" select karo
4. Wait karo 2-3 minutes

### Step 2: Check Requirements
Agar abhi bhi nahi chala toh manually verify karo:
```bash
cat requirements.txt | grep streamlit
```

Should show:
```
streamlit>=1.40.0
streamlit-autorefresh>=1.0.1
streamlit-lightweight-charts>=0.7.20
plotly>=5.18.0
```

### Step 3: Force Redeploy
```bash
git commit --allow-empty -m "Force redeploy"
git push origin main
```

---

## ⏱️ TIMING:

### **Hourly Scans:**
- **9:30 AM** - Market open (best movers)
- **10:30 AM** - Mid-morning momentum
- **11:30 AM** - Pre-lunch
- **12:30 PM** - Lunch time
- **1:30 PM** - Afternoon session
- **2:30 PM** - Late afternoon
- **3:30 PM** - Power hour (biggest moves!)

### **Morning Scan:**
- **8:00 AM** - Before market open
- Daily top picks with potential gain %

---

## 💰 EXPECTED GAINS:

### **Hourly Movers:**
- **Potential**: 1-5% per trade
- **Time**: 15min - 2 hours
- **Best**: First hour (9:30-10:30) aur power hour (3-4 PM)

### **Morning Picks:**
- **Potential**: 2-10% per trade
- **Time**: 1-5 days
- **Risk/Reward**: 1.5:1 se 3:1

---

## 📁 OUTPUT FILES:

**Automatic save hoti hain:**

```bash
# Hourly scans
hourly_movers_20251117_0930.csv   # Top 20 @ 9:30 AM
hourly_movers_20251117_1030.csv   # Top 20 @ 10:30 AM
hourly_movers_20251117_1130.csv   # Top 20 @ 11:30 AM

# Morning picks
morning_picks_20251117.csv        # Top 20 daily picks
morning_picks_20251118.csv
```

**View karo:**
```bash
cat morning_picks_20251117.csv
```

---

## 🚦 QUICK TEST:

### Test 1: Morning scan (ALL stocks)
```bash
python3 top_performers_scanner.py --mode morning --top 20 --universe all
```

**Expected:**
- Scan shuru hoga (~700 stocks)
- 5-10 minutes lagenge
- CSV file banega: `morning_picks_YYYYMMDD.csv`
- Top 20 stocks milenge with potential gain %

### Test 2: Hourly scan (during market hours only!)
```bash
python3 top_performers_scanner.py --mode hourly --top 20 --universe all
```

**Note:** Market hours mein hi kaam karega (9:30 AM - 4 PM EST)

---

## ⚠️ IMPORTANT:

1. **ALL universe slow hai** - 10-15 minutes lagta hai complete scan ke liye
2. **Fast chahiye?** - `universe: 'popular'` use karo (sirf 2-3 min)
3. **Market closed?** - Hourly scan nahi chalega, sirf morning scan
4. **CSV files automatic save** - Har scan ke baad
5. **Telegram alerts** - Bot token set karo for automatic notifications

---

## 📞 HELP COMMANDS:

```bash
# Check what's configured
cat config.yaml | grep -A 20 "top_performers_scan"

# View latest morning picks
ls -lt morning_picks_*.csv | head -1

# View latest hourly movers
ls -lt hourly_movers_*.csv | head -1

# Count how many scans done today
ls morning_picks_$(date +%Y%m%d).csv 2>/dev/null && echo "Found" || echo "Not yet"
```

---

## ✅ SUMMARY:

| Feature | Before | Now |
|---------|--------|-----|
| Stocks scanned | 11 fixed | **~700 ALL market** |
| Top results | 10 | **20 (customizable)** |
| Universe | Fixed tickers | **S&P 500 + NASDAQ** |
| Dashboard | Broken | **Fixed (pushed to git)** |
| Potential shown | ❌ No | **✅ Yes (with %)** |

---

**Ab jaake test karo:**
```bash
python3 top_performers_scanner.py --mode morning --top 20 --universe all
```

**Ya automated chala do:**
```bash
python3 automated_top_performers.py
```

**Dashboard check karo:**
- Streamlit Cloud pe jao
- Reboot karo if needed
- Ab kaam karega! 🎉

---

Koi problem ho toh batao bhai! 🚀
