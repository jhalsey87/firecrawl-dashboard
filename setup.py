#!/usr/bin/env python3
"""
Setup script for Firecrawl Dashboard
For modern installations, prefer: pip install -e .
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_path = Path(__file__).parent / "docs" / "README.md"
long_description = readme_path.read_text() if readme_path.exists() else ""

setup(
    name="firecrawl-dashboard",
    version="0.1.0",
    description="Web monitoring dashboard for self-hosted Firecrawl instances",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Christian",
    python_requires=">=3.12",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    package_data={
        "firecrawl_dashboard": ["templates/*.html"],
    },
    install_requires=[
        "aiohttp>=3.11.18",
        "fastapi>=0.115.12",
        "jinja2>=3.1.6",
        "python-dotenv>=1.1.0",
        "python-multipart>=0.0.20",
        "redis>=6.1.0",
        "uvicorn>=0.34.2",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "firecrawl-dashboard=firecrawl_dashboard.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
    ],
)
