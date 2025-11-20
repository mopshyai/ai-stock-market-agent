#!/usr/bin/env python3
"""
BROKER API INTEGRATION
Auto-trading system with broker API support (Zerodha Kite, Alpaca)
"""

import os
from typing import Dict, List, Optional
from datetime import datetime
import requests


class AlpacaTrading:
    """
    Alpaca API integration for US markets
    Free paper trading available at alpaca.markets
    """
    
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None, paper: bool = True):
        self.api_key = api_key or os.getenv('ALPACA_API_KEY')
        self.api_secret = api_secret or os.getenv('ALPACA_API_SECRET')
        self.paper = paper
        
        self.base_url = "https://paper-api.alpaca.markets" if paper else "https://api.alpaca.markets"
        self.enabled = bool(self.api_key and self.api_secret)
        
        if not self.enabled:
            print("⚠️  Alpaca not configured. Set ALPACA_API_KEY and ALPACA_API_SECRET")
    
    @property
    def headers(self):
        return {
            'APCA-API-KEY-ID': self.api_key,
            'APCA-API-SECRET-KEY': self.api_secret
        }
    
    def get_account(self) -> Dict:
        """Get account information"""
        if not self.enabled:
            return {'error': 'Alpaca not configured'}
        
        try:
            response = requests.get(f"{self.base_url}/v2/account", headers=self.headers)
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    def place_market_order(self, ticker: str, qty: int, side: str = 'buy') -> Dict:
        """
        Place market order
        
        Args:
            ticker: Stock symbol
            qty: Number of shares
            side: 'buy' or 'sell'
        """
        if not self.enabled:
            return {'error': 'Alpaca not configured'}
        
        order_data = {
            'symbol': ticker,
            'qty': qty,
            'side': side,
            'type': 'market',
            'time_in_force': 'day'
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/v2/orders",
                headers=self.headers,
                json=order_data
            )
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    def place_bracket_order(self, ticker: str, qty: int, entry_price: float,
                           stop_loss: float, take_profit: float) -> Dict:
        """
        Place bracket order (entry + stop loss + take profit)
        
        NOTE: Alpaca bracket orders require limit entry orders
        """
        if not self.enabled:
            return {'error': 'Alpaca not configured'}
        
        order_data = {
            'symbol': ticker,
            'qty': qty,
            'side': 'buy',
            'type': 'limit',
            'time_in_force': 'day',
            'limit_price': entry_price,
            'order_class': 'bracket',
            'stop_loss': {
                'stop_price': stop_loss
            },
            'take_profit': {
                'limit_price': take_profit
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/v2/orders",
                headers=self.headers,
                json=order_data
            )
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    def get_open_positions(self) -> List[Dict]:
        """Get all open positions"""
        if not self.enabled:
            return []
        
        try:
            response = requests.get(f"{self.base_url}/v2/positions", headers=self.headers)
            return response.json()
        except:
            return []
    
    def close_position(self, ticker: str) -> Dict:
        """Close entire position for a ticker"""
        if not self.enabled:
            return {'error': 'Alpaca not configured'}
        
        try:
            response = requests.delete(
                f"{self.base_url}/v2/positions/{ticker}",
                headers=self.headers
            )
            return response.json()
        except Exception as e:
            return {'error': str(e)}


class ZerodhaKite:
    """
    Zerodha Kite API integration for Indian markets
    
    NOTE: Requires Kite Connect subscription (₹2000/month)
    Documentation: https://kite.trade
    """
    
    def __init__(self, api_key: Optional[str] = None, access_token: Optional[str] = None):
        self.api_key = api_key or os.getenv('KITE_API_KEY')
        self.access_token = access_token or os.getenv('KITE_ACCESS_TOKEN')
        self.base_url = "https://api.kite.trade"
        self.enabled = bool(self.api_key and self.access_token)
        
        if not self.enabled:
            print("⚠️  Kite not configured. Set KITE_API_KEY and KITE_ACCESS_TOKEN")
    
    @property
    def headers(self):
        return {
            'X-Kite-Version': '3',
            'Authorization': f'token {self.api_key}:{self.access_token}'
        }
    
    def place_order(self, ticker: str, exchange: str, transaction_type: str,
                   quantity: int, order_type: str = 'MARKET', price: float = None) -> Dict:
        """
        Place order on Kite
        
        Args:
            ticker: Trading symbol (e.g., 'INFY')
            exchange: 'NSE' or 'BSE'
            transaction_type: 'BUY' or 'SELL'
            quantity: Number of shares
            order_type: 'MARKET', 'LIMIT', 'SL', 'SL-M'
            price: Limit price (required for LIMIT orders)
        """
        if not self.enabled:
            return {'error': 'Kite not configured'}
        
        order_data = {
            'tradingsymbol': ticker,
            'exchange': exchange,
            'transaction_type': transaction_type,
            'quantity': quantity,
            'order_type': order_type,
            'product': 'CNC',  # Cash and Carry (delivery)
            'validity': 'DAY'
        }
        
        if order_type == 'LIMIT' and price:
            order_data['price'] = price
        
        try:
            response = requests.post(
                f"{self.base_url}/orders/regular",
                headers=self.headers,
                data=order_data
            )
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    def get_positions(self) -> Dict:
        """Get current positions"""
        if not self.enabled:
            return {'error': 'Kite not configured'}
        
        try:
            response = requests.get(f"{self.base_url}/portfolio/positions", headers=self.headers)
            return response.json()
        except Exception as e:
            return {'error': str(e)}


class AutoTradingEngine:
    """
    Automated trading execution engine
    Connects signals to actual broker orders
    """
    
    def __init__(self, broker: str = 'alpaca', paper_trading: bool = True):
        """
        Args:
            broker: 'alpaca' or 'kite'
            paper_trading: Use paper trading account (safer for testing)
        """
        self.broker_name = broker
        self.paper_trading = paper_trading
        
        if broker == 'alpaca':
            self.broker = AlpacaTrading(paper=paper_trading)
        elif broker == 'kite':
            self.broker = ZerodhaKite()
        else:
            self.broker = None
            print(f"❌ Unknown broker: {broker}")
    
    def execute_signal_trade(self, signal_data: Dict) -> Dict:
        """
        Convert signal to actual broker order
        
        Args:
            signal_data: Dict with ticker, entry_price, stop_loss, take_profit, position_size
        """
        if not self.broker or not self.broker.enabled:
            return {
                'success': False,
                'error': 'Broker not configured',
                'help': 'Set API keys to enable auto-trading'
            }
        
        ticker = signal_data['ticker']
        entry = signal_data['entry_price']
        stop_loss = signal_data['stop_loss']
        take_profit = signal_data.get('take_profit_1', signal_data.get('tp1'))
        qty = int(signal_data.get('position_size', 1))
        
        # Place bracket order
        if self.broker_name == 'alpaca':
            result = self.broker.place_bracket_order(
                ticker, qty, entry, stop_loss, take_profit
            )
        elif self.broker_name == 'kite':
            # Kite requires separate orders for stop loss / take profit
            result = self.broker.place_order(
                ticker, 'NSE', 'BUY', qty, 'LIMIT', entry
            )
        else:
            result = {'error': 'Unsupported broker'}
        
        return {
            'success': 'error' not in result,
            'broker': self.broker_name,
            'ticker': ticker,
            'qty': qty,
            'order_result': result,
            'paper_trading': self.paper_trading
        }


if __name__ == "__main__":
    print("🤖 Testing Auto-Trading Integration\n")
    
    # Test Alpaca (paper trading)
    print("Testing Alpaca Paper Trading...")
    alpaca = AlpacaTrading(paper=True)
    
    if alpaca.enabled:
        account = alpaca.get_account()
        if 'error' not in account:
            print(f"✅ Account Status: {account.get('status')}")
            print(f"   Buying Power: ${float(account.get('buying_power', 0)):,.2f}")
        else:
            print(f"❌ {account['error']}")
    else:
        print("⚠️  Alpaca not configured - set ALPACA_API_KEY and ALPACA_API_SECRET")
        print("   Sign up for free paper trading at: https://alpaca.markets")
    
    print("\n" + "="*60)
    print("NOTE: To enable auto-trading:")
    print("  1. Alpaca (US): Sign up at alpaca.markets (free paper trading)")
    print("  2. Kite (India): Subscribe at kite.trade (₹2000/month)")
    print("  3. Set environment variables with your API keys")
    print("  4. Test with paper trading first!")
    print("="*60)
