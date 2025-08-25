from typing import Dict, Optional, Any
import httpx
from utils import cache, get_api_key, make_request, validate_ip

class IPInfoService:
    def __init__(self):
        self.base_url = "https://ipinfo.io"
        self.api_key = get_api_key("ipinfo")
    
    def _get_headers(self) -> Dict[str, str]:
        headers = {"accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    async def get_ip_info(self, ip: str = None) -> Optional[Dict[str, Any]]:
        """Get IP information. If no IP provided, gets info for current IP"""
        if ip and not validate_ip(ip):
            return {"error": "Invalid IP address format"}
        
        cache_key = f"ip_info_{ip or 'current'}"
        cached_data = await cache.get(cache_key)
        if cached_data:
            return cached_data
        
        url = f"{self.base_url}/{ip}" if ip else f"{self.base_url}/json"
        
        data = await make_request(url, headers=self._get_headers())
        if data:
            await cache.set(cache_key, data, ttl=3600)  # Cache for 1 hour
        return data
    
    async def get_current_ip_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the current public IP"""
        return await self.get_ip_info()
    
    async def get_bulk_ip_info(self, ips: list) -> Optional[Dict[str, Any]]:
        """Get information for multiple IPs (requires paid plan)"""
        if not self.api_key:
            return {"error": "IPInfo API key required for bulk requests"}
        
        valid_ips = [ip for ip in ips if validate_ip(ip)]
        if not valid_ips:
            return {"error": "No valid IP addresses provided"}
        
        cache_key = f"bulk_ip_info_{hash(str(sorted(valid_ips)))}"
        cached_data = await cache.get(cache_key)
        if cached_data:
            return cached_data
        
        # For bulk requests, we'll make individual requests for demo
        results = {}
        for ip in valid_ips[:5]:  # Limit to 5 IPs
            info = await self.get_ip_info(ip)
            if info and "error" not in info:
                results[ip] = info
        
        if results:
            await cache.set(cache_key, results, ttl=3600)
        return results

ipinfo_service = IPInfoService()
