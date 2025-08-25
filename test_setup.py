#!/usr/bin/env python3
"""
Simple test script to verify the API Dashboard setup
"""
import sys
import os
import asyncio
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_services():
    """Test all services without requiring API keys"""
    print("🧪 Testing API Dashboard Services...")
    print("=" * 50)
    
    try:
        # Test imports
        print("📦 Testing imports...")
        from services.crypto import crypto_service
        from services.weather import weather_service
        from services.ipinfo import ipinfo_service
        from services.trends import trends_service
        from services.news import news_service
        from services.events import events_service
        from utils.cache import cache
        print("✅ All imports successful")
        
        # Test cache
        print("\n💾 Testing cache system...")
        await cache.set("test_key", {"test": "data"})
        result = await cache.get("test_key")
        assert result == {"test": "data"}
        print("✅ Cache system working")
        
        # Test crypto service (no API key required)
        print("\n₿ Testing crypto service...")
        crypto_data = await crypto_service.get_crypto_prices(["bitcoin"])
        if crypto_data:
            print("✅ Crypto service working")
        else:
            print("⚠️ Crypto service returned no data (this is normal)")
        
        # Test trends service (Hacker News - no API key required)
        print("\n📈 Testing trends service...")
        hn_data = await trends_service.get_hacker_news_top(5)
        if hn_data:
            print("✅ Hacker News API working")
        else:
            print("⚠️ Hacker News API returned no data")
        
        # Test events service
        print("\n📊 Testing events service...")
        await events_service.log_event("Test Event", "Testing the events system", "🧪")
        recent_events = await events_service.get_recent_events(10)
        if recent_events:
            print("✅ Events service working")
        else:
            print("⚠️ Events service returned no data")
        
        print("\n" + "=" * 50)
        print("✅ All basic tests passed!")
        print("\n💡 Tips:")
        print("   - Add API keys to .env file for full functionality")
        print("   - Run 'python app.py' to start the FastAPI backend")
        print("   - Run 'streamlit run dashboard.py' to start the frontend")
        print("   - Or use './start.sh' to start both services")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Try installing dependencies: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    return True

def check_environment():
    """Check if environment is properly set up"""
    print("🔍 Checking environment...")
    
    # Check if .env exists
    env_file = project_root / ".env"
    if env_file.exists():
        print("✅ .env file found")
    else:
        print("⚠️ .env file not found (copy from .env.example)")
    
    # Check if requirements can be imported
    try:
        import httpx
        import pandas
        import plotly
        print("✅ Core dependencies available")
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("💡 Install with: pip install -r requirements.txt")
        return False
    
    return True

async def main():
    """Main test function"""
    print("🚀 API Data Dashboard - Setup Test")
    print("=" * 50)
    
    # Check environment
    if not check_environment():
        print("\n❌ Environment check failed")
        return
    
    # Test services
    if await test_services():
        print("\n🎉 Setup test completed successfully!")
        print("📊 Your API Dashboard is ready to use!")
    else:
        print("\n❌ Some tests failed")

if __name__ == "__main__":
    asyncio.run(main())
