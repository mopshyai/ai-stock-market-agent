
import os
import requests
from typing import List, Dict, Optional, Tuple

# Import Twitter bot
try:
    from twitter_bot import (
        TwitterBot,
        format_new_trade_tweet,
        format_entry_tweet,
        format_exit_tweet,
        format_daily_summary_tweet,
        format_weekly_summary_tweet,
    )
    TWITTER_AVAILABLE = True
except ImportError:
    TWITTER_AVAILABLE = False
    print("[INFO] Twitter bot not available (tweepy not installed)")


def _format_market_cap(value: Optional[float]) -> str:
    if value is None:
        return "—"
    trillions = 1_000_000_000_000
    billions = 1_000_000_000
    millions = 1_000_000
    if value >= trillions:
        return f"${value / trillions:.2f}T"
    if value >= billions:
        return f"${value / billions:.2f}B"
    if value >= millions:
        return f"${value / millions:.2f}M"
    return f"${value:,.0f}"

class TelegramBot:
    """
    Telegram Bot for sending AI Stock Agent alerts
    """

    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"

    def send_message(self, text: str, parse_mode: str = "Markdown") -> bool:
        """Send a text message to the configured chat"""
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": parse_mode
            }
            response = requests.post(url, json=payload, timeout=10)
            return response.ok
        except Exception as e:
            print(f"[TELEGRAM ERROR] Failed to send message: {e}")
            return False

    def send_photo(self, photo_path: str, caption: str = "") -> bool:
        """Send a photo to the configured chat"""
        try:
            url = f"{self.base_url}/sendPhoto"
            with open(photo_path, 'rb') as photo:
                files = {'photo': photo}
                data = {
                    'chat_id': self.chat_id,
                    'caption': caption,
                    'parse_mode': 'Markdown'
                }
                response = requests.post(url, files=files, data=data, timeout=30)
            return response.ok
        except Exception as e:
            print(f"[TELEGRAM ERROR] Failed to send photo: {e}")
            return False


def get_telegram_credentials(cfg: dict) -> Tuple[Optional[str], Optional[str]]:
    telegram_cfg = cfg.get("alerts", {}).get("telegram", {})
    token_env = telegram_cfg.get("bot_token_env", "TELEGRAM_BOT_TOKEN")
    chat_env = telegram_cfg.get("chat_id_env", "TELEGRAM_CHAT_ID")
    token = os.getenv(token_env) or telegram_cfg.get("bot_token")
    chat_id = os.getenv(chat_env) or telegram_cfg.get("chat_id")
    return token, chat_id


def is_telegram_configured(cfg: dict) -> bool:
    telegram_cfg = cfg.get("alerts", {}).get("telegram", {})
    if not telegram_cfg.get("enabled", False):
        return False
    token, chat_id = get_telegram_credentials(cfg)
    return bool(token and chat_id)


