#!/usr/bin/env python3
"""
NewsAPI Client - Professional news aggregation for stocks
https://newsapi.org/docs
"""

import os
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

# Try to import cache
try:
    from cache_manager import cache
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False
    logger.warning("⚠️  Cache manager not available for NewsAPI")


class NewsAPIClient:
    """Fetch stock news from NewsAPI.org"""

    BASE_URL = "https://newsapi.org/v2"

    def __init__(self):
        self.api_key = os.getenv("NEWSAPI_KEY")
        self.enabled = bool(self.api_key)

        if not self.enabled:
            logger.warning("⚠️  NewsAPI key not configured - news features limited")

    def get_stock_news(self, symbol: str, limit: int = 5) -> List[Dict]:
        """
        Get latest news for a stock ticker

        Args:
            symbol: Stock ticker (e.g., 'AAPL', 'TSLA')
            limit: Number of articles to return (default: 5)

        Returns:
            List of news articles with title, publisher, link, published date
        """
        if not self.enabled:
            return []

        symbol = symbol.upper()

        # Check cache first (15 min TTL)
        cache_key = f"newsapi:{symbol}"
        if CACHE_AVAILABLE:
            cached = cache.get(cache_key)
            if cached:
                logger.info(f"✅ Cache HIT: NewsAPI {symbol}")
                return cached[:limit]

        # Cache miss - fetch from NewsAPI
        try:
            # Get company name for better search results
            company_names = {
                'AAPL': 'Apple',
                'TSLA': 'Tesla',
                'MSFT': 'Microsoft',
                'GOOGL': 'Google',
                'AMZN': 'Amazon',
                'META': 'Meta',
                'NVDA': 'Nvidia',
                'AMD': 'AMD',
                'NFLX': 'Netflix',
                'DIS': 'Disney',
            }

            # Search by both symbol and company name
            query = f"{symbol}"
            if symbol in company_names:
                query = f"{company_names[symbol]} OR {symbol}"

            # Fetch last 7 days of news
            from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

            params = {
                'q': query,
                'apiKey': self.api_key,
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': min(limit * 2, 20),  # Fetch extra for filtering
                'from': from_date,
                'domains': 'bloomberg.com,reuters.com,cnbc.com,marketwatch.com,seekingalpha.com,fool.com,benzinga.com,barrons.com,wsj.com,finance.yahoo.com'
            }

            response = requests.get(
                f"{self.BASE_URL}/everything",
                params=params,
                timeout=5
            )

            if response.status_code != 200:
                logger.error(f"NewsAPI error {response.status_code}: {response.text}")
                return []

            data = response.json()

            if data.get('status') != 'ok':
                logger.error(f"NewsAPI returned error: {data.get('message')}")
                return []

            articles = data.get('articles', [])

            # Format articles
            formatted_news = []
            for article in articles:
                # Skip articles without title or URL
                if not article.get('title') or not article.get('url'):
                    continue

                # Skip "[Removed]" articles
                if article.get('title') == '[Removed]':
                    continue

                # Parse published date
                pub_date_str = article.get('publishedAt', '')
                try:
                    pub_date = datetime.fromisoformat(pub_date_str.replace('Z', '+00:00'))
                    published = pub_date.strftime('%b %d, %I:%M %p')
                except:
                    published = 'Recent'

                formatted_news.append({
                    'title': article.get('title', ''),
                    'publisher': article.get('source', {}).get('name', 'Unknown'),
                    'link': article.get('url', ''),
                    'published': published,
                    'description': article.get('description', '')[:200] if article.get('description') else ''
                })

                # Stop when we have enough
                if len(formatted_news) >= limit:
                    break

            # Cache the result (15 minutes)
            if CACHE_AVAILABLE and formatted_news:
                cache.set(cache_key, formatted_news, ttl_seconds=900)
                logger.info(f"📝 Cached: NewsAPI {symbol} ({len(formatted_news)} articles)")

            return formatted_news

        except requests.exceptions.Timeout:
            logger.error(f"NewsAPI timeout for {symbol}")
            return []
        except Exception as e:
            logger.error(f"NewsAPI error for {symbol}: {e}")
            return []

    def get_market_news(self, limit: int = 10) -> List[Dict]:
        """
        Get general market/business news

        Args:
            limit: Number of articles to return

        Returns:
            List of market news articles
        """
        if not self.enabled:
            return []

        # Check cache
        cache_key = "newsapi:market"
        if CACHE_AVAILABLE:
            cached = cache.get(cache_key)
            if cached:
                logger.info("✅ Cache HIT: NewsAPI market news")
                return cached[:limit]

        try:
            params = {
                'q': 'stock market OR stocks OR trading',
                'apiKey': self.api_key,
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': limit,
                'sources': 'bloomberg,reuters,cnbc,the-wall-street-journal,financial-times'
            }

            response = requests.get(
                f"{self.BASE_URL}/top-headlines",
                params=params,
                timeout=5
            )

            if response.status_code != 200:
                return []

            data = response.json()
            articles = data.get('articles', [])

            formatted_news = []
            for article in articles:
                if article.get('title') == '[Removed]':
                    continue

                pub_date_str = article.get('publishedAt', '')
                try:
                    pub_date = datetime.fromisoformat(pub_date_str.replace('Z', '+00:00'))
                    published = pub_date.strftime('%b %d, %I:%M %p')
                except:
                    published = 'Recent'

                formatted_news.append({
                    'title': article.get('title', ''),
                    'publisher': article.get('source', {}).get('name', 'Unknown'),
                    'link': article.get('url', ''),
                    'published': published
                })

            # Cache (15 minutes)
            if CACHE_AVAILABLE and formatted_news:
                cache.set(cache_key, formatted_news, ttl_seconds=900)
                logger.info(f"📝 Cached: NewsAPI market news ({len(formatted_news)} articles)")

            return formatted_news

        except Exception as e:
            logger.error(f"NewsAPI market news error: {e}")
            return []


# Standalone test
if __name__ == "__main__":
    client = NewsAPIClient()

    if not client.enabled:
        print("❌ NEWSAPI_KEY not set in environment")
        print("Set it with: export NEWSAPI_KEY='your_key'")
        exit(1)

    print("\n🧪 Testing NewsAPI Client\n")

    # Test stock news
    print("📰 Fetching TSLA news...")
    news = client.get_stock_news('TSLA', limit=3)

    if news:
        print(f"✅ Found {len(news)} articles:")
        for article in news:
            print(f"\n  📌 {article['title']}")
            print(f"     {article['publisher']} | {article['published']}")
            print(f"     {article['link']}")
    else:
        print("❌ No news found")

    # Test market news
    print("\n\n📊 Fetching market news...")
    market = client.get_market_news(limit=3)

    if market:
        print(f"✅ Found {len(market)} articles:")
        for article in market:
            print(f"\n  📌 {article['title']}")
            print(f"     {article['publisher']} | {article['published']}")
    else:
        print("❌ No market news found")
