"""
Job processing service for handling Firecrawl crawl/scrape operations
"""

import aiohttp
import asyncio
from datetime import datetime
from typing import Dict, Any, List

from ..config import settings


class JobProcessingService:
    """Service for processing crawl and scrape jobs in the background"""
    
    def __init__(self, active_jobs: Dict[str, Dict[str, Any]]):
        self.active_jobs = active_jobs
    
    async def process_crawl_job(self, job_id: str):
        """Background task to process a crawl job"""
        try:
            if job_id not in self.active_jobs:
                raise ValueError(f"Job {job_id} not found in active jobs")
            
            job_data = self.active_jobs[job_id]
            job_data["status"] = "running"
            job_data["started_at"] = datetime.utcnow().isoformat()
            
            async with aiohttp.ClientSession() as session:
                headers = settings.firecrawl_headers
                headers["Content-Type"] = "application/json"
                
                for i, url in enumerate(job_data["urls"]):
                    # Check if job was cancelled
                    if self.active_jobs[job_id]["status"] == "cancelled":
                        break
                    
                    # Update current processing status
                    self.active_jobs[job_id]["current_url"] = url
                    self.active_jobs[job_id]["last_activity"] = datetime.utcnow().isoformat()
                    
                    try:
                        url_start_time = datetime.now()
                        
                        if job_data["job_type"] == "scrape":
                            result = await self._process_scrape_url(session, headers, url, url_start_time)
                        else:  # crawl
                            result = await self._process_crawl_url(session, headers, url, url_start_time, job_data["limit"])
                        
                        # Update job data with result
                        if result["success"]:
                            job_data["completed_urls"] += 1
                            job_data["processed_urls"].append(result["data"])
                        else:
                            job_data["errors"].append(result["error"])
                    
                    except Exception as e:
                        error_msg = f"Error processing {url}: {str(e)}"
                        job_data["errors"].append({
                            "url": url,
                            "error": error_msg,
                            "timestamp": datetime.utcnow().isoformat()
                        })
                    
                    # Update activity timestamp
                    self.active_jobs[job_id]["last_activity"] = datetime.utcnow().isoformat()
                    
                    # Small delay between requests
                    await asyncio.sleep(1)
            
            # Mark job as completed
            await self._finalize_job(job_id)
            
        except Exception as e:
            # Mark job as failed
            self.active_jobs[job_id]["status"] = "failed"
            self.active_jobs[job_id]["error"] = str(e)
            self.active_jobs[job_id]["failed_at"] = datetime.utcnow().isoformat()
    
    async def _process_scrape_url(self, session: aiohttp.ClientSession, headers: Dict[str, str], 
                                  url: str, start_time: datetime) -> Dict[str, Any]:
        """Process a single URL scrape"""
        payload = {
            "url": url,
            "formats": ["markdown", "html"]
        }
        
        async with session.post(f"{settings.firecrawl_api_url}/v0/scrape", 
                              json=payload, headers=headers, timeout=60) as response:
            url_duration = (datetime.now() - start_time).total_seconds()
            
            if response.status == 200:
                data = await response.json()
                if data.get("success", False):
                    return {
                        "success": True,
                        "data": {
                            "url": url,
                            "status": "success",
                            "duration_seconds": round(url_duration, 2),
                            "content_length": len(data.get("data", {}).get("content", "")),
                            "completed_at": datetime.utcnow().isoformat()
                        }
                    }
                else:
                    return {
                        "success": False,
                        "error": {
                            "url": url,
                            "error": f"Scrape failed for {url}: {data.get('error', 'Unknown error')}",
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    }
            else:
                return {
                    "success": False,
                    "error": {
                        "url": url,
                        "error": f"Failed to scrape {url}: HTTP {response.status}",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }
    
    async def _process_crawl_url(self, session: aiohttp.ClientSession, headers: Dict[str, str], 
                                 url: str, start_time: datetime, limit: int) -> Dict[str, Any]:
        """Process a single URL crawl"""
        payload = {
            "url": url,
            "limit": limit,
            "scrapeOptions": {
                "formats": ["markdown", "html"]
            }
        }
        
        async with session.post(f"{settings.firecrawl_api_url}/v0/crawl", 
                              json=payload, headers=headers, timeout=300) as response:
            url_duration = (datetime.now() - start_time).total_seconds()
            
            if response.status == 200:
                data = await response.json()
                if data.get("success", False):
                    return {
                        "success": True,
                        "data": {
                            "url": url,
                            "status": "success", 
                            "duration_seconds": round(url_duration, 2),
                            "pages_found": len(data.get("data", [])) if isinstance(data.get("data"), list) else 1,
                            "completed_at": datetime.utcnow().isoformat()
                        }
                    }
                else:
                    return {
                        "success": False,
                        "error": {
                            "url": url,
                            "error": f"Crawl failed for {url}: {data.get('error', 'Unknown error')}",
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    }
            else:
                return {
                    "success": False,
                    "error": {
                        "url": url,
                        "error": f"Failed to crawl {url}: HTTP {response.status}",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }
    
    async def _finalize_job(self, job_id: str):
        """Finalize job status based on results"""
        job_data = self.active_jobs[job_id]
        
        if job_data["status"] != "cancelled":
            if len(job_data["errors"]) == 0:
                job_data["status"] = "completed"
            else:
                job_data["status"] = "completed_with_errors" if job_data["completed_urls"] > 0 else "failed"
        
        job_data["completed_at"] = datetime.utcnow().isoformat()
