"""
Enhanced job tracking with detailed Redis Bull queue integration
"""

import json
import redis.asyncio as redis
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import asyncio


class EnhancedJobTracker:
    def __init__(self, redis_host: str, redis_port: int, redis_db: int):
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_db = redis_db
        self.redis_client = None

    async def get_redis_client(self):
        """Get or create Redis connection"""
        if self.redis_client is None:
            try:
                self.redis_client = redis.Redis(
                    host=self.redis_host, 
                    port=self.redis_port, 
                    db=self.redis_db, 
                    decode_responses=True
                )
                await self.redis_client.ping()
            except Exception as e:
                print(f"Redis connection failed: {e}")
                self.redis_client = None
        return self.redis_client

    async def get_detailed_queue_jobs(self) -> List[Dict[str, Any]]:
        """Get detailed jobs from Redis Bull queues with full metadata"""
        try:
            r = await self.get_redis_client()
            if not r:
                return []

            # Get all Bull queue keys
            keys = await r.keys("bull:*")
            queue_jobs = []
            
            # Group keys by queue name and status
            queue_data = {}
            for key in keys:
                parts = key.split(":")
                if len(parts) >= 2:
                    queue_name = parts[1]
                    if queue_name not in queue_data:
                        queue_data[queue_name] = {
                            "active": [], "waiting": [], "delayed": [], 
                            "completed": [], "failed": []
                        }
                    
                    # Extract status from key
                    if ":active" in key:
                        queue_data[queue_name]["active"] = await r.lrange(key, 0, -1)
                    elif ":waiting" in key:
                        queue_data[queue_name]["waiting"] = await r.lrange(key, 0, -1)
                    elif ":delayed" in key:
                        queue_data[queue_name]["delayed"] = await r.lrange(key, 0, -1)
                    elif ":completed" in key:
                        queue_data[queue_name]["