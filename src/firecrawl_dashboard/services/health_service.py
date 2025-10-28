"""
Health monitoring service for Firecrawl Dashboard
"""

import aiohttp
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional

from ..config import settings


class HealthService:
    """Service for monitoring Firecrawl health status"""
    
    def __init__(self):
        self.last_check: Optional[datetime] = None
        self.last_status: Dict[str, Any] = {}
    
    async def get_basic_health(self) -> Dict[str, Any]:
        """Get basic health status (fast check)"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = settings.firecrawl_headers
                start_time = datetime.now()
                
                async with session.get(
                    f"{settings.firecrawl_api_url}/", 
                    headers=headers, 
                    timeout=10
                ) as response:
                    response_time = (datetime.now() - start_time).total_seconds() * 1000
                    text_response = await response.text()
                    
                    # Check if Firecrawl is responding correctly
                    if response.status == 200 and ("SCRAPERS" in text_response or "Hello" in text_response):
                        status = {
                            "status": "healthy",
                            "status_code": response.status,
                            "response_time_ms": round(response_time, 2),
                            "timestamp": datetime.utcnow().isoformat(),
                            "message": "Firecrawl service is responding"
                        }
                    else:
                        status = {
                            "status": "unhealthy",
                            "status_code": response.status,
                            "response_time_ms": round(response_time, 2),
                            "timestamp": datetime.utcnow().isoformat(),
                            "message": f"Unexpected response: {text_response[:50]}..."
                        }
                        
        except asyncio.TimeoutError:
            status = {
                "status": "timeout",
                "status_code": 408,
                "response_time_ms": 10000,
                "timestamp": datetime.utcnow().isoformat(),
                "error": "Request timeout"
            }
        except Exception as e:
            status = {
                "status": "error",
                "status_code": 500,
                "response_time_ms": 0,
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
        
        self.last_check = datetime.utcnow()
        self.last_status = status
        return status
    
    async def get_full_health_status(self) -> Dict[str, Any]:
        """Get comprehensive Firecrawl health status including scrape test"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = settings.firecrawl_headers
                
                # Check base URL first (Firecrawl doesn't have /health)
                start_time = datetime.now()
                try:
                    async with session.get(f"{settings.firecrawl_api_url}/", headers=headers, timeout=10) as response:
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
                    async with session.post(f"{settings.firecrawl_api_url}/v2/scrape", 
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
