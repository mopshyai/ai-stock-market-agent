#!/usr/bin/env python3
"""
MARKET INTELLIGENCE MODULE
Real-time stock data, news, and analysis for Telegram bot
"""

import yfinance as yf
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import re

class StockDataFetcher:
    """Fetch real-time stock data using yfinance"""

    @staticmethod
    def get_stock_price(symbol: str) -> Optional[Dict]:
        """Get current price and key metrics for a stock"""
        try:
            ticker = yf.Ticker(symbol.upper())

            # Get current price
            hist = ticker.history(period='1d', interval='1m')
            if hist.empty:
                return None

            current_price = hist['Close'].iloc[-1]

            # Get info
            info = ticker.info

            # Calculate change
            prev_close = info.get('previousClose', current_price)
            change = current_price - prev_close
            change_pct = (change / prev_close) * 100 if prev_close else 0

            # Get volume
            volume = hist['Volume'].iloc[-1] if 'Volume' in hist else 0
            avg_volume = info.get('averageVolume', 0)

            return {
                'symbol': symbol.upper(),
                'name': info.get('shortName', symbol.upper()),
                'price': round(current_price, 2),
                'change': round(change, 2),
                'change_pct': round(change_pct, 2),
                'volume': int(volume),
                'avg_volume': avg_volume,
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE'),
                'day_high': info.get('dayHigh'),
                'day_low': info.get('dayLow'),
                '52w_high': info.get('fiftyTwoWeekHigh'),
                '52w_low': info.get('fiftyTwoWeekLow'),
            }
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return None

    @staticmethod
    def get_top_stocks(list_type: str = 'gainers', limit: int = 10) -> List[Dict]:
        """Get top gainers, losers, or most active stocks

        Args:
            list_type: 'gainers', 'losers', or 'active'
            limit: Number of stocks to return
        """
        try:
            # Use S&P 500 components as universe
            sp500_symbols = [
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'BRK-B',
                'UNH', 'JNJ', 'V', 'XOM', 'WMT', 'JPM', 'PG', 'MA', 'CVX', 'HD',
                'ABBV', 'MRK', 'KO', 'PEP', 'COST', 'AVGO', 'TMO', 'LLY', 'CSCO',
                'ACN', 'MCD', 'ABT', 'DHR', 'VZ', 'NKE', 'NEE', 'ADBE', 'TXN',
                'PM', 'UPS', 'BMY', 'RTX', 'ORCL', 'CRM', 'HON', 'QCOM', 'AMD',
                'IBM', 'INTC', 'NFLX', 'BA', 'GE', 'PYPL', 'DIS', 'SBUX'
            ]

            stocks_data = []

            for symbol in sp500_symbols[:50]:  # Check top 50 to avoid rate limits
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period='1d')

                    if hist.empty:
                        continue

                    current = hist['Close'].iloc[-1]
                    prev_close = ticker.info.get('previousClose', current)
                    change_pct = ((current - prev_close) / prev_close) * 100 if prev_close else 0
                    volume = hist['Volume'].iloc[-1] if 'Volume' in hist else 0

                    stocks_data.append({
                        'symbol': symbol,
                        'price': round(current, 2),
                        'change_pct': round(change_pct, 2),
                        'volume': int(volume)
                    })
                except:
                    continue

            # Sort based on list type
            if list_type == 'gainers':
                stocks_data.sort(key=lambda x: x['change_pct'], reverse=True)
            elif list_type == 'losers':
                stocks_data.sort(key=lambda x: x['change_pct'])
            else:  # active
                stocks_data.sort(key=lambda x: x['volume'], reverse=True)

            return stocks_data[:limit]

        except Exception as e:
            print(f"Error fetching top stocks: {e}")
            return []


class NewsFetcher:
    """Fetch latest news for stocks"""

    @staticmethod
    def get_stock_news(symbol: str, limit: int = 5) -> List[Dict]:
        """Get latest news for a specific stock using yfinance"""
        try:
            ticker = yf.Ticker(symbol.upper())
            news = ticker.news

            if not news:
                return []

            formatted_news = []
            for item in news[:limit]:
                formatted_news.append({
                    'title': item.get('title', ''),
                    'publisher': item.get('publisher', ''),
                    'link': item.get('link', ''),
                    'published': datetime.fromtimestamp(
                        item.get('providerPublishTime', 0)
                    ).strftime('%Y-%m-%d %H:%M') if item.get('providerPublishTime') else 'N/A'
                })

            return formatted_news

        except Exception as e:
            print(f"Error fetching news for {symbol}: {e}")
            return []

    @staticmethod
    def get_market_news(limit: int = 10) -> List[Dict]:
        """Get general market news"""
        try:
            # Use SPY as proxy for market news
            return NewsFetcher.get_stock_news('SPY', limit)
        except Exception as e:
            print(f"Error fetching market news: {e}")
            return []