def format_scan_results(results: List[Dict], send_charts: bool = True) -> str:
    """
    Format scan results into a Telegram-friendly message
    """
    if not results:
        return "🤖 *AI Stock Agent Scan Complete*\n\nNo signals detected."

    # Count signals
    consolidation_count = sum(1 for r in results if r.get('Consolidating'))
    dip_count = sum(1 for r in results if r.get('BuyDip'))
    breakout_count = sum(1 for r in results if r.get('Breakout'))
    volume_count = sum(1 for r in results if r.get('VolSpike'))

    # Build header
    msg = "🤖 *AI Stock Agent Daily Scan*\n"
    msg += "=" * 30 + "\n\n"
    msg += f"📊 Scanned: {len(results)} stocks\n"
    msg += f"🟢 Consolidation: {consolidation_count}\n"
    msg += f"📉 Buy-the-Dip: {dip_count}\n"
    msg += f"🚀 Breakout: {breakout_count}\n"
    msg += f"📈 Volume Spike: {volume_count}\n"
    msg += "\n" + "─" * 30 + "\n\n"

    # Show top opportunities by score
    msg += "*Top Opportunities (by Signal Score):*\n\n"

    # Add signal details
    for r in results:
        ticker = r.get('Ticker', 'N/A')
        score = r.get('Score', 0)
        cons = r.get('Consolidating', False)
        dip = r.get('BuyDip', False)
        brk = r.get('Breakout', False)
        vol = r.get('VolSpike', False)
        trend = r.get('Trend', 'CHOPPY')

        # Skip stocks with no signals
        if not (cons or dip or brk or vol):
            continue

        # Score badge
        if score >= 5:
            score_badge = "🔥"
        elif score >= 3:
            score_badge = "⭐"
        else:
            score_badge = "📍"

        msg += f"{score_badge} *{ticker}* @ ${r.get('Close', 0):.2f} | Score: {score}\n"

        # Signals
        signals = []
        if cons:
            signals.append("🟢 CONSOLIDATION")
        if dip:
            signals.append("📉 BUY-DIP")
        if brk:
            signals.append("🚀 BREAKOUT")
        if vol:
            signals.append("📈 VOL SPIKE")
        if r.get('EMABullish'):
            signals.append("📐 EMA STACK")
        if r.get('MACDBullish'):
            signals.append("🎯 MACD BULL")
        if r.get('VWAPReclaim'):
            signals.append("💧 VWAP RECLAIM")

        msg += "   " + " | ".join(signals) + "\n"

        action = r.get('Action', 'WATCH')
        action_reason = r.get('ActionReason', '')
        msg += f"   • Action: *{action}*"
        if action_reason:
            msg += f" — {action_reason}"
        msg += "\n"

        # Trend
        if trend == "UP":
            msg += "   📊 Trend: ⬆️ UPTREND\n"
        elif trend == "DOWN":
            msg += "   📊 Trend: ⬇️ DOWNTREND\n"
        else:
            msg += "   📊 Trend: ↔️ CHOPPY\n"

        # Key metrics
        msg += f"   • RSI: {r.get('RSI', 0):.1f} | ADX: {r.get('ADX', 0):.1f}\n"
        msg += f"   • BB Width: {r.get('BBWidth_pct', 0):.2f}% | ATR: {r.get('ATR%', 0):.2f}%\n"

        fund_score = r.get('FundamentalScore')
        outlook = r.get('FundamentalOutlook', '')
        if fund_score is not None:
            msg += f"   • Fundamentals: {fund_score} ({outlook})\n"

        pe_ratio = r.get('PERatio')
        rev_growth = r.get('RevenueGrowthPct')
        margin = r.get('ProfitMarginPct')

        pe_text = f"{pe_ratio:.1f}" if isinstance(pe_ratio, (int, float)) else "—"
        rev_text = f"{rev_growth:.1f}%" if isinstance(rev_growth, (int, float)) else "—"
        margin_text = f"{margin:.1f}%" if isinstance(margin, (int, float)) else "—"

        msg += f"   • MC: {_format_market_cap(r.get('MarketCap'))} | P/E: {pe_text} | Rev: {rev_text} | Margin: {margin_text}\n"

        reasons = r.get('FundamentalReasons')
        if reasons:
            msg += f"   • Notes: {reasons}\n"

        msg += "\n"

    if send_charts:
        msg += "\n📸 Charts will be sent separately.\n"

    msg += "\n⚠️ _This is not financial advice. Always do your own research._"

    return msg


def send_telegram_alerts(results: List[Dict], cfg: dict, charts_dir: str = "./charts"):
    """
    Main function to send Telegram alerts based on scan results
    """
    telegram_cfg = cfg.get("alerts", {}).get("telegram", {})

    if not telegram_cfg.get("enabled", False):
        print("[TELEGRAM] Alerts disabled in config")
        return False

    # Get credentials from environment
    bot_token, chat_id = get_telegram_credentials(cfg)

    if not bot_token or not chat_id:
        print("[TELEGRAM] Bot token or chat ID not configured")
        return False

    # Initialize bot
    bot = TelegramBot(bot_token, chat_id)

    # Filter results if only_signal_stocks is enabled
    only_signals = telegram_cfg.get("only_signal_stocks", True)
    filtered_results = results
    if only_signals:
        filtered_results = [
            r for r in results
            if r.get('Consolidating') or r.get('BuyDip') or r.get('Breakout') or r.get('VolSpike')
        ]

    # Send summary message
    summary = format_scan_results(filtered_results, telegram_cfg.get("send_charts", True))
    bot.send_message(summary)
    print(f"[TELEGRAM] Sent summary for {len(filtered_results)} stocks")

    # Send charts if enabled
    if telegram_cfg.get("send_charts", True):
        for r in filtered_results:
            ticker = r.get('Ticker')
            chart_path = f"{charts_dir}/{ticker}.png"

            if os.path.exists(chart_path):
                caption = f"📊 *{ticker}* Chart\nAction: {r.get('Action', 'WATCH')}"
                if r.get('Consolidating'):
                    caption += " 🟢 CONS"
                if r.get('BuyDip'):
                    caption += " 🔻 DIP"
                if r.get('EMABullish'):
                    caption += " 📐 EMA"
                if r.get('MACDBullish'):
                    caption += " 🎯 MACD"
                if r.get('VWAPReclaim'):
                    caption += " 💧 VWAP"

                bot.send_photo(chart_path, caption)
                print(f"[TELEGRAM] Sent chart for {ticker}")

    return True


