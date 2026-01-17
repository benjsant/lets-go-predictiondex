"""
Scrapy settings module for pokepedia_scraper
============================================

This module defines the global Scrapy configuration used for scraping
Poképédia pages related to Pokémon Let's Go (LGPE).

Project context:
- Educational and non-commercial project
- Data collection for Pokémon mechanics analysis
- Part of the letsgo_predictiondex ETL pipeline

Objectives:
- Responsible and transparent web scraping
- Strict compliance with robots.txt directives
- Controlled request rate to avoid server overload
- Deterministic and reproducible data extraction

E1 compliance highlights:
- Explicit bot identification (USER_AGENT)
- robots.txt enforcement
- Throttling, retry limits, and HTTP caching
- Structured logging for traceability

Scope:
This configuration is intentionally conservative and prioritizes
ethical scraping practices over raw performance.
"""

# ==================================================
# 🧱 Core Scrapy configuration
# ==================================================

BOT_NAME = "pokepedia_scraper"

SPIDER_MODULES = ["pokepedia_scraper.spiders"]
NEWSPIDER_MODULE = "pokepedia_scraper.spiders"


# ==================================================
# 🧑‍💻 Bot identification (E1 – transparency requirement)
# ==================================================
# Clear identification of the scraper:
# - Declares educational intent
# - Allows site administrators to understand usage context
# - Avoids ambiguous or misleading user-agent strings

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0 Safari/537.36 "
    "(Educational project – Pokémon Let's Go data analysis)"
)


# ==================================================
# 🤖 Robots.txt compliance
# ==================================================
# Mandatory for responsible scraping.
# Ensures that disallowed paths are never accessed.

ROBOTSTXT_OBEY = True


# ==================================================
# 🐢 Request rate limiting (human-like behavior)
# ==================================================
# Goals:
# - Avoid overloading Poképédia servers
# - Mimic realistic user navigation patterns
# - Stay well below aggressive crawling thresholds

CONCURRENT_REQUESTS = 8
CONCURRENT_REQUESTS_PER_DOMAIN = 2

DOWNLOAD_DELAY = 1.2
RANDOMIZE_DOWNLOAD_DELAY = True

DOWNLOAD_TIMEOUT = 15


# ==================================================
# 🔁 Retry policy (network resilience only)
# ==================================================
# Retries are intentionally limited:
# - Only transient server or timeout errors
# - Prevents retry storms and unintended pressure

RETRY_ENABLED = True
RETRY_TIMES = 2

RETRY_HTTP_CODES = [
    500,
    502,
    503,
    504,
    522,
    524,
    408,
]


# ==================================================
# 🚦 AutoThrottle extension
# ==================================================
# Dynamically adapts crawl speed based on server response times.
# Helps maintain a respectful load even if conditions change.

AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1.0
AUTOTHROTTLE_MAX_DELAY = 5.0
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
AUTOTHROTTLE_DEBUG = False


# ==================================================
# 🧪 Item pipelines
# ==================================================
# Centralized post-processing layer:
# - Data normalization
# - Validation and cleaning
# - Future database persistence

ITEM_PIPELINES = {
    "pokepedia_scraper.pipelines.PokemonMovePipeline": 300,
}


# ==================================================
# 💾 HTTP cache (critical for Poképédia)
# ==================================================
# Benefits:
# - Avoids repeated requests to the same pages
# - Reduces server load
# - Speeds up development and debugging cycles

HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 3600  # 1 hour
HTTPCACHE_DIR = "httpcache"

HTTPCACHE_IGNORE_HTTP_CODES = [
    500,
    502,
    503,
    504,
]

HTTPCACHE_STORAGE = (
    "scrapy.extensions.httpcache.FilesystemCacheStorage"
)


# ==================================================
# 📜 Logging configuration
# ==================================================
# INFO level provides a good balance between visibility
# and noise for ETL-style scraping tasks.

LOG_LEVEL = "INFO"


# ==================================================
# 📤 Feed export settings
# ==================================================
# Ensures consistent UTF-8 encoding for all exported data.

FEED_EXPORT_ENCODING = "utf-8"


# ==================================================
# ⚙️ Modern Scrapy compatibility
# ==================================================
# Explicit configuration to avoid deprecation warnings
# and ensure compatibility with recent Scrapy versions.

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"

TWISTED_REACTOR = (
    "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
)
