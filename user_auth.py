#!/usr/bin/env python3
"""
USER AUTHENTICATION & MANAGEMENT
Multi-user support with authentication and user-specific features
"""

import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
import os


class UserAuth:
    """
    User authentication and session management
    """
    
    def __init__(self, db_path: str = "stock_agent.db"):
        self.db_path = db_path
        self.init_user_tables()
    
    def init_user_tables(self):
        """Initialize user-related database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                username TEXT UNIQUE,
                subscription_tier TEXT DEFAULT 'FREE',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active INTEGER DEFAULT 1,
                api_key TEXT UNIQUE
            )
        """)
        
        # User settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_settings (
                setting_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                setting_key TEXT NOT NULL,
                setting_value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                UNIQUE(user_id, setting_key)
            )
        """)
        
        # User watchlists table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_watchlists (
                watchlist_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                watchlist_name TEXT NOT NULL,
                tickers TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active INTEGER DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_token TEXT UNIQUE NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password: str) -> str:
        """Hash password with salt"""
        salt = secrets.token_hex(16)
        pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}${pwd_hash}"
    
    def verify_password(self, password: str, stored_hash: str) -> bool:
        """Verify password against stored hash"""
        try:
            salt, pwd_hash = stored_hash.split('$')
            test_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return test_hash == pwd_hash
        except:
            return False
    
    def create_user(self, email: str, password: str, username: Optional[str] = None) -> Dict:
        """
        Create a new user account
        
        Returns:
            Dict with user_id and status
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Check if email exists
            cursor.execute("SELECT user_id FROM users WHERE email = ?", (email,))
            if cursor.fetchone():
                return {'success': False, 'error': 'Email already registered'}
            
            # Hash password
            pwd_hash = self.hash_password(password)
            
            # Generate API key
            api_key = f"sk_{secrets.token_urlsafe(32)}"
            
            # Insert user
            cursor.execute("""
                INSERT INTO users (email, password_hash, username, api_key)
                VALUES (?, ?, ?, ?)
            """, (email, pwd_hash, username or email.split('@')[0], api_key))
            
            user_id = cursor.lastrowid
            conn.commit()
            
            return {
                'success': True,
                'user_id': user_id,
                'email': email,
                'api_key': api_key
            }
            
        except Exception as e:
            conn.rollback()
            return {'success': False, 'error': str(e)}
        finally:
            conn.close()
    
    def login(self, email: str, password: str) -> Dict:
        """
        Authenticate user and create session
        
        Returns:
            Dict with session_token and user info
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get user
            cursor.execute("""
                SELECT user_id, password_hash, email, username, subscription_tier, is_active
                FROM users WHERE email = ?
            """, (email,))
            
            user = cursor.fetchone()
            
            if not user:
                return {'success': False, 'error': 'Invalid credentials'}
            
            user_id, pwd_hash, email, username, tier, is_active = user
            
            if not is_active:
                return {'success': False, 'error': 'Account is inactive'}
            
            # Verify password
            if not self.verify_password(password, pwd_hash):
                return {'success': False, 'error': 'Invalid credentials'}
            
            # Create session
            session_token = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(days=7)
            
            cursor.execute("""
                INSERT INTO sessions (user_id, session_token, expires_at)
                VALUES (?, ?, ?)
            """, (user_id, session_token, expires_at))
            
            # Update last login
            cursor.execute("""
                UPDATE users SET last_login = CURRENT_TIMESTAMP
                WHERE user_id = ?
            """, (user_id,))
            
            conn.commit()
            
            return {
                'success': True,
                'session_token': session_token,
                'user_id': user_id,
                'email': email,
                'username': username,
                'subscription_tier': tier,
                'expires_at': expires_at.isoformat()
            }
            
        except Exception as e:
            conn.rollback()
            return {'success': False, 'error': str(e)}
        finally:
            conn.close()
    
    def verify_session(self, session_token: str) -> Optional[Dict]:
        """
        Verify session token and return user info
        
        Returns:
            User dict if valid, None if invalid
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT u.user_id, u.email, u.username, u.subscription_tier, s.expires_at
            FROM sessions s
            JOIN users u ON s.user_id = u.user_id
            WHERE s.session_token = ? AND u.is_active = 1
        """, (session_token,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return None
        
        user_id, email, username, tier, expires_at = result
        
        # Check expiration
        if datetime.fromisoformat(expires_at) < datetime.now():
            return None
        
        return {
            'user_id': user_id,
            'email': email,
            'username': username,
            'subscription_tier': tier
        }
    
    def logout(self, session_token: str) -> bool:
        """Delete session (logout)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessions WHERE session_token = ?", (session_token,))
        conn.commit()
        deleted = cursor.rowcount > 0
        conn.close()
        return deleted


