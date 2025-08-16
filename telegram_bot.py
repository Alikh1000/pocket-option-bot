import os
import asyncio
import json
import logging
import datetime
import numpy as np
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.redis import RedisStorage
from transformers import pipeline
import aiohttp
# import talib  # We'll implement indicators manually
import redis

# --------------------- Manual Technical Indicators ---------------------
class ManualIndicators:
    @staticmethod
    def rsi(prices, period=14):
        """Calculate RSI manually"""
        if len(prices) < period + 1:
            return 50.0  # Default neutral value
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[:period])
        avg_loss = np.mean(losses[:period])
        
        for i in range(period, len(gains)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def macd(prices, fast=12, slow=26, signal=9):
        """Calculate MACD manually"""
        if len(prices) < slow + signal:
            return 0.0, 0.0, 0.0
        
        # Calculate EMAs
        ema_fast = ManualIndicators._ema(prices, fast)
        ema_slow = ManualIndicators._ema(prices, slow)
        
        macd_line = ema_fast - ema_slow
        signal_line = ManualIndicators._ema([macd_line], signal)
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    @staticmethod
    def stochastic(high, low, close, k_period=14, d_period=3):
        """Calculate Stochastic oscillator manually"""
        if len(close) < k_period:
            return 50.0, 50.0
        
        lowest_low = np.min(low[-k_period:])
        highest_high = np.max(high[-k_period:])
        
        if highest_high == lowest_low:
            k_percent = 50.0
        else:
            k_percent = ((close[-1] - lowest_low) / (highest_high - lowest_low)) * 100
        
        # For simplicity, return k_percent for both K and D
        return k_percent, k_percent
    
    @staticmethod
    def adx(high, low, close, period=14):
        """Calculate ADX manually (simplified version)"""
        if len(close) < period + 1:
            return 25.0  # Default neutral trend strength
        
        # Calculate True Range
        tr_list = []
        for i in range(1, len(close)):
            tr1 = high[i] - low[i]
            tr2 = abs(high[i] - close[i-1])
            tr3 = abs(low[i] - close[i-1])
            tr_list.append(max(tr1, tr2, tr3))
        
        if len(tr_list) < period:
            return 25.0
        
        # Simplified ADX calculation
        atr = np.mean(tr_list[-period:])
        price_range = max(high[-period:]) - min(low[-period:])
        
        if price_range == 0:
            return 25.0
        
        adx = min(100, (atr / price_range) * 100)
        return adx
    
    @staticmethod
    def _ema(prices, period):
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return np.mean(prices) if prices else 0.0
        
        multiplier = 2 / (period + 1)
        ema = np.mean(prices[:period])
        
        for price in prices[period:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        return ema

# --------------------- تنظیمات اصلی ---------------------
class Config:
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "YOUR_BOT_TOKEN")
    ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY", "YOUR_API_KEY")
    NEWS_API_KEY = os.getenv("NEWS_API_KEY", "YOUR_NEWS_API_KEY")
    TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN", "YOUR_TWITTER_TOKEN")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    PRO_USERS = json.loads(os.getenv("PRO_USERS", "[]"))
    
    # تنظیمات نمادهای پیش‌فرض
    DEFAULT_SYMBOLS = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "BTCUSD"]
    
    # تنظیمات تحلیل تکنیکال
    RSI_PERIOD = 14
    MACD_FAST = 12
    MACD_SLOW = 26
    MACD_SIGNAL = 9
    SUPPORTED_TIMEFRAMES = ["5m", "15m", "30m", "1h"]

# --------------------- سرویس‌های بازار ---------------------
class MarketServices:
    @staticmethod
    async def get_realtime_data(symbol, timeframe):
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval={timeframe}&apikey={Config.ALPHA_VANTAGE_KEY}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                return data.get(f"Time Series ({timeframe})", {})
    
    @staticmethod
    async def get_financial_news(symbol):
        url = f"https://newsapi.org/v2/everything?q={symbol}&language=en&sortBy=publishedAt&apiKey={Config.NEWS_API_KEY}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                return data.get("articles", [])

