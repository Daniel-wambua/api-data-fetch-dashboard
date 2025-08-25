from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import httpx
from utils import cache, get_api_key, make_request

class CryptoService:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.api_key = get_api_key("coingecko")
        
    def _get_headers(self) -> Dict[str, str]:
        headers = {"accept": "application/json"}
        if self.api_key:
            headers["x-cg-demo-api-key"] = self.api_key
        return headers
    
    async def get_crypto_prices(self, coins: List[str] = None) -> Optional[Dict[str, Any]]:
        """Get current crypto prices for specified coins"""
        if coins is None:
            coins = ["bitcoin", "ethereum", "binancecoin", "cardano", "solana"]
        
        cache_key = f"crypto_prices_{','.join(coins)}"
        cached_data = await cache.get(cache_key)
        if cached_data:
            return cached_data
        
        coins_str = ",".join(coins)
        url = f"{self.base_url}/simple/price"
        params = {
            "ids": coins_str,
            "vs_currencies": "usd",
            "include_24hr_change": "true",
            "include_24hr_vol": "true",
            "include_market_cap": "true"
        }
        
        data = await make_request(url, headers=self._get_headers(), params=params)
        if data:
            await cache.set(cache_key, data, ttl=60)  # Cache for 1 minute
        return data
    
    async def get_crypto_history(self, coin_id: str = "bitcoin", days: int = 7) -> Optional[Dict[str, Any]]:
        """Get historical price data for a coin"""
        cache_key = f"crypto_history_{coin_id}_{days}"
        cached_data = await cache.get(cache_key)
        if cached_data:
            return cached_data
        
        url = f"{self.base_url}/coins/{coin_id}/market_chart"
        params = {
            "vs_currency": "usd",
            "days": str(days),
            "interval": "hourly" if days <= 1 else "daily"
        }
        
        data = await make_request(url, headers=self._get_headers(), params=params)
        if data:
            await cache.set(cache_key, data, ttl=300)  # Cache for 5 minutes
        return data
    
    async def get_trending_coins(self) -> Optional[Dict[str, Any]]:
        """Get trending cryptocurrencies"""
        cache_key = "trending_coins"
        cached_data = await cache.get(cache_key)
        if cached_data:
            return cached_data
        
        url = f"{self.base_url}/search/trending"
        data = await make_request(url, headers=self._get_headers())
        if data:
            await cache.set(cache_key, data, ttl=600)  # Cache for 10 minutes
        return data
    
    async def get_global_market_data(self) -> Optional[Dict[str, Any]]:
        """Get global cryptocurrency market data"""
        cache_key = "global_market_data"
        cached_data = await cache.get(cache_key)
        if cached_data:
            return cached_data
        
        url = f"{self.base_url}/global"
        data = await make_request(url, headers=self._get_headers())
        if data:
            await cache.set(cache_key, data, ttl=300)  # Cache for 5 minutes
        return data

crypto_service = CryptoService()
