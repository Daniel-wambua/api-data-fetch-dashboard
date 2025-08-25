import json
import time
import sqlite3
import aiosqlite
from typing import Any, Optional
from datetime import datetime, timedelta
import os

class Cache:
    def __init__(self, db_path: str = "cache.db", ttl_seconds: int = 300):
        self.db_path = db_path
        self.ttl_seconds = ttl_seconds
        self.setup_database()
    
    def setup_database(self):
        """Initialize the cache database"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS cache (
                key TEXT PRIMARY KEY,
                value TEXT,
                expires_at REAL
            )
        """)
        conn.commit()
        conn.close()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        async with aiosqlite.connect(self.db_path) as conn:
            cursor = await conn.execute(
                "SELECT value, expires_at FROM cache WHERE key = ?", (key,)
            )
            row = await cursor.fetchone()
            
            if row:
                value, expires_at = row
                if time.time() < expires_at:
                    return json.loads(value)
                else:
                    # Remove expired entry
                    await conn.execute("DELETE FROM cache WHERE key = ?", (key,))
                    await conn.commit()
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with TTL"""
        ttl = ttl or self.ttl_seconds
        expires_at = time.time() + ttl
        
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute(
                "INSERT OR REPLACE INTO cache (key, value, expires_at) VALUES (?, ?, ?)",
                (key, json.dumps(value), expires_at)
            )
            await conn.commit()
    
    async def clear_expired(self) -> None:
        """Clear all expired entries"""
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute("DELETE FROM cache WHERE expires_at < ?", (time.time(),))
            await conn.commit()

# Global cache instance
cache = Cache(ttl_seconds=int(os.getenv("CACHE_TTL_SECONDS", "300")))
