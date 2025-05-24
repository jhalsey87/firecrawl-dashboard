#!/bin/bash
# Firecrawl Dashboard Management Script

PROJECT_DIR="/Users/christian/coding/firecrawl-dashboard"

case "$1" in
    "start")
        echo "🚀 Starting Firecrawl Dashboard..."
        cd "$PROJECT_DIR"
        uv run run_dashboard.py
        ;;
    "stop")
        echo "🛑 Stopping Firecrawl Dashboard..."
        cd "$PROJECT_DIR"
        echo "⚠️  Using safe cleanup (only targets dashboard processes)"
        ./scripts/cleanup.sh
        ;;
    "restart")
        echo "🔄 Restarting Firecrawl Dashboard..."
        cd "$PROJECT_DIR"
        echo "⚠️  Using safe cleanup (only targets dashboard processes)"
        ./scripts/cleanup.sh
        echo "⏳ Waiting 2 seconds..."
        sleep 2
        uv run run_dashboard.py
        ;;
    "status")
        echo "📊 Dashboard Status:"
        for port in 8000 8001 8002; do
            pid=$(lsof -ti :$port 2>/dev/null)
            if [ ! -z "$pid" ]; then
                echo "  ✅ Running on port $port (PID: $pid)"
            else
                echo "  ❌ Port $port is free"
            fi
        done
        ;;
    *)
        echo "🕷️  Firecrawl Dashboard Manager"
        echo "Usage: $0 {start|stop|restart|status}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the dashboard"
        echo "  stop    - Stop all dashboard processes"
        echo "  restart - Stop and start the dashboard"
        echo "  status  - Check dashboard status"
        exit 1
        ;;
esac
