# Twitter/X Bot Setup - AI Trading Persona

## System is Ready - Just Need Permissions

Your Twitter bot is **fully coded and integrated**. The only thing needed is enabling write permissions in your Twitter Developer account.

---

## Current Status

✅ **Code Complete:**
- twitter_bot.py - Live trade posting
- Telegram + Twitter dual-channel alerts
- Daily/weekly summaries
- Auto-engagement (optional)

❌ **API Permissions Needed:**
```
Error: "Your client app is not configured with the appropriate oauth1 app permissions"
```

This means your Twitter App needs **Read and Write** permissions enabled.

---

## Fix: Enable Write Permissions (5 Minutes)

### Step 1: Go to Developer Portal

https://developer.twitter.com/en/portal/dashboard

### Step 2: Select Your App/Project

Find the app you created for these API keys

### Step 3: Enable Read & Write

1. Go to **App Settings** → **User authentication settings**
2. Click **Set up** or **Edit**
3. Enable **OAuth 1.0a**
4. Set App permissions to **Read and Write**
5. **Save**

### Step 4: Regenerate Keys (Important!)

After changing permissions, you MUST regenerate:
- Access Token
- Access Token Secret

(API Key and Secret stay the same)

### Step 5: Update setup_twitter.sh

Replace the new tokens in `setup_twitter.sh`:

```bash
export TWITTER_ACCESS_TOKEN="your_new_token"
export TWITTER_ACCESS_SECRET="your_new_secret"
```

### Step 6: Test

```bash
source setup_twitter.sh
python3 twitter_bot.py
```

You should see:
```
✅ Twitter bot connected successfully!
```

And a tweet will appear on your timeline.

---

## Alternative: Apply for Elevated Access

If you can't enable write permissions with Free tier, apply for Elevated:

https://developer.x.com/en/portal/petition/standard/basic-info

**Fill out:**
- Use case: "Automated trading journal / performance tracker"
- How you'll use the API: "Post trade entries, exits, and daily P&L summaries from algorithmic trading system"
- Will you make Twitter content available to government: No

**Approval time:** Usually 1-3 days

Once approved, all permissions unlock automatically.

---

## What the Bot Will Post

### 1. New Trade Setup
```
📋 NEW TRADE SETUP | $AAPL
Entry: $150.00
Stop: $147.00
TP1: $153.00 | TP2: $156.00
R/R: 1:1.0

Signal: BUY-DIP + VOL | UP TREND | Score: 4

#trading #stocks #algotrading #AI
```

### 2. Trade Entered
```
▶️  TRADE ENTERED | $AAPL
Entry: $150.20
Stop: $147.00
TP1: $153.00 | TP2: $156.00

Position active. Monitoring exits...

#tradeentry #stocktrading #systematictrading
```

### 3. Trade Closed
```
✅ TRADE CLOSED | $AAPL
Entry: $150.00
Exit: $153.00
Result: +1.0R ✅
P&L: +$95.00
Exit: TP1

#riskmanagement #tradingresults #AItrader
```

### 4. Daily Summary (4 PM)
```
📊 DAILY PERFORMANCE | Nov 15, 2025
──────────────────────────────

Closed: 5 trades
W/L: 3/2 (60% WR)
Avg R: +0.2R
P&L: +$120.00 ✅

Open: 2 | Pending: 3

#tradingjournal #systemtrading #quant
```

### 5. Weekly Summary (Friday 4 PM)
```
📈 WEEKLY RECAP
──────────────────────────────

Trades: 23 closed
W/L: 14/9 (60.9% WR)
Avg R: +0.5R
Weekly P&L: +$650.00 ✅

#weeklyrecap #trading #AItrader
```

---

## Configuration (config.yaml)

```yaml
alerts:
  twitter:
    enabled: true
    # What to post
    post_new_trades: true
    post_entries: true
    post_exits: true
    post_daily_summary: true
    post_weekly_summary: true
    # Auto-engagement (optional)
    auto_engage:
      enabled: false  # Turn this ON to auto-engage
      query: "stocks OR trading OR $SPY"
      reply_template: "Nice insight, @{username}! 📊"
      max_tweets: 3
```

