# 🚀 Railway Postgres Migration Guide

## Why Migrate to Postgres?

Current SQLite issues:
- ❌ Data lost on every redeploy
- ❌ Can't scale to multiple users
- ❌ No concurrent access support
- ❌ Limited to single server

Postgres benefits:
- ✅ Persistent data (survives redeploys)
- ✅ Ready for multi-user SaaS
- ✅ Better performance at scale
- ✅ Railway includes it **FREE** on your plan

---

## Step 1: Add Postgres to Railway

### 1.1 Open Railway Dashboard
Go to: https://railway.app/dashboard

### 1.2 Add Postgres Database
1. Click your project (ai-stock-market-agent)
2. Click "+ New" button
3. Select "Database" → "PostgreSQL"
4. Railway will provision a Postgres instance (takes ~30 seconds)

### 1.3 Get Connection String
1. Click the new Postgres service
2. Go to "Variables" tab
3. Copy the `DATABASE_URL` value
   - Should look like: `postgresql://user:pass@host:5432/railway`

---

## Step 2: Configure Environment Variables

In your Railway project → Variables tab, add:

```
DB_TYPE=postgres
DATABASE_URL=<paste the DATABASE_URL from Postgres service>
```

**Keep all existing variables:**
- TELEGRAM_BOT_TOKEN
- GEMINI_API_KEY
- GEMINI_MODEL_NAME
- (all your Twitter vars)

---

## Step 3: Update Code to Use New Database Module

The new `database_postgres.py` file supports both SQLite (local) and Postgres (production).

### What Changed:
- ✅ Auto-detects DB type from environment variable
- ✅ Uses Postgres on Railway, SQLite locally
- ✅ Same API - no code changes needed elsewhere
- ✅ Proper connection pooling
- ✅ Index optimization for both DBs

---

## Step 4: Deploy

### 4.1 Commit Changes
```bash
git add requirements.txt database_postgres.py
git commit -m "Add Postgres support for Railway deployment"
git push
```

### 4.2 Railway Auto-Deploys
- Railway detects the push
- Installs new dependencies (psycopg2-binary)
- Starts using Postgres automatically

### 4.3 Verify in Logs
Look for:
```
✅ Database initialized (POSTGRES at Railway)
```

---

## Step 5: Initialize Postgres Schema

The first time you deploy, the schema will be created automatically.

Check Railway logs for:
```
Initializing AI Stock Agent database...
Database type: postgres
Postgres URL: postgresql://...
✅ Database initialized (POSTGRES at Railway)
```

---

## Step 6: Optional - Migrate Existing SQLite Data

If you have important data in local SQLite, run the migration script:

```bash
# Set Railway Postgres URL locally
export DATABASE_URL="postgresql://user:pass@host:5432/railway"

# Run migration
python migrate_sqlite_to_postgres.py
```

This will copy all:
- Scans
- Signals
- Price tracking
- Trades

from local SQLite to Railway Postgres.

---

## Benefits You Get Immediately

### 1. Persistent Data
- Scans survive redeploys
- Trade history preserved
- Signal tracking continues across restarts

### 2. Better Performance
- Indexed queries
- Connection pooling
- Optimized for concurrent access

### 3. Ready for Growth
- Can add more Railway instances
- Multi-user support ready
- Easy to add Redis caching next

---

## Troubleshooting

### "psycopg2 not installed"
**Fix:** Railway will install it from requirements.txt automatically. If testing locally:
```bash
pip3 install psycopg2-binary
```

### "Connection refused"
**Fix:** Check that DATABASE_URL is set correctly in Railway variables.

### "Database does not exist"
**Fix:** Railway Postgres creates the DB automatically. Make sure you're using the correct DATABASE_URL from the Postgres service (not the main app).

### Data not showing up
**Fix:** The first deploy creates empty tables. Run a scan to populate data, or migrate from SQLite.

---

## Next Steps After Postgres

Once Postgres is working, we can add:

1. **Redis Caching**
   - Cache stock prices for 5 minutes
   - Cache news for 15 minutes
   - Reduce API rate limits

2. **NewsAPI Integration**
   - Supplement yfinance with dedicated news API
   - More reliable news fetching
   - Better coverage

3. **Advanced Features**
   - User authentication
   - Per-user watchlists
   - Multi-tenant support

---

## Railway Postgres Dashboard

Access your database directly:
1. Click Postgres service in Railway
2. Go to "Data" tab
3. Query your tables:
   ```sql
   SELECT * FROM scans ORDER BY scan_date DESC LIMIT 10;
   SELECT * FROM signals WHERE score >= 4;
   SELECT * FROM trades WHERE status = 'OPEN';
   ```

---

**Ready to proceed?** Let me know when you've added Postgres in Railway and I'll help with the deployment!
