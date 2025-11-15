# 🚀 Deploy to Railway (FREE 24/7 Hosting)

## ✅ **BEST FREE OPTION - Railway.app**

**Cost:** FREE ($5/month credit - enough for this app)
**Uptime:** 24/7
**Setup Time:** 10 minutes

---

## STEP 1: Push to GitHub

```bash
# Initialize git (if not already)
git init
git add .
git commit -m "AI Stock Agent - Ready for deployment"

# Create repo on GitHub (go to github.com/new)
# Then push:
git remote add origin https://github.com/YOUR_USERNAME/ai-stock-agent.git
git branch -M main
git push -u origin main
```

---

## STEP 2: Deploy on Railway

### A. Sign Up
1. Go to: https://railway.app
2. Click **"Start a New Project"**
3. Sign in with GitHub

### B. Create Project
1. Click **"Deploy from GitHub repo"**
2. Select your `ai-stock-agent` repo
3. Railway will auto-detect Dockerfile

### C. Set Environment Variables

**IMPORTANT:** Click **"Variables"** tab and add these:

```
TELEGRAM_BOT_TOKEN=7909396650:AAHRxUnSIZxWdYSCaEcZcUfQVEzZ3r8qbj0
TELEGRAM_CHAT_ID=8201781672
TWITTER_API_KEY=nHZOfTHMXEZTWsko9AmEsoVdr
TWITTER_API_SECRET=1ZpaPq4j9ZVFcJyHhgMgWc4KnEOS1RS93csuYfqerT8m2qQZFg
TWITTER_ACCESS_TOKEN=1954403714497949696-TdHxlnk2KtiUusrm9aoidomKndhC46
TWITTER_ACCESS_SECRET=4zUJb0lS52AcbJYec6SPG29O8Q335Gu8OuS7LkWuj62wv
```

### D. Deploy
1. Click **"Deploy"**
2. Wait 3-5 minutes
3. Check logs - should see:
```
✅ All environment variables configured
✅ Database initialized
✅ Both systems running
```

---

## STEP 3: Verify It's Working

### Check Logs
Railway dashboard → **Deployments** → **View Logs**

Should see:
```
AI TWITTER PERSONA - AUTOMATED SCHEDULER
Scheduled posts (EST timezone):
  10:00 AM - Market Open Overview
  ...
```

### Check Twitter
Go to: https://twitter.com/MopshyAi

Tweets will start appearing at scheduled times.

---

## ✅ **DONE! System Running 24/7**

**Now:**
- ✅ Laptop OFF - System still runs
- ✅ Phone OFF - System still runs
- ✅ You sleeping - System still runs
- ✅ 6 tweets/day automatically
- ✅ Trade monitoring 24/7
- ✅ FREE (Railway $5 credit/month)

---

## Monitoring

### View Logs
```
Railway Dashboard → Your Project → Deployments → Logs
```

### Restart Service
```
Railway Dashboard → Settings → Restart
```

### Update Code
```bash
# On your laptop
git add .
git commit -m "Update"
git push

# Railway auto-deploys new version
```

---

## Cost Breakdown (Railway)

**Free Tier:**
- $5/month credit (FREE)
- This app uses ~$3-4/month
- **Cost to you: $0**

**If you exceed:**
- Upgrade to Hobby plan: $5/month
- Still very cheap

---

## Alternative: Render.com (Also Free)

If Railway doesn't work:

1. Go to: https://render.com
2. New → **Web Service**
3. Connect GitHub repo
4. Set environment: **Docker**
5. Add environment variables (same as above)
6. Deploy

**Free tier:** 750 hours/month (enough for 24/7)

---

## Troubleshooting

### "Build failed"
- Check Dockerfile syntax
- Check requirements.txt has all dependencies

### "Environment variables missing"
- Double-check all 6 variables in Railway dashboard
- No spaces, no quotes around values

### "Tweets not posting"
- Check logs for errors
- Verify Twitter credentials are correct
- Check Railway service is running

### "Trade monitor not working"
- Needs active trades to post
- Run scan + create trades locally first
- Or wait for scheduled scans

---

## Files Created for Deployment

| File | Purpose |
|------|---------|
| `Dockerfile` | Container configuration |
| `railway.json` | Railway-specific config |
| `main_runner.py` | Runs both services in parallel |
| `requirements.txt` | Python dependencies |
| `.dockerignore` | Exclude unnecessary files |

---

## What Happens After Deploy?

### Immediately
- Container builds (3-5 min)
- Services start
- Database initializes

### At 10 AM EST
- First tweet posts (Market Open)

### At 2 PM EST
- Second tweet posts (Mid-day)

### At 10 PM EST
- Third tweet posts (Night wrap)

**Plus 3 more tweets at other times**

**Plus live trade alerts whenever trades happen**

---

## Pro Tips

### 1. Monitor Health
Add this to Railway:
- **Health Check URL:** Configure if Railway offers it

### 2. Database Persistence
Railway gives ephemeral storage. For permanent database:
- Use Railway PostgreSQL addon (free tier)
- Or use SQLite (resets on redeploy, but okay for this use case)

### 3. Logs
Check logs daily for first week to ensure everything works

### 4. Cost Optimization
Current setup uses minimal resources:
- 512MB RAM
- Minimal CPU
- Should stay under $5/month credit

---

## Summary

**Before deployment:**
```
Laptop ON → System works
Laptop OFF → System stops
```

**After deployment:**
```
Railway cloud → System always works
Laptop irrelevant → 24/7 automated
```

**Cost:** FREE (Railway $5/month credit covers it)

---

## Quick Start Commands

```bash
# 1. Commit code
git add .
git commit -m "Deploy to Railway"
git push origin main

# 2. Go to Railway.app
# 3. Connect GitHub repo
# 4. Add environment variables
# 5. Deploy

# DONE!
```

---

## Need Help?

**Railway Docs:** https://docs.railway.app

**This repo:** Already configured with:
- ✅ Dockerfile
- ✅ railway.json
- ✅ requirements.txt
- ✅ main_runner.py

**Just push to GitHub and deploy!**

---

**Your AI persona will run 24/7 in the cloud, completely free! 🚀**
