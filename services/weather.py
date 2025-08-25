from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import httpx
from utils import cache, get_api_key, make_request

class WeatherService:
    def __init__(self):
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.api_key = get_api_key("openweather")
    
    async def get_current_weather(self, city: str) -> Optional[Dict[str, Any]]:
        """Get current weather for a city"""
        if not self.api_key:
            return {"error": "OpenWeather API key not configured"}
        
        cache_key = f"current_weather_{city.lower()}"
        cached_data = await cache.get(cache_key)
        if cached_data:
            return cached_data
        
        url = f"{self.base_url}/weather"
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric"
        }
        
        data = await make_request(url, params=params)
        if data:
            await cache.set(cache_key, data, ttl=600)  # Cache for 10 minutes
        return data
    
    async def get_weather_forecast(self, city: str, days: int = 5) -> Optional[Dict[str, Any]]:
        """Get weather forecast for a city"""
        if not self.api_key:
            return {"error": "OpenWeather API key not configured"}
        
        cache_key = f"weather_forecast_{city.lower()}_{days}"
        cached_data = await cache.get(cache_key)
        if cached_data:
            return cached_data
        
        url = f"{self.base_url}/forecast"
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric",
            "cnt": days * 8  # 8 forecasts per day (every 3 hours)
        }
        
        data = await make_request(url, params=params)
        if data:
            await cache.set(cache_key, data, ttl=1800)  # Cache for 30 minutes
        return data
    
    async def get_weather_by_coordinates(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        """Get current weather by coordinates"""
        if not self.api_key:
            return {"error": "OpenWeather API key not configured"}
        
        cache_key = f"weather_coords_{lat}_{lon}"
        cached_data = await cache.get(cache_key)
        if cached_data:
            return cached_data
        
        url = f"{self.base_url}/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "metric"
        }
        
        data = await make_request(url, params=params)
        if data:
            await cache.set(cache_key, data, ttl=600)  # Cache for 10 minutes
        return data

weather_service = WeatherService()
