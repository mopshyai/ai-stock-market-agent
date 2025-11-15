
import yfinance as yf
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import random

"""
Content Engine - Generates tweets for stock analysis, market commentary, and AI news
"""


class MarketDataEngine:
    """Fetch and analyze market data"""

    def __init__(self):
        self.major_indices = ['SPY', 'QQQ', 'DIA', 'IWM', '^VIX']
        self.trending_stocks = ['NVDA', 'AAPL', 'TSLA', 'META', 'GOOGL', 'AMZN', 'MSFT']

    def get_market_overview(self) -> Dict:
        """Get current market overview"""
        data = {}

        for ticker in self.major_indices:
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period='1d', interval='1m')

                if not hist.empty:
                    current = hist['Close'].iloc[-1]
                    prev_close = stock.info.get('previousClose', current)
                    change_pct = ((current - prev_close) / prev_close * 100) if prev_close else 0

                    data[ticker] = {
                        'price': current,
                        'change_pct': change_pct,
                        'volume': hist['Volume'].sum()
                    }
            except:
                continue

        return data

    def get_trending_movers(self, n=5) -> List[Dict]:
        """Get top movers from watchlist"""
        movers = []

        for ticker in self.trending_stocks:
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period='1d')

                if not hist.empty:
                    current = hist['Close'].iloc[-1]
                    prev_close = stock.info.get('previousClose', current)
                    change_pct = ((current - prev_close) / prev_close * 100) if prev_close else 0
                    volume = hist['Volume'].iloc[-1]

                    movers.append({
                        'ticker': ticker,
                        'price': current,
                        'change_pct': change_pct,
                        'volume': volume
                    })
            except:
                continue

        # Sort by absolute change
        movers.sort(key=lambda x: abs(x['change_pct']), reverse=True)
        return movers[:n]

    def get_sector_rotation(self) -> Dict:
        """Analyze sector performance"""
        sectors = {
            'Tech': 'XLK',
            'Finance': 'XLF',
            'Energy': 'XLE',
            'Healthcare': 'XLV',
            'Consumer': 'XLY'
        }

        sector_data = {}

        for name, ticker in sectors.items():
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period='1d')

                if not hist.empty:
                    current = hist['Close'].iloc[-1]
                    prev_close = stock.info.get('previousClose', current)
                    change_pct = ((current - prev_close) / prev_close * 100) if prev_close else 0

                    sector_data[name] = change_pct
            except:
                continue

        return dict(sorted(sector_data.items(), key=lambda x: x[1], reverse=True))


class AINewsEngine:
    """Fetch AI industry news and updates"""

    def get_ai_headlines(self, n=3) -> List[str]:
        """Get recent AI news headlines"""
        # Simulated AI news (in production, use NewsAPI or RSS feeds)
        ai_topics = [
            "OpenAI releases GPT-5 with 10T parameters",
            "Google's Gemini Ultra surpasses GPT-4 on benchmarks",
            "Meta open-sources Llama 3 with 405B params",
            "Anthropic's Claude 3.5 dominates coding tasks",
            "NVIDIA announces B200 GPU for AI training",
            "Microsoft integrates AI Copilot across Office",
            "Apple launches on-device LLM for privacy",
            "Mistral AI raises $600M at $6B valuation",
            "Stability AI releases Stable Diffusion 3.0",
            "Character.AI hits 100M monthly users"
        ]

        return random.sample(ai_topics, min(n, len(ai_topics)))

    def get_ai_model_updates(self) -> List[str]:
        """Get latest AI model releases"""
        updates = [
            "LLaMA 3.1 - 405B params, open weights",
            "Claude 3.5 Sonnet - State-of-art reasoning",
            "Gemini 1.5 Pro - 2M token context window",
            "GPT-4o - Multimodal with vision+audio",
            "Mixtral 8x22B - Open-source MoE model"
        ]

        return random.sample(updates, 2)


