# Automation Setup Guide

Set up your AI Stock Agent to run automatically every day at market open (or any time you choose).

---

## Quick Start (Run Scheduler Manually)

The simplest way to start:

```bash
python scheduler.py --time 09:30 --timezone US/Eastern
```

This will:
- Run the scan daily at 9:30 AM Eastern Time (US market open)
- Keep running in the foreground
- Send Telegram alerts automatically

**Leave the terminal window open** or it will stop.

To run immediately (one-time):
```bash
python scheduler.py --run-now
```

---

## Option A: Run in Background (All Platforms)

### Mac/Linux:

**Using nohup:**
```bash
nohup python scheduler.py --time 09:30 --timezone US/Eastern > scheduler.log 2>&1 &
```

**Using screen (better for SSH sessions):**
```bash
screen -S stock_agent
python scheduler.py --time 09:30 --timezone US/Eastern
# Press Ctrl+A, then D to detach
# Reattach later with: screen -r stock_agent
```

**Stop the background process:**
```bash
ps aux | grep scheduler.py
kill <PID>
```

### Windows:

**Using PowerShell with Start-Process:**
```powershell
Start-Process python -ArgumentList "scheduler.py","--time","09:30","--timezone","US/Eastern" -WindowStyle Hidden
```

**Stop the process:**
```powershell
Get-Process | Where-Object {$_.ProcessName -eq "python"} | Stop-Process
```

---

## Option B: System-Level Automation (Survives Reboots)

### Mac: Using launchd

1. Create a plist file:
```bash
nano ~/Library/LaunchAgents/com.stockagent.scheduler.plist
```

2. Paste this content (update paths to your actual paths):
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.stockagent.scheduler</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/Users/YOUR_USERNAME/Downloads/ai_stock_agent_fresh2/scheduler.py</string>
        <string>--time</string>
        <string>09:30</string>
        <string>--timezone</string>
        <string>US/Eastern</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/YOUR_USERNAME/Downloads/ai_stock_agent_fresh2</string>
    <key>StandardOutPath</key>
    <string>/Users/YOUR_USERNAME/Downloads/ai_stock_agent_fresh2/scheduler.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/YOUR_USERNAME/Downloads/ai_stock_agent_fresh2/scheduler_error.log</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>EnvironmentVariables</key>
    <dict>
        <key>TELEGRAM_BOT_TOKEN</key>
        <string>YOUR_BOT_TOKEN_HERE</string>
        <key>TELEGRAM_CHAT_ID</key>
        <string>YOUR_CHAT_ID_HERE</string>
    </dict>
</dict>
</plist>
```

3. Update the file:
   - Replace `YOUR_USERNAME` with your actual username
   - Replace `YOUR_BOT_TOKEN_HERE` with your Telegram bot token
   - Replace `YOUR_CHAT_ID_HERE` with your Telegram chat ID
   - Update Python path if needed (check with: `which python3`)

4. Load the service:
```bash
launchctl load ~/Library/LaunchAgents/com.stockagent.scheduler.plist
```

5. Verify it's running:
```bash
launchctl list | grep stockagent
```

**To stop/remove:**
```bash
launchctl unload ~/Library/LaunchAgents/com.stockagent.scheduler.plist
```

---

### Linux: Using systemd

1. Create a service file:
```bash
sudo nano /etc/systemd/system/stockagent.service
```

2. Paste this content (update paths):
```ini
[Unit]
Description=AI Stock Agent Scheduler
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/ai_stock_agent_fresh2
ExecStart=/usr/bin/python3 /home/YOUR_USERNAME/ai_stock_agent_fresh2/scheduler.py --time 09:30 --timezone US/Eastern
Restart=always
Environment="TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN_HERE"
Environment="TELEGRAM_CHAT_ID=YOUR_CHAT_ID_HERE"

