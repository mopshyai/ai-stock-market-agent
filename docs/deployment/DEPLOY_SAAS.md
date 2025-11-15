# Deploy as SaaS - Complete Guide

## 🚀 Turn Your AI Stock Agent into a Live Web App

This guide shows you how to deploy your AI Stock Market Agent as a **hosted SaaS product** that anyone can access via URL.

**What you'll get:**
- 🌐 Public URL: `https://ai-stock-agent-yourname.streamlit.app`
- ☁️ Always online (no "run on my machine")
- 📱 Works on any device
- 🔄 Auto-refreshes every 15 minutes
- 💾 Persistent database (SQLite → upgrade to Postgres later)

**No servers to manage. No DevOps. Just deploy and share.**

---

## 🎯 Deployment Path: Streamlit Cloud (v1)

For January launch, we're using **Streamlit Community Cloud**:

### Why Streamlit Cloud?

✅ **Free** for public apps
✅ **Zero infrastructure** - no Docker, AWS, servers
✅ **Perfect for Streamlit apps** (built by the same team)
✅ **Deploy in 5 minutes**
✅ **Auto-deploys** from GitHub commits
✅ **Custom domain** support (optional)

---

## 📋 Pre-Flight Checklist

Before deploying, verify these files exist:

```bash
✅ dashboard.py              # Your main app
✅ requirements.txt          # All dependencies with versions
✅ config.yaml               # Stock configuration
✅ .streamlit/config.toml    # Streamlit settings (theme, server)
✅ .gitignore                # Excludes secrets, local files
✅ .python-version           # Python 3.9+ specified
```

All these are already set up for you! ✨

---

## 🚀 Step-by-Step Deployment

### Step 1: Push to GitHub

```bash
# Navigate to your project
cd ai_stock_agent_fresh2

# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "SaaS version: AI Stock Market Agent ready for deployment"

# Create GitHub repo (Option A: via GitHub website)
# Go to: https://github.com/new
# Name: ai-stock-agent
# Don't initialize with README (you already have one)
# Click "Create repository"

# Link your local repo to GitHub
git remote add origin https://github.com/YOUR-USERNAME/ai-stock-agent.git

# Push
git branch -M main
git push -u origin main
```

**OR use GitHub CLI** (Option B):

```bash
# Install GitHub CLI first: brew install gh
gh auth login
gh repo create ai-stock-agent --public --source=. --remote=origin
git push -u origin main
```

✅ **Your code is now on GitHub!**

---

### Step 2: Deploy on Streamlit Cloud

