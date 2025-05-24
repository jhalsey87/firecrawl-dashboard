from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import aiohttp
import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List
import uvicorn
from pathlib import Path
from dotenv import load_dotenv
import redis.asyncio as redis

# Load environment variables from .env file
load_dotenv()

# Configuration from environment variables
FIRECRAWL_API_URL = os.getenv("FIRECRAWL_API_URL", "http://localhost:3002")
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY", "dummy")
DASHBOARD_HOST = os.getenv("DASHBOARD_HOST", "0.0.0.0")
DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", "8000"))
UPDATE_INTERVAL = int(os.getenv("UPDATE_INTERVAL", "5"))

# Redis configuration for direct queue monitoring
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

# Global Redis connection
redis_client = None

# Initialize FastAPI app
app = FastAPI(title="Firecrawl Monitoring Dashboard")

# Set up templates directory
templates_dir = Path(__file__).parent / "templates"
templates_dir.mkdir(exist_ok=True)
templates = Jinja2Templates(directory=str(templates_dir))

# Global storage for job tracking (in production, use Redis or database)
active_jobs: Dict[str, Dict[str, Any]] = {}
job_counter = 0

async def get_redis_client():
    """Get or create Redis connection"""
    global redis_client
    if redis_client is None:
        try:
            redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)
            await redis_client.ping()
        except Exception as e:
            print(f"Redis connection failed: {e}")
            redis_client = None
    return redis_client

async def get_redis_queue_jobs():
    """Get jobs from Redis Bull queues"""
    try:
        r = await get_redis_client()
        if not r:
            return []
        
        # Get all Bull queue keys
        keys = await r.keys("bull:*")
        queue_jobs = []
        
        for key in keys:
            if ":active" in key or ":waiting" in key or ":delayed" in key:
                # Get jobs from this queue
                job_ids = await r.lrange(key, 0, -1)
                for job_id in job_ids:
                    try:
                        # Get job data
                        job_key = f"bull:queue:{job_id}"
                        job_data = await r.hgetall(job_key)
                        
                        if job_data:
                            queue_jobs.append({
                                "job_id": job_id,
                                "status": "active" if ":active" in key else "waiting",
                                "job_type": "queue",
                                "queue": key,
                                "created_at": datetime.utcnow().isoformat(),
                                "source": "redis_queue",
                                "total_urls": 1,
                                "completed_urls": 0,
                                "data": job_data
                            })
                    except Exception:
                        continue
        
        return queue_jobs
    except Exception as e:
        print(f"Error getting Redis queue jobs: {e}")
        return []

@app.get("/api/queue")
async def get_queue_status():
    """Get Redis queue status and jobs"""
    try:
        r = await get_redis_client()
        if not r:
            return {
                "connected": False,
                "error": "Redis not available",
                "queues": {},
                "total_jobs": 0
            }
        
        # Get queue information
        keys = await r.keys("bull:*")
        queues = {}
        total_jobs = 0
        
        for key in keys:
            if any(suffix in key for suffix in [":active", ":waiting", ":delayed", ":completed", ":failed"]):
                queue_name = key.split(":")[1] if len(key.split(":")) > 1 else key
                if queue_name not in queues:
                    queues[queue_name] = {"active": 0, "waiting": 0, "delayed": 0, "completed": 0, "failed": 0}
                
                count = await r.llen(key) if key.endswith(":active") or key.endswith(":waiting") or key.endswith(":delayed") else 0
                
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

