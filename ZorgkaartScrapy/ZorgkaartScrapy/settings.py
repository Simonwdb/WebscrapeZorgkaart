import datetime
from pathlib import Path

# Scrapy settings for ZorgkaartScrapy project

BOT_NAME = "ZorgkaartScrapy"

SPIDER_MODULES = ["ZorgkaartScrapy.spiders"]
NEWSPIDER_MODULE = "ZorgkaartScrapy.spiders"

# Identificeer jezelf netjes
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/114.0.0.0 Safari/537.36"
)

# Robots.txt niet volgen (Zorgkaart blokkeert anders)
ROBOTSTXT_OBEY = False

# Crawl-instellingen voor snelheid
DOWNLOAD_DELAY = 0.1
RANDOMIZE_DOWNLOAD_DELAY = True
CONCURRENT_REQUESTS = 32
CONCURRENT_REQUESTS_PER_DOMAIN = 8
CONCURRENT_REQUESTS_PER_IP = 8

# AutoThrottle actief en ingesteld voor snelheid
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 0.5
AUTOTHROTTLE_MAX_DELAY = 5
AUTOTHROTTLE_TARGET_CONCURRENCY = 4.0
AUTOTHROTTLE_DEBUG = True  # Log automatisch aangepaste vertragingen

# Cookies uitgeschakeld
COOKIES_ENABLED = False

# FEEDS naar JSON
FEEDS = {
    'data/%(name)s.json': {
        'format': 'json',
        'encoding': 'utf8',
        'store_empty': False,
        'overwrite': True
    }
}

# Logging naar bestand
LOG_LEVEL = "INFO"
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

LOG_ENABLED = False
LOG_STDOUT = False
LOG_FILE = str(log_dir / f"scrapy_run_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

# Hertries voor foutcodes
RETRY_ENABLED = True
RETRY_TIMES = 5
RETRY_HTTP_CODES = [429, 503, 500, 502, 504]

# Max wachttijd voor response
DOWNLOAD_TIMEOUT = 5
