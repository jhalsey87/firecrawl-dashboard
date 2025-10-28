# Firecrawl Dashboard Docker Setup

## Overview

Successfully created Docker image for the Firecrawl Monitoring Dashboard to work with your self-hosted Firecrawl instance.

## Files Created

1. **Dockerfile** - Multi-stage build for Python 3.12 dashboard
2. **docker-compose.yml** - Standalone dashboard orchestration
3. **.env** - Environment configuration for Docker deployment

## Docker Image Details

**Image Name**: `firecrawl-dashboard:latest`
**Size**: ~479MB
**Base**: Python 3.12-slim
**Package Manager**: uv (Astral UV)

## Quick Start

### Option 1: Standalone Dashboard (Connect to Running Firecrawl)

If you already have Firecrawl running on your system:

```bash
cd firecrawl-dashboard

# Start the dashboard
docker-compose up -d

# View logs
docker-compose logs -f dashboard

# Stop the dashboard
docker-compose down
```

**Access the dashboard:**
- Enhanced Dashboard: http://localhost:8000/
- Classic Dashboard: http://localhost:8000/classic

### Option 2: Integrated with Firecrawl Services

To run the dashboard alongside Firecrawl in the same network:

1. Update your main Firecrawl `docker-compose.yaml` to add the dashboard service
2. Or connect to the Firecrawl backend network

## Configuration

### Environment Variables

The `.env` file is pre-configured to work with your Firecrawl setup:

```bash
# Firecrawl Connection
FIRECRAWL_API_URL=http://host.docker.internal:3002  # Connects to Firecrawl on host
FIRECRAWL_API_KEY=fc-test-key

# Redis Connection (for queue monitoring)
REDIS_HOST=host.docker.internal
REDIS_PORT=6379
REDIS_DB=0

# Dashboard Settings
DASHBOARD_HOST=0.0.0.0
DASHBOARD_PORT=8000
UPDATE_INTERVAL=5  # Auto-refresh interval in seconds

# Local AI (Ollama)
OLLAMA_MODEL=llama3.2:3b
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

### Connecting to Firecrawl Network

If you want the dashboard to run in the same Docker network as Firecrawl:

**Update `.env`:**
```bash
FIRECRAWL_API_URL=http://api:3002  # Use service name instead of host.docker.internal
REDIS_HOST=redis
```

**Update `docker-compose.yml`:**
```yaml
services:
  dashboard:
    # ... existing config ...
    networks:
      - firecrawl_backend  # Connect to Firecrawl's network

networks:
  firecrawl_backend:
    external: true  # Use existing Firecrawl network
```

## Features

### Enhanced Dashboard (Default)
- Real-time job monitoring with expandable cards
- Live progress bars and current URL tracking
- Comprehensive health checking
- Job creation interface
- Individual and bulk job cancellation
- Auto-refresh mode
- Performance metrics

### Classic Dashboard
- Simple list view of all jobs
- Basic job status and details
- Lightweight alternative interface

## Health Checks

The container includes a built-in health check:
- Interval: 30 seconds
- Timeout: 10 seconds
- Start period: 5 seconds
- Retries: 3

Check health status:
```bash
docker ps  # Look for "(healthy)" status
docker inspect firecrawl-dashboard | grep Health -A 10
```

## Troubleshooting

### Dashboard can't connect to Firecrawl

**Symptom**: Dashboard loads but shows connection errors

**Solution 1** - Check Firecrawl is running:
```bash
curl http://localhost:3002/
```

**Solution 2** - Verify network connectivity:
```bash
docker exec firecrawl-dashboard curl http://host.docker.internal:3002/
```

**Solution 3** - Check environment variables:
```bash
docker exec firecrawl-dashboard env | grep FIRECRAWL
```

### Redis connection issues

**Symptom**: Queue status shows "Connection error"

**Solution**: Ensure Redis is accessible:
```bash
# Test Redis connection from dashboard container
docker exec firecrawl-dashboard nc -zv host.docker.internal 6379
```

If Firecrawl's Redis is not exposed on port 6379, you need to either:
1. Expose Redis port in Firecrawl's docker-compose
2. Run dashboard in same network as Firecrawl

### Port 8000 already in use

**Solution**: Change the port mapping in `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Use port 8001 on host instead
```

Then access at http://localhost:8001/

## Building from Source

To rebuild the image after making changes:

```bash
cd firecrawl-dashboard

# Rebuild without cache
docker-compose build --no-cache

# Restart with new image
docker-compose down
docker-compose up -d
```

## Accessing Dashboard Features

### Creating Jobs

1. Navigate to the Enhanced Dashboard (http://localhost:8000/)
2. Use the "Create New Job" form
3. Select job type (scrape or crawl)
4. Enter URLs (one per line)
5. Set page limit
6. Click "Start Job"

### Monitoring Jobs

**Active Jobs Section:**
- Shows currently running jobs
- Live progress bars
- Cancel individual or all jobs
- Expand for detailed info

**Recent Jobs Section:**
- Shows completed/failed jobs
- View final statistics
- Click eye icon for full details

### Health Monitoring

**Health Status Card:**
- Shows real-time API health
- Response time metrics
- Click "Test" for full health check

**Metrics Cards:**
- Active Jobs count
- Success rate percentage
- Redis queue status

## Integration with n8n

If you're using n8n workflows with Firecrawl, the dashboard will show:
- Jobs created by n8n workflows
- Real-time progress of n8n-triggered crawls
- Success/failure status for automation monitoring

## Advanced Configuration

### Custom Update Interval

Modify in `.env`:
```bash
UPDATE_INTERVAL=10  # Update every 10 seconds instead of 5
```

### Disable Auto-Scrape Testing

If you don't want the dashboard to run test scrapes:
```bash
ENABLE_AUTO_SCRAPE_TEST=false
```

### Custom Firecrawl Parameters

The dashboard uses these defaults for test scrapes:
```bash
FIRECRAWL_FORMATS=markdown,html
FIRECRAWL_ONLY_MAIN_CONTENT=true
FIRECRAWL_WAIT_FOR=3000
FIRECRAWL_TIMEOUT=30
FIRECRAWL_MAX_URLS_PER_SITE=10
```

## Resources

- **Dashboard Repository**: https://github.com/cbl789/firecrawl-dashboard
- **Firecrawl Docs**: https://docs.firecrawl.dev
- **Your Firecrawl Instance**: http://localhost:3002

## Summary

✅ **Docker Image Created**: `firecrawl-dashboard:latest`
✅ **Container Running**: `firecrawl-dashboard` (port 8000)
✅ **Health Status**: Healthy
✅ **Connected to**: Firecrawl API at localhost:3002
✅ **Monitoring**: Redis queue and job status

**Access your dashboard at**: http://localhost:8000/

---

*Created: October 28, 2025*
*Image Built: Successfully*
*Status: Operational*
