#!/usr/bin/env python3
"""
INTERACTIVE TELEGRAM BOT - Chat with AI Trading Assistant

Features:
- Commands: /start, /help, /trades, /summary, /stats, /market
- Natural language Q&A about trades, finance, stocks, AI
- Multi-user support (shareable bot)
- Real-time trade updates
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import sqlite3

# Telegram Bot imports
try:
    from telegram import Update
    from telegram.ext import (
        Application,
        CommandHandler,
        MessageHandler,
        filters,
        ContextTypes,
    )
    TELEGRAM_BOT_AVAILABLE = True
except ImportError:
    TELEGRAM_BOT_AVAILABLE = False
    print("❌ python-telegram-bot not installed. Run: pip install python-telegram-bot")
    sys.exit(1)

# OpenAI for AI responses
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️  OpenAI not available. Install with: pip install openai")

# Import existing modules
try:
    from database import get_db_connection
    from content_engine import MarketDataEngine, TweetContentGenerator
except ImportError:
    print("⚠️  Could not import database/content_engine modules")
    get_db_connection = None
    MarketDataEngine = None
    TweetContentGenerator = None

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class TradingAssistantBot:
    """
    Interactive Telegram bot for AI Stock Trading Agent
    """

    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.openai_key = os.getenv("OPENAI_API_KEY")

        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN not set in environment")

        # Initialize OpenAI if available
        if self.openai_key and OPENAI_AVAILABLE:
            openai.api_key = self.openai_key
            self.ai_enabled = True
            logger.info("✅ OpenAI integration enabled")
        else:
            self.ai_enabled = False
            logger.warning("⚠️  OpenAI not configured - using basic responses")

        # Initialize market data engine
        if MarketDataEngine:
            self.market_engine = MarketDataEngine()
        else:
            self.market_engine = None


    # ============================================================
    # COMMAND HANDLERS
    # ============================================================

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_msg = """
🤖 *AI STOCK TRADING ASSISTANT*

Namaste! I'm your AI trading companion.

*What I can do:*
✅ Answer trading & finance questions
✅ Show your current trades
✅ Provide market updates (SPY, QQQ, VIX)
✅ Share trading stats & performance
✅ Explain stocks, AI, and market concepts

*Commands:*
/help - Show all commands
/trades - View current trades
/summary - Trading performance summary
/stats - Detailed statistics
/market - Live market overview

*Just chat with me!*
Ask anything about trading, stocks, finance, or AI.

Example: "What's the market doing today?"
Example: "Explain RSI indicator"
Example: "Should I buy NVDA?"

⚠️ _Not financial advice. Always DYOR._
"""
        await update.message.reply_text(welcome_msg, parse_mode='Markdown')


    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_msg = """
📖 *COMMANDS GUIDE*

*Trading Commands:*
/trades - View open & pending trades
/summary - Daily/weekly summary
/stats - Win rate, avg R, P&L

*Market Commands:*
/market - SPY, QQQ, VIX overview
/scan - Latest stock scan results

*General:*
/start - Welcome message
/help - This guide

*Chat Mode:*
Just type your question!
Examples:
• "What's RSI?"
• "How's NVDA doing?"
• "Explain breakout pattern"
• "Show me today's winners"

