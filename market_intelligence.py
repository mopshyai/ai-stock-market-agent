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
import logging

# Import cache manager
try:
    from cache_manager import get_cached_stock_price, cache_stock_price, get_cached_news, cache_news
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False
    print("⚠️  Cache manager not available")

# NewsAPI client (optional)
try:
    from news_api_client import NewsAPIClient
    NEWSAPI_AVAILABLE = True
except ImportError:
    NEWSAPI_AVAILABLE = False
    NewsAPIClient = None
    logging.getLogger(__name__).warning("⚠️  news_api_client not available. Falling back to yfinance news.")

class StockDataFetcher:
    """Fetch real-time stock data using yfinance"""

    @staticmethod
    def get_stock_price(symbol: str) -> Optional[Dict]:
        """Get current price and key metrics for a stock (with caching)"""
        symbol = symbol.upper()

        # Try cache first (5 minute TTL)
        if CACHE_AVAILABLE:
            cached = get_cached_stock_price(symbol)
            if cached:
                print(f"✅ Cache HIT: {symbol} price")
                return cached

        # Cache miss - fetch from yfinance
        try:
            ticker = yf.Ticker(symbol)

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

            data = {
                'symbol': symbol,
                'name': info.get('shortName', symbol),
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

            # Cache the result (5 minutes)
            if CACHE_AVAILABLE:
                cache_stock_price(symbol, data, ttl_seconds=300)
                print(f"📝 Cached: {symbol} price (5 min)")

            return data

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

    newsapi_client = NewsAPIClient() if NEWSAPI_AVAILABLE else None

    @staticmethod
    def get_stock_news(symbol: str, limit: int = 5) -> List[Dict]:
        """Get latest news for a specific stock using yfinance (with caching)"""
        symbol = symbol.upper()

        # Try cache first (15 minute TTL for news)
        if CACHE_AVAILABLE:
            cached = get_cached_news(symbol)
            if cached:
                print(f"✅ Cache HIT: {symbol} news")
                return cached[:limit]  # Return requested limit

        # Use NewsAPI first if available
        if NewsFetcher.newsapi_client and NewsFetcher.newsapi_client.enabled:
            newsapi_articles = NewsFetcher.newsapi_client.get_stock_news(symbol, limit)
            if newsapi_articles:
                if CACHE_AVAILABLE:
                    cache_news(symbol, newsapi_articles, ttl_seconds=900)
                return newsapi_articles

        # Cache miss or NewsAPI disabled - fetch from yfinance
        try:
            ticker = yf.Ticker(symbol)
            news = ticker.news

            if not news:
                return []

            formatted_news = []
            for item in news[:limit]:
                # Handle new yfinance API structure (nested under 'content')
                content = item.get('content', {})

                # Extract title
                title = content.get('title', item.get('title', ''))

                # Extract publisher
                provider = content.get('provider', {})
                publisher = provider.get('displayName', item.get('publisher', 'Unknown'))

                # Extract link
                canonical_url = content.get('canonicalUrl', {})
                link = canonical_url.get('url', item.get('link', ''))
                if not link:
                    link = content.get('previewUrl', '')

                # Extract publish date
                pub_date_str = content.get('pubDate', '') or content.get('displayTime', '')
                if pub_date_str:
                    try:
                        # Parse ISO format: 2025-11-15T22:04:51Z
                        pub_date = datetime.fromisoformat(pub_date_str.replace('Z', '+00:00'))
                        published = pub_date.strftime('%b %d, %I:%M %p')
                    except:
                        published = pub_date_str[:10]  # Just the date
                elif item.get('providerPublishTime'):
                    published = datetime.fromtimestamp(
                        item.get('providerPublishTime')
                    ).strftime('%b %d, %I:%M %p')
                else:
                    published = 'Recent'

                # Only add if we have at least a title
                if title:
                    formatted_news.append({
                        'title': title,
                        'publisher': publisher,
                        'link': link,
                        'published': published
                    })

            # Cache the result (15 minutes)
            if CACHE_AVAILABLE and formatted_news:
                cache_news(symbol, formatted_news, ttl_seconds=900)
                print(f"📝 Cached: {symbol} news (15 min)")

            return formatted_news

        except Exception as e:
            print(f"Error fetching news for {symbol}: {e}")
            return []

    @staticmethod
    def get_market_news(limit: int = 10) -> List[Dict]:
        """Get general market news"""
        # Prefer NewsAPI market headlines
        if NewsFetcher.newsapi_client and NewsFetcher.newsapi_client.enabled:
            market_news = NewsFetcher.newsapi_client.get_market_news(limit)
            if market_news:
                return market_news

        # Fallback to SPY ticker news
        try:
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
