# 🔧 Troubleshooting Guide

Common issues and solutions for AI Stock Market Agent.

---

## 🚨 Common Issues

### Issue: "ModuleNotFoundError" or Import Errors

**Symptoms:**
```
ModuleNotFoundError: No module named 'yfinance'
ImportError: cannot import name 'X'
```

**Solution:**
```bash
# Make sure you're in the virtual environment
source .venv/bin/activate  # Mac/Linux
# or
.venv\Scripts\activate  # Windows

# Install/update dependencies
pip install -r requirements.txt --upgrade
```

**Prevention:** Always activate your virtual environment before running scripts.

---

### Issue: Telegram Bot Not Sending Messages

**Symptoms:**
- No alerts received
- Error: "Failed to send message"
- Bot token invalid

**Solution:**

1. **Verify environment variables are set:**
   ```bash
   # Check if variables are loaded
   echo $TELEGRAM_BOT_TOKEN
   echo $TELEGRAM_CHAT_ID
   ```

2. **Test bot connection:**
   ```bash
   python telegram_bot.py
   ```

3. **Verify bot token:**
   - Go to @BotFather on Telegram
   - Send `/mybots`
   - Select your bot
   - Copy the token (format: `123456789:ABCdef...`)

4. **Get your chat ID:**
   - Message your bot on Telegram
   - Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - Find `"chat":{"id":123456789}` in the response

5. **Set environment variables:**
   ```bash
   # Mac/Linux
   export TELEGRAM_BOT_TOKEN="your_token_here"
   export TELEGRAM_CHAT_ID="your_chat_id_here"
   
   # Windows (PowerShell)
   $env:TELEGRAM_BOT_TOKEN="your_token_here"
   $env:TELEGRAM_CHAT_ID="your_chat_id_here"
   
   # Or use .env file (recommended)
   cp .env.example .env
   # Edit .env with your values
   ```

**See:** [SETUP_TELEGRAM.md](SETUP_TELEGRAM.md) for detailed setup.

---

### Issue: "No data available" or Empty Scan Results

**Symptoms:**
- CSV file is empty
- Dashboard shows "No data"
- All stocks return "No data"

**Solution:**

1. **Check internet connection:**
   ```bash
   ping google.com
   ```

2. **Verify ticker symbols:**
   - Check `config.yaml` for valid tickers
   - Test a single ticker: `yfinance.Ticker("AAPL").info`

3. **Check market hours:**
   - Some data may be limited outside market hours
   - Try running during market hours (9:30 AM - 4:00 PM ET)

4. **Verify data period/interval:**
   ```yaml
   # config.yaml
   data:
     period: "5d"      # Try "1mo" if 5d fails
     interval: "15m"   # Try "1d" if 15m fails
   ```

5. **Check yfinance version:**
   ```bash
   pip install yfinance --upgrade
   ```

---

### Issue: Dashboard Won't Start or Crashes

**Symptoms:**
- `streamlit run dashboard.py` fails
- Port 8501 already in use
- Dashboard loads but shows errors

**Solution:**

1. **Port already in use:**
   ```bash
   # Find process using port 8501
   lsof -ti:8501  # Mac/Linux
   netstat -ano | findstr :8501  # Windows
   
   # Kill the process
   kill -9 <PID>  # Mac/Linux
   taskkill /PID <PID> /F  # Windows
   
   # Or use different port
   streamlit run dashboard.py --server.port 8502
   ```

2. **Missing dependencies:**
   ```bash
   pip install streamlit streamlit-autorefresh plotly --upgrade
   ```

3. **Database locked:**
   ```bash
   # Close other instances
   pkill -f streamlit
   pkill -f scan_and_chart
   
   # Restart dashboard
   streamlit run dashboard.py
   ```

4. **Clear Streamlit cache:**
   ```bash
   rm -rf .streamlit/cache  # Mac/Linux
   rmdir /s .streamlit\cache  # Windows
   ```

---

### Issue: Charts Not Generating

**Symptoms:**
- No PNG files in `/charts` directory
- Error: "Failed to generate chart"
- Charts are blank or corrupted

**Solution:**

1. **Check directory permissions:**
   ```bash
   # Ensure charts directory exists and is writable
   mkdir -p charts
   chmod 755 charts  # Mac/Linux
   ```

2. **Verify mplfinance installation:**
   ```bash
   pip install mplfinance --upgrade
   ```

3. **Check for data:**
   - Charts require price data
   - Verify scan completed successfully
   - Check `scan_results.csv` has data

4. **Test chart generation:**
   ```python
   import mplfinance as mpf
   import yfinance as yf
   
   df = yf.download("AAPL", period="5d", interval="15m")
   mpf.plot(df, type='candle', style='charles', savefig='test.png')
   ```

---

### Issue: Scheduler Not Running

**Symptoms:**
- Scans don't run automatically
- Scheduler exits immediately
- Timezone errors

**Solution:**

1. **Verify scheduler is running:**
   ```bash
   # Check if process is active
   ps aux | grep scheduler.py  # Mac/Linux
   tasklist | findstr scheduler  # Windows
   ```

2. **Test scheduler:**
   ```bash
   # Run immediately to test
   python scheduler.py --run-now
   ```

