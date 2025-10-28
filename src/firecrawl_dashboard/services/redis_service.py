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
    
    async def get_active_crawl_jobs(self) -> List[str]:
        """Get list of active crawl job IDs from Redis"""
        try:
            client = await self.get_client()
            if not client:
                return []

            # Get all crawl keys (format: crawl:UUID)
            crawl_keys = await client.keys("crawl:*")
            job_ids = []

            for key in crawl_keys:
                # Extract UUID from keys like "crawl:8f2ba06c-26e6-4610-a503-ab427e1c9a4d"
                # Skip keys with colons after the UUID (those are sub-keys)
                parts = key.split(":")
                if len(parts) == 2:  # Just "crawl:UUID"
                    job_id = parts[1]
                    if job_id and len(job_id) == 36:  # Standard UUID length
                        job_ids.append(job_id)

            return job_ids
        except Exception as e:
            print(f"Error getting active crawl jobs: {e}")
            return []

    async def get_crawl_origin_url(self, job_id: str) -> Optional[str]:
        """Get the origin URL for a crawl job from Redis"""
        try:
            client = await self.get_client()
            if not client:
                return None

            # Get crawl data from Redis
            crawl_data = await client.get(f"crawl:{job_id}")
            if crawl_data:
                import json
                data = json.loads(crawl_data)
                return data.get("originUrl")
            return None
        except Exception as e:
            print(f"Error getting origin URL for job {job_id}: {e}")
            return None

    async def get_crawl_created_at(self, job_id: str) -> Optional[str]:
        """Get the creation timestamp for a crawl job from Redis"""
        try:
            client = await self.get_client()
            if not client:
                return None

            # Get crawl data from Redis
            crawl_data = await client.get(f"crawl:{job_id}")
            if crawl_data:
                import json
                data = json.loads(crawl_data)
                # Redis crawl data has createdAt as Unix timestamp in milliseconds
                created_at_ms = data.get("createdAt")
                if created_at_ms:
                    # Convert milliseconds to seconds and create ISO timestamp
                    from datetime import datetime
                    created_dt = datetime.fromtimestamp(created_at_ms / 1000.0)
                    return created_dt.isoformat()
            return None
        except Exception as e:
            print(f"Error getting creation timestamp for job {job_id}: {e}")
            return None

    async def get_crawl_completed_at(self, job_id: str) -> Optional[str]:
        """Get the completion timestamp for a crawl job from Redis

        This retrieves the timestamp of the last scraped page from the sorted set
        crawl:{job_id}:jobs_donez_ordered, which tracks all scraped pages with timestamps.
        """
        try:
            client = await self.get_client()
            if not client:
                return None

            # Get the last entry from the sorted set (highest score = most recent timestamp)
            # ZRANGE with -1 -1 gets the last element, WITHSCORES includes the timestamp
            result = await client.zrange(
                f"crawl:{job_id}:jobs_donez_ordered",
                -1, -1,
                withscores=True
            )

            if result and len(result) > 0:
                # Result is a list of tuples: [(member, score), ...]
                # The score is the Unix timestamp in milliseconds
                last_page_timestamp_ms = result[0][1]  # Get the score (timestamp)

                # Convert milliseconds to seconds and create ISO timestamp
                from datetime import datetime
                completed_dt = datetime.fromtimestamp(last_page_timestamp_ms / 1000.0)
                return completed_dt.isoformat()

            return None
        except Exception as e:
            print(f"Error getting completion timestamp for job {job_id}: {e}")
            return None

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
