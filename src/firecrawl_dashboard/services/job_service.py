"""
Enhanced job tracking service
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import aiohttp

from ..models import DetailedJob, JobStatus, JobType
from .redis_service import RedisService
from ..config import settings


class JobService:
    """Service for enhanced job tracking and management"""
    
    def __init__(self, redis_service: RedisService):
        self.redis_service = redis_service
        self.active_jobs: Dict[str, DetailedJob] = {}
        self.job_counter = 0
    
    def create_job(self, job_type: str, urls: List[str]) -> DetailedJob:
        """Create a new job"""
        self.job_counter += 1
        job_id = f"dashboard_{self.job_counter}_{int(datetime.utcnow().timestamp())}"
        
        job = DetailedJob(
            job_id=job_id,
            status=JobStatus.WAITING,
            job_type=JobType.SCRAPE if job_type == "scrape" else JobType.CRAWL,
            total_urls=len(urls),
            source="dashboard"
        )
        
        self.active_jobs[job_id] = job
        return job
    
    def get_job(self, job_id: str) -> Optional[DetailedJob]:
        """Get a specific job"""
        return self.active_jobs.get(job_id)
    
    def get_all_jobs(self) -> List[DetailedJob]:
        """Get all tracked jobs"""
        return list(self.active_jobs.values())
    
    def update_job_status(self, job_id: str, status: JobStatus, **kwargs) -> bool:
        """Update job status"""
        if job_id in self.active_jobs:
            job = self.active_jobs[job_id]
            job.status = status
            
            for key, value in kwargs.items():
                if hasattr(job, key):
                    setattr(job, key, value)
            
            return True
        return False
    
    async def get_enhanced_jobs(self) -> List[DetailedJob]:
        """Get enhanced jobs combining dashboard and Redis data"""
        # Start with dashboard jobs
        all_jobs = self.get_all_jobs()

        # Get active crawl jobs from Redis
        try:
            crawl_job_ids = await self.redis_service.get_active_crawl_jobs()

            # Fetch details for each crawl job from Firecrawl API
            for job_id in crawl_job_ids[:20]:  # Limit to 20 jobs to avoid overwhelming
                job_details = await self.get_job_details_enhanced(job_id)
                if job_details:
                    # Convert status to JobStatus enum, fallback to UNKNOWN if invalid
                    try:
                        job_status = JobStatus(job_details.get("status", "unknown"))
                    except ValueError:
                        job_status = JobStatus.UNKNOWN

                    # Convert to DetailedJob object
                    crawl_job = DetailedJob(
                        job_id=job_id,
                        status=job_status,
                        job_type=JobType.CRAWL,
                        total_urls=job_details.get("total_urls", job_details.get("total", 0)),
                        completed_urls=job_details.get("completed_urls", job_details.get("completed", 0)),
                        source="firecrawl"
                    )
                    crawl_job.current_url = job_details.get("current_url")
                    crawl_job.errors = job_details.get("errors", [])
                    crawl_job.metadata = job_details
                    all_jobs.append(crawl_job)
        except Exception as e:
            print(f"Error getting crawl jobs from Redis: {e}")

        # Add Redis queue summary job
        try:
            queue_status = await self.redis_service.get_queue_status()
            if queue_status.get("connected") and queue_status.get("total_jobs", 0) > 0:
                # Create a summary job for Redis queue monitoring
                queue_job = DetailedJob(
                    job_id="redis_queue_monitor",
                    status=JobStatus.ACTIVE if queue_status.get("total_jobs", 0) > 0 else JobStatus.WAITING,
                    job_type=JobType.QUEUE,
                    total_urls=queue_status.get("total_jobs", 0),
                    source="redis_queue"
                )
                queue_job.metadata["queue_summary"] = queue_status.get("queues", {})
                all_jobs.append(queue_job)
        except Exception as e:
            print(f"Error getting Redis queue jobs: {e}")

        return all_jobs
    
    def get_legacy_jobs_format(self) -> List[dict]:
        """Convert jobs to legacy format for backward compatibility"""
        jobs = self.get_all_jobs()
        return [job.to_dict() for job in jobs]
    
    def start_crawl_job(self, urls: List[str], job_type: str = "crawl", limit: int = 10) -> DetailedJob:
        """Start a new crawl job"""
        if not urls:
            raise ValueError("No valid URLs provided")
        
        # Create enhanced job
        job = self.create_job(job_type, urls)
        job.metadata["limit"] = limit
        job.metadata["urls"] = urls
        job.status = JobStatus.WAITING
        
        return job
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a running job"""
        if job_id in self.active_jobs:
            job = self.active_jobs[job_id]
            if job.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
                return False  # Cannot cancel
            
            job.status = JobStatus.CANCELLED
            job.completed_at = datetime.utcnow()
            return True
        return False
    
    async def get_job_details_enhanced(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific job with enhanced metrics"""
        job_data = None
        
        # First check if it's a dashboard-tracked job
        if job_id in self.active_jobs:
            job = self.active_jobs[job_id]
            job_data = job.to_dict()
        else:
            # Try to get job details from Firecrawl directly
            try:
                async with aiohttp.ClientSession() as session:
                    headers = {"Authorization": f"Bearer {settings.firecrawl_api_key}"} if settings.firecrawl_api_key and settings.firecrawl_api_key != "dummy" else {}
                    
                    # Try different endpoints to get job status (v2 first, then v1, v0)
                    for endpoint in [f"/v2/crawl/{job_id}", f"/v1/crawl/{job_id}", f"/v0/crawl/{job_id}", f"/crawl/{job_id}"]:
                        try:
                            async with session.get(f"{settings.firecrawl_api_url}{endpoint}", headers=headers, timeout=10) as response:
                                if response.status == 200:
                                    firecrawl_job = await response.json()
                                    # Convert Firecrawl job format to dashboard format
                                    job_data = {
                                        "job_id": job_id,
                                        "status": firecrawl_job.get("status", "unknown"),
                                        "job_type": "crawl",
                                        "total_urls": firecrawl_job.get("total", 0),
                                        "completed_urls": firecrawl_job.get("completed", 0),
                                        "created_at": firecrawl_job.get("created_at", datetime.utcnow().isoformat()),
                                        "errors": firecrawl_job.get("errors", []),
                                        "source": "firecrawl",
                                        "current_url": firecrawl_job.get("current_url"),
                                        "last_activity": firecrawl_job.get("updated_at", datetime.utcnow().isoformat())
                                    }
                                    break
                        except:
                            continue
            except Exception as e:
                print(f"Could not fetch job {job_id} from Firecrawl: {e}")
        
        if not job_data:
            return None
        
        # Calculate additional metrics
        total_time = None
        if job_data.get("started_at") and job_data.get("status") in ["running", "queued", "active", "processing"]:
            started = datetime.fromisoformat(job_data["started_at"])
            total_time = (datetime.utcnow() - started).total_seconds()
        elif job_data.get("started_at") and job_data.get("completed_at"):
            started = datetime.fromisoformat(job_data["started_at"])
            completed = datetime.fromisoformat(job_data["completed_at"])
            total_time = (completed - started).total_seconds()
        
        # Calculate processing rate
        processing_rate = 0
        if total_time and total_time > 0 and job_data.get("completed_urls", 0) > 0:
            processing_rate = job_data["completed_urls"] / total_time * 60  # URLs per minute
        
        # Estimate completion time
        eta = None
        if job_data["status"] in ["running", "active", "processing"] and processing_rate > 0:
            remaining_urls = job_data.get("total_urls", 0) - job_data.get("completed_urls", 0)
            if remaining_urls > 0:
                eta_seconds = remaining_urls / (processing_rate / 60)
                eta = datetime.utcnow() + timedelta(seconds=eta_seconds)
                eta = eta.isoformat()
        
        # Enhanced job details
        enhanced_job = {
            **job_data,
            "total_time_seconds": total_time,
            "processing_rate_per_minute": round(processing_rate, 2) if processing_rate else 0,
            "estimated_completion": eta,
            "progress_percentage": round((job_data.get("completed_urls", 0) / max(job_data.get("total_urls", 1), 1)) * 100, 1),
            "success_rate": round((job_data.get("completed_urls", 0) / max(job_data.get("completed_urls", 0) + len(job_data.get("errors", [])), 1)) * 100, 1)
        }
        
        return enhanced_job
