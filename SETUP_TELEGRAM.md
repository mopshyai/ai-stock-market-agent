# Telegram Bot Setup Guide

Get daily stock signals delivered directly to your phone via Telegram.

---

## Step 1: Create Your Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Start a chat and send: `/newbot`
3. Follow the prompts:
   - **Bot name**: `AI Stock Agent` (or any name you like)
   - **Username**: `your_username_bot` (must end with `bot`)
4. BotFather will give you a **Bot Token**
   - Looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`
   - **Keep this secret!**

---

## Step 2: Get Your Chat ID

**Option A: Use @userinfobot (Easiest)**

1. Search for **@userinfobot** in Telegram
2. Start a chat with it
3. It will immediately show your **Chat ID**
4. Copy the number (e.g., `123456789`)

**Option B: Use the Telegram API**

1. Send a message to your bot (the one you just created)
2. Visit this URL in your browser:
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   ```
   Replace `<YOUR_BOT_TOKEN>` with your actual token
3. Look for `"chat":{"id":123456789}` in the JSON response
4. Copy that `id` number

---

## Step 3: Configure Environment Variables

Add your bot credentials to your environment:

### Mac/Linux:
```bash
export TELEGRAM_BOT_TOKEN="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
export TELEGRAM_CHAT_ID="123456789"
```

To make it permanent, add to `~/.zshrc` or `~/.bashrc`:
```bash
echo 'export TELEGRAM_BOT_TOKEN="your_token_here"' >> ~/.zshrc
echo 'export TELEGRAM_CHAT_ID="your_chat_id_here"' >> ~/.zshrc
source ~/.zshrc
```

### Windows (PowerShell):
```powershell
$env:TELEGRAM_BOT_TOKEN="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
$env:TELEGRAM_CHAT_ID="123456789"
```

To make it permanent (Windows):
```powershell
[System.Environment]::SetEnvironmentVariable('TELEGRAM_BOT_TOKEN', 'your_token_here', 'User')
[System.Environment]::SetEnvironmentVariable('TELEGRAM_CHAT_ID', 'your_chat_id_here', 'User')
```

---

## Step 4: Test Your Connection

Run the test script:
```bash
python telegram_bot.py
```

You should see:
```
Testing Telegram connection...
✅ Telegram bot connected successfully!
```

And receive a test message in Telegram.

---

## Step 5: Configure Alert Settings

Edit `config.yaml` to customize alerts:

```yaml
alerts:
  telegram:
    enabled: true                    # Turn on/off Telegram alerts
    send_charts: true                # Send chart images
    only_signal_stocks: true         # Only send stocks with signals
```

**Options:**
- `enabled`: Set to `false` to disable Telegram alerts
- `send_charts`: Set to `false` to only send text (no images)
- `only_signal_stocks`: Set to `false` to get alerts for all scanned stocks

---

## Step 6: Run Your First Scan

```bash
python scan_and_chart.py
```

You'll receive:
1. A summary message with all detected signals
2. Individual chart images for each stock (if enabled)

---

## What You'll Receive

**Summary Message:**
```
🤖 AI Stock Agent Daily Scan
==============================

📊 Scanned: 11 stocks
🔔 Consolidation Setups: 2
📉 Buy-the-Dip Setups: 1

──────────────────────────────

*AAPL* @ $178.50
   🟢 CONSOLIDATION detected
   • RSI: 52.3
   • ADX: 18.5
   • BB Width: 3.21%
   • ATR: 1.85%

*NVDA* @ $495.20
   🔻 BUY-THE-DIP setup
   • RSI: 32.1
   • ADX: 25.7
   • BB Width: 5.42%
   • ATR: 2.31%
```

**Chart Images:**
- Clean candlestick charts
- Moving averages (20, 50)
- Volume bars
- One chart per signal stock

---

## Troubleshooting

**"TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set"**
- Make sure you exported the environment variables
- Restart your terminal after setting them
- Verify with: `echo $TELEGRAM_BOT_TOKEN` (Mac/Linux) or `$env:TELEGRAM_BOT_TOKEN` (Windows)

**"Failed to send test message"**
- Check your bot token is correct
- Check your chat ID is correct
- Make sure you've started a chat with your bot (send any message first)

**"No signals detected"**
- This means no stocks met your signal criteria
- Try adjusting thresholds in `config.yaml`
- Check `scan_results.csv` to see all stock data

---

## Security Note

Never share your bot token publicly or commit it to git.
Always use environment variables, never hardcode tokens in your code.

---

## Next Steps

Once Telegram is working, set up automation to run scans daily:
👉 See [SETUP_AUTOMATION.md](SETUP_AUTOMATION.md)
