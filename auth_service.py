"""
Supabase Authentication Module for StockGenie
"""

from supabase import create_client, Client
from typing import Dict, Optional
import os

# Supabase configuration
SUPABASE_URL = "https://pouwcybugvkiaitwjcyc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBvdXdjeWJ1Z3ZraWFpdHdqY3ljIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjM1OTIyNzYsImV4cCI6MjA3OTE2ODI3Nn0.5u9tFGLV3P5EZ4HLeNkE2ZVf3q2ZYf7erq5J2saeoCI"


class SupabaseAuth:
    def __init__(self):
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    def create_user(self, email: str, password: str, username: str = None) -> Dict:
        """
        Create a new user account

        Returns:
            Dict with success status and user info or error
        """
        try:
            # Sign up with Supabase Auth
            response = self.supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "username": username or email.split('@')[0],
                        "subscription_tier": "free"
                    }
                }
            })

            if response.user:
                return {
                    'success': True,
                    'user_id': response.user.id,
                    'email': response.user.email
                }
            else:
                return {'success': False, 'error': 'Failed to create user'}

        except Exception as e:
            error_msg = str(e)
            if "already registered" in error_msg.lower():
                return {'success': False, 'error': 'Email already registered'}
            return {'success': False, 'error': error_msg}

    def login(self, email: str, password: str) -> Dict:
        """
        Authenticate user and create session

        Returns:
            Dict with session info and user data
        """
        try:
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            if response.user and response.session:
                user_metadata = response.user.user_metadata or {}

                return {
                    'success': True,
                    'session_token': response.session.access_token,
                    'refresh_token': response.session.refresh_token,
                    'user_id': response.user.id,
                    'email': response.user.email,
                    'username': user_metadata.get('username', email.split('@')[0]),
                    'subscription_tier': user_metadata.get('subscription_tier', 'free'),
                    'expires_at': response.session.expires_at
                }
            else:
                return {'success': False, 'error': 'Invalid credentials'}

        except Exception as e:
            error_msg = str(e)
            if "invalid" in error_msg.lower():
                return {'success': False, 'error': 'Invalid email or password'}
            return {'success': False, 'error': error_msg}

    def logout(self, token: str = None) -> Dict:
        """
        Log out user and invalidate session

        Returns:
            Dict with success status
        """
        try:
            self.supabase.auth.sign_out()
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_user(self, token: str) -> Optional[Dict]:
        """
        Get user info from session token

        Returns:
            User dict or None if invalid
        """
        try:
            response = self.supabase.auth.get_user(token)

            if response.user:
                user_metadata = response.user.user_metadata or {}
                return {
                    'user_id': response.user.id,
                    'email': response.user.email,
                    'username': user_metadata.get('username', response.user.email.split('@')[0]),
                    'subscription_tier': user_metadata.get('subscription_tier', 'free')
                }
            return None
        except Exception:
            return None

    def refresh_session(self, refresh_token: str) -> Dict:
        """
        Refresh the session using refresh token

        Returns:
            Dict with new session info or error
        """
        try:
            response = self.supabase.auth.refresh_session(refresh_token)

            if response.session:
                return {
                    'success': True,
                    'session_token': response.session.access_token,
                    'refresh_token': response.session.refresh_token,
                    'expires_at': response.session.expires_at
                }
            return {'success': False, 'error': 'Failed to refresh session'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def update_user_tier(self, user_id: str, tier: str) -> Dict:
        """
        Update user's subscription tier

        Returns:
            Dict with success status
        """
        try:
            self.supabase.auth.admin.update_user_by_id(
                user_id,
                {"user_metadata": {"subscription_tier": tier}}
            )
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}


# Create singleton instance
auth = SupabaseAuth()
