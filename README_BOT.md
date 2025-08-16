# 🤖 Pocket Option Signal Bot

ربات تلگرام پیشرفته برای ارائه سیگنال‌های معاملاتی پاکت اپشن با تحلیل تکنیکال و احساسات بازار.

## ✨ ویژگی‌ها

### 🎯 سیگنال‌دهی هوشمند
- سیگنال‌های لحظه‌ای 5، 15، 30 دقیقه و 1 ساعته
- تحلیل تکنیکال کامل با اندیکاتورهای RSI، MACD، استوکاستیک و ADX
- تحلیل احساسات بازار از اخبار مالی و شبکه‌های اجتماعی
- محاسبه درصد اطمینان برای هر سیگنال

### 📊 نمادهای پشتیبانی شده
- **فارکس**: EURUSD، GBPUSD، USDJPY
- **فلزات گرانبها**: XAUUSD (طلا)
- **ارز دیجیتال**: BTCUSD

### 🌟 ویژگی‌های ویژه
- رابط کاربری فارسی و کاربرپسند
- سیستم کاربران VIP با سیگنال‌های پیشرفته
- تحلیل چند نماد همزمان برای کاربران Pro
- ذخیره‌سازی تنظیمات کاربران در Redis

## 🚀 نصب و راه‌اندازی

### پیش‌نیازها
```bash
# نصب Redis
sudo apt install redis-server
redis-server --daemonize yes

# نصب کتابخانه‌های Python
pip install -r bot_requirements.txt
```

### دریافت کلیدهای API

#### 1️⃣ توکن ربات تلگرام
1. به [@BotFather](https://t.me/BotFather) پیام دهید
2. دستور `/newbot` را ارسال کنید
3. نام و نام کاربری ربات را وارد کنید
4. توکن ارائه شده را کپی کنید

#### 2️⃣ کلید Alpha Vantage (داده‌های بازار)
1. به [Alpha Vantage](https://www.alphavantage.co/support/#api-key) بروید
2. فرم درخواست کلید رایگان را پر کنید
3. کلید API را کپی کنید

#### 3️⃣ کلید News API (تحلیل احساسات اخبار)
1. در [NewsAPI](https://newsapi.org/register) ثبت نام کنید
2. کلید API از داشبورد کپی کنید

#### 4️⃣ توکن Twitter (تحلیل احساسات اجتماعی)
1. حساب توسعه‌دهنده در [Twitter Developer](https://developer.twitter.com) بسازید
2. یک اپلیکیشن جدید ایجاد کنید
3. Bearer Token را کپی کنید

### تنظیمات
کلیدهای API را در فایل `.env` وارد کنید:

```bash
# Telegram Bot Configuration
TELEGRAM_TOKEN=1234567890:ABCdefGhIjKlMnOpQrStUvWxYz

# Market Data APIs  
ALPHA_VANTAGE_KEY=YOUR_ALPHA_VANTAGE_KEY
NEWS_API_KEY=YOUR_NEWS_API_KEY
TWITTER_BEARER_TOKEN=YOUR_TWITTER_BEARER_TOKEN

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Pro Users (لیست ID کاربران VIP)
PRO_USERS=["123456789", "987654321"]
```

## 🏃‍♂️ اجرای ربات

### تست ربات
```bash
python test_bot.py
```

### اجرای ربات
```bash
python start_bot.py
```

## 📱 نحوه استفاده

### دستورات اصلی
- `/start` - شروع و انتخاب نماد
- `/5m` - سیگنال 5 دقیقه‌ای
- `/15m` - سیگنال 15 دقیقه‌ای
- `/pro` - سیگنال‌های VIP (فقط کاربران Pro)

### جریان کاری
1. کاربر `/start` را ارسال می‌کند
2. نماد مورد نظر را انتخاب می‌کند
3. تایم‌فریم را انتخاب می‌کند
4. سیگنال با جزئیات کامل دریافت می‌کند

## 📊 نمونه خروجی سیگنال

```
🚀 سیگنال 5m - EURUSD
⏰ زمان: 14:30:25
💰 قیمت فعلی: 1.08450
📊 سیگنال: خرید 🟢 (78% اطمینان)

📈 اندیکاتورها:
- RSI: 45.32
- MACD: 0.0012 | Signal: 0.0008
- Stochastic: K=34.56, D=41.23
- ADX: 28.45
🌐 احساسات بازار: 0.67
```

## ⚙️ تنظیمات پیشرفته

### اضافه کردن کاربران VIP
فایل `.env` را ویرایش کنید:
```bash
PRO_USERS=["USER_ID_1", "USER_ID_2", "USER_ID_3"]
```

### تغییر نمادهای پشتیبانی شده
فایل `telegram_bot.py` را ویرایش کنید:
```python
DEFAULT_SYMBOLS = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "BTCUSD", "SYMBOL_جدید"]
```

### تنظیم اندیکاتورها
```python
RSI_PERIOD = 14      # دوره RSI
MACD_FAST = 12       # EMA سریع MACD
MACD_SLOW = 26       # EMA کند MACD
MACD_SIGNAL = 9      # خط سیگنال MACD
```

## 🛠️ عیب‌یابی

### مشکلات رایج

#### Redis اتصال برقرار نمی‌کند
```bash
redis-server --daemonize yes
redis-cli ping  # باید PONG برگردد
```

#### خطا در مدل‌های Transformers
```bash
# حافظه کافی وجود ندارد
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128
```

#### خطا در API های خارجی
- کلیدهای API را بررسی کنید
- محدودیت‌های نرخ درخواست را چک کنید
- اتصال اینترنت را بررسی کنید

## 📋 فایل‌های پروژه

```
/app/
├── telegram_bot.py          # کد اصلی ربات
├── start_bot.py            # اسکریپت اجرای ربات
├── test_bot.py             # تست‌های ربات
├── bot_requirements.txt    # کتابخانه‌های مورد نیاز
├── .env                    # تنظیمات محیطی
└── README_BOT.md          # مستندات
```

## 🤝 مشارکت

برای اضافه کردن ویژگی‌های جدید یا بهبود عملکرد:

1. کد را Fork کنید
2. تغییرات را اعمال کنید  
3. تست‌ها را اجرا کنید
4. Pull Request ایجاد کنید

## ⚠️ اخطارها

- **مسئولیت**: این ربات صرفاً جهت اطلاع‌رسانی است و مسئولیت سود و زیان با شما است
- **محدودیت API**: کلیدهای رایگان محدودیت درخواست دارند
- **امنیت**: هرگز کلیدهای API را به اشتراک نگذارید

## 📞 پشتیبانی

برای سوالات و پشتیبانی:
- GitHub Issues
- تلگرام: [لینک پشتیبانی]

---
**نوت**: این ربات برای اهداف آموزشی و اطلاع‌رسانی طراحی شده است. 📈