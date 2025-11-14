# Screenshot Guide - AI Stock Market Agent
**Exact specifications for marketing screenshots**

---

## WHY SCREENSHOTS MATTER

Screenshots are your #1 conversion tool:
- Landing page hero image
- Product Hunt gallery
- Twitter/LinkedIn posts
- Demo video frames
- Documentation

**Bad screenshots = low trust = no signups**
**Great screenshots = instant credibility = conversions**

---

## PREPARATION CHECKLIST

### Before You Start
- [ ] Run a fresh scan (`python scan_and_chart.py`)
- [ ] Verify dashboard has real data
- [ ] Clean up desktop (hide icons, close extra windows)
- [ ] Set browser to full screen (F11)
- [ ] Use high DPI display if possible (Retina/4K)
- [ ] Close unnecessary browser tabs
- [ ] Disable desktop notifications

### Dashboard Prep
```bash
# 1. Run scan to get fresh data
python scan_and_chart.py

# 2. Launch dashboard
streamlit run dashboard.py

# 3. Wait for full load (check all tabs work)
```

### Screen Resolution
- **Minimum:** 1920x1080
- **Recommended:** 2560x1440 or 3840x2160 (4K)
- **Browser:** 100% zoom (no scaling)

---

## SCREENSHOT #1: DASHBOARD HOME (Hero Image)

**Purpose:** Landing page hero, Product Hunt #1 image, main marketing asset

**What to Show:**
- Signals tab (default view)
- Signal table with multiple stocks
- At least 2-3 high-score signals (5+)
- Score badges visible (🔥⭐📍)
- Trend indicators (⬆️ UP)
- Clean, uncluttered

**How to Capture:**
1. Open dashboard: `streamlit run dashboard.py`
2. Click "📊 Signals" tab
3. Set filters to show signals: Toggle "Only Show Signals" ON
4. Adjust "Minimum Score" to 2 or 3 (show variety)
5. Wait for page to fully load
6. Press `Cmd+Shift+4` (Mac) or `Windows+Shift+S` (Windows)
7. Select entire dashboard area (exclude browser chrome if possible)

**Framing:**
- Include: Signal table, score column, ticker column, signal badges
- Exclude: Browser tabs, bookmarks bar, desktop background
- Focus: Center the signal table

**File Name:** `dashboard-home-hero.png`

**Editing:**
- Crop to 16:9 ratio (1920x1080 or 2560x1440)
- Slight shadow/border for depth (optional)
- Increase contrast slightly
- Export as PNG (high quality)

**Example Annotation:**
```
[Screenshot shows:]
- AAPL: Score 5 ⭐ | Consolidation + Uptrend
- AMD: Score 7 🔥 | Breakout + Volume Spike
- NVDA: Score 4 ⭐ | Volume Spike + Uptrend
```

---

## SCREENSHOT #2: SIGNAL TABLE (Detail View)

**Purpose:** Feature section, "How It Works" visual

**What to Show:**
- Close-up of signal table rows
- All columns visible: Ticker, Score, Signals, Trend, Price, Indicators
- Highlight 1-2 top signals
- Clear badge visibility

**How to Capture:**
1. Same setup as Screenshot #1
2. Zoom in slightly (Cmd+Plus or browser zoom to 125%)
3. Capture just the table area (not full dashboard)
4. Include header row for context

**Framing:**
- Show 3-5 stock rows
- All columns visible and readable
- Crisp, high contrast

**File Name:** `signal-table-detail.png`

---

## SCREENSHOT #3: HISTORY TAB

**Purpose:** Show historical tracking, prove longevity

**What to Show:**
- 📅 History tab selected
- Scan history table (10+ past scans if possible)
- "Top Signals" section below
- Data-rich, proves system is used over time

**How to Capture:**
1. Click "📅 History" tab
2. Scroll to show both scan list + top signals
3. Capture full tab view

**Framing:**
- Include tab navigation at top
- Show date range of scans
- Visible signal counts

**File Name:** `history-tab.png`

**Note:** If you just started, run scans over 3-5 days to build history before capturing.

---

## SCREENSHOT #4: PERFORMANCE ANALYTICS

**Purpose:** Show data-driven approach, win rates