# --------------------- تحلیل احساسات ---------------------
class SentimentAnalyzer:
    def __init__(self):
        self.news_analyzer = pipeline(
            "text-classification",
            model="mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis"
        )
        self.twitter_analyzer = pipeline(
            "sentiment-analysis",
            model="cardiffnlp/twitter-roberta-base-sentiment"
        )
    
    async def get_news_sentiment(self, symbol):
        news = await MarketServices.get_financial_news(symbol)
        
        if not news:
            return 0.5
        
        sentiments = []
        for article in news[:10]:
            text = f"{article.get('title', '')} {article.get('description', '')}"
            if text.strip():
                try:
                    result = self.news_analyzer(text)[0]
                    score = result['score'] if result['label'] == 'positive' else -result['score']
                    sentiments.append(score)
                except:
                    continue
        
        if not sentiments:
            return 0.5
        
        avg_sentiment = (sum(sentiments) / len(sentiments) + 1) / 2
        return avg_sentiment
    
    async def get_twitter_sentiment(self, symbol):
        url = f"https://api.twitter.com/2/tweets/search/recent?query={symbol} lang:en&max_results=20"
        headers = {"Authorization": f"Bearer {Config.TWITTER_BEARER_TOKEN}"}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                data = await response.json()
                tweets = [tweet['text'] for tweet in data.get('data', [])]
        
        if not tweets:
            return 0.5
        
        sentiments = []
        for tweet in tweets:
            try:
                result = self.twitter_analyzer(tweet)[0]
                if result['label'] == 'LABEL_0':  # Negative
                    sentiment = -result['score']
                elif result['label'] == 'LABEL_1':  # Neutral
                    sentiment = 0
                else:  # Positive
                    sentiment = result['score']
                sentiments.append(sentiment)
            except:
                continue
        
        if not sentiments:
            return 0.5
        
        avg_sentiment = (sum(sentiments) / len(sentiments) + 1) / 2
        return avg_sentiment
    
    async def get_market_sentiment(self, symbol):
        news_sentiment = await self.get_news_sentiment(symbol)
        twitter_sentiment = await self.get_twitter_sentiment(symbol)
        return (news_sentiment + twitter_sentiment) / 2

# --------------------- تحلیل تکنیکال ---------------------
class TechnicalAnalysis:
    @staticmethod
    def calculate_indicators(data):
        if len(data) < max(Config.RSI_PERIOD, Config.MACD_SLOW):
            return None
        
        closes = [float(item["4. close"]) for item in data.values()]
        high = [float(item["2. high"]) for item in data.values()]
        low = [float(item["3. low"]) for item in data.values()]
        
        # Use manual implementations instead of talib
        rsi = ManualIndicators.rsi(closes, Config.RSI_PERIOD)
        macd, macd_signal, _ = ManualIndicators.macd(
            closes, 
            Config.MACD_FAST, 
            Config.MACD_SLOW, 
            Config.MACD_SIGNAL
        )
        
        # محاسبه استوکاستیک
        slowk, slowd = ManualIndicators.stochastic(
            high, low, closes, 14, 3
        )
        
        # محاسبه ADX
        adx = ManualIndicators.adx(high, low, closes, 14)
        
        return {
            "rsi": rsi,
            "macd": macd,
            "macd_signal": macd_signal,
            "stoch_k": slowk,
            "stoch_d": slowd,
            "adx": adx
        }

