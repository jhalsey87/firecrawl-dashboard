# 🕷️ Firecrawl Monitoring Dashboard

> A comprehensive web-based monitoring dashboard for self-hosted Firecrawl instances with enhanced job tracking and real-time monitoring

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Self-hosted Firecrawl instances don't come with a built-in web interface. This enhanced dashboard fills that gap by providing real-time monitoring, advanced job management with expandable job cards, and comprehensive health checking through a modern, responsive web interface.

## 🌟 Enhanced Features

### 🎯 **Enhanced Job Tracking**
- **Expandable Job Cards**: Click to expand/collapse detailed job information
- **Real-time Progress Bars**: Live progress tracking with percentage completion
- **Current URL Display**: See exactly which URL is being processed
- **Estimated Time to Completion (ETA)**: Smart completion time predictions
- **Processing Rate Metrics**: URLs processed per minute tracking
- **Success Rate Analytics**: Real-time success/failure statistics

### 🚀 **Modern Interface**
- **Auto-refresh Toggle**: 5-second auto-refresh with play/pause controls
- **Modal Job Details**: Comprehensive job information in popup modals
- **Dual Dashboard Modes**: Enhanced (/) and Classic (/classic) views
- **Animated Status Indicators**: Spinning, pulsing visual feedback
- **Responsive Design**: Works perfectly on desktop and mobile

### 🏥 **Advanced Monitoring**
- **Real-time Health Status**: Continuous monitoring with color-coded indicators
- **Performance Metrics Dashboard**: Success rates, response times, and job statistics
- **Redis Queue Integration**: Direct connection to Firecrawl's Bull queues
- **Flood Detection**: Automatic detection and emergency controls for runaway jobs
- **Live Updates**: Dashboard refreshes automatically without page reload

### 🛠️ **Professional Job Management**
- **Individual Job Cancellation**: Cancel specific running jobs
- **Bulk Cancel All**: Emergency stop for all active jobs
- **Job Type Selection**: Scrape vs Crawl with intelligent defaults
- **URL Batch Processing**: Submit multiple URLs at once
- **Error Pattern Analysis**: Track and analyze failure patterns

## 🚀 Quick Start

### Prerequisites

- **Python 3.12+** (required)
- **Running Firecrawl instance** (self-hosted)
- **Access to Firecrawl's Redis instance** (for enhanced queue monitoring)
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

3. **Configure your environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your Firecrawl settings
   ```

4. **Start the dashboard:**
   ```bash
   # Using the management script (recommended)
   ./dashboard.sh start
   
   # Or using uv directly
   uv run run_dashboard.py
   
   # Or using the CLI entry point
   firecrawl-dashboard
   ```

5. **Access the enhanced dashboard:**
   - **Enhanced Dashboard**: [http://localhost:8000/](http://localhost:8000) (with expandable job cards)
   - **Classic Dashboard**: [http://localhost:8000/classic](http://localhost:8000/classic) (original view)

## 🎛️ Dashboard Management

### Easy Management Commands

```bash
# Start the dashboard (finds free port automatically)
./dashboard.sh start

# Stop all dashboard processes safely
./dashboard.sh stop

# Restart cleanly
./dashboard.sh restart

# Check what's running
./dashboard.sh status
```

### Safe Process Management

The dashboard includes intelligent port management:
- ✅ **Automatic Port Detection**: Finds free ports (8000, 8001, 8002, etc.)
- ✅ **Safe Process Cleanup**: Only targets dashboard processes
- ✅ **Graceful Shutdown**: Proper signal handling prevents orphaned processes
- ✅ **Recovery Tools**: Helper scripts for service restoration

### Emergency Cleanup

If you encounter port conflicts:
```bash
# Safe cleanup (only targets dashboard processes)
./scripts/cleanup.sh

# Recovery guidance for other services
./scripts/recovery.sh
```

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
DASHBOARD_PORT=8000                        # Dashboard port (auto-detection available)
UPDATE_INTERVAL=5                          # Auto-refresh interval (seconds)
ENABLE_AUTO_SCRAPE_TEST=false              # Enable automatic scrape testing
```

### Enhanced Features Configuration

```bash
# ===== Enhanced Dashboard Features =====
AUTO_REFRESH_INTERVAL=5                    # Auto-refresh interval (seconds)
EXPANDABLE_CARDS_DEFAULT=true              # Default to expanded job cards
SHOW_PROCESSING_URLS=true                  # Display current processing URL
ENABLE_ETA_CALCULATION=true                # Show estimated completion times
ENABLE_SUCCESS_RATE_TRACKING=true          # Track and display success rates
```

## 🎯 Enhanced Usage Guide

### Expandable Job Cards

The enhanced dashboard features expandable job cards that provide detailed information:

