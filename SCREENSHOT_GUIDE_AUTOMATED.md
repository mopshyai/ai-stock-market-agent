# Screenshot Collection Guide - AUTOMATED
**Essential screenshots for launch materials**

---

## CRITICAL SCREENSHOTS NEEDED

### 1. Dashboard Home - Signal Table
**Purpose:** Landing page hero, Product Hunt gallery, demo video
**What to show:**
- Full signal table with at least 8-10 stocks
- Mix of scores (include some 5+, 3-4, and 0-2)
- All columns visible: Score, Ticker, Signals, Trend, Metrics
- Color-coded badges (🔥 ⭐ 📍)
- Clean, professional look

**Setup:**
```bash
streamlit run dashboard.py
# Run fresh scan to populate with today's data
```

**Camera angle:** Full browser window, 1920x1080
**File name:** `dashboard_home.png`

---

### 2. Chart View - Strong Signal
**Purpose:** Demo video, landing page features section
**What to show:**
- Candlestick chart with clear breakout or consolidation pattern
- Bollinger Bands visible
- Moving averages (20, 50)
- Volume bars at bottom
- Clean annotation (if pattern is obvious)

**How to capture:**
- Open charts folder
- Select highest-scoring stock
- Use screenshot tool to capture chart image

**File name:** `chart_breakout_example.png`

---

### 3. Telegram Alert Screenshot
**Purpose:** Landing page, demo video, social proof
**What to show:**
- Phone screen (real or mockup) with Telegram open
- Message from your bot showing:
  - Summary header (stocks scanned, signals found)
  - Individual signal with ticker, score, metrics
  - Chart preview attached
  - Clean, professional formatting

**Setup:**
```bash
python telegram_bot.py
# Ensure test message was sent
# Screenshot from phone or use Telegram Desktop
```

**File name:** `telegram_alert.png`

---

### 4. History/Database View
**Purpose:** Landing page features, demo video analytics section
**What to show:**
- Historical scan records
- Timestamps showing multiple days
- Signal counts over time
- Clean table layout

**How to capture:**
- Dashboard → History tab (if implemented)
- Or SQLite browser showing scans table

**File name:** `history_tracking.png`

---

### 5. Settings/Configuration
**Purpose:** Demo video, documentation
**What to show:**
- config.yaml file open in clean editor
- Highlighted sections: tickers, signals, alerts
- Professional code editor (VS Code recommended)

**File name:** `config_settings.png`

---

### 6. Performance Metrics
**Purpose:** Landing page proof section, demo video
**What to show:**
- Win rate statistics (if available)
- Signal performance breakdown
- Charts or graphs showing results
- Professional data visualization

**Note:** Generate mock data if real tracking data insufficient

**File name:** `performance_metrics.png`

---

## SCREENSHOT SPECIFICATIONS

### Resolution
- **Desktop:** 1920x1080 minimum
- **Mobile mockups:** 375x812 (iPhone size) or 1080x1920 (9:16)

### Format
- **PNG** (for transparency support)
- **High quality** (not compressed)

### Styling
- Clean browser (hide bookmarks bar)
- Consistent zoom level (100%)
- Hide cursor in final shots
- Professional, uncluttered

---

## TOOLS NEEDED

### Screenshot Tools
- **macOS:** Cmd+Shift+4 (selection) or Cmd+Shift+3 (full screen)
- **Windows:** Win+Shift+S or Snipping Tool
- **Linux:** Flameshot, GNOME Screenshot

### Phone Mockups
- **Figma** (free templates)
- **Mockuphone.com**
- **Smartmockups.com**

### Browser Extension
- **Awesome Screenshot** (for clean captures)
- **Fireshot** (full-page screenshots)

---

## QUICK CAPTURE WORKFLOW

### Step 1: Prepare Dashboard
```bash
# Activate environment
source .venv/bin/activate

# Run fresh scan
python scan_and_chart.py

# Launch dashboard
streamlit run dashboard.py
```

### Step 2: Capture Core Shots
1. Dashboard home (full table)
2. Highest-scoring stock details
3. Chart from charts/ folder
4. History tab (if exists)

### Step 3: Telegram Shot
1. Send test alert
```bash
python telegram_bot.py
```
2. Open Telegram on phone or desktop
3. Screenshot clean message

### Step 4: Config Shot
1. Open config.yaml in VS Code
2. Hide sidebar for clean look
3. Screenshot relevant sections

---

## POST-PROCESSING CHECKLIST

- [ ] Crop to remove unnecessary UI
- [ ] Ensure text is readable (not blurry)
- [ ] Add subtle shadow/border if needed
- [ ] Consistent styling across all images
- [ ] File sizes under 500KB each (optimize if needed)

---

## STORAGE

Save all screenshots to:
```
/screenshots_launch/
  ├── dashboard_home.png
  ├── chart_breakout_example.png
  ├── telegram_alert.png
  ├── history_tracking.png
  ├── config_settings.png
  └── performance_metrics.png
```

---

## USAGE PLAN

### Landing Page
- Hero: dashboard_home.png
- Features: telegram_alert.png, chart_breakout_example.png
- Analytics: performance_metrics.png, history_tracking.png

### Product Hunt
- Gallery: All 6 screenshots in order

### Demo Video
- B-roll for each section using appropriate screenshot

### Social Media
- Twitter/LinkedIn: dashboard_home.png with overlay text
- Instagram: Vertical crop of telegram_alert.png

---

**SCREENSHOT GUIDE COMPLETE. Capture, organize, launch. 📸**
