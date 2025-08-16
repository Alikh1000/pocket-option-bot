#!/usr/bin/env python3
"""
Test script for Pocket Option Signal Bot
This script tests the core functionality without requiring actual API keys
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram_bot import TechnicalAnalysis, Config, ManualIndicators
import numpy as np

def test_technical_indicators():
    """Test manual technical indicators"""
    print("🔧 Testing Technical Indicators...")
    
    # Sample price data (mock EURUSD data)
    sample_data = {
        f"2024-01-{i:02d} 10:00:00": {
            "1. open": f"{1.08 + np.random.normal(0, 0.002):.5f}",
            "2. high": f"{1.08 + np.random.normal(0.001, 0.002):.5f}", 
            "3. low": f"{1.08 + np.random.normal(-0.001, 0.002):.5f}",
            "4. close": f"{1.08 + np.random.normal(0, 0.002):.5f}",
            "5. volume": "1000"
        } for i in range(1, 31)  # 30 days of data
    }
    
    try:
        indicators = TechnicalAnalysis.calculate_indicators(sample_data)
        if indicators:
            print("✅ Technical Analysis Working!")
            print(f"   RSI: {indicators['rsi']:.2f}")
            print(f"   MACD: {indicators['macd']:.4f}")
            print(f"   MACD Signal: {indicators['macd_signal']:.4f}")
            print(f"   Stochastic K: {indicators['stoch_k']:.2f}")
            print(f"   Stochastic D: {indicators['stoch_d']:.2f}")
            print(f"   ADX: {indicators['adx']:.2f}")
            return True
        else:
            print("❌ Technical Analysis returned None")
            return False
    except Exception as e:
        print(f"❌ Technical Analysis Error: {str(e)}")
        return False

def test_config():
    """Test configuration"""
    print("⚙️  Testing Configuration...")
    
    try:
        print(f"   Default Symbols: {Config.DEFAULT_SYMBOLS}")
        print(f"   Supported Timeframes: {Config.SUPPORTED_TIMEFRAMES}")
        print(f"   RSI Period: {Config.RSI_PERIOD}")
        print("✅ Configuration OK!")
        return True
    except Exception as e:
        print(f"❌ Configuration Error: {str(e)}")
        return False

def test_manual_indicators():
    """Test individual manual indicators"""
    print("📊 Testing Manual Indicators...")
    
    # Sample price data
    prices = [1.08, 1.082, 1.081, 1.083, 1.085, 1.084, 1.086, 1.087, 1.085, 1.088] * 5
    high = [p + 0.001 for p in prices]
    low = [p - 0.001 for p in prices]
    
    try:
        rsi = ManualIndicators.rsi(prices, 14)
        macd, signal, hist = ManualIndicators.macd(prices, 12, 26, 9)
        stoch_k, stoch_d = ManualIndicators.stochastic(high, low, prices, 14, 3)
        adx = ManualIndicators.adx(high, low, prices, 14)
        
        print(f"✅ RSI: {rsi:.2f}")
        print(f"✅ MACD: {macd:.4f}, Signal: {signal:.4f}")
        print(f"✅ Stochastic: K={stoch_k:.2f}, D={stoch_d:.2f}")
        print(f"✅ ADX: {adx:.2f}")
        return True
    except Exception as e:
        print(f"❌ Manual Indicators Error: {str(e)}")
        return False

def test_dependencies():
    """Test if all required packages are installed"""
    print("📦 Testing Dependencies...")
    
    dependencies = [
        ('aiogram', 'aiogram'),
        ('transformers', 'transformers'),
        ('aiohttp', 'aiohttp'),
        ('redis', 'redis'),
        ('numpy', 'numpy')
    ]
    
    all_ok = True
    for name, module in dependencies:
        try:
            __import__(module)
            print(f"✅ {name}: OK")
        except ImportError as e:
            print(f"❌ {name}: Missing - {str(e)}")
            all_ok = False
    
    return all_ok

async def main():
    """Main test function"""
    print("🤖 Pocket Option Signal Bot - Test Suite")
    print("=" * 50)
    
    tests = [
        ("Dependencies", test_dependencies()),
        ("Configuration", test_config()),
        ("Manual Indicators", test_manual_indicators()),
        ("Technical Analysis", test_technical_indicators())
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, result in tests:
        if result:
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Bot is ready for API keys.")
        print("\n📋 Next Steps:")
        print("1. Get Telegram Bot Token from @BotFather")
        print("2. Get Alpha Vantage API key from alphavantage.co")
        print("3. Get News API key from newsapi.org")
        print("4. Get Twitter Bearer Token from developer.twitter.com")
        print("5. Update .env file with your API keys")
        print("6. Run: python telegram_bot.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(main())