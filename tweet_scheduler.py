
import os
import yaml
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

from twitter_bot import TwitterBot
from content_engine import TweetContentGenerator
from database_postgres import get_trade_summary

"""
Tweet Scheduler - Automated posting at specific times (EST)

Schedule:
- 10 AM EST: Market open overview
- 2 PM EST: Mid-day analysis
- 10 PM EST: Daily wrap + AI news

Plus:
- Random educational tweets (2x/day)
- Auto-engagement after each post
"""


class AutomatedTwitterPersona:
    """Main automation engine"""

    def __init__(self, config_path='config.yaml'):
        self.cfg = yaml.safe_load(open(config_path, 'r'))
        self.bot = TwitterBot.from_env()
        self.content_gen = TweetContentGenerator()
        self.est = pytz.timezone('US/Eastern')

        if not self.bot:
            raise Exception("Twitter bot not configured. Run: source setup_twitter.sh")

        self.twitter_cfg = self.cfg.get('alerts', {}).get('twitter', {})

        if not self.twitter_cfg.get('enabled', False):
            raise Exception("Twitter disabled in config.yaml")

    def post_morning_update(self):
        """10 AM EST - Market open overview"""
        try:
            print(f"\n[{datetime.now(self.est).strftime('%H:%M:%S EST')}] Posting morning update...")

            tweet = self.content_gen.generate_morning_tweet()
            success = self.bot.post(tweet)

            if success:
                print("✅ Morning tweet posted")
                self._maybe_engage()
            else:
                print("❌ Morning tweet failed")

        except Exception as e:
            print(f"Error in morning update: {e}")

    def post_midday_analysis(self):
        """2 PM EST - Mid-day market pulse"""
        try:
            print(f"\n[{datetime.now(self.est).strftime('%H:%M:%S EST')}] Posting midday analysis...")

            tweet = self.content_gen.generate_midday_tweet()
            success = self.bot.post(tweet)

            if success:
                print("✅ Midday tweet posted")
                self._maybe_engage()
            else:
                print("❌ Midday tweet failed")

        except Exception as e:
            print(f"Error in midday analysis: {e}")

    def post_night_wrap(self):
        """10 PM EST - Daily wrap + AI news"""
        try:
            print(f"\n[{datetime.now(self.est).strftime('%H:%M:%S EST')}] Posting night wrap...")

            tweet = self.content_gen.generate_night_tweet()
            success = self.bot.post(tweet)

            if success:
                print("✅ Night tweet posted")
                self._maybe_engage()
            else:
                print("❌ Night tweet failed")

        except Exception as e:
            print(f"Error in night wrap: {e}")

    def post_educational_content(self):
        """Post educational tweet (random times)"""
        try:
            print(f"\n[{datetime.now(self.est).strftime('%H:%M:%S EST')}] Posting educational content...")

            tweet = self.content_gen.generate_educational_tweet()
            success = self.bot.post(tweet)

            if success:
                print("✅ Educational tweet posted")
            else:
                print("❌ Educational tweet failed")

        except Exception as e:
            print(f"Error posting educational content: {e}")

    def post_ai_industry_update(self):
        """Post AI industry news"""
        try:
            print(f"\n[{datetime.now(self.est).strftime('%H:%M:%S EST')}] Posting AI industry update...")

            tweet = self.content_gen.generate_ai_industry_tweet()
            success = self.bot.post(tweet)

            if success:
                print("✅ AI industry tweet posted")
                self._maybe_engage()
            else:
                print("❌ AI industry tweet failed")

        except Exception as e:
            print(f"Error posting AI update: {e}")

    def post_analysis_breakdown(self):
        """Post what's working / not working"""
        try:
            print(f"\n[{datetime.now(self.est).strftime('%H:%M:%S EST')}] Posting analysis breakdown...")

            tweet = self.content_gen.generate_analysis_tweet()
            success = self.bot.post(tweet)

            if success:
                print("✅ Analysis tweet posted")
            else:
                print("❌ Analysis tweet failed")

        except Exception as e:
            print(f"Error posting analysis: {e}")

    def _maybe_engage(self):
        """Auto-engage after posting (if enabled)"""
        engage_cfg = self.twitter_cfg.get('auto_engage', {})

        if engage_cfg.get('enabled', False):
            try:
                query = engage_cfg.get('query', 'stocks OR trading')
                max_tweets = engage_cfg.get('max_tweets', 3)

                print(f"  → Auto-engaging with {max_tweets} tweets...")
                self.bot.search_and_engage(
                    query=query,
                    like=True,
                    max_tweets=max_tweets
                )
                print("  ✅ Engagement complete")
            except Exception as e:
                print(f"  ⚠️ Engagement error: {e}")

    def run_scheduler(self):
        """Start the automated posting schedule"""
        scheduler = BlockingScheduler(timezone=self.est)

        # Core schedule (3 tweets/day)
        scheduler.add_job(
            self.post_morning_update,
            CronTrigger(hour=10, minute=0, timezone=self.est),
            id='morning_update',
            name='10 AM EST - Market Open'
        )

        scheduler.add_job(
            self.post_midday_analysis,
            CronTrigger(hour=14, minute=0, timezone=self.est),
            id='midday_analysis',
            name='2 PM EST - Mid-day Pulse'
        )

        scheduler.add_job(
            self.post_night_wrap,
            CronTrigger(hour=22, minute=0, timezone=self.est),
            id='night_wrap',
            name='10 PM EST - Daily Wrap'
        )

        # Additional content (2 tweets/day)
        scheduler.add_job(
            self.post_educational_content,
            CronTrigger(hour=12, minute=30, timezone=self.est),
            id='educational_1',
            name='12:30 PM EST - Education'
        )

        scheduler.add_job(
            self.post_ai_industry_update,
            CronTrigger(hour=16, minute=0, timezone=self.est),
            id='ai_industry',
            name='4 PM EST - AI Industry'
        )

        # What's working analysis (1 tweet/day)
        scheduler.add_job(
            self.post_analysis_breakdown,
            CronTrigger(hour=11, minute=30, timezone=self.est),
            id='analysis',
            name='11:30 AM EST - Analysis'
        )

        print("\n" + "="*60)
        print("AI TWITTER PERSONA - AUTOMATED SCHEDULER")
        print("="*60)
        print("\nScheduled posts (EST timezone):")
        print("  10:00 AM - Market Open Overview")
        print("  11:30 AM - What's Working / NOT Working")
        print("  12:30 PM - Educational Content")
        print("  02:00 PM - Mid-day Market Pulse")
        print("  04:00 PM - AI Industry Updates")
        print("  10:00 PM - Daily Wrap + AI News")
        print("\n  = 6 tweets/day automatically =")
        print("\nAuto-engagement:", "ENABLED" if self.twitter_cfg.get('auto_engage', {}).get('enabled') else "DISABLED")
        print("\nPress Ctrl+C to stop")
        print("="*60 + "\n")

        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            print("\n🛑 Scheduler stopped")


def run_manual_test():
    """Test individual tweet generation"""
    print("Testing content generation...")
    print("\n" + "="*60)

    persona = AutomatedTwitterPersona()

    print("\n1. MORNING UPDATE TEST")
    print("-" * 60)
    persona.post_morning_update()

    print("\n2. MIDDAY ANALYSIS TEST")
    print("-" * 60)
    persona.post_midday_analysis()

    print("\n3. NIGHT WRAP TEST")
    print("-" * 60)
    persona.post_night_wrap()

    print("\n4. EDUCATIONAL TEST")
    print("-" * 60)
    persona.post_educational_content()

    print("\n5. AI INDUSTRY TEST")
    print("-" * 60)
    persona.post_ai_industry_update()

    print("\n" + "="*60)
    print("✅ Manual test complete. Check @MopshyAi timeline!")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        # Test mode - post one of each type NOW
        run_manual_test()
    else:
        # Start automated scheduler
        persona = AutomatedTwitterPersona()
        persona.run_scheduler()
