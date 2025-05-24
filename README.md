# 🕷️ Firecrawl Monitoring Dashboard

> A comprehensive web-based monitoring dashboard for self-hosted Firecrawl instances

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Self-hosted Firecrawl instances don't come with a built-in web interface. This dashboard fills that gap by providing real-time monitoring, job management, and health checking capabilities through a modern, responsive web interface.

## 🌟 Features

- **🏥 Real-time Health Monitoring** - Continuous monitoring with auto-refresh dashboard
- **📊 Job Management** - Start, monitor, and cancel scrape/crawl jobs from the web interface  
- **📈 Performance Metrics** - Track success rates, response times, and job statistics
- **🎯 Manual Testing** - Run comprehensive health checks including live scrape testing
- **⚡ Live Updates** - Dashboard auto-refreshes with configurable intervals
- **🔄 Queue Monitoring** - Direct connection to Firecrawl's Redis Bull queues for comprehensive job visibility
- **🚨 Flood Detection** - Automatic detection and emergency controls for runaway job queues
- **🎨 Modern Interface** - Responsive design with TailwindCSS and HTMX
- **🛠️ Debug Tools** - Built-in utilities for troubleshooting and diagnostics

## 🚀 Quick Start

### Prerequisites

- **Python 3.12+** (required)
- **Running Firecrawl instance** (self-hosted)
- **Access to Firecrawl's Redis instance** (for queue monitoring and job control)
- **uv** package manager (recommended) or pip

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd firecrawl-dashboard
   ```

2. **Install dependencies using uv (recommended):**
   ```bash
   uv sync
   ```
   
   **Or using pip:**
   ```bash
   pip install -e .
   ```

3. **Configure your environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your Firecrawl settings
   ```

4. **Start the dashboard:**
   ```bash
   # Using the CLI entry point
   firecrawl-dashboard
   
   # Or using the run script
   python run_dashboard.py
   
   # Or with uv
   uv run python run_dashboard.py
   ```

