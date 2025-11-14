
import os
import requests
from typing import List, Dict, Optional

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

        msg += "   " + " | ".join(signals) + "\n"

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
    bot_token = os.getenv(telegram_cfg.get("bot_token_env", "TELEGRAM_BOT_TOKEN"))
    chat_id = os.getenv(telegram_cfg.get("chat_id_env", "TELEGRAM_CHAT_ID"))

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
                caption = f"📊 *{ticker}* Chart"
                if r.get('Consolidating'):
                    caption += " 🟢 CONS"
                if r.get('BuyDip'):
                    caption += " 🔻 DIP"

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


if __name__ == "__main__":
    # Test connection when run directly
    print("Testing Telegram connection...")
    test_telegram_connection()
