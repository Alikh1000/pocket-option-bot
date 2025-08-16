#!/usr/bin/env python3
"""
Quick demo runner for the Pocket Option Bot
"""

import asyncio
import signal
import sys
from demo_bot import DemoPocketOptionBot

class BotRunner:
    def __init__(self):
        self.bot = None
        self.running = False
    
    async def start_demo(self):
        """Start the demo bot"""
        token = "8213340388:AAFAFfx2b2NgMLjsZtAdbWkrAE7GYeTc12A"
        
        try:
            print("🚀 شروع ربات نمایشی پاکت اپشن...")
            print("📱 نام ربات: @Pilotcar_bot")
            print("⏱️  ربات برای 30 ثانیه اجرا خواهد شد...")
            print("📞 در تلگرام پیام /start را به ربات بفرستید")
            print("-" * 50)
            
            self.bot = DemoPocketOptionBot(token)
            self.running = True
            
            # Run bot for 30 seconds
            task = asyncio.create_task(self.bot.dp.start_polling(self.bot.bot))
            
            # Wait for 30 seconds or user interruption
            try:
                await asyncio.wait_for(task, timeout=30.0)
            except asyncio.TimeoutError:
                print("\n⏰ زمان نمایش به پایان رسید")
            except KeyboardInterrupt:
                print("\n⏹️  ربات توسط کاربر متوقف شد")
            
        except Exception as e:
            print(f"❌ خطا در اجرای ربات: {str(e)}")
        finally:
            if self.bot:
                await self.bot.bot.session.close()
            self.running = False
            print("👋 ربات نمایشی متوقف شد")

async def main():
    runner = BotRunner()
    await runner.start_demo()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 خروج...")
    except Exception as e:
        print(f"❌ خطا: {str(e)}")