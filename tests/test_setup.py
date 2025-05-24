#!/usr/bin/env python3
"""
Test script to verify the Firecrawl Dashboard setup
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
project_root = Path(__file__).parent.parent
src_dir = project_root / "src"
sys.path.insert(0, str(src_dir))

def test_setup():
    """Test the dashboard setup"""
    print("🧪 Testing Firecrawl Dashboard Setup")
    print("=" * 40)
    
    # Test 1: Check files exist
    required_files = [
        "src/firecrawl_dashboard/main.py",
        "run_dashboard.py", 
        "requirements.txt",
        ".env",
        "src/firecrawl_dashboard/templates/dashboard.html"
    ]
    
    print("\n📁 Checking required files...")
    for file in required_files:
        file_path = project_root / file
        if file_path.exists():
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} - MISSING!")
            return False
    
    # Test 2: Check imports
    print("\n📦 Testing imports...")
    try:
        from firecrawl_dashboard.main import app, create_dashboard_template
        print("  ✅ FastAPI app import successful")
    except Exception as e:
        print(f"  ❌ Import failed: {e}")
        return False
    
    # Test 3: Check template
    print("\n🎨 Checking template...")
    result = create_dashboard_template()
    if result:
        print("  ✅ Template verification passed")
    else:
        print("  ❌ Template verification failed")
        return False
    
    # Test 4: Check environment variables
    print("\n🔧 Checking configuration...")
    from dotenv import load_dotenv
    load_dotenv()
    
    api_url = os.getenv("FIRECRAWL_API_URL")
    if api_url:
        print(f"  ✅ FIRECRAWL_API_URL: {api_url}")
    else:
        print("  ⚠️  FIRECRAWL_API_URL not set")
    
    dashboard_port = os.getenv("DASHBOARD_PORT", "8000")
    print(f"  ✅ Dashboard will run on port: {dashboard_port}")
    
    print("\n🎉 Setup test completed successfully!")
    print("\n🚀 To start the dashboard, run:")
    print("   uv run python run_dashboard.py")
    print(f"\n🌐 Then open: http://localhost:{dashboard_port}")
    
    return True

if __name__ == "__main__":
    try:
        success = test_setup()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        sys.exit(1)
