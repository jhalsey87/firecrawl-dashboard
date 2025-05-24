#!/bin/bash
# Safe Firecrawl Dashboard Process Cleanup
# Only targets processes specifically running our dashboard

echo "🔍 Safely checking for Firecrawl dashboard processes..."

# Only target processes using specific dashboard ports
for port in 8000 8001 8002 8003; do
    pid=$(lsof -ti :$port 2>/dev/null)
    if [ ! -z "$pid" ]; then
        # Check if this is actually our dashboard process
        process_cmd=$(ps -p $pid -o command= 2>/dev/null)
        if [[ "$process_cmd" == *"run_dashboard.py"* ]] || [[ "$process_cmd" == *"firecrawl_dashboard"* ]]; then
            echo "🛑 Killing dashboard process $pid on port $port"
            echo "   Command: $process_cmd"
            kill $pid
            sleep 1
            # Force kill if still running
            if kill -0 $pid 2>/dev/null; then
                echo "⚠️  Force killing process $pid"
                kill -9 $pid
            fi
        else
            echo "⚠️  Port $port is used by non-dashboard process (PID: $pid)"
            echo "   Command: $process_cmd"
            echo "   Skipping to avoid killing other services"
        fi
    fi
done

# Only target very specific dashboard processes
dashboard_pids=$(ps aux | grep -E "run_dashboard\.py|firecrawl_dashboard/main\.py" | grep -v grep | awk '{print $2}')
if [ ! -z "$dashboard_pids" ]; then
    echo "🛑 Killing specific dashboard processes: $dashboard_pids"
    for pid in $dashboard_pids; do
        process_cmd=$(ps -p $pid -o command= 2>/dev/null)
        echo "   Killing PID $pid: $process_cmd"
        kill $pid 2>/dev/null
    done
fi

echo "✅ Safe dashboard cleanup complete!"
echo "💡 Only targeted Firecrawl dashboard processes"
