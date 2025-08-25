from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import httpx
from utils import cache, get_api_key, make_request

class TrendsService:
    def __init__(self):
        self.github_token = get_api_key("github")
    
    def _get_github_headers(self) -> Dict[str, str]:
        headers = {
            "accept": "application/vnd.github.v3+json",
            "User-Agent": "API-Dashboard/1.0"
        }
        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"
        return headers
    
    async def get_github_trending(self, language: str = "", since: str = "daily") -> Optional[Dict[str, Any]]:
        """Get trending GitHub repositories"""
        cache_key = f"github_trending_{language}_{since}"
        cached_data = await cache.get(cache_key)
        if cached_data:
            return cached_data
        
        # GitHub doesn't have a direct trending API, so we'll use search with stars
        url = "https://api.github.com/search/repositories"
        
        # Calculate date for "since" parameter
        date_map = {
            "daily": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
            "weekly": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
            "monthly": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        }
        
        query_parts = [f"created:>{date_map.get(since, date_map['daily'])}"]
        if language:
            query_parts.append(f"language:{language}")
        
        params = {
            "q": " ".join(query_parts),
            "sort": "stars",
            "order": "desc",
            "per_page": 20
        }
        
        data = await make_request(url, headers=self._get_github_headers(), params=params)
        if data:
            await cache.set(cache_key, data, ttl=1800)  # Cache for 30 minutes
        return data
    
    async def get_hacker_news_top(self, count: int = 20) -> Optional[List[Dict[str, Any]]]:
        """Get top stories from Hacker News"""
        cache_key = f"hn_top_{count}"
        cached_data = await cache.get(cache_key)
        if cached_data:
            return cached_data
        
        # Get top story IDs
        top_stories_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        story_ids = await make_request(top_stories_url)
        
        if not story_ids:
            return None
        
        # Get details for top stories
        stories = []
        for story_id in story_ids[:count]:
            story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
            story = await make_request(story_url)
            if story and story.get("type") == "story":
                stories.append(story)
        
        if stories:
            await cache.set(cache_key, stories, ttl=900)  # Cache for 15 minutes
        return stories
    
    async def get_dev_to_trending(self) -> Optional[List[Dict[str, Any]]]:
        """Get trending articles from Dev.to"""
        cache_key = "devto_trending"
        cached_data = await cache.get(cache_key)
        if cached_data:
            return cached_data
        
        url = "https://dev.to/api/articles"
        params = {
            "top": "7",  # Top articles from past 7 days
            "per_page": 20
        }
        
        data = await make_request(url, params=params)
        if data:
            await cache.set(cache_key, data, ttl=1800)  # Cache for 30 minutes
        return data
    
    async def get_reddit_programming(self, subreddit: str = "programming") -> Optional[Dict[str, Any]]:
        """Get hot posts from programming subreddits"""
        cache_key = f"reddit_{subreddit}"
        cached_data = await cache.get(cache_key)
        if cached_data:
            return cached_data
        
        url = f"https://www.reddit.com/r/{subreddit}/hot.json"
        params = {"limit": 20}
        headers = {"User-Agent": "API-Dashboard/1.0"}
        
        data = await make_request(url, headers=headers, params=params)
        if data:
            await cache.set(cache_key, data, ttl=900)  # Cache for 15 minutes
        return data

trends_service = TrendsService()