3. **Check timezone:**
   ```bash
   # Use correct timezone format
   python scheduler.py --time 09:30 --timezone US/Eastern
   # Valid timezones: US/Eastern, US/Central, US/Mountain, US/Pacific, UTC
   ```

4. **Run in background:**
   ```bash
   # Mac/Linux
   nohup python scheduler.py --time 09:30 --timezone US/Eastern > scheduler.log 2>&1 &
   
   # Windows (use Task Scheduler instead)
   ```

5. **Check logs:**
   ```bash
   tail -f scheduler.log  # Mac/Linux
   ```

**See:** [SETUP_AUTOMATION.md](SETUP_AUTOMATION.md) for detailed setup.

---

### Issue: Database Errors

**Symptoms:**
- "Database is locked"
- "No such table"
- "Error loading performance data"

**Solution:**

1. **Database locked:**
   ```bash
   # Close all connections
   pkill -f python
   # Wait a few seconds, then restart
   ```

2. **Initialize database:**
   ```python
   from database import init_database
   init_database()
   ```

3. **Check database exists:**
   ```bash
   ls -la stock_agent.db  # Mac/Linux
   dir stock_agent.db  # Windows
   ```

4. **Reset database (if corrupted):**
   ```bash
   # Backup first!
   cp stock_agent.db stock_agent.db.backup
   
   # Delete and recreate
   rm stock_agent.db
   python -c "from database import init_database; init_database()"
   ```

**See:** [DATABASE_GUIDE.md](DATABASE_GUIDE.md) for more details.

---

### Issue: Slow Performance

**Symptoms:**
- Scans take >5 minutes
- Dashboard is slow to load
- High CPU/memory usage

**Solution:**

1. **Reduce ticker count:**
   ```yaml
   # config.yaml - start with fewer tickers
   tickers:
     - AAPL
     - MSFT
     - TSLA
   ```

2. **Increase data interval:**
   ```yaml
   # Use daily instead of 15m for faster scans
   data:
     interval: "1d"  # Instead of "15m"
   ```

3. **Check system resources:**
   ```bash
   # Monitor CPU/memory
   top  # Mac/Linux
   taskmgr  # Windows
   ```

4. **Optimize database:**
   ```python
   # Run periodically to optimize
   import sqlite3
   conn = sqlite3.connect('stock_agent.db')
   conn.execute('VACUUM')
   conn.close()
   ```

---

### Issue: Environment Variables Not Loading

**Symptoms:**
- Variables work in terminal but not in script
- `.env` file not being read

**Solution:**

1. **Install python-dotenv:**
   ```bash
   pip install python-dotenv
   ```

2. **Load .env in your script:**
   ```python
   from dotenv import load_dotenv
   import os
   
   load_dotenv()  # Load .env file
   
   token = os.getenv('TELEGRAM_BOT_TOKEN')
   ```

3. **Verify .env file location:**
   - Must be in project root directory
   - Same directory as `config.yaml`

4. **Check .env file format:**
   ```bash
   # Correct format (no spaces around =)
   TELEGRAM_BOT_TOKEN=your_token_here
   TELEGRAM_CHAT_ID=123456789
   
   # Wrong format
   TELEGRAM_BOT_TOKEN = your_token_here  # ❌
   ```

---

## 🔍 Debugging Tips

### Enable Verbose Logging

```python
# Add to your scripts
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test Individual Components

```bash
# Test data fetching
python -c "import yfinance as yf; print(yf.Ticker('AAPL').info)"

# Test database
python -c "from database import init_database; init_database(); print('OK')"

# Test Telegram
python telegram_bot.py

# Test scanner
python scan_and_chart.py
```

### Check System Requirements

```bash
# Python version (need 3.8+)
python --version

# Check installed packages
pip list | grep -E "yfinance|streamlit|pandas"

# Check disk space
df -h  # Mac/Linux
dir  # Windows
```

---

## 📞 Getting Help

1. **Check documentation:**
   - [README.md](README.md) - Quick start
   - [SETUP_TELEGRAM.md](SETUP_TELEGRAM.md) - Telegram setup
   - [SETUP_AUTOMATION.md](SETUP_AUTOMATION.md) - Scheduler setup
   - [DATABASE_GUIDE.md](DATABASE_GUIDE.md) - Database usage

2. **Check logs:**
   - Terminal output
   - `scheduler.log` (if using scheduler)
   - Streamlit error messages

3. **Common solutions:**
   - Restart the application
   - Update dependencies: `pip install -r requirements.txt --upgrade`
   - Check internet connection
   - Verify configuration files

4. **Report issues:**
   - Include error messages
   - Include your Python version
   - Include your OS
   - Include relevant config snippets

---

## ✅ Quick Health Check

Run this to verify everything is working:

```bash
# 1. Check Python version
python --version  # Should be 3.8+

# 2. Check dependencies
pip list | grep -E "yfinance|streamlit|pandas|ta"

# 3. Test data fetch
python -c "import yfinance as yf; df = yf.download('AAPL', period='1d'); print('Data OK' if not df.empty else 'Data FAIL')"

# 4. Test database
python -c "from database import init_database; init_database(); print('DB OK')"

# 5. Test scan
python scan_and_chart.py

# 6. Test dashboard
streamlit run dashboard.py
```

If all pass, your setup is working! 🎉

---

*Last updated: January 2025*