class StockQueryDetector:
    """Detect stock symbols and query intent from natural language"""

    # Common stock symbols and their variations
    POPULAR_STOCKS = {
        'tesla': 'TSLA',
        'apple': 'AAPL',
        'microsoft': 'MSFT',
        'google': 'GOOGL',
        'alphabet': 'GOOGL',
        'amazon': 'AMZN',
        'nvidia': 'NVDA',
        'meta': 'META',
        'facebook': 'META',
        'netflix': 'NFLX',
        'amd': 'AMD',
        'intel': 'INTC',
        'walmart': 'WMT',
        'disney': 'DIS',
        'coca cola': 'KO',
        'pepsi': 'PEP',
        'mcdonalds': 'MCD',
        'visa': 'V',
        'mastercard': 'MA',
        'boeing': 'BA',
        'sp500': 'SPY',
        's&p 500': 'SPY',
        'nasdaq': 'QQQ',
        'dow': 'DIA'
    }

    @classmethod
    def extract_symbol(cls, text: str) -> Optional[str]:
        """Extract stock symbol from text"""
        text_lower = text.lower()

        # Check for direct symbol mentions (e.g., TSLA, $TSLA)
        symbol_match = re.search(r'\$?([A-Z]{1,5})\b', text)
        if symbol_match:
            return symbol_match.group(1)

        # Check for company name mentions
        for company, symbol in cls.POPULAR_STOCKS.items():
            if company in text_lower:
                return symbol

        return None

    @staticmethod
    def detect_query_type(text: str) -> str:
        """Detect what type of query this is

        Returns: 'price', 'news', 'why', 'top_stocks', 'general'
        """
        text_lower = text.lower()

        # Price queries
        if any(word in text_lower for word in ['price', 'cost', 'trading at', 'worth', 'value']):
            return 'price'

        # News queries
        if any(word in text_lower for word in ['news', 'latest', 'update', 'happening', 'headlines']):
            return 'news'

        # "Why" queries
        if any(word in text_lower for word in ['why', 'reason', 'because', 'explain why']):
            return 'why'

        # Top stocks
        if any(phrase in text_lower for phrase in ['top stocks', 'top gainers', 'top losers',
                                                      'best stocks', 'worst stocks', 'most active']):
            return 'top_stocks'

        # General query
        return 'general'


class MarketIntelligence:
    """Main class combining all market intelligence features"""

    def __init__(self):
        self.stock_fetcher = StockDataFetcher()
        self.news_fetcher = NewsFetcher()
        self.query_detector = StockQueryDetector()

    def process_query(self, query: str) -> Dict:
        """Process a natural language market query

        Returns a dict with query type and relevant data
        """
        query_type = self.query_detector.detect_query_type(query)
        symbol = self.query_detector.extract_symbol(query)

        result = {
            'query_type': query_type,
            'symbol': symbol,
            'data': None,
            'context': query
        }

        # Fetch relevant data based on query type
        if symbol and query_type == 'price':
            result['data'] = self.stock_fetcher.get_stock_price(symbol)

        elif query_type == 'news':
            # If symbol specified, get stock news; otherwise get general market news
            if symbol:
                result['data'] = self.news_fetcher.get_stock_news(symbol)
            else:
                result['data'] = self.news_fetcher.get_market_news()
                result['symbol'] = 'SPY'  # Use SPY as proxy for general market

        elif symbol and query_type == 'why':
            # Get both price and news for context
            result['data'] = {
                'price_data': self.stock_fetcher.get_stock_price(symbol),
                'news': self.news_fetcher.get_stock_news(symbol, limit=3)
            }

        elif query_type == 'top_stocks':
            # Determine which list
            if 'gainer' in query.lower() or 'best' in query.lower():
                result['data'] = self.stock_fetcher.get_top_stocks('gainers')
            elif 'loser' in query.lower() or 'worst' in query.lower():
                result['data'] = self.stock_fetcher.get_top_stocks('losers')
            else:
                result['data'] = self.stock_fetcher.get_top_stocks('active')

        elif symbol:
            # Generic stock query - get everything
            result['data'] = {
                'price_data': self.stock_fetcher.get_stock_price(symbol),
                'news': self.news_fetcher.get_stock_news(symbol, limit=3)
            }

        return result


# Standalone test
if __name__ == "__main__":
    mi = MarketIntelligence()

    # Test queries
    test_queries = [
        "What's Tesla's price?",
        "News on Apple",
        "Why did NVDA drop today?",
        "Top gainers today",
        "Tell me about Microsoft"
    ]

    for query in test_queries:
        print(f"\nQuery: {query}")
        result = mi.process_query(query)
        print(f"Type: {result['query_type']}, Symbol: {result['symbol']}")
        print(f"Data: {result['data']}")
