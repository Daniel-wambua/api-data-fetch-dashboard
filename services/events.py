from typing import Dict, List, Optional, Any
from datetime import datetime
import httpx
import os
from utils import cache, get_api_key, make_request

class EventsService:
    def __init__(self):
        self.api_key = get_api_key("logsnag")
        self.project = os.getenv("LOGSNAG_PROJECT", "api-dashboard")
        self.base_url = "https://api.logsnag.com/v1"
        self.events = []  # In-memory storage for demo
    
    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}" if self.api_key else ""
        }
        return headers
    
    async def log_event(self, event: str, description: str, icon: str = "📊", notify: bool = False) -> bool:
        """Log an event to LogSnag"""
        if not self.api_key:
            # Store locally if no API key
            self.events.append({
                "event": event,
                "description": description,
                "icon": icon,
                "timestamp": datetime.now().isoformat(),
                "channel": "dashboard"
            })
            return True
        
        url = f"{self.base_url}/log"
        payload = {
            "project": self.project,
            "channel": "dashboard",
            "event": event,
            "description": description,
            "icon": icon,
            "notify": notify
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=self._get_headers())
                return response.status_code == 200
        except Exception as e:
            print(f"Failed to log event: {e}")
            # Store locally as fallback
            self.events.append({
                "event": event,
                "description": description,
                "icon": icon,
                "timestamp": datetime.now().isoformat(),
                "channel": "dashboard"
            })
            return False
    
    async def get_recent_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent events"""
        cache_key = f"recent_events_{limit}"
        cached_data = await cache.get(cache_key)
        if cached_data:
            return cached_data
        
        if not self.api_key:
            # Return local events if no API key
            return self.events[-limit:] if self.events else []
        
        # For demo purposes, return local events + some sample events
        sample_events = [
            {
                "event": "Dashboard Started",
                "description": "API Dashboard application initialized",
                "icon": "🚀",
                "timestamp": datetime.now().isoformat(),
                "channel": "dashboard"
            },
            {
                "event": "Crypto Data Fetched",
                "description": "Successfully retrieved cryptocurrency prices",
                "icon": "₿",
                "timestamp": datetime.now().isoformat(),
                "channel": "dashboard"
            },
            {
                "event": "Weather Updated",
                "description": "Weather information refreshed",
                "icon": "🌤️",
                "timestamp": datetime.now().isoformat(),
                "channel": "dashboard"
            }
        ]
        
        all_events = sample_events + self.events
        events = all_events[-limit:] if all_events else []
        
        await cache.set(cache_key, events, ttl=60)  # Cache for 1 minute
        return events
    
    async def log_dashboard_view(self, page: str):
        """Log dashboard page view"""
        await self.log_event(
            event="Page View",
            description=f"User viewed {page} dashboard",
            icon="👀"
        )
    
    async def log_api_call(self, service: str, endpoint: str, success: bool):
        """Log API call"""
        icon = "✅" if success else "❌"
        status = "successful" if success else "failed"
        await self.log_event(
            event="API Call",
            description=f"{service} {endpoint} call {status}",
            icon=icon
        )
    
    async def log_error(self, error: str, context: str = ""):
        """Log error event"""
        await self.log_event(
            event="Error",
            description=f"Error in {context}: {error}" if context else f"Error: {error}",
            icon="🚨",
            notify=True
        )

events_service = EventsService()
