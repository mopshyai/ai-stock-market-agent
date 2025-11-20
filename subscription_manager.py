#!/usr/bin/env python3
"""
SUBSCRIPTION & PAYMENT MANAGER
Stripe integration for managing subscriptions
"""

import os
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import sqlite3


# Subscription tiers and limits
SUBSCRIPTION_TIERS = {
    'FREE': {
        'max_watchlists': 1,
        'max_tickers': 10,
        'max_scans_per_day': 3,
        'telegram_alerts': False,
        'backtesting': False,
        'auto_trading': False,
        'price_monthly': 0
    },
    'PRO': {
        'max_watchlists': 10,
        'max_tickers': 100,
        'max_scans_per_day': 50,
        'telegram_alerts': True,
        'backtesting': True,
        'auto_trading': False,
        'price_monthly': 29
    },
    'ENTERPRISE': {
        'max_watchlists': 'unlimited',
        'max_tickers': 'unlimited',
        'max_scans_per_day': 'unlimited',
        'telegram_alerts': True,
        'backtesting': True,
        'auto_trading': True,
        'price_monthly': 99
    }
}


class SubscriptionManager:
    """
    Manage user subscriptions and usage limits
    """
    
    def __init__(self, db_path: str = "stock_agent.db"):
        self.db_path = db_path
        self.init_tables()
    
    def init_tables(self):
        """Initialize subscription tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Subscription history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                subscription_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                tier TEXT NOT NULL,
                status TEXT DEFAULT 'ACTIVE',
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ends_at TIMESTAMP,
                stripe_subscription_id TEXT,
                stripe_customer_id TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Usage tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usage_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                action_type TEXT NOT NULL,
                performed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def get_user_tier(self, user_id: int) -> str:
        """Get current subscription tier for user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT subscription_tier FROM users WHERE user_id = ?
        """, (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else 'FREE'
    
    def get_tier_limits(self, tier: str) -> Dict:
        """Get usage limits for a tier"""
        return SUBSCRIPTION_TIERS.get(tier, SUBSCRIPTION_TIERS['FREE'])
    
    def check_usage_limit(self, user_id: int, action_type: str) -> Dict:
        """
        Check if user can perform an action based on tier limits
        
        Returns:
            Dict with 'allowed' (bool) and 'reason' (str)
        """
        tier = self.get_user_tier(user_id)
        limits = self.get_tier_limits(tier)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check scan limit
        if action_type == 'scan':
            max_scans = limits['max_scans_per_day']
            
            if max_scans == 'unlimited':
                conn.close()
                return {'allowed': True}
            
            # Count today's scans
            cursor.execute("""
                SELECT COUNT(*) FROM usage_logs
                WHERE user_id = ? 
                AND action_type = 'scan'
                AND DATE(performed_at) = DATE('now')
            """, (user_id,))
            
            count = cursor.fetchone()[0]
            conn.close()
            
            if count >= max_scans:
                return {
                    'allowed': False,
                    'reason': f'Daily scan limit reached ({max_scans} scans). Upgrade to PRO for more.'
                }
            
            return {'allowed': True, 'remaining': max_scans - count}
        
        # Check watchlist limit
        elif action_type == 'create_watchlist':
            max_watchlists = limits['max_watchlists']
            
            if max_watchlists == 'unlimited':
                conn.close()
                return {'allowed': True}
            
            cursor.execute("""
                SELECT COUNT(*) FROM user_watchlists
                WHERE user_id = ? AND is_active = 1
            """, (user_id,))
            
            count = cursor.fetchone()[0]
            conn.close()
            
            if count >= max_watchlists:
                return {
                    'allowed': False,
                    'reason': f'Watchlist limit reached ({max_watchlists}). Upgrade for more.'
                }
            
            return {'allowed': True}
        
        conn.close()
        return {'allowed': True}
    
    def log_usage(self, user_id: int, action_type: str) -> bool:
        """Log user action for usage tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO usage_logs (user_id, action_type)
                VALUES (?, ?)
            """, (user_id, action_type))
            conn.commit()
            return True
        except:
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def upgrade_subscription(self, user_id: int, new_tier: str) -> Dict:
        """
        Upgrade user subscription
        
        NOTE: This is a simplified version. In production, integrate with Stripe API:
        - stripe.Subscription.create()
        - Handle webhooks for payment status
        """
        if new_tier not in SUBSCRIPTION_TIERS:
            return {'success': False, 'error': 'Invalid tier'}
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Update user tier
            cursor.execute("""
                UPDATE users SET subscription_tier = ?
                WHERE user_id = ?
            """, (new_tier, user_id))
            
            # Log subscription
            cursor.execute("""
                INSERT INTO subscriptions (user_id, tier, status, ends_at)
                VALUES (?, ?, 'ACTIVE', DATE('now', '+30 days'))
            """, (user_id, new_tier))
            
            conn.commit()
            
            return {
                'success': True,
                'tier': new_tier,
                'message': f'Successfully upgraded to {new_tier}'
            }
            
        except Exception as e:
            conn.rollback()
            return {'success': False, 'error': str(e)}
        finally:
            conn.close()
    
    def get_usage_stats(self, user_id: int, days: int = 30) -> Dict:
        """Get user usage statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                action_type,
                COUNT(*) as count
            FROM usage_logs
            WHERE user_id = ?
            AND performed_at >= DATE('now', '-' || ? || ' days')
            GROUP BY action_type
        """, (user_id, days))
        
        stats = {}
        for row in cursor.fetchall():
            stats[row[0]] = row[1]
        
        conn.close()
        return stats


class StripeIntegration:
    """
    Stripe payment integration (placeholder - requires stripe library)
    
    To implement fully:
    1. pip install stripe
    2. Set STRIPE_SECRET_KEY environment variable
    3. Implement webhook handler for payment events
    """
    
    def __init__(self):
        self.api_key = os.getenv('STRIPE_SECRET_KEY')
        self.enabled = bool(self.api_key)
        
        if not self.enabled:
            print("⚠️  Stripe not configured. Set STRIPE_SECRET_KEY to enable payments.")
    
    def create_checkout_session(self, user_id: int, tier: str) -> Dict:
        """
        Create Stripe checkout session (placeholder)
        
        Real implementation:
        ```python
        import stripe
        stripe.api_key = self.api_key
        
        session = stripe.checkout.Session.create(
            customer_email=user_email,
            payment_method_types=['card'],
            line_items=[{
                'price': TIER_PRICE_IDS[tier],
                'quantity': 1,
            }],
            mode='subscription',
            success_url='https://your-domain.com/success',
            cancel_url='https://your-domain.com/cancel',
        )
        return {'url': session.url}
        ```
        """
        if not self.enabled:
            return {'error': 'Stripe not configured'}
        
        # Placeholder
        return {
            'checkout_url': f'https://checkout.stripe.com/placeholder?tier={tier}',
            'message': 'Stripe integration pending - add stripe library and configure keys'
        }


if __name__ == "__main__":
    print("💳 Testing Subscription Manager\n")
    
    sub_mgr = SubscriptionManager()
    
    # Test with user_id = 1 (assuming exists from previous test)
    user_id = 1
    
    print(f"Current tier: {sub_mgr.get_user_tier(user_id)}")
    
    # Check scan limit
    print("\nChecking scan limit...")
    result = sub_mgr.check_usage_limit(user_id, 'scan')
    print(f"  Can scan: {result['allowed']}")
    if 'remaining' in result:
        print(f"  Remaining today: {result['remaining']}")
    
    # Log a scan
    sub_mgr.log_usage(user_id, 'scan')
    print("  ✅ Scan logged")
    
    # Upgrade test
    print("\nUpgrading to PRO...")
    upgrade_result = sub_mgr.upgrade_subscription(user_id, 'PRO')
    if upgrade_result['success']:
        print(f"  ✅ {upgrade_result['message']}")
        
        # Check new limits
        limits = sub_mgr.get_tier_limits('PRO')
        print(f"  New limits: {limits['max_scans_per_day']} scans/day, {limits['max_watchlists']} watchlists")
    
    # Usage stats
    stats = sub_mgr.get_usage_stats(user_id, 7)
    print(f"\n📊 Usage (last 7 days): {stats}")
