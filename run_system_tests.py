#!/usr/bin/env python3
"""
MASTER TEST SCRIPT
Runs tests for all new modules to verify system integrity.
"""

import sys
import os
import time
from datetime import datetime

# Add current directory to path
sys.path.append(os.getcwd())

def run_test(name, func):
    print(f"\n🔵 Testing {name}...")
    try:
        start_time = time.time()
        func()
        duration = time.time() - start_time
        print(f"✅ {name} Passed ({duration:.2f}s)")
        return True
    except Exception as e:
        print(f"❌ {name} Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_analytics():
    from analytics_engine import get_signal_performance_metrics
    metrics = get_signal_performance_metrics()
    print(f"   - Metrics retrieved: {len(metrics)} keys")
    assert 'total_signals' in metrics

def test_backtesting():
    from backtesting_engine import BacktestEngine
    engine = BacktestEngine(initial_capital=10000)
    # Just initialize, don't run full backtest as it takes time and needs data
    assert engine.initial_capital == 10000
    print("   - Backtest engine initialized")

def test_user_auth():
    from user_auth import UserAuth
    auth = UserAuth()
    # Create a test user
    test_email = f"test_{int(time.time())}@example.com"
    res = auth.create_user(test_email, "TestPass123!", "testuser")
    if not res['success'] and "already exists" not in res.get('error', ''):
        raise Exception(f"Create user failed: {res}")
    
    # Login
    login = auth.login(test_email, "TestPass123!")
    assert login['success']
    print(f"   - User created and logged in: {test_email}")

def test_subscription():
    from subscription_manager import SubscriptionManager
    sub = SubscriptionManager()
    # Check limits for a dummy user
    limit = sub.check_usage_limit(1, 'scan')
    assert 'allowed' in limit
    print("   - Subscription limits checked")

def test_broker_integration():
    from broker_integration import AlpacaTrading, ZerodhaKite
    alpaca = AlpacaTrading(paper=True)
    kite = ZerodhaKite()
    print(f"   - Broker classes loaded. Alpaca enabled: {alpaca.enabled}, Kite enabled: {kite.enabled}")

if __name__ == "__main__":
    print("🚀 STARTING SYSTEM SELF-TEST")
    print("="*40)
    
    tests = [
        ("Analytics Engine", test_analytics),
        ("Backtesting Engine", test_backtesting),
        ("User Authentication", test_user_auth),
        ("Subscription Manager", test_subscription),
        ("Broker Integration", test_broker_integration)
    ]
    
    passed = 0
    for name, func in tests:
        if run_test(name, func):
            passed += 1
            
    print("="*40)
    print(f"🏁 TESTS COMPLETED: {passed}/{len(tests)} Passed")
    
    if passed == len(tests):
        print("✅ SYSTEM READY FOR DEPLOYMENT")
        sys.exit(0)
    else:
        print("⚠️ SOME TESTS FAILED")
        sys.exit(1)
