#!/usr/bin/env python3
"""
Demo version of Pocket Option Signal Bot
This version works with mock data for demonstration purposes
"""

import asyncio
import json
import logging
import datetime
import numpy as np
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
import redis
import random

# Mock data for demonstration
MOCK_MARKET_DATA = {
    "EURUSD": {"price": 1.08450, "trend": "up"},
    "GBPUSD": {"price": 1.27820, "trend": "down"}, 
    "USDJPY": {"price": 149.85, "trend": "up"},
    "XAUUSD": {"price": 2024.50, "trend": "up"},
    "BTCUSD": {"price": 43250.00, "trend": "down"}
}

class DemoConfig:
    TELEGRAM_TOKEN = "DEMO_MODE"  # Will be replaced with real token
    DEFAULT_SYMBOLS = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "BTCUSD"]
    SUPPORTED_TIMEFRAMES = ["5m", "15m", "30m", "1h"]
    PRO_USERS = []

class MockTechnicalAnalysis:
    @staticmethod
    def generate_mock_indicators(symbol: str):
        """Generate realistic mock technical indicators"""
        base_price = MOCK_MARKET_DATA[symbol]["price"]
        trend = MOCK_MARKET_DATA[symbol]["trend"]
        
        # Generate RSI (30-70 range mostly)
        if trend == "up":
            rsi = random.uniform(45, 75)
        else:
            rsi = random.uniform(25, 55)
        
        # Generate MACD
        if trend == "up":
            macd = random.uniform(0.0005, 0.002)
            macd_signal = macd - random.uniform(0.0001, 0.0005)
        else:
            macd = random.uniform(-0.002, -0.0005)
            macd_signal = macd + random.uniform(0.0001, 0.0005)
        
        # Generate Stochastic
        stoch_k = random.uniform(20, 80)
        stoch_d = stoch_k + random.uniform(-10, 10)
        stoch_d = max(0, min(100, stoch_d))
        
        # Generate ADX (trend strength)
        if trend == "up":
            adx = random.uniform(25, 45)
        else:
            adx = random.uniform(15, 35)
        
        return {
            "rsi": rsi,
            "macd": macd,
            "macd_signal": macd_signal,
            "stoch_k": stoch_k,
            "stoch_d": stoch_d,
            "adx": adx
        }

