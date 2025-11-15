# SaaS Deployment Checklist

## ✅ Pre-Deployment Verification

Run through this checklist before deploying:

### 1. Code Files
- [ ] `dashboard.py` exists and runs locally: `streamlit run dashboard.py`
- [ ] `scan_and_chart.py` executes without errors: `python scan_and_chart.py`
- [ ] `database.py` creates tables successfully: `python database.py`
- [ ] `config.yaml` has your stock tickers configured

### 2. Dependencies
- [ ] `requirements.txt` exists with all packages listed
- [ ] All packages install successfully: `pip install -r requirements.txt`
- [ ] No hardcoded paths (use relative paths only)
- [ ] No local-only dependencies

### 3. Configuration Files
- [ ] `.streamlit/config.toml` exists (theme & server settings)
- [ ] `.streamlit/secrets.toml.example` exists (for users)
- [ ] `.python-version` exists (specifies Python 3.9+)
- [ ] `.gitignore` configured properly

### 4. Git Status
- [ ] Git repository initialized: `git status` works
- [ ] All files added: `git add .`
- [ ] Changes committed: `git commit -m "SaaS deployment v1.0"`
- [ ] No sensitive data in commits (check `.gitignore`)

### 5. Local Testing
- [ ] Dashboard runs without errors
- [ ] Can run a scan successfully
- [ ] Charts display correctly
- [ ] Database saves scan history
- [ ] No errors in console

---

## 🚀 Deployment Steps

### Step 1: Push to GitHub
- [ ] GitHub repo created: `ai-stock-agent`
- [ ] Remote added: `git remote add origin <url>`
- [ ] Code pushed: `git push -u origin main`
- [ ] Verify on GitHub: all files visible

