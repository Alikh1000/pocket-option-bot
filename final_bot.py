#!/usr/bin/env python3
"""
Final Production Bot with Real Token
Runs the demo bot continuously until stopped
"""

import asyncio
import logging
from demo_bot import DemoPocketOptionBot

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def run_production_bot():
    """Run the bot in production mode"""
    token = "8213340388:AAFAFfx2b2NgMLjsZtAdbWkrAE7GYeTc12A"
    
    try:
        print("🚀 راه‌اندازی ربات پاکت اپشن...")
        print("📱 نام ربات: @Pilotcar_bot")
        print("📞 در تلگرام پیام /start را به ربات ارسال کنید")
        print("⏹️  برای توقف ربات Ctrl+C را فشار دهید")
        print("=" * 60)
        
        bot = DemoPocketOptionBot(token)
        
        # Start polling
        await bot.dp.start_polling(bot.bot)
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        print("\n⏹️  ربات توسط کاربر متوقف شد")
    except Exception as e:
        logger.error(f"Bot error: {str(e)}")
        print(f"❌ خطا در اجرای ربات: {str(e)}")
    finally:
        try:
            await bot.bot.session.close()
        except:
            pass
        print("👋 ربات متوقف شد")

def main():
    """Main function"""
    print("🤖 Pocket Option Signal Bot")
    print("نسخه نمایشی با داده‌های تصادفی")
    print("=" * 40)
    
    try:
        asyncio.run(run_production_bot())
    except KeyboardInterrupt:
        print("\n👋 خروج...")
    except Exception as e:
        print(f"❌ خطای سیستم: {str(e)}")

if __name__ == "__main__":
    main()