class UserWatchlistManager:
    """
    Manage user-specific watchlists
    """
    
    def __init__(self, db_path: str = "stock_agent.db"):
        self.db_path = db_path
    
    def create_watchlist(self, user_id: int, name: str, tickers: List[str]) -> Dict:
        """Create a new watchlist for user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            tickers_str = ','.join(tickers)
            cursor.execute("""
                INSERT INTO user_watchlists (user_id, watchlist_name, tickers)
                VALUES (?, ?, ?)
            """, (user_id, name, tickers_str))
            
            watchlist_id = cursor.lastrowid
            conn.commit()
            
            return {
                'success': True,
                'watchlist_id': watchlist_id,
                'name': name,
                'tickers': tickers
            }
        except Exception as e:
            conn.rollback()
            return {'success': False, 'error': str(e)}
        finally:
            conn.close()
    
    def get_user_watchlists(self, user_id: int) -> List[Dict]:
        """Get all watchlists for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT watchlist_id, watchlist_name, tickers, created_at, updated_at
            FROM user_watchlists
            WHERE user_id = ? AND is_active = 1
            ORDER BY created_at DESC
        """, (user_id,))
        
        watchlists = []
        for row in cursor.fetchall():
            watchlists.append({
                'watchlist_id': row[0],
                'name': row[1],
                'tickers': row[2].split(','),
                'created_at': row[3],
                'updated_at': row[4]
            })
        
        conn.close()
        return watchlists
    
    def update_watchlist(self, watchlist_id: int, user_id: int, tickers: List[str]) -> bool:
        """Update watchlist tickers"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        tickers_str = ','.join(tickers)
        cursor.execute("""
            UPDATE user_watchlists 
            SET tickers = ?, updated_at = CURRENT_TIMESTAMP
            WHERE watchlist_id = ? AND user_id = ?
        """, (tickers_str, watchlist_id, user_id))
        
        conn.commit()
        updated = cursor.rowcount > 0
        conn.close()
        return updated
    
    def delete_watchlist(self, watchlist_id: int, user_id: int) -> bool:
        """Soft delete a watchlist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE user_watchlists SET is_active = 0
            WHERE watchlist_id = ? AND user_id = ?
        """, (watchlist_id, user_id))
        
        conn.commit()
        deleted = cursor.rowcount > 0
        conn.close()
        return deleted


if __name__ == "__main__":
    print("🔐 Testing User Authentication System\n")
    
    # Initialize
    auth = UserAuth()
    watchlist_mgr = UserWatchlistManager()
    
    # Create test user
    print("Creating test user...")
    result = auth.create_user("test@stockgenie.com", "TestPass123!", "testuser")
    
    if result['success']:
        print(f"✅ User created: {result['email']}")
        print(f"   API Key: {result['api_key']}")
        
        # Login
        print("\nTesting login...")
        login_result = auth.login("test@stockgenie.com", "TestPass123!")
        
        if login_result['success']:
            print(f"✅ Login successful")
            print(f"   Session Token: {login_result['session_token'][:20]}...")
            
            # Create watchlist
            print("\nCreating watchlist...")
            wl = watchlist_mgr.create_watchlist(
                login_result['user_id'],
                "Tech Stocks",
                ["AAPL", "MSFT", "GOOGL", "NVDA"]
            )
            
            if wl['success']:
                print(f"✅ Watchlist created: {wl['name']}")
                print(f"   Tickers: {', '.join(wl['tickers'])}")
            
            # Get watchlists
            watchlists = watchlist_mgr.get_user_watchlists(login_result['user_id'])
            print(f"\n📋 Total watchlists: {len(watchlists)}")
            
        else:
            print(f"❌ Login failed: {login_result['error']}")
    else:
        print(f"❌ User creation failed: {result['error']}")