[Install]
WantedBy=multi-user.target
```

3. Update the file with your paths and credentials

4. Enable and start the service:
```bash
sudo systemctl enable stockagent.service
sudo systemctl start stockagent.service
```

5. Check status:
```bash
sudo systemctl status stockagent.service
```

**To stop/disable:**
```bash
sudo systemctl stop stockagent.service
sudo systemctl disable stockagent.service
```

---

### Windows: Using Task Scheduler

1. Open **Task Scheduler** (search in Start menu)

2. Click **"Create Basic Task"**

3. Fill in:
   - **Name**: AI Stock Agent
   - **Description**: Daily stock market scanner
   - **Trigger**: Daily
   - **Time**: 9:30 AM
   - **Action**: Start a program

4. For "Program/script":
   ```
   C:\Python\python.exe
   ```
   (Find your Python path with: `where python` in CMD)

5. For "Add arguments":
   ```
   scheduler.py --time 09:30 --timezone US/Eastern
   ```

6. For "Start in":
   ```
   C:\Users\YOUR_USERNAME\Downloads\ai_stock_agent_fresh2
   ```

7. Before finishing, check **"Open Properties dialog"**

8. In Properties:
   - Go to **"General"** tab
   - Check **"Run whether user is logged on or not"**
   - Go to **"Settings"** tab
   - Check **"Run task as soon as possible after a scheduled start is missed"**

9. Click **OK** and enter your Windows password

**To set environment variables for Task Scheduler:**
- Add them to System Environment Variables (Control Panel → System → Advanced → Environment Variables)
- Or use a `.env` file and load with `python-dotenv`

---

## Option C: Using Cron (Mac/Linux - Simple Daily Job)

If you just want to run the scan once per day (not keep scheduler running):

1. Edit your crontab:
```bash
crontab -e
```

2. Add this line (update paths):
```bash
30 9 * * 1-5 cd /Users/YOUR_USERNAME/Downloads/ai_stock_agent_fresh2 && /usr/local/bin/python3 scan_and_chart.py >> /Users/YOUR_USERNAME/Downloads/ai_stock_agent_fresh2/cron.log 2>&1
```

This runs Monday-Friday at 9:30 AM.

3. Save and exit (`:wq` in vim, or `Ctrl+X` in nano)

4. Verify:
```bash
crontab -l
```

**Cron time syntax:**
```
* * * * *
│ │ │ │ │
│ │ │ │ └─ Day of week (0-7, Sun=0 or 7)
│ │ │ └─── Month (1-12)
│ │ └───── Day of month (1-31)
│ └─────── Hour (0-23)
└───────── Minute (0-59)
```

**Common schedules:**
```bash
# Every weekday at 9:30 AM
30 9 * * 1-5

# Every day at 6:00 PM
0 18 * * *

# Every Monday at 8:00 AM
0 8 * * 1

# Twice a day (9:30 AM and 3:30 PM)
30 9,15 * * 1-5
```

---

## Recommended Schedule Times

**US Markets:**
- **Pre-market scan**: 8:30 AM ET (`--time 08:30 --timezone US/Eastern`)
- **Market open**: 9:30 AM ET (most popular)
- **Mid-day**: 12:00 PM ET
- **Market close**: 4:00 PM ET

**Other Markets:**
- **Europe**: 9:00 AM CET (`--timezone Europe/Berlin`)
- **UK**: 8:00 AM GMT (`--timezone Europe/London`)
- **Asia**: 9:00 AM HKT (`--timezone Asia/Hong_Kong`)

---

## Monitoring Your Automation

### Check if it's running:

**Mac/Linux:**
```bash
ps aux | grep scheduler.py
```

**Windows:**
```powershell
Get-Process | Where-Object {$_.ProcessName -eq "python"}
```

### Check logs:

**If using scheduler.py manually:**
```bash
tail -f scheduler.log
```

**If using system services:**
```bash
# Mac
tail -f ~/Library/LaunchAgents/scheduler.log

# Linux
journalctl -u stockagent.service -f

# Windows
# Check Task Scheduler History tab
```

---

## Testing Your Automation

Before setting up daily automation, test it:

1. Run once immediately:
```bash
python scheduler.py --run-now
```

2. Run in foreground with short schedule:
```bash
python scheduler.py --time 10:05 --timezone US/Eastern
```
(Set time to 5 minutes from now)

3. Check you receive Telegram alerts

4. Once working, set up permanent automation

---

## Troubleshooting

**"Scheduler not running"**
- Check if Python process is active
- Check log files for errors
- Verify paths in config files are absolute paths

**"No Telegram alerts"**
- Verify environment variables are set in the automation config
- Test manually first: `python telegram_bot.py`
- Check that bot has permission to send messages

**"Scan failed"**
- Check internet connection
- Verify yfinance can access data
- Check log files for specific errors

**"Only runs once, doesn't repeat"**
- Make sure you're using `scheduler.py`, not directly calling `scan_and_chart.py`
- Check the scheduler process is still running

---

## Cloud Deployment (Optional)

Want to run this 24/7 without your computer on?

Deploy to:
- **AWS Lambda** (scheduled with EventBridge)
- **Google Cloud Functions** (scheduled with Cloud Scheduler)
- **Heroku** (scheduled with Heroku Scheduler)
- **DigitalOcean Droplet** (use systemd)
- **Raspberry Pi** (use systemd/cron)

Let me know if you need cloud deployment instructions!

---

## Next Steps

Once automation is working:
- Monitor for a few days to ensure reliability
- Adjust scan times based on your needs
- Consider adding more tickers or signals
- Build a dashboard to visualize historical results

---

**You now have a fully automated AI stock agent that runs itself!**
