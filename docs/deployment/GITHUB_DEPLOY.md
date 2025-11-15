# Deploy to GitHub → Streamlit Cloud

## Quick Commands (Copy-Paste Ready)

### Step 1: Commit Your Code

```bash
# Make sure you're in the project directory
cd ai_stock_agent_fresh2

# Add all files
git add .

# Commit
git commit -m "SaaS deployment: AI Stock Market Agent v1.0"
```

### Step 2A: Create GitHub Repo (Website Method)

1. Go to: **[https://github.com/new](https://github.com/new)**
2. Repository name: `ai-stock-agent`
3. Description: `AI-powered stock market scanner with automated alerts`
4. Make it **Public** (required for free Streamlit hosting)
5. **Do NOT** check "Initialize with README" (you already have one)
6. Click **"Create repository"**

Then run:

```bash
# Link your local repo to GitHub
git remote add origin https://github.com/YOUR-USERNAME/ai-stock-agent.git

# Push to GitHub
git push -u origin main
```

### Step 2B: Create GitHub Repo (CLI Method)

If you have GitHub CLI installed:

```bash
# Login to GitHub (first time only)
gh auth login

# Create repo and push in one command
gh repo create ai-stock-agent --public --source=. --remote=origin --push
```

**That's it!** Your code is now on GitHub.

---

## Step 3: Deploy on Streamlit Cloud

### 3.1 Sign Up

1. Go to: **[share.streamlit.io](https://share.streamlit.io)**
2. Click **"Sign in with GitHub"**
3. Authorize Streamlit Cloud to access your repos

### 3.2 Deploy

1. Click **"New app"**
2. Fill in:

```
Repository:       YOUR-USERNAME/ai-stock-agent
Branch:           main
Main file path:   dashboard.py
App URL (slug):   ai-stock-agent
```

3. Click **"Deploy!"**

### 3.3 Wait

- Deployment takes **3-5 minutes**
- Watch the logs for any errors
- Look for: **"Your app is live at..."**

### 3.4 Get Your URL

You'll receive:
```
https://ai-stock-agent-YOUR-USERNAME.streamlit.app
```

**Bookmark this!** Share it everywhere.

---

## Step 4: Update README with Your URL

Once deployed, update the README:

```bash
# Open README.md
code README.md  # or nano, vim, etc.

# Find line 11:
### [**→ Open Web App**](https://ai-stock-agent-yourname.streamlit.app) 🌐

# Replace with your actual URL:
### [**→ Open Web App**](https://ai-stock-agent-YOUR-ACTUAL-USERNAME.streamlit.app) 🌐

# Also update line 393:
- **[Try Live App](https://ai-stock-agent-YOUR-ACTUAL-USERNAME.streamlit.app)** 🌐
```

Then push the update:

```bash
git add README.md
git commit -m "Update with live app URL"
git push
```

Streamlit Cloud will **auto-redeploy** with the updated README!

---

## Step 5: Test Your Live App

Visit your URL and verify:

- ✅ Dashboard loads
- ✅ Can click "Run New Scan"
- ✅ Charts display
- ✅ History tab shows data
- ✅ Auto-refresh works (wait 15 min)

---

## Troubleshooting Deployment

### "Build failed: Could not find requirements.txt"

**Fix:** Make sure `requirements.txt` is in the root directory (not in a subdirectory)

```bash
# Check file location
ls -la requirements.txt

# Should show: requirements.txt in current directory
```

### "Module not found: streamlit"

**Fix:** Ensure `requirements.txt` includes:
```
streamlit>=1.28.0
```

### "Your app has errors"

Check Streamlit Cloud logs:
1. Go to Streamlit Cloud dashboard
2. Click your app
3. Click "Manage app" → "Logs"
4. Look for error messages

Common fixes:
- Missing dependency in `requirements.txt`
- Syntax error in code
- File path issues (use relative paths)

### "Database locked"

SQLite concurrency issue. Two fixes:

**Short-term:**
```python
# In database.py, add timeout
engine = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={"timeout": 30}
)
```

**Long-term:** Migrate to Postgres (see DEPLOY_SAAS.md)

---

## Auto-Deployment (Already Set Up!)

Every time you push to GitHub:

```bash
# Make changes locally
git add .
git commit -m "Add new feature"
git push

# Streamlit Cloud automatically:
# 1. Detects the commit
# 2. Rebuilds the app
# 3. Deploys new version
# Takes 2-3 minutes
```

No manual redeployment needed!

---

## Adding Secrets (Optional)

If you want Telegram alerts on the hosted app:

1. Go to Streamlit Cloud dashboard
2. Click your app → **"Settings"** ⚙️
3. Click **"Secrets"**
4. Add in TOML format:

```toml
[telegram]
bot_token = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
chat_id = "987654321"
```

5. Click **"Save"**
6. App auto-restarts with secrets

Then update `telegram_bot.py` to read from Streamlit secrets:

```python
import streamlit as st

# Try Streamlit secrets first, fall back to .env
try:
    BOT_TOKEN = st.secrets["telegram"]["bot_token"]
    CHAT_ID = st.secrets["telegram"]["chat_id"]
except:
    # Fall back to .env for local development
    from dotenv import load_dotenv
    load_dotenv()
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
```

---

## Managing Your App

### View Analytics

Streamlit Cloud dashboard shows:
- Daily active users
- Session count
- Geographic distribution
- Error rate

### View Logs

Real-time logs:
1. Click your app
2. "Manage app" → "Logs"
3. See print statements, errors

### Restart App

If app is stuck:
1. "Manage app" → "Reboot app"
2. Takes ~30 seconds

### Delete App

To take it offline:
1. "Settings" → "Delete app"
2. Confirm

Your GitHub repo stays intact - you can redeploy anytime.

---

## Cost Breakdown

| Service | Cost |
|---------|------|
| GitHub (public repo) | **FREE** |
| Streamlit Cloud (public app) | **FREE** |
| **Total** | **$0/month** |

Upgrading later:
- **Streamlit Teams:** $250/month (private apps, auth, SSO)
- **Custom domain:** $10-15/year (optional)

---

## Quick Reference

| Task | Command |
|------|---------|
| **Check status** | `git status` |
| **Add all changes** | `git add .` |
| **Commit** | `git commit -m "message"` |
| **Push to GitHub** | `git push` |
| **View remote** | `git remote -v` |
| **Create branch** | `git checkout -b feature-name` |
| **View logs** | Streamlit Cloud → Manage app → Logs |
| **Reboot app** | Streamlit Cloud → Manage app → Reboot |

---

## Next Steps After Deployment

1. ✅ **Test the live app** thoroughly
2. ✅ **Update README** with your actual URL
3. ✅ **Share on social media** (Twitter, LinkedIn)
4. ✅ **Launch on Product Hunt** (see PRODUCT_HUNT_COMPLETE_GUIDE.md)
5. ✅ **Send to beta users** via DM/email
6. ✅ **Add to your portfolio/resume**

---

## Congratulations! 🎉

You just deployed a **SaaS product** to the cloud.

**Your app is now:**
- ✅ Accessible via public URL
- ✅ Always online (no downtime)
- ✅ Auto-deploying from Git pushes
- ✅ Free to host (Streamlit Cloud)
- ✅ Mobile-responsive
- ✅ HTTPS by default

**Share your URL with the world!** 🚀

---

## Support

**Streamlit Docs:**
- [Deployment guide](https://docs.streamlit.io/streamlit-community-cloud/get-started)
- [Secrets management](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)

**Need help?**
- [Streamlit Forum](https://discuss.streamlit.io/)
- [Streamlit Discord](https://discord.gg/streamlit)
- [GitHub Issues](https://github.com/YOUR-USERNAME/ai-stock-agent/issues)
