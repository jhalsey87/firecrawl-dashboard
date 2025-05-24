#!/usr/bin/env python3
"""
🚨 EMERGENCY FLOOD STOPPER - NO REDIS ACCESS NEEDED

Since Redis is not exposed, use this to stop the flood immediately.
"""

import subprocess
import sys

def run_command(cmd, description):
    """Run a command and show result"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} successful")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
        else:
            print(f"❌ {description} failed")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()}")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ {description} error: {e}")
        return False

def emergency_flood_stop():
    """Stop the flood emergency procedure"""
    print("🚨 EMERGENCY FIRECRAWL FLOOD STOPPER")
    print("=" * 50)
    
    # Method 1: Try to clear Redis directly
    print("\n1. 🛑 Attempting to clear Redis queues...")
    if run_command("docker-compose exec redis redis-cli FLUSHALL", "Clear Redis queues"):
        print("🎉 Redis queues cleared! Flood should stop.")
        return True
    
    # Method 2: Restart services
    print("\n2. 🔄 Attempting service restart...")
    if run_command("docker-compose restart", "Restart all services"):
        print("🎉 Services restarted! This may have cleared the flood.")
        return True
    
    # Method 3: Nuclear option
    print("\n3. 💥 Nuclear option - Full reset...")
    print("⚠️  This will stop all services and clear all data!")
    confirm = input("Continue? (type 'YES' to confirm): ")
    
    if confirm == "YES":
        commands = [
            ("docker-compose down", "Stop all services"),
            ("docker-compose up redis -d", "Start only Redis"),
            ("docker-compose exec redis redis-cli FLUSHALL", "Clear all Redis data"),
            ("docker-compose down", "Stop Redis"),
            ("docker-compose up -d", "Start all services clean")
        ]
        
        for cmd, desc in commands:
            if not run_command(cmd, desc):
                print(f"❌ Failed at step: {desc}")
                return False
        
        print("🎉 Full reset complete! Flood should be eliminated.")
        return True
    else:
        print("❌ Emergency stop cancelled")
        return False

if __name__ == "__main__":
    print(__doc__)
    
    # Check if we're in the right directory
    import os
    if not os.path.exists("docker-compose.yaml") and not os.path.exists("docker-compose.yml"):
        print("❌ No docker-compose.yaml found!")
        print("💡 Run this script from your Firecrawl directory")
        sys.exit(1)
    
    success = emergency_flood_stop()
    
    if success:
        print("\n✅ FLOOD STOPPED!")
        print("📊 Check your Firecrawl logs:")
        print("   docker-compose logs worker --tail=20")
        print("\n🚀 Now expose Redis and start dashboard:")
        print("   1. Add 'ports: - \"6379:6379\"' to redis service")
        print("   2. docker-compose up -d")
        print("   3. uv run python run_dashboard.py")
    else:
        print("\n❌ Could not stop flood automatically")
        print("💡 Manual steps:")
        print("   1. docker-compose down")
        print("   2. docker volume rm $(docker volume ls -q | grep redis)")
        print("   3. docker-compose up -d")
