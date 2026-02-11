"""Scrapy settings for the Pokepedia scraper (rate-limited, robots.txt compliant)."""

# ==================================================
# Core Scrapy configuration
# ==================================================

BOT_NAME = "pokepedia_scraper"

SPIDER_MODULES = ["pokepedia_scraper.spiders"]
NEWSPIDER_MODULE = "pokepedia_scraper.spiders"


# Bot identification
# Educational project user-agent for transparency

USER_AGENT = (
 "Mozilla/5.0 (X11; Linux x86_64) "
 "AppleWebKit/537.36 (KHTML, like Gecko) "
 "Chrome/120.0 Safari/537.36 "
 "(Educational project – Pokémon Let's Go data analysis)"
)


# Robots.txt compliance

ROBOTSTXT_OBEY = True


# Request rate limiting

CONCURRENT_REQUESTS = 8
CONCURRENT_REQUESTS_PER_DOMAIN = 2

DOWNLOAD_DELAY = 1.2
RANDOMIZE_DOWNLOAD_DELAY = True

DOWNLOAD_TIMEOUT = 15


# Retry policy (transient errors only)

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


# AutoThrottle

AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1.0
AUTOTHROTTLE_MAX_DELAY = 5.0
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
AUTOTHROTTLE_DEBUG = False


# Item pipelines

ITEM_PIPELINES = {
 "pokepedia_scraper.pipelines.PokemonMovePipeline": 300,
}


# HTTP cache

HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 3600 # 1 hour
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


# Logging

LOG_LEVEL = "INFO"


# Feed export

FEED_EXPORT_ENCODING = "utf-8"


# Scrapy compatibility

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"

TWISTED_REACTOR = (
 "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
)