#### 2.1 Go to Streamlit Cloud
- Visit: **[share.streamlit.io](https://share.streamlit.io)**
- Click **"Sign up"** or **"Sign in with GitHub"**

#### 2.2 Connect GitHub
- Authorize Streamlit Cloud to access your GitHub repos
- You may need to grant access to specific repos

#### 2.3 Deploy Your App

Click **"New app"** and configure:

| Setting | Value |
|---------|-------|
| **Repository** | `YOUR-USERNAME/ai-stock-agent` |
| **Branch** | `main` |
| **Main file path** | `dashboard.py` |
| **App URL** | `ai-stock-agent` (or custom name) |

Click **"Deploy!"**

#### 2.4 Wait for Deployment
- First deployment takes 3-5 minutes
- You'll see logs showing package installation
- Watch for "Your app is live!" message

✅ **You'll get a URL like:**
```
https://ai-stock-agent-yourname.streamlit.app
```

---

### Step 3: Configure Secrets (Optional)

If you want to add Telegram alerts to your hosted app:

1. In Streamlit Cloud dashboard, click your app
2. Click **"Settings"** (⚙️ icon)
3. Click **"Secrets"**
4. Add your secrets in TOML format:

```toml
[telegram]
bot_token = "123456:ABC-DEF..."
chat_id = "987654321"
```

5. Click **"Save"**
6. App will auto-restart with new secrets

---

## 🎨 Customization Options

### Custom Domain (Optional)

Want `stockagent.com` instead of `.streamlit.app`?

1. Buy domain (Namecheap, Google Domains)
2. In Streamlit Cloud: **Settings → General → Custom domain**
3. Add your domain
4. Update DNS settings (CNAME record)

**Cost:** ~$10-15/year for domain

### App Settings

Already configured in `.streamlit/config.toml`:
- 🎨 **Theme:** Purple gradient (`#667eea`)
- 🖥️ **Headless mode:** Enabled (for cloud)
- 🔒 **XSRF protection:** Enabled
- 📊 **Usage stats:** Disabled (privacy)

### Auto-Refresh Settings

In `dashboard.py` line 31:
```python
st_autorefresh(interval=900000, key="ai_stock_agent_autorefresh")
```
- Default: 15 minutes (900000 ms)
- Adjust as needed (but don't go below 5 min to avoid rate limits)

---

## 💾 Database Strategy

### v1: SQLite (Current)

**Pros:**
- ✅ Simple, no setup
- ✅ Good for demo / early users
- ✅ Works on Streamlit Cloud

**Cons:**
- ⚠️ May reset on redeployment
- ⚠️ Limited to single instance
- ⚠️ Not ideal for high traffic

**Verdict:** Perfect for January launch + first 100 users.

### v2: Postgres (Upgrade Later)

When you're ready for production (paying users, scale):

**Free Postgres Hosting:**
- [Neon](https://neon.tech) - Free tier, serverless
- [Supabase](https://supabase.com) - Free tier, includes auth
- [Railway](https://railway.app) - $5/month

**Migration Guide:**

1. Create Postgres database on Neon
2. Get connection URL: `postgresql://user:pass@host/db`
3. Update `database.py` to use PostgreSQL:

```python
# Old (SQLite)
DB_PATH = "stock_agent.db"
engine = create_engine(f"sqlite:///{DB_PATH}")

# New (Postgres)
import os
DB_URL = os.getenv("DATABASE_URL")  # From secrets
engine = create_engine(DB_URL)
```

4. Add to Streamlit secrets:
```toml
[database]
url = "postgresql://user:pass@host/db"
```

5. Run migration:
```bash
python database.py  # Recreates tables in Postgres
```

**Cost:** Free tier handles 1000s of users.

---

## 🔄 Continuous Deployment

Every time you push to GitHub, Streamlit Cloud auto-deploys:

```bash
# Make changes locally
git add .
git commit -m "Add new feature"
git push

# Streamlit Cloud automatically:
# 1. Detects the commit
# 2. Rebuilds the app
# 3. Deploys new version
# Takes ~2-3 minutes
```

**This is your CI/CD pipeline!** No Jenkins, no GitHub Actions needed.

---

## 📊 Monitoring & Analytics

### Built-in Streamlit Analytics

In Streamlit Cloud dashboard:
- 📈 **Usage stats:** Daily active users, sessions
- 🌍 **Geographic data:** Where users are from
- ⏱️ **Performance:** Load times, errors
- 🔍 **Logs:** Real-time app logs

### Adding Google Analytics (Optional)

In `dashboard.py`, add to the `<head>`:

```python
st.markdown("""
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
""", unsafe_allow_html=True)
```

---

## 🛠️ Troubleshooting

### "Requirements installation failed"

**Fix:** Check `requirements.txt` versions are compatible
```bash
# Test locally first
pip install -r requirements.txt
```

### "ModuleNotFoundError"

**Fix:** Missing package in requirements.txt
```bash
# Add to requirements.txt
missing-package>=1.0.0
```

### "Memory limit exceeded"

Streamlit Cloud free tier: **1GB RAM**

**Fix:**
- Reduce data fetching (fewer tickers)
- Use caching: `@st.cache_data`
- Upgrade to paid plan ($20/month for 4GB)

### "Database locked" or "no such table"

SQLite concurrency issue.

**Fix (short term):**
```python
# In database.py, add timeout
engine = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={"timeout": 30}
)
```

**Fix (long term):** Migrate to Postgres (see above)

### App is slow / timing out

**Causes:**
- Fetching too many stocks
- No caching on data fetching
- Heavy computations

**Fixes:**
```python
# Cache yfinance calls
@st.cache_data(ttl=900)  # 15 min cache
def get_stock_data(ticker, period, interval):
    return yf.download(ticker, period=period, interval=interval)
```

---

## 🎯 Post-Deployment Checklist

After deploying, verify:

```
✅ App loads at your .streamlit.app URL
✅ Scan button works (can run new scans)
✅ Charts display correctly
✅ Database history tab shows data
✅ Auto-refresh is working (wait 15 min)
✅ Mobile responsive (check on phone)
✅ No errors in Streamlit Cloud logs
```

---

## 📣 Launch Checklist

Once deployed, you're ready to share:

### 1. Update Landing Page
```markdown
[Try Live Demo](https://ai-stock-agent-yourname.streamlit.app)
```

### 2. Social Media Posts
```
🚀 Launched: AI Stock Market Agent

Get real-time AI-powered stock signals:
📊 Consolidation patterns
📉 Buy-the-dip setups
🚀 Breakout alerts

Try it now: [your-url]

#StockMarket #AI #Trading
```

### 3. Product Hunt
- **Demo URL:** Your Streamlit app
- **Tagline:** "AI-powered stock signals delivered to your phone"
- **Description:** (use from PRODUCT_HUNT_COMPLETE_GUIDE.md)

### 4. Direct Outreach
Send to beta users:
```
Hey [Name],

I just launched the AI Stock Agent we discussed.

No installation needed - just open this link:
[your-url]

Would love your feedback!
```

---

## 💰 Cost Breakdown (v1)

| Service | Cost | Notes |
|---------|------|-------|
| Streamlit Cloud | **FREE** | Public apps free forever |
| GitHub | **FREE** | Public repos unlimited |
| Custom Domain | $10-15/year | Optional |
| **Total** | **$0-15/year** | 🎉 |

**For v2 (Scaling):**
- Streamlit Cloud Teams: $250/month (private apps, auth)
- Postgres (Neon): Free → $20/month
- Auth (Clerk/Supabase): Free → $25/month

---

## 🔐 Security Notes

### Current Setup (v1)
- ✅ No user auth (single-tenant)
- ✅ No sensitive data stored
- ✅ Secrets in Streamlit secrets (not in code)
- ✅ XSRF protection enabled
- ✅ HTTPS by default

### For v2 (Multi-User)
When you add user accounts:
- Use [Streamlit Authenticator](https://github.com/mkhorasani/Streamlit-Authenticator)
- Or [Clerk](https://clerk.com) (free tier: 5k users)
- Or [Supabase Auth](https://supabase.com/auth)

---

## 🎓 What You Just Built

You now have:

✅ **A real SaaS product** running in the cloud
✅ **Public URL** anyone can access
✅ **Auto-deployment** from Git pushes
✅ **Zero infrastructure costs** (v1)
✅ **Professional web dashboard**
✅ **Persistent data** (SQLite → Postgres later)

**This is a launchable product.** 🚀

---

## 📚 Next Steps

### Week 1: Launch
- [x] Deploy to Streamlit Cloud
- [ ] Share URL on socials
- [ ] Product Hunt launch
- [ ] Gather feedback

### Week 2-4: Iterate
- [ ] Add more signals based on feedback
- [ ] Improve chart interactivity
- [ ] Add email/SMS alerts (optional)
- [ ] Create demo video

### Month 2: Scale
- [ ] Migrate to Postgres (when you hit SQLite limits)
- [ ] Add user authentication
- [ ] Custom tickers per user
- [ ] Pricing page + Stripe

---

## 🆘 Need Help?

**Streamlit Docs:**
- [Deploy apps](https://docs.streamlit.io/streamlit-community-cloud/get-started)
- [App secrets](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)
- [Custom domains](https://docs.streamlit.io/streamlit-community-cloud/manage-your-app/custom-domains)

**Streamlit Community:**
- [Forum](https://discuss.streamlit.io/)
- [Discord](https://discord.gg/streamlit)

**Database Migration:**
- [Neon Quickstart](https://neon.tech/docs/get-started-with-neon/signing-up)
- [Supabase Quickstart](https://supabase.com/docs/guides/getting-started/quickstarts/python)

---

**You're ready to go live. Let's ship this! 🚢**
