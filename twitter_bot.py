
import os
from typing import Dict, Optional
from datetime import datetime

import tweepy


class TwitterBot:
    """
    Twitter/X Bot for AI Trading Persona
    Posts live trades, stats, and engages with trading community
    Uses API v2 (works with Free tier)
    """

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        access_token: str,
        access_secret: str,
    ):
        # Use Client for v2 API (Free tier compatible)
        self.client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_secret
        )

        # Also keep v1.1 API for media uploads (if available)
        try:
            auth = tweepy.OAuth1UserHandler(
                api_key, api_secret, access_token, access_secret
            )
            self.api = tweepy.API(auth)
        except:
            self.api = None

    @classmethod
    def from_env(cls) -> Optional["TwitterBot"]:
        """Create bot from environment variables"""
        api_key = os.getenv("TWITTER_API_KEY")
        api_secret = os.getenv("TWITTER_API_SECRET")
        access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        access_secret = os.getenv("TWITTER_ACCESS_SECRET")

        if not all([api_key, api_secret, access_token, access_secret]):
            print("⚠️  Twitter credentials missing in env")
            return None

        return cls(api_key, api_secret, access_token, access_secret)

    def post(self, text: str, media_path: Optional[str] = None) -> bool:
        """Post a tweet (with optional image/chart)"""
        try:
            # For now, just post text (Free tier)
            # Media uploads require elevated access
            response = self.client.create_tweet(text=text[:280])

            print(f"🐦 Tweeted: {text[:80]}...")
            return True

        except tweepy.errors.Forbidden as e:
            print(f"❌ Twitter API Forbidden: {e}")
            print("💡 Your API key may need elevated access for posting.")
            print("   Go to: https://developer.x.com/en/portal/petition/standard/basic-info")
            return False

        except Exception as e:
            print(f"❌ Twitter post error: {e}")
            return False

    def search_and_engage(
        self,
        query: str,
        like: bool = True,
        max_tweets: int = 5,
    ) -> None:
        """
        Auto-engage with trading community (requires elevated access)
        Note: Free tier has limited search/engagement capabilities
        """
        try:
            # Search recent tweets
            response = self.client.search_recent_tweets(
                query=query,
                max_results=min(max_tweets, 10),
                tweet_fields=['author_id']
            )

            if not response.data:
                print("No tweets found")
                return

            for tweet in response.data:
                try:
                    if like:
                        self.client.like(tweet.id)
                        print(f"👍 Liked tweet: {tweet.id}")

                except tweepy.errors.Forbidden:
                    print("⚠️  Like action requires elevated access")
                    break
                except Exception as e:
                    print(f"⚠️  Engage error: {e}")

        except tweepy.errors.Forbidden:
            print("⚠️  Search requires elevated access")
        except Exception as e:
            print(f"❌ Twitter search error: {e}")


# ---------- TWEET FORMATTERS (AI TRADING PERSONA) ----------

def format_new_trade_tweet(trade: Dict) -> str:
    """
    Format NEW TRADE SETUP tweet
    trade: {'ticker', 'entry_price', 'stop_loss', 'tp1', 'tp2', 'notes', ...}
    """
    lines = []
    lines.append(f"📋 NEW TRADE SETUP | ${trade['ticker']}")
    lines.append(f"Entry: ${trade['entry_price']:.2f}")
    lines.append(f"Stop: ${trade['stop_loss']:.2f}")
    lines.append(f"TP1: ${trade['tp1']:.2f} | TP2: ${trade['tp2']:.2f}")

    # R-multiple risk/reward
    risk = trade['entry_price'] - trade['stop_loss']
    reward1 = trade['tp1'] - trade['entry_price']
    if risk > 0:
        rr = reward1 / risk
        lines.append(f"R/R: 1:{rr:.1f}")

    notes = trade.get("notes")
    if notes:
        # Truncate if too long
        notes_short = notes[:60] + "..." if len(notes) > 60 else notes
        lines.append(f"Signal: {notes_short}")

    lines.append("")
    lines.append("#trading #stocks #algotrading #AI")
    return "\n".join(lines)


def format_entry_tweet(trade: Dict) -> str:
    """
    Format TRADE ENTERED tweet
    trade: {'ticker', 'actual_entry' or 'entry_price', 'stop_loss', 'tp1', 'tp2'}
    """
    entry = trade.get("actual_entry", trade["entry_price"])
    lines = []
    lines.append(f"▶️  TRADE ENTERED | ${trade['ticker']}")
    lines.append(f"Entry: ${entry:.2f}")
    lines.append(f"Stop: ${trade['stop_loss']:.2f}")
    lines.append(f"TP1: ${trade['tp1']:.2f} | TP2: ${trade['tp2']:.2f}")
    lines.append("")
    lines.append("Position active. Monitoring exits...")
    lines.append("")
    lines.append("#tradeentry #stocktrading #systematictrading")
    return "\n".join(lines)