**What to Show:**
- 🎯 Performance tab
- Overall statistics (total signals, avg score)
- Win rate section (even if empty, shows capability)
- Top tickers table

**How to Capture:**
1. Click "🎯 Performance" tab
2. Scroll to show all metrics
3. Capture full tab

**Framing:**
- Metrics cards at top
- Win rate section (middle)
- Top tickers (bottom)

**File Name:** `performance-analytics.png`

---

## SCREENSHOT #5: CHARTS TAB

**Purpose:** Visual appeal, technical analysis proof

**What to Show:**
- 📈 Charts tab
- 2-4 candlestick charts visible
- Charts with clear indicators (MAs, volume)
- High-quality chart images

**How to Capture:**
1. Click "📈 Charts" tab
2. Ensure charts have loaded (check `charts/` folder has PNG files)
3. Scroll to show grid of charts
4. Capture 2x2 or 2x3 grid

**Framing:**
- Multiple charts in view
- Ticker names visible
- Clean grid layout

**File Name:** `charts-tab.png`

---

## SCREENSHOT #6: TELEGRAM NOTIFICATION

**Purpose:** Show mobile delivery, instant alerts

**What to Show:**
- Telegram app on phone or desktop
- Message from your bot
- Signal summary (ticker, score, signals)
- Chart preview (if you configured chart sending)

**How to Capture:**

**Option A: Phone Screenshot**
1. Send test alert: Configure Telegram, run scan
2. Wait for message to arrive
3. Take phone screenshot (Power + Volume on most phones)
4. Crop to show message clearly

**Option B: Desktop Telegram**
1. Open Telegram desktop app
2. Navigate to your bot chat
3. Screenshot the message
4. Crop to show just the message bubble

**Framing:**
- Clean, readable text
- Bot name visible at top
- Message content clear
- Avoid personal info

**File Name:** `telegram-alert.png`

---

## SCREENSHOT #7: FULL DATA TAB (Optional)

**Purpose:** Show data export capability, transparency

**What to Show:**
- 📋 Full Data tab
- Complete results table
- Download CSV button visible

**How to Capture:**
1. Click "📋 Full Data" tab
2. Scroll to show table + download button
3. Capture

**File Name:** `full-data-export.png`

---

## SCREENSHOT #8: MOBILE VIEW (Optional)

**Purpose:** Show responsiveness, mobile-friendly