**Card Overview (Collapsed):**
- Job status with animated indicators
- Progress bar with percentage
- URL count and creation time
- Quick action buttons (view, cancel, expand)

**Expanded Details:**
- Complete job timeline (created, started, completed)
- Success rate and error count
- Processing rate and performance metrics
- Individual URL processing status

**Interactive Controls:**
- 👁️ **Eye Icon**: Open detailed modal with comprehensive job information
- ⏹️ **Stop Icon**: Cancel individual running jobs
- 🔽 **Chevron**: Expand/collapse job details inline

### Auto-Refresh Features

- **Toggle Control**: Play/pause auto-refresh with visual feedback
- **Smart Updates**: Only refreshes when data changes
- **Performance Optimized**: Minimal resource usage during refresh
- **Visual Indicators**: Shows when updates are in progress

### Modal Job Details

Click the eye icon to view comprehensive job information:
- **Job Information**: ID, type, status, URL counts
- **Performance Metrics**: Processing rate, ETA, duration
- **Success Analytics**: Success rate, error patterns
- **Timeline Data**: Creation, start, and completion times

### Enhanced Job Management

**Starting Jobs:**
1. Select job type (Scrape for individual URLs, Crawl for site exploration)
2. Set page limit for crawl jobs
3. Enter URLs (one per line, supports batch submission)
4. Click "Start Job" and watch real-time progress

**Monitoring Active Jobs:**
- Live progress bars with percentage completion
- Current URL being processed
- Processing rate (URLs per minute)
- Estimated time to completion
- Real-time error tracking

**Job Controls:**
- Cancel individual jobs without affecting others
- Bulk "Cancel All" for emergency stops
- Safe cancellation with confirmation prompts

## 🏗️ Project Architecture

### Refactored Service Architecture

The dashboard has been completely refactored for better maintainability:

```
firecrawl-dashboard/
├── 📦 src/firecrawl_dashboard/
│   ├── main.py (390 lines - 54% reduction!)   # FastAPI app & endpoints
│   ├── config.py                              # Configuration management
│   ├── models.py                              # Data models & enums
│   ├── services/                              # Service layer architecture
│   │   ├── health_service.py                  # Health monitoring
│   │   ├── redis_service.py                   # Redis/queue management
│   │   ├── job_service.py                     # Job lifecycle management
│   │   ├── job_processing_service.py          # Background processing
│   │   └── metrics_service.py                 # Performance analytics
│   └── templates/
│       ├── enhanced_dashboard.html            # Enhanced UI with expandable cards
│       └── dashboard.html                     # Classic dashboard view
│
├── 🛠️ Management Scripts
│   ├── dashboard.sh                           # Main management script
│   ├── scripts/cleanup.sh                     # Safe process cleanup
│   ├── scripts/recovery.sh                    # Service recovery helper
│   └── run_dashboard.py                       # Enhanced startup script
│
└── 📚 Documentation
    ├── README.md                              # This comprehensive guide
    ├── REFACTORING_PROGRESS.md                # Development history
    └── docs/                                  # Additional documentation
```

### Code Quality Improvements

- ✅ **54% Code Reduction**: From 852 to 390 lines in main.py
- ✅ **Service Architecture**: Clean separation of concerns
- ✅ **Type Safety**: Full type hints with enums and models
- ✅ **Error Handling**: Comprehensive error handling throughout
- ✅ **Performance**: Async/await patterns for optimal performance

## 🔧 API Reference

### Enhanced Job Endpoints

| Endpoint | Method | Description | Enhanced Features |
|----------|--------|-------------|------------------|
| `/api/jobs` | GET | List active and recent jobs | Includes expandable card data |
| `/api/jobs/{job_id}` | GET | Get detailed job information | Enhanced metrics and analytics |
| `/api/jobs/start` | POST | Start new scrape/crawl job | Background processing with live updates |
| `/api/jobs/{job_id}` | DELETE | Cancel specific job | Individual job cancellation |
| `/api/jobs` | DELETE | Cancel all active jobs | Bulk cancellation with detailed results |

### Real-time Monitoring Endpoints

| Endpoint | Method | Description | Real-time Features |
|----------|--------|-------------|-------------------|
| `/api/health` | GET | Basic health check | Animated status indicators |
| `/api/health/full` | GET | Comprehensive health test | Full scrape testing |
| `/api/metrics` | GET | Performance analytics | Success rates, processing speeds |
| `/api/queue` | GET | Redis queue monitoring | Bull queue integration |

### Enhanced API Responses

Jobs now include enhanced tracking data:
```json
{
  "job_id": "dashboard_1_1234567890",
  "status": "running",
  "progress_percentage": 65.5,
  "processing_rate_per_minute": 12.3,
  "estimated_completion": "2024-01-15T14:30:00Z",
  "success_rate": 94.2,
  "current_url": "https://example.com/page-123",
  "total_time_seconds": 145.7,
  "errors": [],
  "expandable_details": { ... }
}
```