### Step 2: Deploy on Streamlit Cloud
- [ ] Signed up at [share.streamlit.io](https://share.streamlit.io)
- [ ] Connected GitHub account
- [ ] Created new app with correct settings:
  - Repository: `YOUR-USERNAME/ai-stock-agent`
  - Branch: `main`
  - Main file: `dashboard.py`
- [ ] Deployment started (watch logs)

### Step 3: Post-Deployment
- [ ] App deployed successfully (no errors in logs)
- [ ] URL received: `https://ai-stock-agent-USERNAME.streamlit.app`
- [ ] App loads in browser
- [ ] Can run a scan from hosted app
- [ ] Charts display correctly
- [ ] No console errors

---

## 🧪 Testing Your Live App

Visit your Streamlit Cloud URL and test:

### Basic Functionality
- [ ] Dashboard loads within 5 seconds
- [ ] "Run New Scan" button works
- [ ] Scan completes without errors
- [ ] Signal metrics update
- [ ] Charts tab shows interactive charts

### Navigation
- [ ] All 5 tabs are accessible:
  - [ ] Signals
  - [ ] Charts
  - [ ] Full Data
  - [ ] History
  - [ ] Performance
- [ ] Sidebar controls work
- [ ] Filters apply correctly

### Data Persistence
- [ ] After running scan, data persists
- [ ] History tab shows previous scans
- [ ] CSV download works
- [ ] Database doesn't reset randomly

### Performance
- [ ] Page load: < 5 seconds
- [ ] Scan execution: < 30 seconds
- [ ] Chart rendering: < 3 seconds
- [ ] Auto-refresh: works after 15 minutes

### Mobile Testing
- [ ] Open on phone
- [ ] Layout is responsive
- [ ] All features accessible
- [ ] Charts render correctly

---

## 🔧 Common Issues & Fixes

### "Your app has an error"

**Check:**
1. Streamlit Cloud logs (Manage app → Logs)
2. Missing packages in `requirements.txt`
3. Hardcoded file paths (use relative paths)
4. Environment-specific code (remove if any)

**Fix:**
```bash
# Add missing package to requirements.txt
echo "missing-package>=1.0.0" >> requirements.txt
git add requirements.txt
git commit -m "Add missing dependency"
git push
# Streamlit auto-redeploys
```

### "Module not found"

**Fix:** Add to `requirements.txt`:
```
streamlit>=1.28.0
pandas>=1.5.0
yfinance>=0.2.28
streamlit-autorefresh>=0.0.1
streamlit-lightweight-charts>=0.2.0
```

### "Database is locked"

**Quick Fix:** Add to `database.py`:
```python
engine = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={"timeout": 30}
)
```

**Long-term:** Migrate to Postgres (see DEPLOY_SAAS.md)

### "Memory limit exceeded"

Streamlit Cloud free tier: 1GB RAM

**Fix:**
- Reduce number of tickers in `config.yaml`
- Add caching to data fetching functions
- Or upgrade to paid tier ($20/month for 4GB)

### "Rate limit exceeded" (yfinance)

**Fix:** Add caching:
```python
@st.cache_data(ttl=900)  # Cache for 15 minutes
def get_stock_data(ticker, period, interval):
    return yf.download(ticker, period=period, interval=interval)
```

---

## 📊 Monitoring Checklist

After 24 hours of being live:

### Analytics
- [ ] Check daily active users (Streamlit Cloud dashboard)
- [ ] Review error logs
- [ ] Monitor performance metrics
- [ ] Check geographic distribution

### User Feedback
- [ ] Collect feedback from beta users
- [ ] Monitor GitHub issues
- [ ] Check social media mentions
- [ ] Note feature requests

### Performance
- [ ] Average load time < 5 seconds
- [ ] Scan success rate > 95%
- [ ] No critical errors in logs
- [ ] Auto-refresh working reliably

---

## 🎯 Post-Launch Actions

### Week 1
- [ ] Share URL on Twitter/LinkedIn
- [ ] Launch on Product Hunt
- [ ] Send to 10+ beta users
- [ ] Monitor for bugs
- [ ] Gather initial feedback

### Week 2
- [ ] Iterate based on feedback
- [ ] Fix reported bugs
- [ ] Add requested features
- [ ] Update documentation

### Week 3-4
- [ ] Optimize performance
- [ ] Add more signals/indicators
- [ ] Improve charts
- [ ] Consider Postgres migration

---

## 💰 Cost Verification

Current costs (should be $0):

- [ ] GitHub public repo: **FREE** ✅
- [ ] Streamlit Cloud (public app): **FREE** ✅
- [ ] yfinance data: **FREE** ✅
- [ ] **Total:** $0/month ✅

Optional upgrades:
- Custom domain: ~$10-15/year
- Streamlit Teams: $250/month (private apps)
- Postgres hosting: Free → $20/month

---

## 🔐 Security Verification

- [ ] No API keys in code
- [ ] No passwords in code
- [ ] Secrets use Streamlit secrets or env vars
- [ ] `.env` in `.gitignore`
- [ ] `.streamlit/secrets.toml` in `.gitignore`
- [ ] XSRF protection enabled (in config.toml)
- [ ] HTTPS by default (Streamlit Cloud)

---

## 🎓 Knowledge Check

Before launching, make sure you can:

- [ ] Deploy updates: `git push` → auto-deploys
- [ ] View logs: Streamlit Cloud dashboard → Logs
- [ ] Restart app: Manage app → Reboot
- [ ] Add secrets: Settings → Secrets (TOML format)
- [ ] Monitor usage: Analytics tab
- [ ] Update configuration: Edit `config.yaml` → push

---

## 📣 Marketing Checklist

Before sharing publicly:

### Content Ready
- [ ] README has correct live URL
- [ ] Screenshot of dashboard (for social media)
- [ ] Demo video (optional but recommended)
- [ ] Product Hunt listing prepared
- [ ] Social media posts drafted

### Channels to Share
- [ ] Twitter with hashtags (#StockMarket #AI #Trading)
- [ ] LinkedIn with professional angle
- [ ] Product Hunt launch
- [ ] Reddit (r/algotrading, r/stocks) - follow rules
- [ ] Discord communities (trading, Python, AI)
- [ ] Personal network via email/DM

### Messaging Tested
- [ ] Elevator pitch: 1 sentence
- [ ] Value prop: Why use this vs. others
- [ ] Call-to-action: Clear next step (click URL)
- [ ] Disclaimer: Educational purposes only

---

## ✅ Final Go/No-Go Decision

**You're ready to launch if:**

✅ All "Pre-Deployment Verification" boxes checked
✅ All "Deployment Steps" completed successfully
✅ All "Testing Your Live App" items pass
✅ No critical errors in Streamlit Cloud logs
✅ App loads reliably for 24+ hours
✅ Database persists data correctly
✅ Marketing materials ready

**If ANY of these are NO, fix before launching:**

❌ App crashes on load
❌ Scan button doesn't work
❌ Charts don't display
❌ Critical errors in logs
❌ Database resets constantly
❌ Performance < 10 seconds load time

---

## 🎉 You're Ready to Launch!

If you've completed this checklist, you have:

✅ A working SaaS product
✅ Deployed on cloud infrastructure
✅ Zero hosting costs (v1)
✅ Auto-deployment pipeline
✅ Public URL to share

**Time to ship!** 🚀

---

**Last updated:** After SaaS deployment setup
**Next review:** After first 100 users
