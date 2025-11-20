# StockGenie - New Features Quick Start

## 🚀 Quick Setup Guide

This guide helps you get started with the newly implemented features.

---

## 1. Analytics Dashboard

### What it does
- Real-time performance metrics
- Win rate by signal type
- P/L charts
- R-multiple distribution
- Best performing tickers

### How to use

```bash
# Start Streamlit dashboard
streamlit run dashboard.py

# Navigate to sidebar → "Analytics" page
```

**Features:**
- Filter by time range (7, 14, 30, 60, 90 days)
- Interactive Plotly charts
- Export-ready tables

---

## 2. Backtesting Engine

### What it does
Replay historical signals on real price data to see how they would have performed.

### How to use

```bash
# Run standalone backtest
python3 backtesting_engine.py
```

**Or in your code:**

```python
from backtesting_engine import BacktestEngine

# Create engine
engine = BacktestEngine(
    initial_capital=10000,    # Starting capital
    risk_per_trade_pct=1.0     # Risk 1% per trade
)

# Run backtest
results = engine.run_backtest(
    days=90,           # Last 90 days
    min_score=3,       # Min signal score
    holding_days=5     # Hold for 5 days max
)

# Print results
engine.print_results(results)
```

**Output:**
- Total return %
- Win rate
- Avg R-multiple
- Best/worst trades
- Equity curve

---

## 3. User Authentication

### What it does
Multi-user support with secure login and custom watchlists.

### How to use

```python
from user_auth import UserAuth, UserWatchlistManager

# Initialize
auth = UserAuth()

# Create user
result = auth.create_user(
    email="user@example.com",
    password="SecurePass123!",
    username="trader1"
)

# Login
login = auth.login("user@example.com", "SecurePass123!")
session_token = login['session_token']

# Verify session
user = auth.verify_session(session_token)

# Create watchlist
wl_mgr = UserWatchlistManager()
wl_mgr.create_watchlist(
    user_id=user['user_id'],
    name="Tech Stocks",
    tickers=["AAPL", "MSFT", "GOOGL"]
)
```

---

## 4. Subscription Management

### What it does
Enforce usage limits based on subscription tier (Free/Pro/Enterprise).

### How to use

```python
from subscription_manager import SubscriptionManager

sub_mgr = SubscriptionManager()

# Check if user can perform action
result = sub_mgr.check_usage_limit(user_id=1, action_type='scan')

if result['allowed']:
    # Perform scan
    sub_mgr.log_usage(user_id=1, action_type='scan')
else:
    print(f"Limit reached: {result['reason']}")

# Upgrade user
sub_mgr.upgrade_subscription(user_id=1, new_tier='PRO')

# Get usage stats
stats = sub_mgr.get_usage_stats(user_id=1, days=30)
```

**Tier Limits:**
- **FREE**: 1 watchlist, 3 scans/day
- **PRO**: 10 watchlists, 50 scans/day, alerts
- **ENTERPRISE**: Unlimited, auto-trading

---

## 5. Auto-Trading (Broker Integration)

### What it does
Connect to real brokers and execute trades automatically.

### Alpaca Setup (US Markets)

```bash
# Sign up at https://alpaca.markets (free paper trading)
# Get your API keys

export ALPACA_API_KEY="your_key_here"
export ALPACA_API_SECRET="your_secret_here"
```

```python
from broker_integration import AlpacaTrading

# Initialize (paper trading)
alpaca = AlpacaTrading(paper=True)

# Check account
account = alpaca.get_account()
print(f"Buying Power: ${account['buying_power']}")

# Place bracket order
order = alpaca.place_bracket_order(
    ticker="AAPL",
    qty=10,
    entry_price=175.00,
    stop_loss=170.00,
    take_profit=180.00
)

print(f"Order ID: {order['id']}")
```

### Zerodha Kite Setup (Indian Markets)

```bash
# Subscribe at https://kite.trade (₹2000/month)
# Get API key and access token

export KITE_API_KEY="your_key"
export KITE_ACCESS_TOKEN="your_token"
```

```python
from broker_integration import ZerodhaKite

kite = ZerodhaKite()

# Place market order
order = kite.place_order(
    ticker="INFY",
    exchange="NSE",
    transaction_type="BUY",
    quantity=10,
    order_type="MARKET"
)
```

### Auto-Execute Signals

```python
from broker_integration import AutoTradingEngine

# Initialize with broker
engine = AutoTradingEngine(broker='alpaca', paper_trading=True)

# Convert signal to trade
signal = {
    'ticker': 'TSLA',
    'entry_price': 250.00,
    'stop_loss': 245.00,
    'take_profit_1': 255.00,
    'position_size': 10
}

result = engine.execute_signal_trade(signal)
print(result)
```

---

## 6. Stripe Payments (Coming Soon)

### Setup

```bash
# Get keys from https://stripe.com
export STRIPE_SECRET_KEY="sk_test_..."
export STRIPE_PUBLISHABLE_KEY="pk_test_..."
```

```python
from subscription_manager import StripeIntegration

stripe = StripeIntegration()

# Create checkout session
session = stripe.create_checkout_session(
    user_id=1,
    tier='PRO'
)

# Redirect user to session['checkout_url']
```

**Note:** Full Stripe integration requires:
1. Install stripe library: `pip install stripe`
2. Set up webhook endpoint
3. Handle payment events

---

## 📊 Testing Everything

### Run All Tests

```bash
# Analytics
python3 analytics_engine.py

# Backtesting
python3 backtesting_engine.py

# User Auth
python3 user_auth.py

# Subscriptions
python3 subscription_manager.py

# Broker Integration
python3 broker_integration.py
```

---

## 🔧 Common Issues

### Issue: "No signals found for backtest"
**Solution:** Run scanner first to generate signals
```bash
python3 scan_and_chart.py
```

### Issue: "Alpaca not configured"
**Solution:** Set environment variables
```bash
export ALPACA_API_KEY="..."
export ALPACA_API_SECRET="..."
```

### Issue: "Database table doesn't exist"
**Solution:** Initialize database
```python
from database import init_database
init_database()
```

---

## 📚 Next Steps

1. **Integrate with Streamlit**
   - Add login page
   - Protect routes with session checks
   - Add subscription upgrade UI

2. **Test Broker APIs**
   - Sign up for Alpaca paper trading
   - Test with small positions
   - Verify order execution

3. **Enable Payments**
   - Set up Stripe account
   - Create product/price IDs
   - Implement webhook handler

---

## 🎯 Feature Status

| Feature | Status | Ready for Use |
|---------|--------|---------------|
| Analytics Dashboard | ✅ Complete | ✅ Yes |
| Backtesting | ✅ Complete | ✅ Yes |
| User Auth | ✅ Complete | ⚠️ Needs UI integration |
| Subscriptions | ✅ Complete | ⚠️ Needs Stripe testing |
| Broker APIs | ✅ Complete | ⚠️ Needs API keys |
| Legal Docs | ✅ Complete | ✅ Yes |

---

**Questions?** Check the main implementation plan or run individual test scripts.