def test_telegram_connection():
    """
    Test Telegram bot connection
    """
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        print("❌ TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set")
        print("\nSet them with:")
        print('  export TELEGRAM_BOT_TOKEN="your_token_here"')
        print('  export TELEGRAM_CHAT_ID="your_chat_id_here"')
        return False

    bot = TelegramBot(bot_token, chat_id)
    success = bot.send_message("✅ *AI Stock Agent*\n\nTelegram connection test successful!")

    if success:
        print("✅ Telegram bot connected successfully!")
        return True
    else:
        print("❌ Failed to send test message")
        return False


def send_new_trade_alert(bot: TelegramBot, trade_data: Dict) -> bool:
    """
    Send alert for new pending trade setup
    """
    ticker = trade_data['ticker']
    entry = trade_data['entry_price']
    stop = trade_data['stop_loss']
    tp1 = trade_data['tp1']
    tp2 = trade_data['tp2']
    notes = trade_data.get('notes', '')

    msg = f"📋 *NEW TRADE SETUP*\n"
    msg += "─" * 30 + "\n\n"
    msg += f"*{ticker}* @ ${entry:.2f}\n\n"
    msg += f"🎯 Entry: ${entry:.2f}\n"
    msg += f"🛑 Stop: ${stop:.2f}\n"
    msg += f"✅ TP1: ${tp1:.2f} (1R)\n"
    msg += f"🎯 TP2: ${tp2:.2f} (2R)\n\n"
    msg += f"📝 {notes}\n\n"
    msg += "_Waiting for entry..._"

    return bot.send_message(msg)


def send_entry_alert(bot: TelegramBot, trade_data: Dict) -> bool:
    """
    Send alert when trade entry is filled
    """
    ticker = trade_data['ticker']
    entry = trade_data.get('actual_entry', trade_data['entry_price'])
    stop = trade_data['stop_loss']
    tp1 = trade_data['tp1']
    tp2 = trade_data['tp2']

    msg = f"▶️  *TRADE ENTERED*\n"
    msg += "─" * 30 + "\n\n"
    msg += f"*{ticker}* @ ${entry:.2f}\n\n"
    msg += f"🛑 Stop: ${stop:.2f}\n"
    msg += f"✅ TP1: ${tp1:.2f}\n"
    msg += f"🎯 TP2: ${tp2:.2f}\n\n"
    msg += "_Monitoring for exits..._"

    return bot.send_message(msg)


def send_exit_alert(bot: TelegramBot, trade_result: Dict) -> bool:
    """
    Send alert when trade is closed
    """
    ticker = trade_result['ticker']
    entry = trade_result['entry_price']
    exit_price = trade_result['exit_price']
    exit_reason = trade_result['exit_reason']
    r_multiple = trade_result['r_multiple']
    pnl = trade_result['pnl']

    # Choose emoji based on result
    if exit_reason == 'STOP':
        emoji = "❌"
        title = "STOP HIT"
    elif exit_reason == 'TP1':
        emoji = "✅"
        title = "TP1 HIT"
    elif exit_reason == 'TP2':
        emoji = "🎯"
        title = "TP2 HIT"
    else:
        emoji = "🔔"
        title = "TRADE CLOSED"

    msg = f"{emoji} *{title}*\n"
    msg += "─" * 30 + "\n\n"
    msg += f"*{ticker}*\n"
    msg += f"Entry: ${entry:.2f}\n"
    msg += f"Exit: ${exit_price:.2f}\n\n"

    # R-multiple with color indication
    if r_multiple > 0:
        msg += f"✅ *+{r_multiple}R*"
    else:
        msg += f"❌ *{r_multiple}R*"

    if pnl != 0:
        pnl_sign = "+" if pnl > 0 else ""
        msg += f" | {pnl_sign}${pnl:.2f}"

    return bot.send_message(msg)


