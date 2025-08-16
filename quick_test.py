#!/usr/bin/env python3
import asyncio
from aiogram import Bot

async def test_bot_token():
    """Test if the bot token is valid"""
    token = "8213340388:AAFAFfx2b2NgMLjsZtAdbWkrAE7GYeTc12A"
    
    try:
        bot = Bot(token=token)
        me = await bot.get_me()
        print(f"✅ Bot token valid!")
        print(f"🤖 Bot name: {me.first_name}")
        print(f"👤 Username: @{me.username}")
        print(f"🆔 Bot ID: {me.id}")
        await bot.session.close()
        return True
    except Exception as e:
        print(f"❌ Bot token error: {str(e)}")
        await bot.session.close() if 'bot' in locals() else None
        return False

if __name__ == "__main__":
    result = asyncio.run(test_bot_token())
    if result:
        print("\n🚀 ربات آماده اجرا است!")
    else:
        print("\n❌ مشکل در توکن ربات")