**What to Show:**
- Dashboard on phone/tablet
- Streamlit mobile view (it's responsive)

**How to Capture:**
1. Open dashboard on phone browser
2. Navigate to Signals tab
3. Take screenshot on phone
4. Or use browser dev tools (F12 → responsive design mode)

**File Name:** `mobile-dashboard.png`

---

## BATCH CAPTURE WORKFLOW

### Efficient Method (All Screenshots in 10 Minutes)

1. **Setup (5 min)**
   - Run fresh scan
   - Launch dashboard
   - Open Telegram desktop
   - Prepare screenshot tool

2. **Capture Session (5 min)**
   - Screenshot #1: Dashboard home → Save
   - Screenshot #2: Zoom in on table → Save
   - Screenshot #3: History tab → Save
   - Screenshot #4: Performance tab → Save
   - Screenshot #5: Charts tab → Save
   - Screenshot #6: Telegram app → Save
   - Screenshot #7: Full Data tab → Save

3. **Post-Process (10 min)**
   - Rename files descriptively
   - Crop to 16:9 where needed
   - Adjust brightness/contrast (subtle)
   - Add subtle border/shadow (optional)
   - Export all as PNG (high quality)
   - Organize in `/screenshots` folder

---

## EDITING GUIDELINES

### Do:
✅ Crop to remove browser chrome
✅ Increase contrast slightly (5-10%)
✅ Sharpen text (if needed)
✅ Add subtle drop shadow for depth
✅ Maintain aspect ratio (16:9 or 4:3)
✅ Save as PNG (lossless)

### Don't:
❌ Over-saturate colors
❌ Add fake data
❌ Use stock photos
❌ Heavy filters
❌ Compress to JPEG (artifacts)
❌ Resize smaller than 1920px wide

---

## SCREENSHOT SPECS FOR PLATFORMS

### Landing Page Hero
- **Size:** 1920x1080 or 2560x1440
- **Format:** PNG or WebP
- **Optimization:** Compress to <500KB
- **Which Shot:** #1 (Dashboard Home)

### Product Hunt Gallery
- **Images:** 5-8 images
- **Size:** 1280x800 minimum (16:10 ratio)
- **Format:** PNG or JPG
- **Order:**
  1. Dashboard Home (hero)
  2. Signal Table Detail
  3. Telegram Alert
  4. Charts Tab
  5. History Tab
  6. Performance Analytics

### Twitter/LinkedIn Posts
- **Size:** 1200x675 (16:9)
- **Format:** PNG or JPG
- **Compression:** <1MB
- **Annotation:** Add text overlay or arrow pointing to key feature

### Documentation/Blog
- **Size:** 1600x900 or original
- **Format:** PNG (with transparency if needed)
- **Annotation:** Arrows, circles, text labels welcome

---

## ANNOTATION TOOLS (Optional)

### For Adding Arrows/Text to Screenshots

**Mac:**
- Preview (built-in, basic)
- Skitch (free, easy annotations)
- CleanShot X (paid, professional)

**Windows:**
- Snip & Sketch (built-in)
- Greenshot (free)
- ShareX (free, powerful)

**Cross-Platform:**
- Figma (free, web-based)
- Canva (free, templates)
- Photoshop/GIMP (advanced)

### Common Annotations:
- 🎯 Circle important UI elements
- ➡️ Arrow pointing to key features
- 💬 Text bubble with explanation
- ⭐ Highlight high scores with glow effect

---

## FILE ORGANIZATION

```
screenshots/
├── raw/               # Original, unedited captures
│   ├── dashboard-home.png
│   ├── signal-table.png
│   └── ...
├── edited/            # Cropped, color-corrected
│   ├── dashboard-home-hero.png
│   ├── signal-table-detail.png
│   └── ...
└── annotated/         # With text/arrows for specific use
    ├── dashboard-home-landing.png
    ├── telegram-alert-twitter.png
    └── ...
```

---

## QUALITY CHECKLIST

Before publishing any screenshot, verify:

- [ ] Resolution: 1920px wide minimum
- [ ] Aspect ratio: 16:9 or 16:10
- [ ] Text: Crisp and readable (no blur)
- [ ] Data: Real (no Lorem Ipsum or placeholder data)
- [ ] UI: Clean (no error messages, loading spinners)
- [ ] Personal info: Removed (no API keys, personal emails)
- [ ] File size: Optimized (<1MB for web)
- [ ] Format: PNG for sharp UI, JPG for photos
- [ ] Filename: Descriptive (not "Screen Shot 2025-01-13.png")

---

## SCREENSHOT USE CASES

### Where You'll Use These

1. **Landing Page** → Screenshot #1 (hero), #2 (features), #6 (how it works)
2. **Product Hunt** → All screenshots (#1-6)
3. **Twitter Launch** → #1 + #6 (dashboard + Telegram)
4. **LinkedIn Post** → #1 (professional, data-focused)
5. **Demo Video** → All (screen recordings)
6. **Documentation** → #1, #3, #4, #5 (guide users)
7. **Investor Deck** → #1, #4 (traction, analytics)

---

## ADVANCED: ANIMATED SCREENSHOTS

For extra engagement on social media:

### Create GIFs
1. Record 3-5 second screen interaction
2. Use QuickTime (Mac) or OBS (Windows) to record
3. Convert to GIF with Gifski or ezgif.com
4. Show: scan running → results populating

### Use Cases:
- Twitter threads (show signal appearing)
- Landing page (dashboard animation)
- Product Hunt (interactive preview)

**Tools:**
- **Mac:** QuickTime + Gifski
- **Windows:** ScreenToGif
- **Cross-platform:** OBS Studio + ezgif.com

---

## FINAL DELIVERABLES

After following this guide, you should have:

✅ **7 core screenshots** (PNG, 1920x1080+)
✅ **Organized folder structure** (raw/edited/annotated)
✅ **Platform-specific exports** (Product Hunt, landing page, social)
✅ **Optional: 1-2 animated GIFs** (for social media)

**Total time investment:** 30-45 minutes
**ROI:** Professional-looking launch that converts

---

**SCREENSHOT GUIDE COMPLETE. Capture, edit, convert. 📸**
