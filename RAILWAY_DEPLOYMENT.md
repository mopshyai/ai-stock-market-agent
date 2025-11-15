# Railway Deployment Instructions

## ✅ Code Successfully Pushed to GitHub

Your bot improvements are now live on GitHub at:
`https://github.com/mopshyai/ai-stock-market-agent`

## 🚀 Deploy to Railway

### Step 1: Configure Environment Variables

Go to your Railway project dashboard and add/update these variables:

```
TELEGRAM_BOT_TOKEN=7909396650:AAHRxUnSIZxWdYSCaEcZcUfQVEzZ3r8qbj0
GEMINI_API_KEY=AIzaSyAqoJASCUYm0L2yW1u0qYd54Ps-Nr_MVZ0
GEMINI_MODEL_NAME=gemini-pro
```

### Step 2: Redeploy

Railway will automatically detect the new commit and redeploy. If not:
1. Go to Deployments tab
2. Click "Deploy Latest" or trigger a new deployment

### Step 3: Verify Deployment

Check the deployment logs for these success messages:
- `✅ Gemini AI integration enabled (model: gemini-pro)`
- `✅ Market Intelligence enabled (stocks, news, analysis)`
- `✅ Bot started! Press Ctrl+C to stop`

If you see `409 Conflict` errors, it means there's still a local instance running.

## 📱 Test on Telegram

Once deployed, test these queries on your Telegram bot:

### Financial Planning
- "what is SIP" → Systematic Investment Plan explanation
- "what is EMI" → Loan calculator info

### Market Data
- "AAPL price" → Real-time Apple stock price
- "Tesla news" → Latest Tesla news
- "news" → General market news
- "top gainers" → Best performing stocks

### Trading Indicators
- "what is RSI" → Technical indicator explanation
- "what is MACD" → Moving average convergence divergence

### Commands
- `/start` → Welcome message
- `/help` → All commands
- `/market` → Market overview (SPY, QQQ, VIX)
- `/trades` → Current trades (if any in database)

## 🐛 Troubleshooting

### Bot not responding?
1. Check Railway logs for errors
2. Verify environment variables are set correctly
3. Ensure only ONE bot instance is running (stop local instances)

### "No news available"?
- Market might be closed
- yfinance rate limit hit (wait a few minutes)
- Try with a specific stock: "AAPL news"

### Gemini errors?
- Verify GEMINI_API_KEY is correct
- Check you have API quota remaining
- Try GEMINI_MODEL_NAME=gemini-1.0-pro if gemini-pro fails

## 📊 New Features Added

1. **SIP Support** - Explains Systematic Investment Plans with examples and benefits
2. **EMI Calculator** - Provides loan installment information and formulas
3. **General News** - Can fetch market news without specifying a stock
4. **Better Error Handling** - Graceful fallbacks when AI/data unavailable
5. **Improved Responses** - More informative and user-friendly messages

## 🔗 Links

- GitHub Repo: https://github.com/mopshyai/ai-stock-market-agent
- Railway Dashboard: https://railway.app
- Telegram Bot: @YourBotUsername (check /start for details)

---

**Need help?** Check the Railway logs or test locally first by stopping Railway and running:
```bash
export TELEGRAM_BOT_TOKEN="your_token"
export GEMINI_API_KEY="your_key"
python3 interactive_telegram_bot.py
```