def send_daily_trade_summary(bot: TelegramBot, summary: Dict) -> bool:
    """
    Send daily trade performance summary
    """
    msg = f"📊 *DAILY TRADE SUMMARY*\n"
    msg += "─" * 30 + "\n\n"

    msg += f"Trades Today: {summary['closed']}\n"

    if summary['closed'] > 0:
        msg += f"Wins: {summary['wins']} | Losses: {summary['closed'] - summary['wins']}\n"
        msg += f"Win Rate: {summary['win_rate']}%\n"
        msg += f"Avg R: {summary['avg_r']}R\n\n"

        # P&L with emoji
        pnl = summary['total_pnl']
        if pnl > 0:
            msg += f"✅ P&L: *+${pnl:.2f}*\n"
        elif pnl < 0:
            msg += f"❌ P&L: *${pnl:.2f}*\n"
        else:
            msg += f"➖ P&L: $0.00\n"
    else:
        msg += "\nNo trades closed today.\n"

    msg += f"\n📂 Open: {summary['open']} | Pending: {summary['pending']}"

    return bot.send_message(msg)


def notify_trade_lifecycle(trade_event: str, data: Dict, cfg: dict) -> bool:
    """
    Main function to handle all trade notifications
    Sends to Telegram + Twitter (if enabled)

    trade_event: 'NEW', 'ENTRY', 'EXIT', 'DAILY_SUMMARY', 'WEEKLY_SUMMARY'
    """
    alerts_cfg = cfg.get("alerts", {})
    telegram_sent = False
    twitter_sent = False

    # ----- TELEGRAM -----
    telegram_cfg = alerts_cfg.get("telegram", {})

    if telegram_cfg.get("enabled", False):
        bot_token = os.getenv(telegram_cfg.get("bot_token_env", "TELEGRAM_BOT_TOKEN"))
        chat_id = os.getenv(telegram_cfg.get("chat_id_env", "TELEGRAM_CHAT_ID"))

        if bot_token and chat_id:
            bot = TelegramBot(bot_token, chat_id)

            if trade_event == 'NEW':
                telegram_sent = send_new_trade_alert(bot, data)
            elif trade_event == 'ENTRY':
                telegram_sent = send_entry_alert(bot, data)
            elif trade_event == 'EXIT':
                telegram_sent = send_exit_alert(bot, data)
            elif trade_event == 'DAILY_SUMMARY':
                telegram_sent = send_daily_trade_summary(bot, data)

    # ----- TWITTER/X -----
    if TWITTER_AVAILABLE:
        twitter_cfg = alerts_cfg.get("twitter", {})

        if twitter_cfg.get("enabled", False):
            tbot = TwitterBot.from_env()

            if tbot:
                text = None

                # Check which events to post
                if trade_event == "NEW" and twitter_cfg.get("post_new_trades", True):
                    text = format_new_trade_tweet(data)

                elif trade_event == "ENTRY" and twitter_cfg.get("post_entries", True):
                    text = format_entry_tweet(data)

                elif trade_event == "EXIT" and twitter_cfg.get("post_exits", True):
                    text = format_exit_tweet(data)

                elif trade_event == "DAILY_SUMMARY" and twitter_cfg.get("post_daily_summary", True):
                    text = format_daily_summary_tweet(data)

                elif trade_event == "WEEKLY_SUMMARY" and twitter_cfg.get("post_weekly_summary", True):
                    text = format_weekly_summary_tweet(data)

                # Post tweet
                if text:
                    twitter_sent = tbot.post(text)

                # Optional auto-engage after daily summary
                if (
                    trade_event == "DAILY_SUMMARY"
                    and twitter_cfg.get("auto_engage", {}).get("enabled", False)
                ):
                    ae = twitter_cfg["auto_engage"]
                    tbot.search_and_engage(
                        query=ae.get("query", "stocks"),
                        like=True,
                        reply_template=ae.get("reply_template"),
                        max_tweets=ae.get("max_tweets", 3),
                    )

    return telegram_sent or twitter_sent


if __name__ == "__main__":
    # Test connection when run directly
    print("Testing Telegram connection...")
    test_telegram_connection()
