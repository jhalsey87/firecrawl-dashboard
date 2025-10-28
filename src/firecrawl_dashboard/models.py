"""
Data models for Firecrawl Dashboard
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from enum import Enum


class JobStatus(str, Enum):
    """Job status enumeration"""
    WAITING = "waiting"
    ACTIVE = "active"
    PROCESSING = "processing"
    RUNNING = "running"
    SCRAPING = "scraping"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    DELAYED = "delayed"
    STUCK = "stuck"
    UNKNOWN = "unknown"


class JobType(str, Enum):
    """Job type enumeration"""
    SCRAPE = "scrape"
    CRAWL = "crawl"
    QUEUE = "queue"
    UNKNOWN = "unknown"


class UrlStatus:
    """Status of individual URL in a job"""
    def __init__(
        self,
        url: str,
        status: str = "pending",
        response_time_ms: Optional[float] = None,
        error: Optional[str] = None,
        worker_id: Optional[str] = None,
        completed_at: Optional[datetime] = None
    ):
        self.url = url
        self.status = status
        self.response_time_ms = response_time_ms
        self.error = error
        self.worker_id = worker_id
        self.completed_at = completed_at
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "status": self.status,
            "response_time_ms": self.response_time_ms,
            "error": self.error,
            "worker_id": self.worker_id,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


class JobError:
    """Job error information"""
    def __init__(
        self,
        message: str,
        url: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        error_type: Optional[str] = None
    ):
        self.message = message
        self.url = url
        self.timestamp = timestamp or datetime.utcnow()
        self.error_type = error_type
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "message": self.message,
            "url": self.url,
            "timestamp": self.timestamp.isoformat(),
            "error_type": self.error_type
        }


class DetailedJob:
    """Enhanced job model with detailed tracking"""
    def __init__(
        self,
        job_id: str,
        status: JobStatus = JobStatus.UNKNOWN,
        job_type: JobType = JobType.UNKNOWN,
        created_at: Optional[datetime] = None,
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
        total_urls: int = 0,
        completed_urls: int = 0,
        failed_urls: int = 0,
        queue_name: Optional[str] = None,
        worker_id: Optional[str] = None,
        source: str = "dashboard"
    ):
        self.job_id = job_id
        self.status = status
        self.job_type = job_type
        self.created_at = created_at or datetime.utcnow()
        self.started_at = started_at
        self.completed_at = completed_at
        self.total_urls = total_urls
        self.completed_urls = completed_urls
        self.failed_urls = failed_urls
        self.queue_name = queue_name
        self.worker_id = worker_id
        self.source = source
        
        # Collections
        self.urls: List[UrlStatus] = []
        self.errors: List[JobError] = []
        self.metadata: Dict[str, Any] = {}
    
    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage"""
        if self.total_urls == 0:
            return 0.0
        return round((self.completed_urls / self.total_urls) * 100, 1)
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        processed = self.completed_urls + self.failed_urls
        if processed == 0:
            return 0.0
        return round((self.completed_urls / processed) * 100, 1)
    
    @property
    def total_duration_seconds(self) -> Optional[float]:
        """Calculate total job duration in seconds"""
        if not self.started_at:
            return None
        end_time = self.completed_at or datetime.utcnow()
        return (end_time - self.started_at).total_seconds()
    
    @property
    def processing_rate_per_minute(self) -> float:
        """Calculate processing rate in URLs per minute"""
        duration = self.total_duration_seconds
        if not duration or duration <= 0 or self.completed_urls == 0:
            return 0.0
        return round((self.completed_urls / duration) * 60, 2)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "job_id": self.job_id,
            "status": self.status.value,
            "job_type": self.job_type.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "total_urls": self.total_urls,
            "completed_urls": self.completed_urls,
            "failed_urls": self.failed_urls,
            "progress_percentage": self.progress_percentage,
            "success_rate": self.success_rate,
            "total_duration_seconds": self.total_duration_seconds,
            "processing_rate_per_minute": self.processing_rate_per_minute,
            "queue_name": self.queue_name,
            "worker_id": self.worker_id,
            "source": self.source,
            "urls": [url.to_dict() for url in self.urls],
            "errors": [error.to_dict() for error in self.errors],
            "metadata": self.metadata
        }
