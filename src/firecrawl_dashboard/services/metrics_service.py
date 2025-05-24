"""
Metrics service for calculating dashboard performance metrics
"""

from datetime import datetime
from typing import Dict, Any


class MetricsService:
    """Service for calculating and tracking performance metrics"""
    
    def __init__(self, active_jobs: Dict[str, Dict[str, Any]]):
        self.active_jobs = active_jobs
        self.historical_metrics = []
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Calculate current performance metrics"""
        total_jobs = len(self.active_jobs)
        completed_jobs = len([j for j in self.active_jobs.values() if j["status"] == "completed"])
        failed_jobs = len([j for j in self.active_jobs.values() if j["status"] == "failed"])
        active_count = len([j for j in self.active_jobs.values() if j["status"] in ["running", "queued"]])
        
        success_rate = (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0
        
        # Calculate average response time from recent health checks
        avg_response_time = self._calculate_avg_response_time()
        
        return {
            "total_jobs": total_jobs,
            "active_jobs": active_count,
            "completed_jobs": completed_jobs,
            "failed_jobs": failed_jobs,
            "success_rate": round(success_rate, 1),
            "average_response_time": avg_response_time,
            "requests_per_minute": self._calculate_requests_per_minute(),
            "uptime_hours": self._calculate_uptime_hours()
        }
    
    def get_detailed_job_metrics(self) -> Dict[str, Any]:
        """Get detailed job analytics"""
        jobs = list(self.active_jobs.values())
        
        if not jobs:
            return {
                "total_processing_time": 0,
                "average_job_duration": 0,
                "success_rate_by_type": {},
                "error_patterns": [],
                "peak_processing_time": "N/A"
            }
        
        # Calculate processing times
        completed_jobs = [j for j in jobs if j.get("completed_at")]
        total_processing_time = 0
        processing_times = []
        
        for job in completed_jobs:
            if job.get("started_at") and job.get("completed_at"):
                start = datetime.fromisoformat(job["started_at"].replace('Z', '+00:00'))
                end = datetime.fromisoformat(job["completed_at"].replace('Z', '+00:00'))
                duration = (end - start).total_seconds()
                total_processing_time += duration
                processing_times.append(duration)
        
        avg_duration = total_processing_time / len(completed_jobs) if completed_jobs else 0
        
        # Success rate by job type
        success_by_type = {}
        for job_type in ["scrape", "crawl"]:
            type_jobs = [j for j in jobs if j.get("job_type") == job_type]
            if type_jobs:
                successful = len([j for j in type_jobs if j.get("status") == "completed"])
                success_by_type[job_type] = round((successful / len(type_jobs)) * 100, 1)
        
        # Error patterns
        error_patterns = self._analyze_error_patterns(jobs)
        
        return {
            "total_processing_time": round(total_processing_time, 2),
            "average_job_duration": round(avg_duration, 2),
            "success_rate_by_type": success_by_type,
            "error_patterns": error_patterns,
            "peak_processing_time": self._find_peak_processing_time(processing_times)
        }
    
    def _calculate_avg_response_time(self) -> float:
        """Calculate average response time from job data"""
        # Placeholder - would calculate from actual response times
        return 1250.0
    
    def _calculate_requests_per_minute(self) -> float:
        """Calculate current requests per minute"""
        # Placeholder - would calculate from recent activity
        return 12.5
    
    def _calculate_uptime_hours(self) -> int:
        """Calculate dashboard uptime in hours"""
        # Placeholder - would track actual uptime
        return 72
    
    def _analyze_error_patterns(self, jobs) -> list:
        """Analyze common error patterns"""
        error_counts = {}
        
        for job in jobs:
            for error in job.get("errors", []):
                error_msg = error.get("error", "Unknown error")
                # Simplified error categorization
                if "timeout" in error_msg.lower():
                    error_type = "Timeout errors"
                elif "403" in error_msg or "401" in error_msg:
                    error_type = "Authentication errors"
                elif "404" in error_msg:
                    error_type = "Not found errors"
                elif "500" in error_msg:
                    error_type = "Server errors"
                else:
                    error_type = "Other errors"
                
                error_counts[error_type] = error_counts.get(error_type, 0) + 1
        
        return [{"type": k, "count": v} for k, v in error_counts.items()]
    
    def _find_peak_processing_time(self, processing_times) -> str:
        """Find peak processing time period"""
        if not processing_times:
            return "N/A"
        
        # Simple implementation - would be more sophisticated in production
        peak_time = max(processing_times) if processing_times else 0
        return f"{peak_time:.1f}s"
