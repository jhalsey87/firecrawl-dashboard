#!/bin/bash
# Recovery script for accidentally killed processes

echo "🔄 Process Recovery Helper"
echo "=========================="
echo ""
echo "I apologize for the overly aggressive cleanup that may have killed your other processes."
echo "Here are some commands to help restart common services:"
echo ""

echo "🐳 Docker Services:"
echo "   # Restart Docker Desktop (if it was killed)"
echo "   open -a Docker"
echo "   # Or restart Docker daemon"
echo "   sudo launchctl kickstart -k system/com.docker.dockerd"
echo ""

echo "💻 VS Code:"
echo "   # Restart VS Code"
echo "   code ."
echo "   # Or open specific project"
echo "   code /path/to/your/project"
echo ""

echo "📊 Common Development Services:"
echo "   # If you had any local servers running, you may need to restart them"
echo "   # Check what processes are running:"
echo "   ps aux | grep -E '(node|python|docker|code)' | grep -v grep"
echo ""

echo "🔍 Check Docker Status:"
docker --version 2>/dev/null && echo "✅ Docker is available" || echo "❌ Docker may need to be restarted"
echo ""

echo "🔍 Check VS Code:"
which code >/dev/null 2>&1 && echo "✅ VS Code command is available" || echo "❌ VS Code may need to be restarted"
echo ""

echo "💡 If any services are not working, please restart them manually."
echo "   The cleanup script has been fixed to be much more targeted."
