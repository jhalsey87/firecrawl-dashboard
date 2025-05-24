#!/usr/bin/env python3
"""
Debug script to test Firecrawl health endpoint directly
"""

import asyncio
import aiohttp
import json
from pathlib import Path
import sys
import os

# Add project root to path for .env loading
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv(project_root / ".env")

FIRECRAWL_API_URL = os.getenv("FIRECRAWL_API_URL", "http://localhost:3002")
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY", "dummy")

async def debug_health():
    print("🔍 Debugging Firecrawl Health Check")
    print("=" * 50)
    print(f"Testing URL: {FIRECRAWL_API_URL}")
    print(f"API Key: {FIRECRAWL_API_KEY}")
    print()
    
    try:
        async with aiohttp.ClientSession() as session:
            headers = {}
            if FIRECRAWL_API_KEY and FIRECRAWL_API_KEY != "dummy":
                headers["Authorization"] = f"Bearer {FIRECRAWL_API_KEY}"
            
            print("🌐 Testing /health endpoint...")
            try:
                async with session.get(f"{FIRECRAWL_API_URL}/health", headers=headers, timeout=10) as response:
                    print(f"Status Code: {response.status}")
                    print(f"Headers: {dict(response.headers)}")
                    print(f"Content Type: {response.content_type}")
                    
                    if response.content_type == 'application/json':
                        data = await response.json()
                        print(f"Response Data: {json.dumps(data, indent=2)}")
                    else:
                        text = await response.text()
                        print(f"Response Text: {text[:500]}...")
                        
                    if response.status == 200:
                        print("✅ Health endpoint is working!")
                    else:
                        print(f"❌ Health endpoint returned status {response.status}")
                        
            except asyncio.TimeoutError:
                print("❌ Request timed out after 10 seconds")
            except Exception as e:
                print(f"❌ Error connecting: {e}")
            
            print("\n🧪 Testing basic connectivity...")
            try:
                async with session.get(f"{FIRECRAWL_API_URL}", headers=headers, timeout=5) as response:
                    print(f"Base URL Status: {response.status}")
                    if response.status == 200:
                        print("✅ Base URL is accessible")
                    else:
                        print(f"⚠️ Base URL returned {response.status}")
            except Exception as e:
                print(f"❌ Base URL failed: {e}")
            
            print("\n🔍 Testing alternative health endpoints...")
            for endpoint in ["/health", "/healthcheck", "/status", "/"]:
                try:
                    async with session.get(f"{FIRECRAWL_API_URL}{endpoint}", headers=headers, timeout=5) as response:
                        print(f"{endpoint}: {response.status}")
                except Exception as e:
                    print(f"{endpoint}: Error - {e}")
                    
    except Exception as e:
        print(f"💥 Overall error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_health())
