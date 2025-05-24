#!/usr/bin/env python3
"""
Firecrawl Monitoring Dashboard Entry Point

A simple FastAPI dashboard for monitoring Firecrawl instances.
Run with: python run_dashboard.py
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from firecrawl_dashboard.main import app, create_dashboard_template
import uvicorn

if __name__ == "__main__":
    # Ensure template exists
    create_dashboard_template()
    
    # Load config
    from dotenv import load_dotenv
    load_dotenv()
    
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
