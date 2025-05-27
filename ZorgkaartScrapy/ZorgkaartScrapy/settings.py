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

# Downloadvertraging tussen requests
DOWNLOAD_DELAY = 1  # seconden

# Maximaal aantal gelijktijdige requests per domein
CONCURRENT_REQUESTS_PER_DOMAIN = 4

# AutoThrottle inschakelen voor dynamische snelheid
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 2
AUTOTHROTTLE_DEBUG = False

# Cookies uitgeschakeld (indien niet nodig)
COOKIES_ENABLED = False

# Pipelines activeren om naar Excel te schrijven
ITEM_PIPELINES = {
    "ZorgkaartScrapy.pipelines.ExcelExportPipeline": 300,
}

# Excel-pipeline vereist UTF-8 encoding
FEED_EXPORT_ENCODING = "utf-8"

# Logging (optioneel)
LOG_LEVEL = "INFO"
