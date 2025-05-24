#!/usr/bin/env python3
"""
Firecrawl Monitoring Dashboard Entry Point

A simple FastAPI dashboard for monitoring Firecrawl instances.
Run with: python run_dashboard.py
"""

import os
import sys
import signal
import asyncio
from pathlib import Path

# Add the src directory to the Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from firecrawl_dashboard.main import app, create_dashboard_template
import uvicorn

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    print(f"\n🛑 Received signal {signum}. Shutting down gracefully...")
    sys.exit(0)

def find_free_port(start_port=8000, max_attempts=10):
    """Find a free port starting from start_port"""
    import socket
    
    for i in range(max_attempts):
        port = start_port + i
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    
    raise RuntimeError(f"Could not find a free port in range {start_port}-{start_port + max_attempts}")

if __name__ == "__main__":
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Ensure template exists
    create_dashboard_template()
    
    # Load config
    from dotenv import load_dotenv
    load_dotenv()
    
    host = os.getenv("DASHBOARD_HOST", "0.0.0.0")
    
    # Try to find a free port
    try:
        preferred_port = int(os.getenv("DASHBOARD_PORT", "8000"))
        port = find_free_port(preferred_port)
        
        if port != preferred_port:
            print(f"⚠️  Port {preferred_port} is busy, using port {port} instead")
    except RuntimeError as e:
        print(f"❌ {e}")
        sys.exit(1)
    
    print("🕷️  Firecrawl Monitoring Dashboard")
    print("=" * 50)
    print(f"Firecrawl API URL: {os.getenv('FIRECRAWL_API_URL', 'http://localhost:3002')}")
    print(f"Enhanced Dashboard: http://{host}:{port}/")
    print(f"Classic Dashboard: http://{host}:{port}/classic")
    print(f"Update Interval: {os.getenv('UPDATE_INTERVAL', '5')} seconds")
    print("=" * 50)
    print("💡 Press Ctrl+C to stop the server")
    
    try:
        uvicorn.run(
            app, 
            host=host, 
            port=port,
            reload=False,
            access_log=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
    finally:
        print("🔄 Cleaning up...")