## 🧪 Testing

### Running the Enhanced Dashboard

```bash
# Start with enhanced features
./dashboard.sh start

# Test specific features
curl http://localhost:8000/api/jobs     # Enhanced job data
curl http://localhost:8000/api/metrics  # Performance analytics
curl http://localhost:8000/             # Enhanced UI
curl http://localhost:8000/classic      # Classic UI
```

### Feature Testing

**Enhanced Job Cards:**
1. Start a crawl job with multiple URLs
2. Watch real-time progress updates
3. Click chevron to expand job details
4. Click eye icon for modal view
5. Test individual job cancellation

**Auto-refresh:**
1. Toggle auto-refresh on/off
2. Watch live updates every 5 seconds
3. Verify visual feedback for refresh state

**Performance Monitoring:**
1. Monitor processing rates during jobs
2. Check ETA accuracy
3. Verify success rate calculations

## 🔒 Security & Production

### Enhanced Security Features

- 🛡️ **Safe Process Management**: Only targets dashboard processes
- 🔐 **Input Validation**: Enhanced form validation and sanitization
- 🚨 **Error Handling**: Comprehensive error handling without data leaks
- 📊 **Activity Logging**: Enhanced logging for security monitoring

### Production Deployment

```bash
# Production startup with port detection
DASHBOARD_PORT=8000 ./dashboard.sh start

# Or use environment-specific configuration
DASHBOARD_HOST=0.0.0.0 DASHBOARD_PORT=80 ./dashboard.sh start
```

## 🎉 Migration from Basic Dashboard

### Enhanced Features Available

If you're upgrading from a basic dashboard:

✅ **Immediate Benefits:**
- Expandable job cards with detailed information
- Real-time progress tracking with live updates
- Auto-refresh with visual feedback
- Modal job details with comprehensive analytics
- Individual job cancellation capabilities
- Enhanced error tracking and reporting

✅ **Backward Compatibility:**
- Classic dashboard still available at `/classic`
- All existing API endpoints continue to work
- Configuration remains the same
- No breaking changes to existing integrations

### Upgrade Process

1. **Backup current configuration:**
   ```bash
   cp .env .env.backup
   ```

2. **Update to enhanced version:**
   ```bash
   git pull origin main
   uv sync
   ```

3. **Test enhanced features:**
   ```bash
   ./dashboard.sh start
   # Visit http://localhost:8000 for enhanced UI
   # Visit http://localhost:8000/classic for original UI
   ```

## 🤝 Contributing

The enhanced dashboard welcomes contributions:

### Development Areas

- 🎨 **UI/UX Enhancements**: Improve the expandable card interface
- 📊 **Analytics Features**: Add more performance metrics
- 🔧 **Job Management**: Enhance job control capabilities
- 📱 **Mobile Experience**: Optimize for mobile devices
- 🧪 **Testing**: Expand test coverage for new features

### Development Setup

```bash
# Development with enhanced features
uv sync --dev
./dashboard.sh start  # Auto-detects free port
```

## 🆘 Support & Troubleshooting

### Enhanced Dashboard Issues

**Expandable Cards Not Working:**
- Check browser JavaScript console for errors
- Verify enhanced template is loading correctly
- Try classic dashboard at `/classic` as fallback

**Auto-refresh Issues:**
- Check UPDATE_INTERVAL configuration
- Verify network connectivity
- Monitor browser developer tools for failed requests

**Job Details Modal Problems:**
- Ensure `/api/jobs/{job_id}` endpoint is working
- Check browser popup blockers
- Verify job exists in dashboard tracking

### Getting Help

For enhanced dashboard issues:
1. 📚 Check this updated README
2. 🔧 Run `./dashboard.sh status` for diagnostics
3. 🧪 Test classic dashboard at `/classic`
4. 💬 Create issue with enhanced feature details

---

## 🌟 Why Choose the Enhanced Dashboard?

**Before Enhancement:**
❌ Basic job lists without details  
❌ Manual refresh required  
❌ Limited job management  
❌ No real-time progress tracking  
❌ Basic error reporting  

**After Enhancement:**
✅ **Expandable Job Cards** with detailed metrics  
✅ **Real-time Progress** with live updates  
✅ **Auto-refresh** with visual feedback  
✅ **Individual Job Control** with safe cancellation  
✅ **Performance Analytics** with ETA and success rates  
✅ **Professional Interface** rivaling commercial dashboards  

Perfect for teams running production Firecrawl infrastructure! 🕷️✨

---

**Enhanced Dashboard - Built with ❤️ for the Firecrawl community**

*Featuring 54% code reduction, enhanced job tracking, and professional-grade monitoring capabilities*
