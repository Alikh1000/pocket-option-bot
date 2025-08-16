#!/usr/bin/env python3
"""
Start script for Pocket Option Signal Bot
This script checks configuration and starts the bot
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_api_keys():
    """Check if all required API keys are configured"""
    required_keys = {
        'TELEGRAM_TOKEN': 'Telegram Bot Token',
        'ALPHA_VANTAGE_KEY': 'Alpha Vantage API Key', 
        'NEWS_API_KEY': 'News API Key',
        'TWITTER_BEARER_TOKEN': 'Twitter Bearer Token'
    }
    
    missing_keys = []
    
    print("🔑 Checking API Keys...")
    for key, description in required_keys.items():
        value = os.getenv(key)
        if not value or value.startswith('YOUR_'):
            missing_keys.append((key, description))
            print(f"❌ {description}: Not configured")
        else:
            print(f"✅ {description}: Configured")
    
    if missing_keys:
        print("\n⚠️  Missing API Keys:")
        for key, desc in missing_keys:
            print(f"   {key} - {desc}")
        
        print("\n📋 How to get API keys:")
        print("1. Telegram Bot Token:")
        print("   - Message @BotFather on Telegram")
        print("   - Send /newbot and follow instructions")
        print("   - Copy the token provided")
        print()
        print("2. Alpha Vantage API Key:")
        print("   - Go to https://www.alphavantage.co/support/#api-key")
        print("   - Fill out the form for free API key")
        print("   - Use the key provided")
        print()
        print("3. News API Key:")
        print("   - Go to https://newsapi.org/register")
        print("   - Register for free account")
        print("   - Copy your API key from dashboard")
        print()
        print("4. Twitter Bearer Token:")
        print("   - Go to https://developer.twitter.com")
        print("   - Apply for developer account")
        print("   - Create an app and get Bearer Token")
        print()
        print("🔧 Update the .env file with your keys and try again.")
        return False
    
    print("✅ All API keys configured!")
    return True

def check_redis():
    """Check if Redis is running"""
    print("🔴 Checking Redis connection...")
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✅ Redis: Connected")
        return True
    except Exception as e:
        print(f"❌ Redis: Connection failed - {str(e)}")
        print("   Please start Redis server: redis-server --daemonize yes")
        return False

async def start_bot():
    """Start the telegram bot"""
    try:
        from telegram_bot import PocketOptionSignalBot
        print("🤖 Starting Pocket Option Signal Bot...")
        bot = PocketOptionSignalBot()
        await bot.dp.start_polling(bot.bot)
    except KeyboardInterrupt:
        print("\n⏹️  Bot stopped by user")
    except Exception as e:
        print(f"❌ Bot error: {str(e)}")
        return False
    
    return True

async def main():
    """Main function"""
    print("🚀 Pocket Option Signal Bot Launcher")
    print("=" * 50)
    
    # Check prerequisites
    if not check_api_keys():
        return False
    
    if not check_redis():
        return False
    
    print("\n🎯 All checks passed! Starting bot...")
    print("Press Ctrl+C to stop the bot")
    print("=" * 50)
    
    await start_bot()
    return True

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Startup error: {str(e)}")
        sys.exit(1)