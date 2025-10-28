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

# Import our new configuration and services
from .config import settings
from .services.redis_service import RedisService
from .services.health_service import HealthService
from .services.job_service import JobService
from .services.job_processing_service import JobProcessingService
from .services.metrics_service import MetricsService

# Configuration from settings
FIRECRAWL_API_URL = settings.firecrawl_api_url
FIRECRAWL_API_KEY = settings.firecrawl_api_key
DASHBOARD_HOST = settings.dashboard_host
DASHBOARD_PORT = settings.dashboard_port
UPDATE_INTERVAL = settings.update_interval

# Global storage for job tracking (in production, use Redis or database)
active_jobs: Dict[str, Dict[str, Any]] = {}
job_counter = 0

# Initialize services
redis_service = RedisService()
health_service = HealthService()
job_service = JobService(redis_service)
job_processing_service = JobProcessingService(active_jobs, job_service)
metrics_service = MetricsService(active_jobs)

# Initialize FastAPI app
app = FastAPI(title="Firecrawl Monitoring Dashboard")

# Set up templates directory
templates_dir = Path(__file__).parent / "templates"
templates_dir.mkdir(exist_ok=True)
templates = Jinja2Templates(directory=str(templates_dir))


@app.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request):
    """Enhanced dashboard page with expandable job cards"""
    return templates.TemplateResponse("enhanced_dashboard.html", {"request": request})


@app.get("/classic", response_class=HTMLResponse)
async def dashboard_classic(request: Request):
    """Classic dashboard page"""
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/jobs/{job_id}/data", response_class=HTMLResponse)
async def job_data_viewer(request: Request, job_id: str):
    """View scraped data for a specific job"""
    return templates.TemplateResponse("job_data_viewer.html", {
        "request": request,
        "job_id": job_id
    })


@app.get("/api/health")
async def get_health_status():
    """Get current Firecrawl health status using HealthService"""
    try:
        health_status = await health_service.get_basic_health()
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
    """Get comprehensive Firecrawl health status including scrape test using HealthService"""
    return await health_service.get_full_health_status()


@app.get("/api/queue")
async def get_queue_status():
    """Get Redis queue status using RedisService"""
    return await redis_service.get_queue_status()


@app.delete("/api/queue")
async def clear_redis_queues():
    """Emergency: Clear all Redis queues using RedisService"""
    result = await redis_service.clear_all_queues()
    if result.get("success"):
        return result
    else:
        return JSONResponse(
            status_code=500 if "error" in result else 503,
            content=result
        )


@app.get("/api/jobs")
async def get_jobs():
    """Get list of active and recent jobs using JobService"""
    try:
        # Get enhanced jobs from JobService
        enhanced_jobs = await job_service.get_enhanced_jobs()

        # Convert to legacy format for backward compatibility
        jobs_data = [job.to_dict() for job in enhanced_jobs]

        # Separate active and recent jobs
        active_jobs_list = []
        recent_jobs_list = []

        for job in jobs_data:
            if job.get("status") in ["running", "queued", "active", "processing", "waiting", "scraping"]:
                active_jobs_list.append(job)
            else:
                recent_jobs_list.append(job)

        # Sort by creation time (newest first)
        active_jobs_list.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        recent_jobs_list.sort(key=lambda x: x.get("created_at", ""), reverse=True)

        return {
            "active_jobs": active_jobs_list[:50],  # Increased from 20 to show more jobs
            "recent_jobs": recent_jobs_list[:50],  # Increased from 20 to show more jobs
            "queue_count": len([j for j in jobs_data if j.get("source") == "redis_queue"]),
            "dashboard_count": len([j for j in jobs_data if j.get("source") == "dashboard"]),
            "firecrawl_count": 0  # Can be enhanced later
        }
    except Exception as e:
        return {
            "active_jobs": [],
            "recent_jobs": [],
            "queue_count": 0,
            "dashboard_count": 0,
            "firecrawl_count": 0,
            "error": str(e)
        }


@app.get("/api/jobs/{job_id}")
async def get_job_details(job_id: str):
    """Get detailed information about a specific job using JobService"""
    enhanced_job = await job_service.get_job_details_enhanced(job_id)

    if not enhanced_job:
        raise HTTPException(status_code=404, detail="Job not found")

    return enhanced_job