@app.delete("/api/queue")
async def clear_redis_queues():
    """Emergency: Clear all Redis queues"""
    try:
        r = await get_redis_client()
        if not r:
            return JSONResponse(
                status_code=503,
                content={"success": False, "error": "Redis not available"}
            )
        
        # Get all Bull queue keys
        keys = await r.keys("bull:*")
        deleted_keys = []
        
        for key in keys:
            await r.delete(key)
            deleted_keys.append(key)
        
        return {
            "success": True,
            "message": f"Cleared {len(deleted_keys)} Redis queue keys",
            "deleted_keys": deleted_keys
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@app.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request):
    """Main dashboard page"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/api/jobs/{job_id}")
async def get_job_details(job_id: str):
    """Get detailed information about a specific job"""
    job_data = None
    
    # First check if it's a dashboard-tracked job
    if job_id in active_jobs:
        job_data = active_jobs[job_id]
    else:
        # Try to get job details from Firecrawl directly
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {FIRECRAWL_API_KEY}"} if FIRECRAWL_API_KEY and FIRECRAWL_API_KEY != "dummy" else {}
                
                # Try different endpoints to get job status
                for endpoint in [f"/v0/crawl/{job_id}", f"/v1/crawl/{job_id}", f"/crawl/{job_id}"]:
                    try:
                        async with session.get(f"{FIRECRAWL_API_URL}{endpoint}", headers=headers, timeout=10) as response:
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
    
    # If we still don't have job data, return 404
    if not job_data:
        raise HTTPException(status_code=404, detail="Job not found")
    
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

@app.get("/api/health")
async def get_health_status():
    """Get current Firecrawl health status"""
    try:
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {FIRECRAWL_API_KEY}"} if FIRECRAWL_API_KEY and FIRECRAWL_API_KEY != "dummy" else {}
            
            # Since Firecrawl doesn't have a /health endpoint, check the base URL
            start_time = datetime.now()
            try:
                async with session.get(f"{FIRECRAWL_API_URL}/", headers=headers, timeout=10) as response:
                    response_time = (datetime.now() - start_time).total_seconds() * 1000
                    text_response = await response.text()
                    
                    # Firecrawl base URL should return something like "SCRAPERS-JS: Hello, world!"
                    if response.status == 200 and ("SCRAPERS" in text_response or "Hello" in text_response):
                        health_status = {
                            "status": "healthy",
                            "status_code": response.status,
                            "response_time_ms": round(response_time, 2),
                            "timestamp": datetime.utcnow().isoformat(),
                            "message": "Firecrawl service is responding"
                        }
                    else:
                        health_status = {
                            "status": "unhealthy",
                            "status_code": response.status,
                            "response_time_ms": round(response_time, 2),
                            "timestamp": datetime.utcnow().isoformat(),
                            "message": f"Unexpected response: {text_response[:50]}..."
                        }
            except asyncio.TimeoutError:
                health_status = {
                    "status": "timeout",
                    "status_code": 408,
                    "response_time_ms": 10000,
                    "timestamp": datetime.utcnow().isoformat(),
                    "error": "Request timeout"
                }
            except Exception as e:
                health_status = {
                    "status": "error",
                    "status_code": 0,
                    "response_time_ms": 0,
                    "timestamp": datetime.utcnow().isoformat(),
                    "error": str(e)
                }
        
        # For regular health checks, just use the base URL check
        overall_status = health_status["status"]
        
        return {
            "overall_status": overall_status,
            "health_endpoint": health_status,
            "scrape_endpoint": {"status": "not_tested", "message": "Use /api/health/full for scrape testing"},
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "overall_status": "error",
            "error": str(e),
            "health_endpoint": {"status": "error", "error": str(e)},
            "scrape_endpoint": {"status": "error", "error": str(e)},
            "timestamp": datetime.utcnow().isoformat()
        }

@app.get("/api/health/full")
async def get_full_health_status():
    """Get comprehensive Firecrawl health status including scrape test"""
    try:
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {FIRECRAWL_API_KEY}"} if FIRECRAWL_API_KEY and FIRECRAWL_API_KEY != "dummy" else {}
            
            # Check base URL first (Firecrawl doesn't have /health)
            start_time = datetime.now()
            try:
                async with session.get(f"{FIRECRAWL_API_URL}/", headers=headers, timeout=10) as response:
                    response_time = (datetime.now() - start_time).total_seconds() * 1000
                    text_response = await response.text()
                    
                    if response.status == 200 and ("SCRAPERS" in text_response or "Hello" in text_response):
                        health_status = {
                            "status": "healthy",
                            "status_code": response.status,
                            "response_time_ms": round(response_time, 2),
                            "timestamp": datetime.utcnow().isoformat(),
                            "message": "Firecrawl service is responding"
                        }
                    else:
                        health_status = {
                            "status": "unhealthy",
                            "status_code": response.status,
                            "response_time_ms": round(response_time, 2),
                            "timestamp": datetime.utcnow().isoformat(),
                            "message": f"Unexpected response: {text_response[:50]}..."
                        }
            except Exception as e:
                health_status = {
                    "status": "error",
                    "status_code": 0,
                    "response_time_ms": 0,
                    "timestamp": datetime.utcnow().isoformat(),
                    "error": str(e)
                }
            
            # Test scrape endpoint with a simple page
            start_time = datetime.now()
            try:
                test_payload = {"url": "https://httpbin.org/html", "formats": ["markdown"]}
                async with session.post(f"{FIRECRAWL_API_URL}/v0/scrape", 
                                      json=test_payload, headers=headers, timeout=30) as response:
                    response_time = (datetime.now() - start_time).total_seconds() * 1000
                    if response.status == 200:
                        data = await response.json()
                        if data.get("success", False):
                            scrape_status = {
                                "status": "healthy",
                                "status_code": response.status,
                                "response_time_ms": round(response_time, 2),
                                "message": "Scrape test successful"
                            }
                        else:
                            scrape_status = {
                                "status": "unhealthy",
                                "status_code": response.status,
                                "response_time_ms": round(response_time, 2),
                                "message": "Scrape test failed"
                            }
                    else:
                        scrape_status = {
                            "status": "unhealthy",
                            "status_code": response.status,
                            "response_time_ms": round(response_time, 2),
                            "message": f"HTTP {response.status}"
                        }
            except Exception as e:
                scrape_status = {
                    "status": "error",
                    "status_code": 0,
                    "response_time_ms": 0,
                    "error": str(e)
                }
        
        overall_status = "healthy" if (health_status["status"] == "healthy" and 
                                     scrape_status["status"] == "healthy") else "degraded"
        
        return {
            "overall_status": overall_status,
            "health_endpoint": health_status,
            "scrape_endpoint": scrape_status,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "overall_status": "error",
            "error": str(e),
            "health_endpoint": {"status": "error", "error": str(e)},
            "scrape_endpoint": {"status": "error", "error": str(e)},
            "timestamp": datetime.utcnow().isoformat()
        }


@app.get("/api/jobs")
async def get_jobs():
    """Get list of active and recent jobs from dashboard, Firecrawl, and Redis queues"""
    dashboard_jobs = []
    firecrawl_jobs = []
    redis_jobs = []
    
    # Get jobs tracked by the dashboard
    for job_id, job_data in active_jobs.items():
        dashboard_jobs.append({**job_data, "source": "dashboard"})
    
    # Get jobs from Redis queues (the flood you're experiencing)
    redis_jobs = await get_redis_queue_jobs()
    
    # Query Firecrawl directly for any active crawl jobs
    try:
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {FIRECRAWL_API_KEY}"} if FIRECRAWL_API_KEY and FIRECRAWL_API_KEY != "dummy" else {}
            
            # Try to get crawl jobs from Firecrawl (this endpoint may vary by version)
            try:
                async with session.get(f"{FIRECRAWL_API_URL}/v0/crawl", headers=headers, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Process Firecrawl job data if available
                        if isinstance(data, list):
                            for job in data:
                                firecrawl_jobs.append({
                                    "job_id": job.get("id", "unknown"),
                                    "status": job.get("status", "unknown"),
                                    "job_type": "crawl",
                                    "total_urls": job.get("total", 0),
                                    "completed_urls": job.get("completed", 0),
                                    "created_at": job.get("created_at", datetime.utcnow().isoformat()),
                                    "source": "firecrawl",
                                    "errors": []
                                })
            except:
                # Firecrawl may not have a jobs listing endpoint
                pass
    except Exception as e:
        print(f"Could not query Firecrawl for active jobs: {e}")
    
    # Combine and deduplicate jobs
    all_jobs = {}
    
    # Add dashboard jobs
    for job in dashboard_jobs:
        all_jobs[job["job_id"]] = job
    
    # Add Redis queue jobs (these are likely causing your flood!)
    for job in redis_jobs:
        if job["job_id"] not in all_jobs:
            all_jobs[job["job_id"]] = job
    
    # Add Firecrawl jobs (don't overwrite existing)
    for job in firecrawl_jobs:
        if job["job_id"] not in all_jobs:
            all_jobs[job["job_id"]] = job
    
    # Separate active and recent jobs
    active_jobs_list = []
    recent_jobs_list = []
    
    for job_data in all_jobs.values():
        if job_data["status"] in ["running", "queued", "active", "processing", "waiting"]:
            active_jobs_list.append(job_data)
        else:
            recent_jobs_list.append(job_data)
    
    # Sort by creation time
    active_jobs_list.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    recent_jobs_list.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    return {
        "active_jobs": active_jobs_list[:20],  # Increased limit to see flood
        "recent_jobs": recent_jobs_list[:20],
        "queue_count": len(redis_jobs),
        "dashboard_count": len(dashboard_jobs),
        "firecrawl_count": len(firecrawl_jobs)
    }

@app.get("/api/metrics")
async def get_metrics():
    """Get performance metrics"""
    total_jobs = len(active_jobs)
    completed_jobs = len([j for j in active_jobs.values() if j["status"] == "completed"])
    failed_jobs = len([j for j in active_jobs.values() if j["status"] == "failed"])
    active_count = len([j for j in active_jobs.values() if j["status"] in ["running", "queued"]])
    
    success_rate = (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0
    
    # Calculate average response time from recent health checks
    avg_response_time = 1250  # Placeholder - would calculate from actual metrics
    
    return {
        "total_jobs": total_jobs,
        "active_jobs": active_count,
        "completed_jobs": completed_jobs,
        "failed_jobs": failed_jobs,
        "success_rate": round(success_rate, 1),
        "average_response_time": avg_response_time,
        "requests_per_minute": 12.5,  # Placeholder
        "uptime_hours": 72  # Placeholder
    }


@app.post("/api/jobs/start")
async def start_crawl_job(
    urls: str = Form(...),
    limit: int = Form(default=10),
    job_type: str = Form(default="crawl")
):
    """Start a new crawl job"""
    global job_counter
    
    try:
        # Parse URLs
        url_list = [url.strip() for url in urls.split('\n') if url.strip()]
        if not url_list:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "No valid URLs provided"}
            )
        
        # Generate job ID
        job_counter += 1
        job_id = f"job_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{job_counter}"
        
        # Create job record
        job_data = {
            "job_id": job_id,
            "status": "queued",
            "job_type": job_type,
            "urls": url_list,
            "total_urls": len(url_list),
            "completed_urls": 0,
            "limit": limit,
            "created_at": datetime.utcnow().isoformat(),
            "errors": [],
            "processed_urls": [],  # Track individual URL results
            "current_url": None,
            "last_activity": datetime.utcnow().isoformat()
        }
        
        active_jobs[job_id] = job_data
        
        # Start background job processing
        asyncio.create_task(process_crawl_job(job_id))
        
        return {
            "success": True,
            "job_id": job_id,
            "message": f"Started {job_type} job with {len(url_list)} URLs"
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )


@app.delete("/api/jobs/{job_id}")
async def cancel_job(job_id: str):
    """Cancel a running job (dashboard or external)"""
    try:
        # First check if it's a dashboard-tracked job
        if job_id in active_jobs:
            job_data = active_jobs[job_id]
            if job_data["status"] in ["completed", "failed", "cancelled"]:
                return JSONResponse(
                    status_code=400,
                    content={"success": False, "error": "Job cannot be cancelled in current state"}
                )
            
            # Update dashboard job status
            active_jobs[job_id]["status"] = "cancelled"
            active_jobs[job_id]["cancelled_at"] = datetime.utcnow().isoformat()
            
            return {"success": True, "message": "Dashboard job cancelled successfully"}
        
        # Try to cancel external job via Firecrawl API
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {FIRECRAWL_API_KEY}"} if FIRECRAWL_API_KEY and FIRECRAWL_API_KEY != "dummy" else {}
            
            # Try different endpoints to cancel the job
            for endpoint in [f"/v0/crawl/{job_id}", f"/v1/crawl/{job_id}", f"/crawl/{job_id}"]:
                try:
                    async with session.delete(f"{FIRECRAWL_API_URL}{endpoint}", headers=headers, timeout=30) as response:
                        if response.status == 200:
                            return {"success": True, "message": "External job cancelled successfully"}
                        elif response.status == 404:
                            continue  # Try next endpoint
                        else:
                            # Try PATCH or PUT with status update
                            patch_payload = {"status": "cancelled"}
                            async with session.patch(f"{FIRECRAWL_API_URL}{endpoint}", 
                                                   json=patch_payload, headers=headers, timeout=30) as patch_response:
                                if patch_response.status == 200:
                                    return {"success": True, "message": "External job cancelled successfully"}
                except Exception:
                    continue
        
        # If we get here, we couldn't find or cancel the job
        return JSONResponse(
            status_code=404,
            content={"success": False, "error": "Job not found or cannot be cancelled"}
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@app.delete("/api/jobs")
async def cancel_all_jobs():
    """Cancel all active jobs (dashboard and external)"""
    try:
        cancelled_jobs = []
        failed_jobs = []
        
        # Get all active jobs first
        jobs_response = await get_jobs()
        all_active_jobs = jobs_response.get("active_jobs", [])
        
        # Cancel each active job
        for job in all_active_jobs:
            job_id = job["job_id"]
            try:
                # Use the single job cancel logic
                cancel_response = await cancel_job(job_id)
                if isinstance(cancel_response, dict) and cancel_response.get("success"):
                    cancelled_jobs.append(job_id)
                else:
                    failed_jobs.append({"job_id": job_id, "error": "Failed to cancel"})
            except Exception as e:
                failed_jobs.append({"job_id": job_id, "error": str(e)})
        
        return {
            "success": True,
            "message": f"Cancelled {len(cancelled_jobs)} jobs",
            "cancelled_jobs": cancelled_jobs,
            "failed_jobs": failed_jobs,
            "total_attempted": len(all_active_jobs)
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

async def process_crawl_job(job_id: str):
    """Background task to process a crawl job"""
    try:
        job_data = active_jobs[job_id]
        job_data["status"] = "running"
        job_data["started_at"] = datetime.utcnow().isoformat()
        
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {FIRECRAWL_API_KEY}"} if FIRECRAWL_API_KEY and FIRECRAWL_API_KEY != "dummy" else {}
            headers["Content-Type"] = "application/json"
            
            for i, url in enumerate(job_data["urls"]):
                # Check if job was cancelled
                if active_jobs[job_id]["status"] == "cancelled":
                    break
                
                # Update current processing status
                active_jobs[job_id]["current_url"] = url
                active_jobs[job_id]["last_activity"] = datetime.utcnow().isoformat()
                
                try:
                    url_start_time = datetime.now()
                    
                    if job_data["job_type"] == "scrape":
                        # Single URL scrape
                        payload = {
                            "url": url,
                            "formats": ["markdown", "html"]
                        }
                        async with session.post(f"{FIRECRAWL_API_URL}/v0/scrape", 
                                              json=payload, headers=headers, timeout=60) as response:
                            url_duration = (datetime.now() - url_start_time).total_seconds()
                            
                            if response.status == 200:
                                data = await response.json()
                                if data.get("success", False):
                                    job_data["completed_urls"] += 1
                                    job_data["processed_urls"].append({
                                        "url": url,
                                        "status": "success",
                                        "duration_seconds": round(url_duration, 2),
                                        "content_length": len(data.get("data", {}).get("content", "")),
                                        "completed_at": datetime.utcnow().isoformat()
                                    })
                                else:
                                    error_msg = f"Scrape failed for {url}: {data.get('error', 'Unknown error')}"
                                    job_data["errors"].append({
                                        "url": url,
                                        "error": error_msg,
                                        "timestamp": datetime.utcnow().isoformat()
                                    })
                            else:
                                error_msg = f"Failed to scrape {url}: HTTP {response.status}"
                                job_data["errors"].append({
                                    "url": url,
                                    "error": error_msg,
                                    "timestamp": datetime.utcnow().isoformat()
                                })
                    
                    else:  # crawl
                        # Multi-URL crawl
                        payload = {
                            "url": url,
                            "limit": job_data["limit"],
                            "scrapeOptions": {
                                "formats": ["markdown", "html"]
                            }
                        }
                        async with session.post(f"{FIRECRAWL_API_URL}/v0/crawl", 
                                              json=payload, headers=headers, timeout=300) as response:
                            url_duration = (datetime.now() - url_start_time).total_seconds()
                            
                            if response.status == 200:
                                data = await response.json()
                                if data.get("success", False):
                                    job_data["completed_urls"] += 1
                                    job_data["processed_urls"].append({
                                        "url": url,
                                        "status": "success", 
                                        "duration_seconds": round(url_duration, 2),
                                        "pages_found": len(data.get("data", [])) if isinstance(data.get("data"), list) else 1,
                                        "completed_at": datetime.utcnow().isoformat()
                                    })
                                else:
                                    error_msg = f"Crawl failed for {url}: {data.get('error', 'Unknown error')}"
                                    job_data["errors"].append({
                                        "url": url,
                                        "error": error_msg,
                                        "timestamp": datetime.utcnow().isoformat()
                                    })
                            else:
                                error_msg = f"Failed to crawl {url}: HTTP {response.status}"
                                job_data["errors"].append({
                                    "url": url,
                                    "error": error_msg,
                                    "timestamp": datetime.utcnow().isoformat()
                                })
                
                except Exception as e:
                    error_msg = f"Error processing {url}: {str(e)}"
                    job_data["errors"].append({
                        "url": url,
                        "error": error_msg,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                
                # Update activity timestamp
                active_jobs[job_id]["last_activity"] = datetime.utcnow().isoformat()
                
                # Small delay between requests
                await asyncio.sleep(1)
        
        # Mark job as completed
        if job_data["status"] != "cancelled":
            if len(job_data["errors"]) == 0:
                job_data["status"] = "completed"
            else:
                job_data["status"] = "completed_with_errors" if job_data["completed_urls"] > 0 else "failed"
        
        job_data["completed_at"] = datetime.utcnow().isoformat()
        
    except Exception as e:
        # Mark job as failed
        active_jobs[job_id]["status"] = "failed"
        active_jobs[job_id]["error"] = str(e)
        active_jobs[job_id]["failed_at"] = datetime.utcnow().isoformat()


def create_dashboard_template():
    """Create the HTML template for the dashboard"""
    # Template already exists in templates/dashboard.html
    template_path = templates_dir / "dashboard.html"
    if template_path.exists():
        print(f"✅ Dashboard template found at {template_path}")
    else:
        print(f"❌ Dashboard template missing at {template_path}")
        print("   Please ensure templates/dashboard.html exists")
    return template_path.exists()


def main():
    """Main entry point for the dashboard"""
    import uvicorn
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    # Ensure template exists
    create_dashboard_template()
    
    host = os.getenv("DASHBOARD_HOST", "0.0.0.0")
    port = int(os.getenv("DASHBOARD_PORT", "8000"))
    
    print("🕷️  Firecrawl Monitoring Dashboard")
    print("=" * 50)
    print(f"Firecrawl API URL: {os.getenv('FIRECRAWL_API_URL', 'http://localhost:3002')}")
    print(f"Dashboard URL: http://{host}:{port}")
    print(f"Update Interval: {os.getenv('UPDATE_INTERVAL', '5')} seconds")
    print("=" * 50)
    
    uvicorn.run(
        app, 
        host=host, 
        port=port,
        reload=False,
        access_log=True
    )

if __name__ == "__main__":
    main()