def format_exit_tweet(result: Dict) -> str:
    """
    Format TRADE CLOSED tweet
    result: {'ticker', 'entry_price', 'exit_price', 'exit_reason', 'r_multiple', 'pnl'}
    """
    emoji_map = {
        "STOP": "❌",
        "TP1": "✅",
        "TP2": "🎯",
    }
    emoji = emoji_map.get(result["exit_reason"], "🔔")

    lines = []
    lines.append(f"{emoji} TRADE CLOSED | ${result['ticker']}")
    lines.append(f"Entry: ${result['entry_price']:.2f}")
    lines.append(f"Exit: ${result['exit_price']:.2f}")

    r = result['r_multiple']
    if r > 0:
        lines.append(f"Result: +{r:.2f}R ✅")
    else:
        lines.append(f"Result: {r:.2f}R")

    pnl = result.get("pnl", 0)
    if pnl:
        sign = "+" if pnl > 0 else ""
        lines.append(f"P&L: {sign}${pnl:.2f}")

    lines.append(f"Exit: {result['exit_reason']}")
    lines.append("")
    lines.append("#riskmanagement #tradingresults #AItrader")
    return "\n".join(lines)


def format_daily_summary_tweet(summary: Dict) -> str:
    """
    Format DAILY PERFORMANCE tweet
    summary: output of get_trade_summary()
    """
    today = datetime.now().strftime("%b %d, %Y")

    lines = []
    lines.append(f"📊 DAILY PERFORMANCE | {today}")
    lines.append("─" * 30)

    lines.append(f"Closed: {summary['closed']} trades")

    if summary["closed"] > 0:
        losses = summary["closed"] - summary["wins"]
        lines.append(
            f"W/L: {summary['wins']}/{losses} "
            f"({summary['win_rate']}% WR)"
        )
        lines.append(f"Avg R: {summary['avg_r']}R")

        pnl = summary["total_pnl"]
        if pnl > 0:
            lines.append(f"P&L: +${pnl:.2f} ✅")
        elif pnl < 0:
            lines.append(f"P&L: ${pnl:.2f} ❌")
        else:
            lines.append("P&L: $0.00")
    else:
        lines.append("No trades closed today")

    lines.append("")
    lines.append(f"Open: {summary['open']} | Pending: {summary['pending']}")
    lines.append("")
    lines.append("#tradingjournal #systemtrading #quant")
    return "\n".join(lines)


def format_weekly_summary_tweet(summary_7d: Dict) -> str:
    """
    Format WEEKLY PERFORMANCE tweet
    """
    lines = []
    lines.append("📈 WEEKLY RECAP")
    lines.append("─" * 30)

    lines.append(f"Trades: {summary_7d['closed']} closed")

    if summary_7d["closed"] > 0:
        losses = summary_7d["closed"] - summary_7d["wins"]
        lines.append(
            f"W/L: {summary_7d['wins']}/{losses} "
            f"({summary_7d['win_rate']}% WR)"
        )
        lines.append(f"Avg R: {summary_7d['avg_r']}R")

        pnl = summary_7d["total_pnl"]
        if pnl > 0:
            lines.append(f"Weekly P&L: +${pnl:.2f} ✅")
        elif pnl < 0:
            lines.append(f"Weekly P&L: ${pnl:.2f}")
        else:
            lines.append("Weekly P&L: $0.00")
    else:
        lines.append("No trades this week")

    lines.append("")
    lines.append("#weeklyrecap #trading #AItrader")
    return "\n".join(lines)


def format_scan_summary_tweet(scan_data: Dict) -> str:
    """
    Format SCAN RESULTS tweet (optional - for signal scanning)
    scan_data: {'total': X, 'signals': Y, 'top_tickers': [...]}
    """
    lines = []
    lines.append("🔍 MARKET SCAN COMPLETE")
    lines.append(f"Scanned: {scan_data.get('total', 0)} stocks")
    lines.append(f"Signals: {scan_data.get('signals', 0)} detected")

    top = scan_data.get('top_tickers', [])
    if top:
        lines.append("")
        lines.append("Top Setups:")
        for ticker in top[:3]:  # Show top 3
            lines.append(f"  • ${ticker}")

    lines.append("")
    lines.append("#marketanalysis #stocks #technicalanalysis")
    return "\n".join(lines)


if __name__ == "__main__":
    # Test connection
    bot = TwitterBot.from_env()
    if bot:
        test_msg = "🤖 AI Stock Agent online.\n\nLive trades + performance stats.\n\n#trading #AI #algotrading"

        print("\nAttempting to post test tweet...")
        success = bot.post(test_msg)

        if success:
            print("\n✅ Twitter bot connected successfully!")
            print("Your account can post tweets!")
        else:
            print("\n❌ Could not post tweet")
            print("\nNote: Free tier Twitter API has limitations.")
            print("To post tweets, you may need to apply for Elevated access:")
            print("  → https://developer.x.com/en/portal/petition/standard/basic-info")
            print("\nOnce approved, this bot will work automatically.")
    else:
        print("❌ Twitter credentials not configured")
        print("\nSet environment variables:")
        print("  export TWITTER_API_KEY='your_key'")
        print("  export TWITTER_API_SECRET='your_secret'")
        print("  export TWITTER_ACCESS_TOKEN='your_token'")
        print("  export TWITTER_ACCESS_SECRET='your_token_secret'")