@app.get("/api/jobs/{job_id}/data")
async def get_job_scraped_data(job_id: str, skip: int = 0, limit: int = 100):
    """Get scraped data for a crawl job from Firecrawl API"""
    try:
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {FIRECRAWL_API_KEY}"} if FIRECRAWL_API_KEY and FIRECRAWL_API_KEY != "dummy" else {}

            # Try to fetch scraped data from Firecrawl API
            url = f"{FIRECRAWL_API_URL}/v2/crawl/{job_id}?skip={skip}&limit={limit}"
            async with session.get(url, headers=headers, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "job_id": job_id,
                        "status": data.get("status"),
                        "total": data.get("total", 0),
                        "completed": data.get("completed", 0),
                        "data": data.get("data", []),
                        "next": data.get("next"),
                        "has_more": len(data.get("data", [])) > 0
                    }
                elif response.status == 404:
                    return JSONResponse(
                        status_code=404,
                        content={
                            "success": False,
                            "error": "Job not found or data expired",
                            "message": "Scraped data may have expired (TTL: 24 hours) or the job never existed"
                        }
                    )
                else:
                    return JSONResponse(
                        status_code=response.status,
                        content={
                            "success": False,
                            "error": f"Failed to fetch data: HTTP {response.status}"
                        }
                    )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )


@app.get("/api/metrics")
async def get_metrics():
    """Get performance metrics using MetricsService"""
    return metrics_service.get_performance_metrics()


@app.post("/api/jobs/start")
async def start_crawl_job(
    urls: str = Form(...),
    limit: int = Form(default=10),
    job_type: str = Form(default="crawl")
):
    """Start a new crawl job using JobService"""
    try:
        # Parse URLs
        url_list = [url.strip() for url in urls.split('\n') if url.strip()]
        if not url_list:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "No valid URLs provided"}
            )
        
        # Create job using JobService
        job = job_service.start_crawl_job(url_list, job_type, limit)
        print(f"📝 Created job {job.job_id} with JobService")

        # Also add to global active_jobs for job_processing_service
        active_jobs[job.job_id] = {
            "job_id": job.job_id,
            "status": job.status.value,
            "job_type": job.job_type.value,
            "urls": url_list,
            "limit": limit,
            "created_at": job.created_at.isoformat(),
            "started_at": None,
            "completed_at": None,
            "completed_urls": 0,
            "total_urls": len(url_list),
            "errors": [],
            "processed_urls": []
        }
        print(f"📊 Added job {job.job_id} to global active_jobs dictionary")
        print(f"   Active jobs now: {list(active_jobs.keys())}")

        # Start background processing task
        print(f"🎬 Starting background task for job {job.job_id}")
        task = asyncio.create_task(job_processing_service.process_crawl_job(job.job_id))
        print(f"✅ Background task created: {task}")
        
        return {
            "success": True,
            "job_id": job.job_id,
            "message": f"Started {job_type} job with {len(url_list)} URLs"
        }
        
    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": str(e)}
        )
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
            
            # Try different endpoints to cancel the job (v2 first, then v1, v0)
            for endpoint in [f"/v2/crawl/{job_id}", f"/v1/crawl/{job_id}", f"/v0/crawl/{job_id}", f"/crawl/{job_id}"]:
                try:
                    async with session.delete(f"{FIRECRAWL_API_URL}{endpoint}", headers=headers, timeout=30) as response:
                        if response.status == 200:
                            return {"success": True, "message": "External job cancelled successfully"}
                        elif response.status == 404:
                            continue  # Try next endpoint
                        else:
                            # Try PATCH with status update
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


def create_dashboard_template():
    """Create the HTML template for the dashboard"""
    # Template already exists in templates/dashboard.html
    template_path = templates_dir / "dashboard.html"
    enhanced_template_path = templates_dir / "enhanced_dashboard.html"
    
    if template_path.exists():
        print(f"✅ Classic dashboard template found at {template_path}")
    else:
        print(f"❌ Classic dashboard template missing at {template_path}")
    
    if enhanced_template_path.exists():
        print(f"✅ Enhanced dashboard template found at {enhanced_template_path}")
    else:
        print(f"❌ Enhanced dashboard template missing at {enhanced_template_path}")
    
    return template_path.exists() or enhanced_template_path.exists()


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
    print(f"Enhanced Dashboard: http://{host}:{port}/")
    print(f"Classic Dashboard: http://{host}:{port}/classic")
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