class DemoPocketOptionBot:
    def __init__(self, token: str):
        if not token or token == "DEMO_MODE":
            raise ValueError("Please provide a real Telegram bot token!")
        
        self.bot = Bot(token=token)
        self.storage = MemoryStorage()  # Use memory instead of Redis for demo
        self.dp = Dispatcher(storage=self.storage)
        self.user_symbols = {}  # Simple dict to store user selections
        self.logger = self.setup_logger()
        
        # Register handlers
        self.register_handlers()
    
    def setup_logger(self):
        logger = logging.getLogger("demo_pocket_option_bot")
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
    
    def register_handlers(self):
        """Register message handlers"""
        self.dp.message.register(self.handle_start, commands=["start"])
        self.dp.message.register(self.handle_5m_signal, commands=["5m"])
        self.dp.message.register(self.handle_15m_signal, commands=["15m"])
        self.dp.message.register(self.handle_30m_signal, commands=["30m"])
        self.dp.message.register(self.handle_1h_signal, commands=["1h"])
        self.dp.message.register(self.handle_pro_command, commands=["pro"])
        self.dp.message.register(self.handle_help, commands=["help"])
        self.dp.message.register(self.handle_symbol_selection, 
                                lambda msg: msg.text.upper() in DemoConfig.DEFAULT_SYMBOLS)
    
    async def handle_start(self, message: types.Message):
        """Handle /start command"""
        keyboard = types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton(symbol) for symbol in DemoConfig.DEFAULT_SYMBOLS[:3]],
                [types.KeyboardButton(symbol) for symbol in DemoConfig.DEFAULT_SYMBOLS[3:]],
                [types.KeyboardButton("📊 همه نمادها"), types.KeyboardButton("ℹ️ راهنما")]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        
        await message.answer(
            "🤖 به ربات نمایشی سیگنال‌دهی پاکت اپشن خوش آمدید!\n\n"
            "🎯 این نسخه نمایشی با داده‌های تصادفی کار می‌کند\n\n"
            "💎 ویژگی‌ها:\n"
            "- سیگنال‌های 5، 15، 30 دقیقه و 1 ساعته\n"
            "- تحلیل تکنیکال کامل\n"
            "- محاسبه درصد اطمینان\n"
            "- رابط کاربری فارسی\n\n"
            "🔮 برای شروع، یک نماد را انتخاب کنید:",
            reply_markup=keyboard
        )
    
    async def handle_symbol_selection(self, message: types.Message):
        """Handle symbol selection"""
        symbol = message.text.upper()
        user_id = message.from_user.id
        
        # Store user's symbol choice
        self.user_symbols[user_id] = symbol
        
        # Create timeframe selection keyboard
        keyboard = types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton("/5m - ۵ دقیقه"), types.KeyboardButton("/15m - ۱۵ دقیقه")],
                [types.KeyboardButton("/30m - ۳۰ دقیقه"), types.KeyboardButton("/1h - ۱ ساعت")],
                [types.KeyboardButton("🔙 تغییر نماد"), types.KeyboardButton("/pro - VIP")]
            ],
            resize_keyboard=True
        )
        
        current_price = MOCK_MARKET_DATA[symbol]["price"]
        trend = MOCK_MARKET_DATA[symbol]["trend"]
        trend_emoji = "📈" if trend == "up" else "📉"
        
        await message.answer(
            f"✅ نماد {symbol} انتخاب شد\n"
            f"💰 قیمت فعلی: {current_price}\n"
            f"{trend_emoji} روند: {'صعودی' if trend == 'up' else 'نزولی'}\n\n"
            "⏱ لطفاً تایم‌فریم مورد نظر را انتخاب کنید:",
            reply_markup=keyboard
        )
    
    async def handle_5m_signal(self, message: types.Message):
        await self.generate_and_send_signal(message, "5m")
    
    async def handle_15m_signal(self, message: types.Message):
        await self.generate_and_send_signal(message, "15m")
    
    async def handle_30m_signal(self, message: types.Message):
        await self.generate_and_send_signal(message, "30m")
    
    async def handle_1h_signal(self, message: types.Message):
        await self.generate_and_send_signal(message, "1h")
    
    async def handle_pro_command(self, message: types.Message):
        """Handle /pro command"""
        user_id = str(message.from_user.id)
        
        if user_id in DemoConfig.PRO_USERS:
            await self.generate_vip_signal(message)
        else:
            await message.answer(
                "🔒 ویژگی‌های VIP در نسخه نمایشی\n\n"
                "💎 در نسخه کامل شامل:\n"
                "- تحلیل چند نماد همزمان\n"
                "- سیگنال‌های پیشرفته با دقت بالاتر\n"
                "- تحلیل احساسات بازار\n"
                "- گزارش‌های تحلیلی روزانه\n"
                "- پشتیبانی اختصاصی\n\n"
                "📞 برای اطلاعات بیشتر با پشتیبانی تماس بگیرید"
            )
    
    async def handle_help(self, message: types.Message):
        """Handle /help command"""
        help_text = (
            "📋 راهنمای استفاده از ربات:\n\n"
            "🔹 /start - شروع و انتخاب نماد\n"
            "🔹 /5m - سیگنال 5 دقیقه‌ای\n"
            "🔹 /15m - سیگنال 15 دقیقه‌ای\n"
            "🔹 /30m - سیگنال 30 دقیقه‌ای\n"
            "🔹 /1h - سیگنال 1 ساعته\n"
            "🔹 /pro - سیگنال‌های VIP\n"
            "🔹 /help - نمایش این راهنما\n\n"
            "📊 نمادهای پشتیبانی شده:\n"
            "- EURUSD (یورو/دلار)\n"
            "- GBPUSD (پوند/دلار)\n"
            "- USDJPY (دلار/ین)\n"
            "- XAUUSD (طلا/دلار)\n"
            "- BTCUSD (بیت‌کوین/دلار)\n\n"
            "⚠️ توجه: این نسخه نمایشی با داده‌های تصادفی کار می‌کند"
        )
        await message.answer(help_text)
    
    async def generate_and_send_signal(self, message: types.Message, timeframe: str):
        """Generate and send trading signal"""
        user_id = message.from_user.id
        
        if user_id not in self.user_symbols:
            await message.answer("⚠️ لطفاً ابتدا نماد را انتخاب کنید (/start)")
            return
        
        symbol = self.user_symbols[user_id]
        
        await message.answer(f"⏳ در حال تولید سیگنال {symbol} در تایم‌فریم {timeframe}...")
        
        # Generate mock signal
        signal = self.generate_demo_signal(symbol, timeframe)
        
        await message.answer(signal, parse_mode="HTML")
    
    def generate_demo_signal(self, symbol: str, timeframe: str) -> str:
        """Generate demo trading signal"""
        try:
            # Get mock indicators
            indicators = MockTechnicalAnalysis.generate_mock_indicators(symbol)
            
            # Generate signal logic
            signal_type, confidence = self.calculate_signal(indicators)
            
            # Get current price and time
            current_price = MOCK_MARKET_DATA[symbol]["price"]
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            
            # Format result
            result = (
                f"🚀 <b>سیگنال {timeframe} - {symbol}</b>\n"
                f"⏰ زمان: {timestamp}\n"
                f"💰 قیمت فعلی: {current_price}\n"
                f"📊 سیگنال: <b>{signal_type}</b> ({confidence}% اطمینان)\n\n"
                f"📈 <b>اندیکاتورها:</b>\n"
                f"• RSI: {indicators['rsi']:.2f}\n"
                f"• MACD: {indicators['macd']:.4f} | Signal: {indicators['macd_signal']:.4f}\n"
                f"• Stochastic: K={indicators['stoch_k']:.2f}, D={indicators['stoch_d']:.2f}\n"
                f"• ADX: {indicators['adx']:.2f}\n\n"
                f"🌐 احساسات بازار: {random.uniform(0.3, 0.8):.2f}\n\n"
                f"⚠️ <i>نسخه نمایشی - داده‌های تصادفی</i>"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error generating demo signal: {str(e)}")
            return "❌ خطا در تولید سیگنال. لطفاً دوباره تلاش کنید."
    
    def calculate_signal(self, indicators: dict) -> tuple:
        """Calculate trading signal from indicators"""
        # Simple signal logic
        rsi_score = 0
        if indicators['rsi'] < 30:
            rsi_score = 1.0  # Oversold - Buy
        elif indicators['rsi'] > 70:
            rsi_score = -1.0  # Overbought - Sell
        elif indicators['rsi'] < 40:
            rsi_score = 0.5
        elif indicators['rsi'] > 60:
            rsi_score = -0.5
        
        macd_score = 1.0 if indicators['macd'] > indicators['macd_signal'] else -1.0
        
        stoch_score = 0
        if indicators['stoch_k'] < 20:
            stoch_score = 1.0  # Oversold
        elif indicators['stoch_k'] > 80:
            stoch_score = -1.0  # Overbought
        
        # Calculate total score
        total_score = (rsi_score * 0.4 + macd_score * 0.4 + stoch_score * 0.2)
        
        # Calculate confidence
        confidence = min(100, int(abs(total_score) * 80 + random.uniform(10, 20)))
        
        # Determine signal
        if total_score > 0.6:
            return "خرید قوی 🟢", confidence
        elif total_score > 0.2:
            return "خرید 🟢", confidence
        elif total_score < -0.6:
            return "فروش قوی 🔴", confidence
        elif total_score < -0.2:
            return "فروش 🔴", confidence
        else:
            return "انتظار ⚪️", confidence
    
    async def generate_vip_signal(self, message: types.Message):
        """Generate VIP signal for multiple symbols"""
        await message.answer("🕒 در حال تولید سیگنال‌های VIP...")
        
        signals = []
        for symbol in DemoConfig.DEFAULT_SYMBOLS:
            indicators = MockTechnicalAnalysis.generate_mock_indicators(symbol)
            signal_type, confidence = self.calculate_signal(indicators)
            current_price = MOCK_MARKET_DATA[symbol]["price"]
            
            signals.append(
                f"📈 <b>{symbol}</b>: {signal_type} ({confidence}%)\n"
                f"💰 قیمت: {current_price}"
            )
        
        vip_message = (
            "🌟 <b>سیگنال‌های VIP</b>\n\n" +
            "\n\n".join(signals) +
            "\n\n🌍 <b>تحلیل کلی بازار:</b>\n"
            "📊 روند کلی: متغیر\n"
            "📈 احساسات: خنثی تا مثبت\n"
            "⚠️ ریسک: متوسط\n\n"
            "<i>نسخه نمایشی - داده‌های تصادفی</i>"
        )
        
        await message.answer(vip_message, parse_mode="HTML")

# Start function
async def start_demo_bot(token: str):
    """Start the demo bot"""
    try:
        demo_bot = DemoPocketOptionBot(token)
        print("🤖 Demo Pocket Option Bot started!")
        print("Press Ctrl+C to stop")
        await demo_bot.dp.start_polling(demo_bot.bot)
    except Exception as e:
        print(f"❌ Error starting demo bot: {str(e)}")

# Main function for testing
if __name__ == "__main__":
    print("🎮 Pocket Option Demo Bot")
    print("=" * 40)
    
    token = input("📱 لطفاً توکن ربات تلگرام را وارد کنید: ").strip()
    
    if not token:
        print("❌ توکن وارد نشده!")
        exit(1)
    
    try:
        asyncio.run(start_demo_bot(token))
    except KeyboardInterrupt:
        print("\n👋 ربات نمایشی متوقف شد!")
    except Exception as e:
        print(f"❌ خطا: {str(e)}")