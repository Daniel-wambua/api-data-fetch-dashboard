import os
from datetime import datetime
from typing import Any, Dict, Optional
import httpx

def get_api_key(service: str) -> Optional[str]:
    """Get API key for a service from environment"""
    key_map = {
        "coingecko": "COINGECKO_API_KEY",
        "openweather": "OPENWEATHER_API_KEY", 
        "ipinfo": "IPINFO_API_KEY",
        "news": "NEWS_API_KEY",
        "github": "GITHUB_TOKEN",
        "logsnag": "LOGSNAG_API_KEY"
    }
    return os.getenv(key_map.get(service))

def format_currency(amount: float, currency: str = "USD") -> str:
    """Format currency with proper symbols"""
    if currency == "USD":
        return f"${amount:,.2f}"
    elif currency == "EUR":
        return f"€{amount:,.2f}"
    elif currency == "GBP":
        return f"£{amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"

def format_percentage(value: float) -> str:
    """Format percentage with proper sign and color indication"""
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.2f}%"

def validate_ip(ip: str) -> bool:
    """Basic IP address validation"""
    parts = ip.split('.')
    if len(parts) != 4:
        return False
    try:
        for part in parts:
            if not 0 <= int(part) <= 255:
                return False
        return True
    except ValueError:
        return False

async def make_request(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    timeout: int = 30
) -> Optional[Dict[str, Any]]:
    """Make HTTP request with error handling"""
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        print(f"HTTP error occurred: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def parse_iso_date(date_string: str) -> datetime:
    """Parse ISO date string to datetime object"""
    try:
        return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
    except ValueError:
        return datetime.now()

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."