# --------------------- سیستم ربات ---------------------
class PocketOptionSignalBot:
    def __init__(self):
        self.bot = Bot(token=Config.TELEGRAM_TOKEN)
        self.storage = RedisStorage.from_url(Config.REDIS_URL)
        self.dp = Dispatcher(storage=self.storage)
        self.sentiment_analyzer = SentimentAnalyzer()
        self.redis = redis.Redis.from_url(Config.REDIS_URL)
        self.logger = self.setup_logger()
        
        # ثبت هندلرها
        from aiogram.filters import Command
        self.dp.message.register(self.handle_start, Command("start"))
        self.dp.message.register(self.handle_5m_signal, Command("5m"))
        self.dp.message.register(self.handle_15m_signal, Command("15m"))
        self.dp.message.register(self.handle_pro_command, Command("pro"))
        self.dp.message.register(self.handle_symbol_selection, lambda msg: msg.text and msg.text.upper() in Config.DEFAULT_SYMBOLS)
    
    def setup_logger(self):
        logger = logging.getLogger("pocket_option_bot")
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
    
    async def handle_start(self, message: types.Message):
        # ایجاد صفحه کلید برای انتخاب نماد
        keyboard = types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton(symbol) for symbol in Config.DEFAULT_SYMBOLS[:3]],
                [types.KeyboardButton(symbol) for symbol in Config.DEFAULT_SYMBOLS[3:]],
                [types.KeyboardButton("🎯 سیگنال VIP")]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        
        await message.answer(
            "🤖 به ربات سیگنال‌دهی پیشرفته پاکت اپشن خوش آمدید!\n\n"
            "💎 ویژگی‌های اصلی:\n"
            "- سیگنال‌های لحظه‌ای 5 و 15 دقیقه‌ای\n"
            "- تحلیل تکنیکال حرفه‌ای\n"
            "- تحلیل احساسات بازار از اخبار و توییتر\n"
            "- پشتیبانی از نمادهای اصلی فارکس و ارز دیجیتال\n\n"
            "🔮 برای شروع، یک نماد را انتخاب کنید:",
            reply_markup=keyboard
        )
    
    async def handle_5m_signal(self, message: types.Message):
        user_id = message.from_user.id
        symbol = self.redis.get(f"user:{user_id}:symbol")
        
        if not symbol:
            await message.answer("⚠️ لطفاً ابتدا نماد را انتخاب کنید")
            return
            
        await self.generate_and_send_signal(message, symbol.decode(), "5m")
    
    async def handle_15m_signal(self, message: types.Message):
        user_id = message.from_user.id
        symbol = self.redis.get(f"user:{user_id}:symbol")
        
        if not symbol:
            await message.answer("⚠️ لطفاً ابتدا نماد را انتخاب کنید")
            return
            
        await self.generate_and_send_signal(message, symbol.decode(), "15m")
    
    async def handle_symbol_selection(self, message: types.Message):
        symbol = message.text.upper()
        user_id = message.from_user.id
        
        # ذخیره نماد انتخاب شده
        self.redis.setex(f"user:{user_id}:symbol", 3600, symbol)
        
        # ایجاد صفحه کلید برای انتخاب تایم‌فریم
        keyboard = types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton("5m"), types.KeyboardButton("15m")],
                [types.KeyboardButton("30m"), types.KeyboardButton("1h")],
                [types.KeyboardButton("🔙 تغییر نماد")]
            ],
            resize_keyboard=True
        )
        
        await message.answer(
            f"✅ نماد {symbol} انتخاب شد\n\n"
            "⏱ لطفاً تایم‌فریم مورد نظر را انتخاب کنید:",
            reply_markup=keyboard
        )
    
    async def handle_pro_command(self, message: types.Message):
        user_id = str(message.from_user.id)
        if user_id in Config.PRO_USERS:
            # سیگنال VIP برای کاربران Pro
            await self.generate_vip_signal(message)
        else:
            await message.answer(
                "🔒 برای دسترسی به سیگنال‌های VIP نسخه Pro لطفاً اشتراک تهیه کنید:\n"
                "🌐 https://your-website.com/pro-subscription\n\n"
                "💎 مزایای نسخه Pro:\n"
                "- سیگنال‌های لحظه‌ای VIP با دقت بالا\n"
                "- تحلیل چند نماد همزمان\n"
                "- پشتیبانی 24/7 اختصاصی\n"
                "- گزارش‌های تحلیلی روزانه"
            )
    
    async def generate_vip_signal(self, message: types.Message):
        """سیگنال VIP برای کاربران Pro"""
        await message.answer("🕒 در حال تولید سیگنال VIP...")
        
        # تحلیل چند نماد به صورت همزمان
        signals = []
        for symbol in Config.DEFAULT_SYMBOLS:
            signal = await self.generate_signal(symbol, "5m", vip=True)
            signals.append(f"📈 {symbol}:\n{signal}")
        
        # تحلیل بازار کلی
        market_analysis = await self.generate_market_analysis()
        
        # ارسال نتایج
        await message.answer("\n\n".join(signals))
        await message.answer(f"🌍 تحلیل کلی بازار:\n{market_analysis}")
    
    async def generate_and_send_signal(self, message: types.Message, symbol: str, timeframe: str):
        await message.answer(f"⏳ در حال تولید سیگنال {symbol} در تایم‌فریم {timeframe}...")
        
        # تولید سیگنال
        signal = await self.generate_signal(symbol, timeframe)
        
        # ارسال نتیجه
        await message.answer(signal)
    
    async def generate_signal(self, symbol: str, timeframe: str, vip: bool = False) -> str:
        try:
            # دریافت داده‌های بازار
            market_data = await MarketServices.get_realtime_data(symbol, timeframe)
            
            if not market_data:
                return "⚠️ خطا در دریافت داده‌های بازار"
            
            # تحلیل تکنیکال
            tech_analysis = TechnicalAnalysis.calculate_indicators(market_data)
            if not tech_analysis:
                return "⚠️ داده‌های کافی برای تحلیل تکنیکال موجود نیست"
            
            # تحلیل احساسات بازار
            sentiment = await self.sentiment_analyzer.get_market_sentiment(symbol)
            
            # تولید سیگنال
            signal, confidence = self.generate_signal_logic(tech_analysis, sentiment, vip)
            
            # اطلاعات قیمت
            last_price = list(market_data.values())[0]["4. close"]
            
            # اطلاعات زمانی
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            
            # فرمت‌بندی نتیجه
            result = (
                f"🚀 سیگنال {timeframe} - {symbol}\n"
                f"⏰ زمان: {timestamp}\n"
                f"💰 قیمت فعلی: {last_price}\n"
                f"📊 سیگنال: {signal} ({confidence}% اطمینان)\n\n"
                f"📈 اندیکاتورها:\n"
                f"- RSI: {tech_analysis['rsi']:.2f}\n"
                f"- MACD: {tech_analysis['macd']:.4f} | Signal: {tech_analysis['macd_signal']:.4f}\n"
                f"- Stochastic: K={tech_analysis['stoch_k']:.2f}, D={tech_analysis['stoch_d']:.2f}\n"
                f"- ADX: {tech_analysis['adx']:.2f}\n"
                f"🌐 احساسات بازار: {sentiment:.2f}"
            )
            
            return result
        except Exception as e:
            self.logger.error(f"Error in signal generation: {str(e)}")
            return "⚠️ خطا در تولید سیگنال. لطفاً دوباره امتحان کنید"
    
    def generate_signal_logic(self, tech: dict, sentiment: float, vip: bool = False) -> tuple:
        """منطق تولید سیگنال با محاسبه درصد اطمینان"""
        # محاسبه امتیازات
        rsi_score = 0
        if tech['rsi'] < 30:
            rsi_score = 1.0  # اشباع فروش قوی
        elif tech['rsi'] < 40:
            rsi_score = 0.7  # اشباع فروش
        elif tech['rsi'] > 70:
            rsi_score = -1.0  # اشباع خرید قوی
        elif tech['rsi'] > 60:
            rsi_score = -0.7  # اشباع خرید
        
        macd_score = 1.0 if tech['macd'] > tech['macd_signal'] else -1.0
        
        stoch_score = 0
        if tech['stoch_k'] < 20 and tech['stoch_d'] < 20:
            stoch_score = 1.0  # اشباع فروش
        elif tech['stoch_k'] > 80 and tech['stoch_d'] > 80:
            stoch_score = -1.0  # اشباع خرید
        
        adx_score = 0.5 if tech['adx'] > 25 else 0  # روند قوی
        
        sentiment_score = 1.0 if sentiment > 0.7 else -1.0 if sentiment < 0.3 else 0
        
        # محاسبه امتیاز نهایی
        total_score = (
            rsi_score * 0.3 +
            macd_score * 0.3 +
            stoch_score * 0.2 +
            adx_score * 0.1 +
            sentiment_score * 0.1
        )
        
        # محاسبه درصد اطمینان
        confidence = min(100, int(abs(total_score) * 100))
        
        # تصمیم‌گیری
        if vip:
            # منطق پیشرفته برای کاربران Pro
            if total_score > 0.7:
                return "خرید قوی 🟢", confidence
            elif total_score > 0.4:
                return "خرید متوسط 🟢", confidence
            elif total_score < -0.7:
                return "فروش قوی 🔴", confidence
            elif total_score < -0.4:
                return "فروش متوسط 🔴", confidence
        else:
            # منطق استاندارد
            if total_score > 0.5:
                return "خرید 🟢", confidence
            elif total_score < -0.5:
                return "فروش 🔴", confidence
        
        return "بدون سیگنال واضح ⚪️", confidence
    
    async def generate_market_analysis(self) -> str:
        """تحلیل کلی بازار برای کاربران VIP"""
        analysis = []
        for symbol in Config.DEFAULT_SYMBOLS:
            sentiment = await self.sentiment_analyzer.get_market_sentiment(symbol)
            analysis.append(f"📊 {symbol}: احساسات {sentiment:.2f} ({'صعودی' if sentiment > 0.6 else 'نزولی' if sentiment < 0.4 else 'خنثی'})")
        
        return "\n".join(analysis)

# --------------------- اجرای ربات ---------------------
async def main():
    bot = PocketOptionSignalBot()
    await bot.dp.start_polling(bot.bot)

if __name__ == "__main__":
    asyncio.run(main())