Turn individual tweet types on/off without touching code.

---

##How to Run

### Option 1: Automatic (With Trade Monitor)

```bash
# Terminal 1
source setup_telegram.sh
source setup_twitter.sh
python3 scan_and_chart.py
python3 signals_to_trades.py
```

```bash
# Terminal 2 - Leave running
source setup_telegram.sh
source setup_twitter.sh
python3 trade_monitor.py
```

**Result:**
- Every trade → Telegram + Twitter
- 4 PM daily → Summary posted
- Friday 4 PM → Weekly recap

### Option 2: Manual Test

```bash
source setup_telegram.sh
source setup_twitter.sh

# Create test trade
python3 signals_to_trades.py
```

Telegram + Twitter will get "NEW TRADE SETUP" message.

---

## Auto-Engagement (Community Building)

Set this to build your trading persona:

```yaml
auto_engage:
  enabled: true
  query: "stocks OR daytrading OR $SPY OR options"
  reply_template: "Solid analysis, @{username}! My AI trades systematic setups. 📊 #algotrading"
  max_tweets: 3
```

**What it does:**
- After daily summary, searches for tweets matching query
- Likes 3 recent tweets
- Optionally replies with template

**Note:** Engagement features require Elevated access.

---

## Persona Strategy

### Profile Setup

**Username ideas:**
- @AITradeJournal
- @AlgoTraderBot
- @SystematicEdge
- @QuantSignals

**Bio:**
```
🤖 AI-powered systematic trader
📊 Live trades + daily stats
📈 R-multiple based risk mgmt
⚙️ 100% automated • Not financial advice
```

**Banner:**
- Include equity curve chart
- Or: "Live Trade Performance Dashboard"

### Posting Strategy

1. **Daily consistency** - Summary at 4 PM every day
2. **Full transparency** - Show wins AND losses
3. **Focus on process** - R-multiples, win rate, discipline
4. **No hype** - Let numbers speak
5. **Educational** - Explain signals, risk mgmt

### Growth Tips

- Use relevant hashtags (#trading, #algotrading, #quant)
- Reply to big accounts (respectfully)
- Share weekly recap every Friday
- Post charts when possible (once you have elevated access)

---

## Troubleshooting

### "Client app not configured with permissions"

→ Enable Read & Write in App Settings
→ Regenerate Access Token + Secret

### "Forbidden: 403"

→ Apply for Elevated access
→ Or check if app permissions are saved

### Tweets not posting

1. Check credentials:
```bash
source setup_twitter.sh
python3 twitter_bot.py
```

2. Verify in config.yaml:
```yaml
twitter:
  enabled: true  # Must be true
```

3. Check logs when monitor runs

### Only Telegram working, not Twitter

→ Twitter is disabled or credentials missing
→ Run: `source setup_twitter.sh` before starting monitor

---

## Files Created

| File | Purpose |
|------|---------|
| `twitter_bot.py` | Twitter posting engine |
| `setup_twitter.sh` | API credentials |
| `config.yaml` | Twitter settings (updated) |
| `telegram_bot.py` | Dual-channel integration (updated) |
| `trade_monitor.py` | Weekly summaries (updated) |

---

## Next Steps

1. **Enable write permissions** in Twitter Developer Portal
2. **Regenerate tokens**
3. **Update setup_twitter.sh** with new tokens
4. **Test:** `source setup_twitter.sh && python3 twitter_bot.py`
5. **Run system:** `python3 trade_monitor.py`
6. **Watch your timeline** fill with live trades!

---

## Once Permissions Are Fixed...

Your AI trading persona goes **fully automatic**:
- Scans → Trades → Twitter posts
- Every entry/exit → Tweet
- Daily recap → Tweet
- Weekly summary → Tweet
- Zero manual work

**Just run the monitor and let it build your persona 24/7.**

---

**Need help?**
- Twitter API docs: https://developer.twitter.com/en/docs
- Tweepy docs: https://docs.tweepy.org
- Test connection: `python3 twitter_bot.py`
