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

# Niet verplicht robots.txt te volgen, anders blokkeert zorgkaart alles
ROBOTSTXT_OBEY = False

# Zorg voor rustiger en evenwichtiger crawling
DOWNLOAD_DELAY = 1  # 1 seconde vertraging tussen requests
RANDOMIZE_DOWNLOAD_DELAY = True  # voeg random jitter toe
CONCURRENT_REQUESTS_PER_DOMAIN = 2  # max 2 tegelijk naar hetzelfde domein
CONCURRENT_REQUESTS_PER_IP = 2  # optioneel als IP-throttling nodig is

# Schakel AutoThrottle in om snelheid aan te passen aan de serverrespons
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0  # gemiddeld 1 gelijktijdige request
AUTOTHROTTLE_DEBUG = False

# Cookies uitgeschakeld (indien niet nodig)
COOKIES_ENABLED = False

# Pipelines activeren om naar Excel te schrijven
ITEM_PIPELINES = {
    "ZorgkaartScrapy.pipelines.ExcelExportPipeline": 300,
}

# Excel-pipeline vereist UTF-8 encoding
FEEDS = {
    'data/%(name)s.json': {
        'format': 'json',
        'encoding': 'utf8',
        'store_empty': False,
        'overwrite': True
    }
}

# Logging (optioneel)
LOG_LEVEL = "INFO"

# Zorg voor robuustheid bij fouten
RETRY_ENABLED = True
RETRY_TIMES = 5
RETRY_HTTP_CODES = [429, 503, 500, 502, 504]
DOWNLOAD_TIMEOUT = 30