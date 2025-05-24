📁 FIRECRAWL DASHBOARD - PROJECT OVERVIEW
==========================================

🎯 **PURPOSE**: Web monitoring dashboard for self-hosted Firecrawl instances

## 📂 PROJECT STRUCTURE

```
firecrawl-dashboard/
├── 📦 src/
│   └── firecrawl_dashboard/     # Main application package
│       ├── __init__.py          # Package initialization
│       ├── main.py              # FastAPI app with all endpoints
│       └── templates/           # Jinja2 templates
│           └── dashboard.html   # Main dashboard interface
│
├── 🧪 scripts/                  # Utility and debug scripts
│   ├── debug_health.py          # Health endpoint testing
│   └── emergency_flood_stop.py  # Emergency Redis queue control
│
├── 🔧 tests/                    # Test suite
│   └── test_*.py                # Unit and integration tests
│
├── 📚 docs/                     # Documentation
│   └── PROJECT_OVERVIEW.md      # This overview document
│
├── ⚙️ Configuration Files
│   ├── pyproject.toml           # Project metadata & dependencies
│   ├── requirements.txt         # Pip-compatible requirements
│   ├── uv.lock                  # Dependency lock file
│   ├── .env.example             # Environment template
│   └── .env                     # Local configuration
│
└── 🚀 Entry Points
    ├── README.md                # Complete setup guide & documentation
    ├── run_dashboard.py         # Development entry point
    ├── firecrawl-dashboard      # CLI script (after installation)
    └── setup.py                 # Package installation
```

## 🚀 QUICK START

1. **Configure**: `cp .env.example .env` and edit with your Firecrawl settings
2. **Install**: `uv sync` (or `pip install -e .`)
3. **Run**: `python run_dashboard.py` (or `firecrawl-dashboard`)
4. **Open**: [http://localhost:8000](http://localhost:8000)

## ✨ FEATURES

### 🏥 Core Monitoring
- **Real-time health monitoring** with auto-refresh
- **Job management** - start, monitor, cancel scrape/crawl jobs
- **Performance metrics** and success rate tracking
- **Manual health testing** with comprehensive checks
### 🔄 Advanced Queue Management
- **Direct Redis connection** to Firecrawl's Bull job queues
- **Flood detection** - automatic alerts for runaway job queues
- **Emergency controls** - clear stuck jobs with one click
- **Queue visibility** - see jobs invisible to standard API

### 🎨 Professional Interface
- **Clean responsive UI** with TailwindCSS
- **Real-time updates** using HTMX (no page refreshes)
- **Color-coded status** indicators and progress bars
- **Debug tools** integrated into the interface

## 🔧 TECHNOLOGY STACK

- **Backend**: FastAPI with async/await
- **Frontend**: HTML5 + TailwindCSS + HTMX
- **Templates**: Jinja2 server-side rendering
- **HTTP Client**: aiohttp for Firecrawl communication
- **Queue Monitoring**: Direct Redis connection to Bull queues
- **Package Management**: UV for modern Python dependency management

## 🎯 CURRENT STATUS

### ✅ **FULLY OPERATIONAL**
- Health checks working correctly
- Job management fully functional
- Redis queue monitoring active
- Emergency flood controls tested
- All API endpoints operational
- Documentation complete and up-to-date


## 🎪 **USE CASES**

### 🏢 **Perfect For**
- Teams running self-hosted Firecrawl instances
- Organizations needing web-based job management
- Developers requiring real-time monitoring
- Operations teams managing large-scale crawling
- Troubleshooting and debugging Firecrawl issues

### 🚨 **Especially Useful For**
- **Job Flood Management**: See and stop runaway crawl jobs
- **Queue Visibility**: Monitor Redis Bull queues directly
- **Health Monitoring**: Continuous status tracking
- **Performance Analysis**: Success rates and response times
- **Emergency Response**: Quick tools for crisis situations

## 🛠️ **INSTALLATION OPTIONS**

### Option 1: UV (Recommended)
```bash
uv sync && uv run python run_dashboard.py
```

### Option 2: Pip Install
```bash
pip install -e . && firecrawl-dashboard
```

### Option 3: Direct Dependencies
```bash
pip install -r requirements.txt && python run_dashboard.py
```

## 🌐 **INTEGRATION**

### **Firecrawl Requirements**
- Self-hosted Firecrawl instance (any recent version)
- Accessible Redis instance (for queue monitoring)
- Network connectivity between dashboard and Firecrawl

### **Configuration**
- Update `FIRECRAWL_API_URL` to your instance
- Set `REDIS_HOST` to your Firecrawl's Redis
- Optional: Configure API key if authentication enabled

---

**Status: ✅ Production Ready & Fully Functional! 🕷️✨**

*The dashboard successfully fills the missing web interface gap for self-hosted Firecrawl instances, providing professional monitoring and management capabilities.*