5. **Access the dashboard:**
   Open [http://localhost:8000](http://localhost:8000) in your browser

## ⚙️ Configuration

All configuration is managed through environment variables in the `.env` file:

### Core Configuration

```bash
# ===== Firecrawl Core Configuration =====
FIRECRAWL_API_URL=http://localhost:3002    # Your Firecrawl instance URL
FIRECRAWL_API_KEY=dummy                     # API key if authentication enabled

# ===== Redis Configuration (Firecrawl's Redis instance) =====
# Connect to the same Redis instance that Firecrawl uses for job queues
REDIS_HOST=localhost                        # Redis host from your Firecrawl setup
REDIS_PORT=6379                            # Redis port from your Firecrawl setup  
REDIS_DB=0                                 # Redis database (usually 0 for Bull queues)

# ===== Dashboard Configuration =====
DASHBOARD_HOST=0.0.0.0                     # Dashboard bind address
DASHBOARD_PORT=8000                        # Dashboard port
UPDATE_INTERVAL=10                         # Auto-refresh interval (seconds)
ENABLE_AUTO_SCRAPE_TEST=false              # Enable automatic scrape testing
```

### Scraping Parameters

```bash
# ===== Firecrawl Scraping Parameters =====
FIRECRAWL_FORMATS=markdown,html             # Content formats to extract
FIRECRAWL_ONLY_MAIN_CONTENT=true           # Extract main content only
FIRECRAWL_INCLUDE_TAGS=h1,h2,h3,p,code     # HTML tags to include
FIRECRAWL_EXCLUDE_TAGS=nav,footer,header   # HTML tags to exclude
FIRECRAWL_WAIT_FOR=3000                    # Page load wait time (ms)
FIRECRAWL_TIMEOUT=30                       # Request timeout (seconds)
FIRECRAWL_MOBILE=false                     # Use mobile user agent
```

### Crawling & Performance

```bash
# ===== Firecrawl Crawling Parameters =====
FIRECRAWL_MAX_URLS_PER_SITE=10             # Maximum URLs per crawl job

# ===== Client Script Configuration =====
MAX_CONCURRENT_REQUESTS=3                  # Concurrent request limit
DELAY_BETWEEN_BATCHES=2.0                  # Delay between request batches
```

### Complete Configuration Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `FIRECRAWL_API_URL` | `http://localhost:3002` | Firecrawl instance endpoint |
| `FIRECRAWL_API_KEY` | `dummy` | API authentication key |
| `REDIS_HOST` | `localhost` | Firecrawl's Redis server host (same Redis that Firecrawl uses) |
| `REDIS_PORT` | `6379` | Firecrawl's Redis server port |
| `REDIS_DB` | `0` | Redis database number (Bull queues typically use DB 0) |
| `DASHBOARD_HOST` | `0.0.0.0` | Dashboard server bind address |
| `DASHBOARD_PORT` | `8000` | Dashboard web interface port |
| `UPDATE_INTERVAL` | `10` | Auto-refresh interval in seconds |
| `ENABLE_AUTO_SCRAPE_TEST` | `false` | Enable automatic scrape testing in health checks |

## 🎯 Usage Guide

### Health Monitoring

The dashboard provides comprehensive health monitoring:

- **🟢 Healthy**: All systems operational, fast response times
- **🟡 Degraded**: System running but with issues or slow responses  
- **🔴 Error**: System unavailable or critical failures

**Health Check Features:**
- Automatic monitoring with configurable refresh intervals
- Basic health checks (fast, non-intrusive)
- Full health checks including live scrape testing
- Response time tracking and performance metrics

### Job Management

#### Starting Jobs

1. **Navigate to Job Controls** section
2. **Enter URLs** (one per line in the text area)
3. **Select Job Type**:
   - **Scrape**: Process individual URLs independently
   - **Crawl**: Follow links and discover additional pages
4. **Set Crawl Limit** (for crawl jobs only)
5. **Click "Start Job"**

#### Job Types Explained

**Scrape Jobs:**
- Process each URL independently
- Fast execution for known URLs
- Best for extracting content from specific pages
- No link following or discovery

**Crawl Jobs:**
- Start from seed URLs and follow links
- Discover additional pages automatically
- Respect the crawl limit setting
- Ideal for exploring websites or sitemaps

#### Monitoring Active Jobs

- **Real-time Progress**: Live progress bars and completion percentages
- **Status Tracking**: See completed vs total URLs
- **Error Monitoring**: Track failed requests and error rates
- **Job Controls**: Cancel running jobs if needed

### Dashboard Sections

#### 🏥 Health Status Panel
- Current service status with color-coded indicators
- Response time metrics and performance tracking
- Manual "Full Test" button for comprehensive checks
- Last update timestamp

#### 📊 Active Jobs Panel  
- List of currently running jobs with progress bars
- Job details: type, URL count, completion status
- Cancel buttons for job management
- Real-time updates without page refresh

#### 🔄 Queue Monitoring Panel
- **Direct Redis Access**: Connects to Firecrawl's Redis instance to monitor Bull job queues
- **Real-time Queue Stats**: Shows active, waiting, and delayed jobs in Firecrawl's queues
- **Flood Detection**: Automatic alerts when queue activity exceeds normal thresholds
- **Emergency Controls**: Built-in tools to clear stuck or runaway job queues
- **Queue Job Visibility**: See jobs that may not appear in the main Firecrawl API

This is particularly useful for detecting and resolving "job floods" where many jobs get stuck in Redis queues, causing performance issues or log spam.

#### 📈 Performance Metrics
- Overall success rate statistics
- Job completion trends
- Error rate tracking
- Historical performance data

#### 🎮 Job Controls
- URL input form for new jobs
- Job type selection (Scrape vs Crawl)
- Crawl limit configuration
- Batch job submission

## 🛠️ API Reference

The dashboard exposes a RESTful API for integration and automation:

### Health Endpoints

| Endpoint | Method | Description | Response |
|----------|--------|-------------|----------|
| `/api/health` | GET | Basic health check (fast) | `{status, response_time, timestamp}` |
| `/api/health/full` | GET | Comprehensive health with scrape test | `{status, response_time, test_results, timestamp}` |

### Job Management Endpoints

| Endpoint | Method | Description | Body/Params |
|----------|--------|-------------|-------------|
| `/api/jobs` | GET | List active and recent jobs | None |
| `/api/jobs/start` | POST | Start new scrape/crawl job | `{urls, job_type, crawl_limit}` |
| `/api/jobs/{job_id}` | DELETE | Cancel running job | None |
| `/api/jobs/{job_id}/status` | GET | Get specific job status | None |

### Metrics Endpoints

| Endpoint | Method | Description | Response |
|----------|--------|-------------|----------|
| `/api/metrics` | GET | Performance metrics and statistics | `{success_rate, avg_response_time, job_counts}` |
| `/api/queue/stats` | GET | Firecrawl Redis queue statistics | `{queue_length, active_jobs, failed_jobs}` |
| `/api/queue` | GET | Get Redis Bull queue status and jobs | `{connected, queues, total_jobs}` |
| `/api/queue` | DELETE | Emergency clear all Redis queues | `{success, cleared_jobs, message}` |

### Example API Usage

```bash
# Check health status
curl http://localhost:8000/api/health

# Start a scrape job
curl -X POST http://localhost:8000/api/jobs/start \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://example.com"], "job_type": "scrape"}'

# Get Redis queue status (connects to Firecrawl's Redis)
curl http://localhost:8000/api/queue

# Emergency clear stuck job queues  
curl -X DELETE http://localhost:8000/api/queue
```

## 🏗️ Project Architecture

```
firecrawl-dashboard/
├── 📦 src/
│   └── firecrawl_dashboard/          # Main application package
│       ├── __init__.py               # Package initialization
│       ├── main.py                   # FastAPI application & endpoints
│       └── templates/                # Jinja2 templates
│           └── dashboard.html        # Main dashboard interface
│
├── 🧪 scripts/                       # Utility and debug scripts
│   ├── debug_health.py               # Health endpoint testing
│   └── emergency_flood_stop.py       # Emergency Redis queue control
│
├── 📚 docs/                          # Project documentation
│   ├── PROJECT_OVERVIEW.md           # High-level project overview
│   ├── README.md                     # This comprehensive guide
│   └── *.md                          # Additional technical documentation
│
├── 🔧 tests/                         # Test suite
│   └── test_*.py                     # Unit and integration tests
│
├── ⚙️ Configuration Files
│   ├── pyproject.toml                # Project metadata & dependencies
│   ├── requirements.txt              # Pip-compatible requirements
│   ├── uv.lock                       # Dependency lock file
│   ├── .env.example                  # Environment template
│   └── .env                          # Local environment (create from example)
│
└── 🚀 Entry Points
    ├── run_dashboard.py              # Development entry point
    ├── firecrawl-dashboard           # CLI script (installed)
    └── setup.py                      # Package installation
```

### Technology Stack

- **🐍 Backend**: FastAPI with async/await for high performance
- **🎨 Frontend**: HTML5 + TailwindCSS for responsive design
- **⚡ Interactivity**: HTMX for dynamic updates without JavaScript frameworks
- **🗄️ Storage**: Direct connection to Firecrawl's Redis instance for Bull queue monitoring
- **📡 HTTP Client**: aiohttp for async Firecrawl communication
- **🔧 Template Engine**: Jinja2 for server-side rendering

### Key Design Principles

- **🚀 Performance**: Async operations prevent blocking
- **📱 Responsive**: Mobile-friendly interface design
- **🔄 Real-time**: Live updates with minimal resource usage
- **🛠️ Modular**: Clean separation of concerns
- **📈 Scalable**: Stateless design for easy deployment

## 🔧 Troubleshooting

### Common Issues and Solutions

#### Dashboard Shows "Unhealthy" Status

1. **Verify Firecrawl is running:**
   ```bash
   # Check if Firecrawl is accessible
   curl http://your-firecrawl-host:3002/
   # Expected response: "SCRAPERS-JS: Hello, world!"
   ```

2. **Check network connectivity:**
   ```bash
   # Use the built-in debug script
   python scripts/debug_health.py
   ```

3. **Verify configuration:**
   ```bash
   # Check your .env file
   cat .env | grep FIRECRAWL_API_URL
   ```

#### Jobs Fail to Start

- ✅ Verify `FIRECRAWL_API_URL` is correct and accessible
- ✅ Check `FIRECRAWL_API_KEY` if authentication is enabled
- ✅ Ensure Firecrawl has available workers (check Docker logs)
- ✅ Review error messages in the dashboard interface

#### Redis Connection Issues

**Important**: The dashboard connects to the **same Redis instance** that your Firecrawl installation uses for its job queues (Bull queues).

- ✅ **Find your Firecrawl Redis host**: Check your Firecrawl `docker-compose.yml` for the Redis service configuration
- ✅ **Update REDIS_HOST**: Set this to match your Firecrawl setup:
  - If Redis is in the same docker-compose: `REDIS_HOST=redis`  
  - If on a different host: `REDIS_HOST=192.168.50.51`
  - If local development: `REDIS_HOST=localhost`
- ✅ **Expose Redis port**: You may need to add `ports: ["6379:6379"]` to your Firecrawl Redis service
- ✅ **Test connection**: `redis-cli -h $REDIS_HOST ping` should return "PONG"
- ✅ **Check Bull queues**: `redis-cli -h $REDIS_HOST keys "bull:*"` shows Firecrawl job queues

**Note**: Without Redis connection, you lose queue monitoring and flood detection capabilities, but basic dashboard functionality remains.

#### Performance Issues

- ✅ Reduce `UPDATE_INTERVAL` for less frequent updates
- ✅ Disable `ENABLE_AUTO_SCRAPE_TEST` for faster health checks
- ✅ Check Firecrawl resource allocation and scaling
- ✅ Monitor network latency between dashboard and Firecrawl

### Debug Tools

The project includes several debugging utilities:

```bash
# Test health endpoints directly
python scripts/debug_health.py

# Emergency stop for runaway jobs
python scripts/emergency_flood_stop.py

# Verify complete setup
python -m pytest tests/
```

### Network Diagnostics

| Test | Command | Expected Result |
|------|---------|-----------------|
| Basic connectivity | `curl $FIRECRAWL_API_URL` | "SCRAPERS-JS: Hello, world!" |
| Health endpoint | `curl $FIRECRAWL_API_URL/health` | `{"status": "healthy"}` |
| Redis connectivity | `redis-cli -h $REDIS_HOST ping` | "PONG" |
| Firecrawl Bull queues | `redis-cli -h $REDIS_HOST keys "bull:*"` | List of queue keys |
| Dashboard access | `curl http://localhost:8000/api/health` | Health status JSON |

## 🚀 Deployment

### Development Mode

```bash
# Start with auto-reload for development
python run_dashboard.py
```

### Production Deployment

```bash
# Install production dependencies
uv sync --no-dev

# Run with production ASGI server
uvicorn firecrawl_dashboard.main:app --host 0.0.0.0 --port 8000 --workers 4

# Or use the CLI entry point
firecrawl-dashboard
```

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . .

RUN pip install uv && uv sync --no-dev
EXPOSE 8000

CMD ["uv", "run", "python", "run_dashboard.py"]
```

### Environment-Specific Configuration

**Development:**
```bash
DASHBOARD_HOST=127.0.0.1
UPDATE_INTERVAL=5
ENABLE_AUTO_SCRAPE_TEST=true
```

**Production:**
```bash
DASHBOARD_HOST=0.0.0.0
UPDATE_INTERVAL=30
ENABLE_AUTO_SCRAPE_TEST=false
```

## 🔒 Security Considerations

### Important Security Notes

- 🚨 **No Built-in Authentication**: Dashboard doesn't implement user authentication
- 🌐 **Network Exposure**: Default configuration binds to all interfaces (`0.0.0.0`)
- 🔑 **API Key Security**: Store Firecrawl API keys securely
- 🛡️ **Reverse Proxy**: Consider placing behind nginx/Apache for production

### Recommended Security Measures

1. **Use a Reverse Proxy:**
   ```nginx
   server {
       listen 80;
       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

2. **Firewall Configuration:**
   ```bash
   # Allow dashboard to access Firecrawl's Redis
   ufw allow from 192.168.1.0/24 to any port 6379
   ufw allow from 192.168.1.0/24 to any port 8000
   ```

3. **Environment Security:**
   ```bash
   # Restrict .env file permissions
   chmod 600 .env
   
   # Use environment-specific configurations
   export FIRECRAWL_API_KEY=$(cat /secure/path/api_key)
   ```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run with verbose output
python -m pytest tests/ -v

# Run specific test category
python -m pytest tests/test_setup.py
```

### Manual Testing

```bash
# Test dashboard setup
python tests/test_setup.py

# Debug health endpoints
python scripts/debug_health.py

# Verify API endpoints
curl -s http://localhost:8000/api/health | jq
```

### Test Coverage

The test suite covers:
- ✅ Configuration validation
- ✅ Health endpoint functionality  
- ✅ Job management operations
- ✅ API response validation
- ✅ Error handling scenarios

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Development Setup

1. **Fork and clone the repository**
2. **Set up development environment:**
   ```bash
   uv sync --dev  # Install dev dependencies
   pre-commit install  # Set up code formatting
   ```

3. **Make your changes**
4. **Run tests and formatting:**
   ```bash
   python -m pytest tests/
   black src/
   isort src/
   flake8 src/
   ```

5. **Submit a pull request**

### Code Style

- **Formatting**: Black with 88-character line limit
- **Import Sorting**: isort with black profile
- **Linting**: flake8 for code quality
- **Type Hints**: Encouraged for new code

### Areas for Contribution

- 🎨 UI/UX improvements
- 📊 Additional metrics and visualizations
- 🔧 New debugging tools
- 📚 Documentation enhancements
- 🧪 Test coverage expansion
- 🚀 Performance optimizations

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🆘 Support & Community

### Getting Help

1. **📚 Check Documentation**: Review this README and docs/ folder
2. **🧪 Run Debug Scripts**: Use included diagnostic tools
3. **🔍 Search Issues**: Look for similar problems in GitHub issues
4. **💬 Create Issue**: Provide debug output and configuration details

### Reporting Issues

When reporting issues, please include:

- 🐍 Python version and operating system
- 🔧 Complete `.env` configuration (remove sensitive data)
- 📋 Full error messages and stack traces
- 🔍 Output from `python scripts/debug_health.py`
- 🌐 Firecrawl version and configuration

### Feature Requests

We're always looking to improve! Feel free to request features like:

- 📊 Additional monitoring capabilities
- 🎨 UI/UX enhancements  
- 🔧 New debugging tools
- 📈 Advanced analytics
- 🚀 Performance improvements

## 🌟 Why Use This Dashboard?

Self-hosted Firecrawl instances are powerful but lack a web interface. This creates challenges:

❌ **Without Dashboard:**
- No visibility into job progress
- Difficult to monitor system health
- Manual API calls required for management
- No real-time performance insights
- Complex debugging and troubleshooting

✅ **With Dashboard:**
- 🎯 **Real-time Monitoring**: Live health status and performance metrics
- 📊 **Job Management**: Visual job tracking and control interface
- 🛠️ **Debug Tools**: Built-in diagnostics and troubleshooting utilities  
- 📈 **Performance Insights**: Success rates, response times, and trends
- 🎨 **Professional Interface**: Clean, responsive web-based management
- ⚡ **Instant Feedback**: Real-time updates without page refreshes

Perfect for teams and organizations running their own Firecrawl infrastructure! 🕷️✨

---

**Built with ❤️ for the Firecrawl community**