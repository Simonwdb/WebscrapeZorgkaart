import scrapy


class ZorgkaartTypesSpider(scrapy.Spider):
    name = "zorgkaart_types"
    allowed_domains = ["zorgkaartnederland.nl"]
    start_urls = ["https://www.zorgkaartnederland.nl/overzicht/organisatietypes"]

    def parse(self, response):
        base_url = "https://www.zorgkaartnederland.nl"
        links = response.css('div.search-list a[href]')
        for link in links:
            relative_url = link.attrib['href'].strip()
            name = link.css('::text').get().strip()

            if relative_url.startswith('/'):
                relative_url = relative_url[1:]

            yield {
                'organisatietype': name,
                'url': f"{base_url}/{relative_url}"
            }
