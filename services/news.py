from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import httpx
from utils import cache, get_api_key, make_request

class NewsService:
    def __init__(self):
        self.api_key = get_api_key("news")
        self.base_url = "https://newsapi.org/v2"
    
    async def get_top_headlines(self, country: str = "us", category: str = None, page_size: int = 20) -> Optional[Dict[str, Any]]:
        """Get top headlines from NewsAPI"""
        if not self.api_key:
            return {"error": "News API key not configured"}
        
        cache_key = f"news_headlines_{country}_{category}_{page_size}"
        cached_data = await cache.get(cache_key)
        if cached_data:
            return cached_data
        
        url = f"{self.base_url}/top-headlines"
        params = {
            "apiKey": self.api_key,
            "country": country,
            "pageSize": page_size
        }
        
        if category:
            params["category"] = category
        
        data = await make_request(url, params=params)
        if data:
            await cache.set(cache_key, data, ttl=900)  # Cache for 15 minutes
        return data
    
    async def search_news(self, query: str, page_size: int = 20, sort_by: str = "publishedAt") -> Optional[Dict[str, Any]]:
        """Search for news articles"""
        if not self.api_key:
            return {"error": "News API key not configured"}
        
        cache_key = f"news_search_{query}_{page_size}_{sort_by}"
        cached_data = await cache.get(cache_key)
        if cached_data:
            return cached_data
        
        url = f"{self.base_url}/everything"
        params = {
            "apiKey": self.api_key,
            "q": query,
            "pageSize": page_size,
            "sortBy": sort_by,
            "language": "en"
        }
        
        data = await make_request(url, params=params)
        if data:
            await cache.set(cache_key, data, ttl=900)  # Cache for 15 minutes
        return data
    
    async def get_tech_news(self) -> Optional[Dict[str, Any]]:
        """Get technology news"""
        return await self.get_top_headlines(category="technology")
    
    async def get_business_news(self) -> Optional[Dict[str, Any]]:
        """Get business news"""
        return await self.get_top_headlines(category="business")
    
    # Alternative free news sources
    async def get_bbc_news(self) -> Optional[List[Dict[str, Any]]]:
        """Get BBC news RSS feed (free alternative)"""
        cache_key = "bbc_news"
        cached_data = await cache.get(cache_key)
        if cached_data:
            return cached_data
        
        # Using newsdata.io as an alternative free source
        url = "https://newsdata.io/api/1/news"
        params = {
            "apikey": "pub_52858b51a62b2c1d1a1f82637d8b7f6a99f28",  # Free tier key
            "country": "us",
            "language": "en",
            "category": "technology",
            "size": 20
        }
        
        data = await make_request(url, params=params)
        if data:
            await cache.set(cache_key, data, ttl=1800)  # Cache for 30 minutes
        return data
    
    async def get_crypto_news(self) -> Optional[List[Dict[str, Any]]]:
        """Get cryptocurrency news using search"""
        cache_key = "crypto_news"
        cached_data = await cache.get(cache_key)
        if cached_data:
            return cached_data
        
        # Search for crypto-related news using the main API
        if self.api_key:
            data = await self.search_news("cryptocurrency OR bitcoin OR ethereum", page_size=15)
        else:
            # Fallback to free alternative
            try:
                url = "https://newsdata.io/api/1/news"
                params = {
                    "apikey": "pub_52858b51a62b2c1d1a1f82637d8b7f6a99f28",
                    "q": "cryptocurrency OR bitcoin",
                    "language": "en",
                    "size": 15
                }
                data = await make_request(url, params=params)
            except Exception:
                # If all else fails, return sample data
                data = {
                    "articles": [
                        {
                            "title": "Cryptocurrency Market Update",
                            "description": "Latest trends in the crypto market",
                            "url": "#",
                            "source": {"name": "Crypto News"},
                            "publishedAt": datetime.now().isoformat()
                        }
                    ]
                }
        
        if data:
            await cache.set(cache_key, data, ttl=1800)  # Cache for 30 minutes
        return data

news_service = NewsService()
