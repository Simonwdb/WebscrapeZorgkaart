import scrapy


class ZorgkaartNumberSpiderSpider(scrapy.Spider):
    name = "zorgkaart_number_spider"
    allowed_domains = ["zorgkaartnederland.nl"]
    start_urls = ["https://zorgkaartnederland.nl"]

    def parse(self, response):
        pass
