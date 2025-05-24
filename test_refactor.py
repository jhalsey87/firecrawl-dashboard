#!/usr/bin/env python3
"""
Test script to verify the refactoring works correctly
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

try:
    # Test config import
    from firecrawl_dashboard.config import settings
    print(f"✅ Config loaded - Firecrawl URL: {settings.firecrawl_api_url}")
    print(f"✅ Config loaded - Redis: {settings.redis_host}:{settings.redis_port}")
    
    # Test service imports
    from firecrawl_dashboard.services.redis_service import RedisService
    from firecrawl_dashboard.services.health_service import HealthService
    from firecrawl_dashboard.services.job_service import JobService
    print("✅ All services imported successfully")
    
    # Test model imports
    from firecrawl_dashboard.models import DetailedJob, JobStatus, JobType
    print("✅ Models imported successfully")
    
    # Test service instantiation
    redis_service = RedisService()
    health_service = HealthService()
    job_service = JobService(redis_service)
    print("✅ All services instantiated successfully")
    
    # Test job creation
    job = job_service.create_job("scrape", ["https://example.com"])
    print(f"✅ Job created: {job.job_id} ({job.job_type.value})")
    
    print("\n🎉 Refactoring Stage 2 completed successfully!")
    print("✨ New structure:")
    print("  - Config management ✅")
    print("  - Data models ✅") 
    print("  - Redis service ✅")
    print("  - Health service ✅")
    print("  - Job service ✅")
    print("\n🚀 Ready for enhanced job tracking implementation!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