💬 I understand natural language!
"""
        await update.message.reply_text(help_msg, parse_mode='Markdown')


    async def trades_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /trades command - show current trades"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Get open trades
            cursor.execute("""
                SELECT ticker, entry_price, current_price, stop_loss, tp1, tp2,
                       entry_time, status, notes
                FROM trades
                WHERE status IN ('PENDING', 'OPEN')
                ORDER BY entry_time DESC
                LIMIT 10
            """)

            trades = cursor.fetchall()
            conn.close()

            if not trades:
                msg = "📂 *CURRENT TRADES*\n\n"
                msg += "No open or pending trades right now.\n\n"
                msg += "_System is monitoring for opportunities..._"
                await update.message.reply_text(msg, parse_mode='Markdown')
                return

            msg = "📂 *CURRENT TRADES*\n"
            msg += "─" * 30 + "\n\n"

            for trade in trades:
                ticker, entry, current, sl, tp1, tp2, entry_time, status, notes = trade

                # Status emoji
                if status == 'OPEN':
                    status_emoji = "▶️"
                else:
                    status_emoji = "⏸️"

                msg += f"{status_emoji} *{ticker}* ({status})\n"
                msg += f"Entry: ${entry:.2f}"

                if current:
                    pnl_pct = ((current - entry) / entry) * 100
                    if pnl_pct > 0:
                        msg += f" → ${current:.2f} (+{pnl_pct:.1f}%)"
                    else:
                        msg += f" → ${current:.2f} ({pnl_pct:.1f}%)"

                msg += f"\n🛑 SL: ${sl:.2f} | ✅ TP1: ${tp1:.2f} | 🎯 TP2: ${tp2:.2f}\n"

                if notes:
                    msg += f"📝 {notes}\n"

                msg += "\n"

            await update.message.reply_text(msg, parse_mode='Markdown')

        except Exception as e:
            logger.error(f"Error fetching trades: {e}")
            await update.message.reply_text(
                "❌ Error fetching trades. Database may not be initialized."
            )


    async def summary_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /summary command - trading performance"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Get today's closed trades
            today = datetime.now().date()
            cursor.execute("""
                SELECT COUNT(*),
                       SUM(CASE WHEN r_multiple > 0 THEN 1 ELSE 0 END) as wins,
                       AVG(r_multiple) as avg_r,
                       SUM(pnl) as total_pnl
                FROM trades
                WHERE status = 'CLOSED'
                  AND DATE(exit_time) = ?
            """, (today,))

            today_stats = cursor.fetchone()

            # Get week's stats
            week_ago = today - timedelta(days=7)
            cursor.execute("""
                SELECT COUNT(*),
                       SUM(CASE WHEN r_multiple > 0 THEN 1 ELSE 0 END) as wins,
                       AVG(r_multiple) as avg_r,
                       SUM(pnl) as total_pnl
                FROM trades
                WHERE status = 'CLOSED'
                  AND DATE(exit_time) >= ?
            """, (week_ago,))

            week_stats = cursor.fetchone()

            # Get open/pending count
            cursor.execute("""
                SELECT
                    SUM(CASE WHEN status = 'OPEN' THEN 1 ELSE 0 END) as open_count,
                    SUM(CASE WHEN status = 'PENDING' THEN 1 ELSE 0 END) as pending_count
                FROM trades
            """)

            current_counts = cursor.fetchone()
            conn.close()

            # Format message
            msg = "📊 *TRADING SUMMARY*\n"
            msg += "─" * 30 + "\n\n"

            # Today
            msg += "*📅 Today:*\n"
            if today_stats[0] > 0:
                wins = today_stats[1] or 0
                win_rate = (wins / today_stats[0]) * 100 if today_stats[0] > 0 else 0
                avg_r = today_stats[2] or 0
                pnl = today_stats[3] or 0

                msg += f"Trades: {today_stats[0]} | Wins: {wins} ({win_rate:.0f}%)\n"
                msg += f"Avg R: {avg_r:.2f}R"

                if pnl > 0:
                    msg += f" | ✅ +${pnl:.2f}\n"
                elif pnl < 0:
                    msg += f" | ❌ ${pnl:.2f}\n"
                else:
                    msg += f" | ➖ $0.00\n"
            else:
                msg += "No closed trades today\n"

            msg += "\n"

            # Week
            msg += "*📆 This Week:*\n"
            if week_stats[0] > 0:
                wins = week_stats[1] or 0
                win_rate = (wins / week_stats[0]) * 100 if week_stats[0] > 0 else 0
                avg_r = week_stats[2] or 0
                pnl = week_stats[3] or 0

                msg += f"Trades: {week_stats[0]} | Wins: {wins} ({win_rate:.0f}%)\n"
                msg += f"Avg R: {avg_r:.2f}R"

                if pnl > 0:
                    msg += f" | ✅ +${pnl:.2f}\n"
                elif pnl < 0:
                    msg += f" | ❌ ${pnl:.2f}\n"
                else:
                    msg += f" | ➖ $0.00\n"
            else:
                msg += "No closed trades this week\n"

            msg += "\n"

            # Current
            open_count = current_counts[0] or 0
            pending_count = current_counts[1] or 0
            msg += f"*📂 Current:*\n"
            msg += f"Open: {open_count} | Pending: {pending_count}\n"

            await update.message.reply_text(msg, parse_mode='Markdown')

        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            await update.message.reply_text(
                "❌ Error generating summary. Try again later."
            )


    async def market_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /market command - market overview"""
        try:
            if not self.market_engine:
                await update.message.reply_text(
                    "❌ Market data not available. Check configuration."
                )
                return

            # Get market overview
            market_data = self.market_engine.get_market_overview()

            msg = "📈 *MARKET OVERVIEW*\n"
            msg += "─" * 30 + "\n\n"

            for ticker, data in market_data.items():
                change_pct = data.get('change_pct', 0)

                if change_pct > 0:
                    emoji = "🟢"
                    sign = "+"
                elif change_pct < 0:
                    emoji = "🔴"
                    sign = ""
                else:
                    emoji = "⚪"
                    sign = ""

                msg += f"{emoji} *{ticker}*: ${data.get('current', 0):.2f} "
                msg += f"({sign}{change_pct:.2f}%)\n"

            msg += f"\n_Updated: {datetime.now().strftime('%I:%M %p ET')}_"

            await update.message.reply_text(msg, parse_mode='Markdown')

        except Exception as e:
            logger.error(f"Error fetching market data: {e}")
            await update.message.reply_text(
                "❌ Error fetching market data. Try again."
            )


    # ============================================================
    # MESSAGE HANDLER (AI Responses)
    # ============================================================

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle natural language questions using AI"""
        user_message = update.message.text
        user_name = update.effective_user.first_name or "there"

        logger.info(f"User question: {user_message}")

        # If OpenAI is available, use it
        if self.ai_enabled:
            try:
                response = await self.get_ai_response(user_message)
                await update.message.reply_text(response, parse_mode='Markdown')
                return
            except Exception as e:
                logger.error(f"OpenAI error: {e}")
                # Fall through to basic responses

        # Basic keyword-based responses (fallback)
        response = self.get_basic_response(user_message)
        await update.message.reply_text(response, parse_mode='Markdown')


    async def get_ai_response(self, question: str) -> str:
        """Get AI-powered response using OpenAI"""
        try:
            # System prompt for AI
            system_prompt = """You are an AI Stock Trading Assistant.

