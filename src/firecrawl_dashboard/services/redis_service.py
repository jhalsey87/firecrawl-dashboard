"""
Redis service for Bull queue monitoring and management
"""

import redis.asyncio as redis
from typing import Optional, Dict, Any, List
import json
from datetime import datetime

from ..config import settings


class RedisService:
    """Service for managing Redis connections and Bull queue operations"""
    
    def __init__(self):
        self._client: Optional[redis.Redis] = None
    
    async def get_client(self) -> Optional[redis.Redis]:
        """Get or create Redis connection"""
        if self._client is None:
            try:
                self._client = redis.Redis(
                    host=settings.redis_host,
                    port=settings.redis_port,
                    db=settings.redis_db,
                    decode_responses=True
                )
                await self._client.ping()
                print(f"✅ Connected to Redis at {settings.redis_host}:{settings.redis_port}")
            except Exception as e:
                print(f"❌ Redis connection failed: {e}")
                self._client = None
        return self._client
    
    async def get_queue_status(self) -> Dict[str, Any]:
        """Get Redis queue status and statistics"""
        try:
            client = await self.get_client()
            if not client:
                return {
                    "connected": False,
                    "error": "Redis not available",
                    "queues": {},
                    "total_jobs": 0
                }
            
            # Get queue information
            keys = await client.keys("bull:*")
            queues = {}
            total_jobs = 0
            
            for key in keys:
                if any(suffix in key for suffix in [":active", ":waiting", ":delayed", ":completed", ":failed"]):
                    queue_name = key.split(":")[1] if len(key.split(":")) > 1 else key
                    if queue_name not in queues:
                        queues[queue_name] = {"active": 0, "waiting": 0, "delayed": 0, "completed": 0, "failed": 0}
                    
                    count = await client.llen(key) if key.endswith((":active", ":waiting", ":delayed")) else 0
                    
                    if ":active" in key:
                        queues[queue_name]["active"] = count
                    elif ":waiting" in key:
                        queues[queue_name]["waiting"] = count
                    elif ":delayed" in key:
                        queues[queue_name]["delayed"] = count
                    
                    total_jobs += count
            
            return {
                "connected": True,
                "queues": queues,
                "total_jobs": total_jobs,
                "redis_keys": len(keys)
            }
        except Exception as e:
            return {
                "connected": False,
                "error": str(e),
                "queues": {},
                "total_jobs": 0
            }
    
    async def clear_all_queues(self) -> Dict[str, Any]:
        """Emergency: Clear all Redis queues"""
        try:
            client = await self.get_client()
            if not client:
                return {"success": False, "error": "Redis not available"}
            
            # Get all Bull queue keys
            keys = await client.keys("bull:*")
            deleted_keys = []
            
            for key in keys:
                await client.delete(key)
                deleted_keys.append(key)
            
            return {
                "success": True,
                "message": f"Cleared {len(deleted_keys)} Redis queue keys",
                "deleted_keys": deleted_keys
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
