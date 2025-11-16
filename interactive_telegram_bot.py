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

# AI providers for responses
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️  Gemini not available. Install with: pip install google-generativeai")

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️  OpenAI not available. Install with: pip install openai")

# Configure logging FIRST (before any logger usage)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Import existing modules
try:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from content_engine import MarketDataEngine
    from market_intelligence import MarketIntelligence
    MARKET_INTELLIGENCE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"⚠️  Could not import modules: {e}")
    MarketDataEngine = None
    MarketIntelligence = None
    MARKET_INTELLIGENCE_AVAILABLE = False


class TradingAssistantBot:
    """
    Interactive Telegram bot for AI Stock Trading Agent
    """

    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")

        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN not set in environment")

        # Initialize AI provider (prioritize Gemini over OpenAI)
        self.ai_provider = None
        self.ai_enabled = False

        if self.gemini_key and GEMINI_AVAILABLE:
            self.gemini_model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-2.0-flash-exp")
            try:
                genai.configure(api_key=self.gemini_key)
                self.gemini_model = genai.GenerativeModel(self.gemini_model_name)
                self.ai_provider = "gemini"
                self.ai_enabled = True
                logger.info(f"✅ Gemini AI integration enabled (model: {self.gemini_model_name})")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Gemini model '{self.gemini_model_name}': {e}")
                self.gemini_model = None
                self.ai_provider = None
                self.ai_enabled = False

        if not self.ai_enabled:
            if self.openai_key and OPENAI_AVAILABLE:
                openai.api_key = self.openai_key
                self.ai_provider = "openai"
                self.ai_enabled = True
                logger.info("✅ OpenAI integration enabled")
            else:
                logger.warning("⚠️  No AI provider configured - using basic responses")

        # Initialize market data engine
        if MarketDataEngine:
            self.market_engine = MarketDataEngine()
        else:
            self.market_engine = None

        # Initialize market intelligence
        if MARKET_INTELLIGENCE_AVAILABLE and MarketIntelligence:
            self.market_intel = MarketIntelligence()
            logger.info("✅ Market Intelligence enabled (stocks, news, analysis)")
        else:
            self.market_intel = None


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
            conn = sqlite3.connect('stock_agent.db')
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
            conn = sqlite3.connect('stock_agent.db')
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
        """Handle natural language questions using AI + Market Intelligence"""
        user_message = update.message.text
        user_name = update.effective_user.first_name or "there"

        logger.info(f"User question: {user_message}")

        # First, check if this is a stock/market query using Market Intelligence
        market_context = None
        if self.market_intel:
            try:
                market_result = self.market_intel.process_query(user_message)
                if market_result and market_result.get('data'):
                    market_context = market_result
                    logger.info(f"Market query detected: {market_result['query_type']}, Symbol: {market_result.get('symbol')}")
            except Exception as e:
                logger.error(f"Market intelligence error: {e}")

        # Use AI with market context if available
        if self.ai_enabled:
            try:
                response = await self.get_ai_response(user_message, market_context)
                await update.message.reply_text(response, parse_mode='Markdown')
                return
            except Exception as e:
                logger.error(f"AI error: {e}", exc_info=True)
                # Fall through to format market data or basic responses

        # If market context available but AI failed, format market data manually
        if market_context:
            response = self.format_market_response(market_context)
            await update.message.reply_text(response, parse_mode='Markdown')
            return

        # Basic keyword-based responses (fallback)
        response = self.get_basic_response(user_message)
        await update.message.reply_text(response, parse_mode='Markdown')


    async def get_ai_response(self, question: str, market_context: Optional[Dict] = None) -> str:
        """Get AI-powered response using Gemini or OpenAI with optional market data context"""
        try:
            # Base system prompt
            system_prompt = """You are an AI Stock Trading Assistant with real-time market data access.

You help users with:
- Real-time stock prices, news, and analysis
- Trading concepts (RSI, MACD, breakouts, etc.)
- Stock market questions
- AI industry updates
- Finance education
- Risk management

Keep responses:
- Concise (2-3 paragraphs max)
- Data-driven when market data is provided
- Educational and helpful
- Include emojis when appropriate
- End with: "⚠️ Not financial advice. DYOR."

Use Markdown formatting."""

            # Build context from market data if available
            context_data = ""
            if market_context:
                query_type = market_context.get('query_type')
                symbol = market_context.get('symbol')
                data = market_context.get('data')

                if data:
                    context_data = "\n\n**REAL-TIME MARKET DATA:**\n"

                    # Price data
                    if isinstance(data, dict) and 'price_data' in data:
                        price_info = data['price_data']
                        if price_info:
                            context_data += f"\n{symbol} Current Data:\n"
                            context_data += f"- Price: ${price_info.get('price', 'N/A')}\n"
                            context_data += f"- Change: {price_info.get('change', 0):+.2f} ({price_info.get('change_pct', 0):+.2f}%)\n"
                            context_data += f"- Volume: {price_info.get('volume', 0):,}\n"
                            context_data += f"- Day Range: ${price_info.get('day_low', 'N/A')} - ${price_info.get('day_high', 'N/A')}\n"
                            if price_info.get('market_cap'):
                                context_data += f"- Market Cap: ${price_info['market_cap']/1e9:.2f}B\n"
                    elif isinstance(data, dict) and 'price' in data:
                        context_data += f"\n{symbol}: ${data['price']} ({data.get('change_pct', 0):+.2f}%)\n"

                    # News data
                    if isinstance(data, dict) and 'news' in data:
                        news_items = data['news']
                        if news_items:
                            context_data += f"\nLatest News for {symbol}:\n"
                            for i, news in enumerate(news_items[:3], 1):
                                context_data += f"{i}. {news['title']} ({news['published']})\n"

                    # Top stocks
                    if isinstance(data, list) and len(data) > 0 and 'symbol' in data[0]:
                        context_data += "\nTop Stocks Today:\n"
                        for i, stock in enumerate(data[:10], 1):
                            context_data += f"{i}. {stock['symbol']}: ${stock['price']} ({stock['change_pct']:+.2f}%)\n"

            # Combine everything
            full_question = question
            if context_data:
                full_question = f"{context_data}\n\nUser Question: {question}\n\nProvide an intelligent analysis using the above real-time data."

            # Use Gemini if available
            if self.ai_provider == "gemini":
                full_prompt = f"{system_prompt}\n\n{full_question}"
                response = self.gemini_model.generate_content(full_prompt)
                return response.text.strip()

            # Otherwise use OpenAI
            elif self.ai_provider == "openai":
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": full_question}
                    ],
                    max_tokens=700,
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"AI API error ({self.ai_provider}): {e}")
            raise


    def format_market_response(self, market_context: Dict) -> str:
        """Format market intelligence data into a readable response (fallback when AI unavailable)"""
        query_type = market_context.get('query_type')
        symbol = market_context.get('symbol')
        data = market_context.get('data')

        # Debug logging
        logger.info(f"Formatting response - Query type: {query_type}, Symbol: {symbol}, Data type: {type(data)}")

        if not data:
            return "❌ No market data available for this query."

        response = ""

        # Price query
        if query_type == 'price' and isinstance(data, dict) and 'price' in data:
            response = f"📊 *{symbol}* - {data.get('name', symbol)}\n\n"
            response += f"💰 Price: ${data['price']}\n"
            change_emoji = "🟢" if data.get('change', 0) >= 0 else "🔴"
            response += f"{change_emoji} Change: {data.get('change', 0):+.2f} ({data.get('change_pct', 0):+.2f}%)\n"
            response += f"📈 Volume: {data.get('volume', 0):,}\n"
            response += f"📉 Day Range: ${data.get('day_low', 'N/A')} - ${data.get('day_high', 'N/A')}\n"
            if data.get('market_cap'):
                response += f"💎 Market Cap: ${data['market_cap']/1e9:.2f}B\n"

        # News query
        elif query_type == 'news' and isinstance(data, list):
            if not data:
                response = f"📰 *Latest News*\n\nNo news available at the moment. Try again later or specify a stock symbol.\n"
            else:
                label = f"Latest News for {symbol}" if symbol and symbol != 'SPY' else "Market News"
                response = f"📰 *{label}*\n\n"
                for i, news in enumerate(data[:5], 1):
                    response += f"{i}. {news['title']}\n"
                    response += f"   📅 {news['published']} | {news['publisher']}\n\n"

        # Why query
        elif query_type == 'why' and isinstance(data, dict):
            price_data = data.get('price_data', {})
            news = data.get('news', [])

            response = f"🔍 *Analysis for {symbol}*\n\n"

            if price_data:
                response += f"💰 Price: ${price_data['price']} ({price_data['change_pct']:+.2f}%)\n\n"

            if news:
                response += "📰 *Recent News:*\n"
                for i, item in enumerate(news[:3], 1):
                    response += f"{i}. {item['title']}\n"
                response += "\n"

            response += "💡 _For AI-powered analysis, ensure Gemini API key is configured._\n"

        # Top stocks
        elif isinstance(data, list) and len(data) > 0:
            list_type = "Top Stocks"
            if 'gainer' in market_context.get('context', '').lower():
                list_type = "🔥 Top Gainers"
            elif 'loser' in market_context.get('context', '').lower():
                list_type = "📉 Top Losers"
            elif 'active' in market_context.get('context', '').lower():
                list_type = "📊 Most Active"

            response = f"*{list_type} Today*\n\n"
            for i, stock in enumerate(data[:10], 1):
                emoji = "🟢" if stock['change_pct'] >= 0 else "🔴"
                response += f"{i}. {emoji} *{stock['symbol']}*: ${stock['price']} ({stock['change_pct']:+.2f}%)\n"

        # Generic stock data
        elif isinstance(data, dict) and 'price_data' in data:
            price_info = data['price_data']
            if price_info:
                response = f"📊 *{symbol}* - {price_info.get('name', symbol)}\n\n"
                response += f"💰 ${price_info['price']} ({price_info['change_pct']:+.2f}%)\n"
                response += f"📈 Volume: {price_info['volume']:,}\n\n"

            news_items = data.get('news', [])
            if news_items:
                response += "*Latest News:*\n"
                for news in news_items[:3]:
                    response += f"• {news['title']}\n"

        if not response:
            # Fallback with debug info
            logger.warning(f"Could not format market data - Type: {query_type}, Data: {str(data)[:100]}")
            response = f"❌ Unable to format market data.\n\n"
            response += f"Query type: {query_type}\n"
            response += f"Symbol: {symbol or 'None'}\n\n"
            response += "Try these instead:\n"
            response += "• 'AAPL price' - Get stock price\n"
            response += "• 'Tesla news' - Get company news\n"
            response += "• 'what is SIP' - Financial planning\n"
            response += "• /market - Market overview"

        response += "\n\n⚠️ _Not financial advice. DYOR._"
        return response


    def get_basic_response(self, message: str) -> str:
        """Basic keyword-based responses (fallback)"""
        message_lower = message.lower()

        # Financial Planning - SIP
        if 'sip' in message_lower:
            return """
📊 *SIP (Systematic Investment Plan)*

SIP is a disciplined way to invest in mutual funds.

*How it works:*
• Invest a fixed amount regularly (monthly/weekly)
• Buys more units when prices are low
• Buys fewer units when prices are high
• This is called "Rupee Cost Averaging"

*Benefits:*
• 💰 Start with as little as ₹500/month
• 📈 Compound growth over time
• 🎯 Disciplined investing habit
• ⚖️ Reduces market timing risk

*Example:*
₹5,000/month for 10 years @ 12% return
= ~₹11.6 Lakhs invested → ~₹20 Lakhs value

*Popular for:* Retirement, child education, wealth creation

⚠️ _Not financial advice. DYOR. Mutual funds subject to market risk._
"""

        # Financial Planning - EMI
        elif 'emi' in message_lower:
            return """
💳 *EMI (Equated Monthly Installment)*

EMI is a fixed monthly payment for loans.

*How it works:*
• Split your loan into equal monthly payments
• Each EMI = Principal + Interest
• Interest is higher in early EMIs
• Principal portion increases over time

*EMI Calculation:*
EMI = [P × r × (1+r)^n] / [(1+r)^n - 1]
Where: P = Loan, r = Monthly rate, n = Months

*Example:*
₹10 Lakh loan @ 9% for 5 years
= ₹20,758/month
Total paid = ₹12.45 Lakhs (₹2.45L interest)

*Tips:*
• 💡 Lower tenure = Less interest
• 📉 Prepay when possible
• 🎯 Keep EMIs < 40% of income

⚠️ _Not financial advice. Calculate carefully before borrowing._
"""

        # Trading indicators
        elif 'rsi' in message_lower:
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

    def run(self, in_thread=False):
        """Start the bot

        Args:
            in_thread: Set to True when running in a background thread
        """
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

        if in_thread:
            # Running in thread - disable signal handlers
            app.run_polling(allowed_updates=Update.ALL_TYPES, stop_signals=None)
        else:
            # Running in main thread - use signal handlers
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
