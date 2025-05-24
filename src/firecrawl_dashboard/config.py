"""
Configuration management for Firecrawl Dashboard
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """Application settings loaded from environment variables"""
    
    def __init__(self):
        # Firecrawl configuration
        self.firecrawl_api_url: str = os.getenv("FIRECRAWL_API_URL", "http://localhost:3002")
        self.firecrawl_api_key: str = os.getenv("FIRECRAWL_API_KEY", "dummy")
        
        # Redis configuration
        self.redis_host: str = os.getenv("REDIS_HOST", "localhost")
        self.redis_port: int = int(os.getenv("REDIS_PORT", "6379"))
        self.redis_db: int = int(os.getenv("REDIS_DB", "0"))
        
        # Dashboard configuration
        self.dashboard_host: str = os.getenv("DASHBOARD_HOST", "0.0.0.0")
        self.dashboard_port: int = int(os.getenv("DASHBOARD_PORT", "8000"))
        self.update_interval: int = int(os.getenv("UPDATE_INTERVAL", "5"))
        
        # Feature flags
        self.enable_auto_scrape_test: bool = os.getenv("ENABLE_AUTO_SCRAPE_TEST", "false").lower() == "true"
        
        # Firecrawl scraping parameters
        self.firecrawl_formats: str = os.getenv("FIRECRAWL_FORMATS", "markdown,html")
        self.firecrawl_only_main_content: bool = os.getenv("FIRECRAWL_ONLY_MAIN_CONTENT", "true").lower() == "true"
        self.firecrawl_include_tags: str = os.getenv("FIRECRAWL_INCLUDE_TAGS", "h1,h2,h3,p,code,pre,ul,ol,li")
        self.firecrawl_exclude_tags: str = os.getenv("FIRECRAWL_EXCLUDE_TAGS", "nav,footer,header,ads,sidebar")
        self.firecrawl_wait_for: int = int(os.getenv("FIRECRAWL_WAIT_FOR", "3000"))
        self.firecrawl_timeout: int = int(os.getenv("FIRECRAWL_TIMEOUT", "30"))
        self.firecrawl_mobile: bool = os.getenv("FIRECRAWL_MOBILE", "false").lower() == "true"
        self.firecrawl_max_urls_per_site: int = int(os.getenv("FIRECRAWL_MAX_URLS_PER_SITE", "10"))
        
        # Client configuration
        self.max_concurrent_requests: int = int(os.getenv("MAX_CONCURRENT_REQUESTS", "3"))
        self.delay_between_batches: float = float(os.getenv("DELAY_BETWEEN_BATCHES", "2.0"))
    
    @property
    def redis_url(self) -> str:
        """Get Redis connection URL"""
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    @property
    def firecrawl_headers(self) -> dict:
        """Get headers for Firecrawl API requests"""
        headers = {}
        if self.firecrawl_api_key and self.firecrawl_api_key != "dummy":
            headers["Authorization"] = f"Bearer {self.firecrawl_api_key}"
        return headers
    
    def get_scraping_params(self) -> dict:
        """Get default scraping parameters"""
        return {
            "formats": self.firecrawl_formats.split(","),
            "onlyMainContent": self.firecrawl_only_main_content,
            "includeTags": self.firecrawl_include_tags.split(","),
            "excludeTags": self.firecrawl_exclude_tags.split(","),
            "waitFor": self.firecrawl_wait_for,
            "timeout": self.firecrawl_timeout,
            "mobile": self.firecrawl_mobile
        }
    
    def get_crawling_params(self) -> dict:
        """Get default crawling parameters"""
        params = self.get_scraping_params()
        params["limit"] = self.firecrawl_max_urls_per_site
        return params


# Global settings instance
settings = Settings()