class TweetContentGenerator:
    """Generate tweet content for different times of day"""

    def __init__(self):
        self.market_engine = MarketDataEngine()
        self.ai_engine = AINewsEngine()

    def generate_morning_tweet(self) -> str:
        """10 AM EST - Market open overview"""
        market_data = self.market_engine.get_market_overview()
        movers = self.market_engine.get_trending_movers(3)

        lines = []
        lines.append("📈 Market Open Overview – AI Scan")
        lines.append("")

        # SPY and QQQ
        if 'SPY' in market_data:
            spy = market_data['SPY']
            trend = "Bullish" if spy['change_pct'] > 0 else "Bearish"
            lines.append(f"SPY: {trend} @ ${spy['price']:.2f} ({spy['change_pct']:+.2f}%)")

        if 'QQQ' in market_data:
            qqq = market_data['QQQ']
            trend = "Tech strong" if qqq['change_pct'] > 0 else "Tech weak"
            lines.append(f"QQQ: {trend} ({qqq['change_pct']:+.2f}%)")

        # VIX
        if '^VIX' in market_data:
            vix = market_data['^VIX']
            vix_desc = "Low vol" if vix['price'] < 15 else "High vol" if vix['price'] > 20 else "Moderate"
            lines.append(f"VIX: {vix_desc} at {vix['price']:.1f}")

        # Top movers
        if movers:
            lines.append("")
            lines.append("Active tickers:")
            for m in movers[:3]:
                emoji = "🔥" if abs(m['change_pct']) > 3 else "📊"
                lines.append(f"{emoji} ${m['ticker']}: {m['change_pct']:+.2f}%")

        lines.append("")
        lines.append("#stocks #trading #marketopen")

        return "\n".join(lines)

    def generate_midday_tweet(self) -> str:
        """2 PM EST - Mid-day market pulse"""
        sectors = self.market_engine.get_sector_rotation()
        movers = self.market_engine.get_trending_movers(3)

        lines = []
        lines.append("📊 Mid-Day Market Pulse (AI Analysis)")
        lines.append("")

        # What's working
        if sectors:
            top_sectors = list(sectors.items())[:2]
            bottom_sectors = list(sectors.items())[-2:]

            lines.append("What's Working:")
            for sector, perf in top_sectors:
                emoji = "🚀" if perf > 1 else "✅"
                lines.append(f"• {sector} {emoji} ({perf:+.1f}%)")

            lines.append("")
            lines.append("What's NOT Working:")
            for sector, perf in bottom_sectors:
                emoji = "❌" if perf < -1 else "⚠️"
                lines.append(f"• {sector} {emoji} ({perf:+.1f}%)")

        # Volume leaders
        if movers:
            lines.append("")
            top_vol = movers[0]
            lines.append(f"Volume leader: ${top_vol['ticker']}")

        lines.append("")
        lines.append("#trading #marketpulse #stocks")

        return "\n".join(lines)

    def generate_night_tweet(self) -> str:
        """10 PM EST - Daily wrap + AI news"""
        market_data = self.market_engine.get_market_overview()
        ai_news = self.ai_engine.get_ai_headlines(2)

        lines = []
        lines.append("🌙 Daily Market + AI Briefing")
        lines.append("")

        # Market close summary
        if 'SPY' in market_data:
            spy = market_data['SPY']
            result = "closed strong" if spy['change_pct'] > 0.5 else "closed weak" if spy['change_pct'] < -0.5 else "held range"
            lines.append(f"• SPY {result} @ ${spy['price']:.2f}")

        # Top mover
        movers = self.market_engine.get_trending_movers(1)
        if movers:
            top = movers[0]
            direction = "bullish" if top['change_pct'] > 0 else "bearish"
            lines.append(f"• ${top['ticker']} flow remains {direction}")

        # AI updates
        if ai_news:
            lines.append("")
            lines.append("AI Updates:")
            for news in ai_news:
                lines.append(f"• {news}")

        lines.append("")
        lines.append("Watchlist for tomorrow → Check scan")
        lines.append("")
        lines.append("#finance #aitrading #marketwrap")

        return "\n".join(lines)

    def generate_analysis_tweet(self) -> str:
        """Generate what's working / not working analysis"""
        sectors = self.market_engine.get_sector_rotation()
        movers = self.market_engine.get_trending_movers(5)

        lines = []
        lines.append("🔍 What's Working vs What's NOT")
        lines.append("")

        if movers:
            gainers = [m for m in movers if m['change_pct'] > 0]
            losers = [m for m in movers if m['change_pct'] < 0]

            if gainers:
                lines.append("✅ Working:")
                for g in gainers[:2]:
                    lines.append(f"  ${g['ticker']}: +{g['change_pct']:.1f}%")

            lines.append("")

            if losers:
                lines.append("❌ NOT Working:")
                for l in losers[:2]:
                    lines.append(f"  ${l['ticker']}: {l['change_pct']:.1f}%")

        lines.append("")
        lines.append("AI scoring each ticker 1-10 based on:")
        lines.append("• Volume profile")
        lines.append("• Technical structure")
        lines.append("• Momentum divergence")
        lines.append("")
        lines.append("#stockanalysis #daytrading #AI")

        return "\n".join(lines)

    def generate_ai_industry_tweet(self) -> str:
        """Generate AI industry update tweet"""
        ai_updates = self.ai_engine.get_ai_model_updates()

        lines = []
        lines.append("🤖 AI Industry Pulse")
        lines.append("")

        lines.append("Latest Model Releases:")
        for update in ai_updates:
            lines.append(f"• {update}")

        lines.append("")
        lines.append("The AI race intensifies 🔥")
        lines.append("")
        lines.append("What this means for markets:")
        lines.append("NVDA, AMD, MSFT remain top picks")
        lines.append("")
        lines.append("#AI #MachineLearning #tech")

        return "\n".join(lines)

    def generate_educational_tweet(self) -> str:
        """Generate educational content"""
        topics = [
            ("Risk Management", "Never risk more than 1-2% per trade. Your edge = consistent sizing + good entries."),
            ("R-Multiples", "Win rate doesn't matter if you cut winners early. Aim for 2R+ on best setups."),
            ("Volume Analysis", "Price + Volume = truth. High volume breakouts > low volume pumps."),
            ("Trend Following", "The trend is your friend until it bends. Ride momentum, cut noise."),
            ("Stop Placement", "Stops should be technical, not emotional. Use structure, not hope."),
        ]

        topic, explanation = random.choice(topics)

        lines = []
        lines.append(f"📚 Trading Lesson: {topic}")
        lines.append("")
        lines.append(explanation)
        lines.append("")
        lines.append("AI can scan 1000s of stocks.")
        lines.append("But discipline executes the edge.")
        lines.append("")
        lines.append("#trading101 #riskmanagement")

        return "\n".join(lines)


if __name__ == "__main__":
    # Test content generation
    generator = TweetContentGenerator()

    print("=== MORNING TWEET (10 AM) ===")
    print(generator.generate_morning_tweet())
    print("\n")

    print("=== MIDDAY TWEET (2 PM) ===")
    print(generator.generate_midday_tweet())
    print("\n")

    print("=== NIGHT TWEET (10 PM) ===")
    print(generator.generate_night_tweet())
    print("\n")

    print("=== ANALYSIS TWEET ===")
    print(generator.generate_analysis_tweet())