You help users with:
- Trading concepts (RSI, MACD, breakouts, etc.)
- Stock market questions
- AI industry updates
- Finance education
- Risk management

Keep responses:
- Concise (2-3 paragraphs max)
- Educational and helpful
- Include emojis when appropriate
- End with: "⚠️ Not financial advice. DYOR."

Use Markdown formatting."""

            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question}
                ],
                max_tokens=500,
                temperature=0.7
            )

            answer = response.choices[0].message.content.strip()
            return answer

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise


    def get_basic_response(self, message: str) -> str:
        """Basic keyword-based responses (fallback)"""
        message_lower = message.lower()

        # Trading indicators
        if 'rsi' in message_lower:
            return """
📊 *RSI (Relative Strength Index)*

RSI measures momentum on a 0-100 scale.

• *Above 70*: Overbought (potential sell)
• *Below 30*: Oversold (potential buy)
• *50*: Neutral

Used to spot reversals & confirm trends.

⚠️ Not financial advice. DYOR.
"""

        elif 'macd' in message_lower:
            return """
📈 *MACD (Moving Average Convergence Divergence)*

Shows trend & momentum.

*Signals:*
• MACD crosses above signal → Bullish
• MACD crosses below signal → Bearish
• Histogram growing → Momentum increasing

Common timeframe: 12, 26, 9 periods.

⚠️ Not financial advice. DYOR.
"""

        elif 'breakout' in message_lower:
            return """
🚀 *Breakout Pattern*

Price moves above resistance with volume.

*What to look for:*
• Clear resistance level
• Volume spike (2x+ average)
• Strong close above resistance
• Follow-through next day

Risk: False breakouts (avoid low volume).

⚠️ Not financial advice. DYOR.
"""

        # Market questions
        elif 'market' in message_lower or 'spy' in message_lower:
            return "Use /market command to see live SPY, QQQ, VIX data! 📊"

        # Trade questions
        elif 'trade' in message_lower or 'position' in message_lower:
            return "Use /trades to see current positions! 📂"

        # Default response
        else:
            return f"""
💬 I can help with:

• Trading indicators (RSI, MACD, etc.)
• Market analysis
• Stock questions
• Finance concepts

Try asking:
"What's RSI?"
"Show market overview" (or /market)
"Explain consolidation pattern"

Or use commands:
/trades - Your positions
/summary - Performance stats
/help - All commands

⚠️ Not financial advice. DYOR.
"""


    # ============================================================
    # RUN BOT
    # ============================================================

    def run(self):
        """Start the bot"""
        logger.info("🤖 Starting Interactive Telegram Bot...")

        # Create application
        app = Application.builder().token(self.bot_token).build()

        # Add command handlers
        app.add_handler(CommandHandler("start", self.start_command))
        app.add_handler(CommandHandler("help", self.help_command))
        app.add_handler(CommandHandler("trades", self.trades_command))
        app.add_handler(CommandHandler("summary", self.summary_command))
        app.add_handler(CommandHandler("market", self.market_command))

        # Add message handler for natural language
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

        # Start bot
        logger.info("✅ Bot started! Press Ctrl+C to stop")
        app.run_polling(allowed_updates=Update.ALL_TYPES)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    try:
        bot = TradingAssistantBot()
        bot.run()
    except KeyboardInterrupt:
        logger.info("\n👋 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Bot crashed: {e}")
        sys.exit(1)
