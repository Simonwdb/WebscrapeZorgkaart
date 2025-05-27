import scrapy
from typing import Generator, Dict, Any


class ZorgkaartOrganisatietypesSpider(scrapy.Spider):
    name = "zorgkaart_organisatietypes"
    allowed_domains = ["zorgkaartnederland.nl"]
    start_urls = ["https://www.zorgkaartnederland.nl/overzicht/organisatietypes"]

    custom_settings = {
        "FEEDS": {
            "data/organisatietypes.json": {
                "format": "json",
                "encoding": "utf8",
                "overwrite": True,
            }
        }
    }

    def parse(self, response: scrapy.http.Response) -> Generator[Dict[str, Any], None, None]:
        for a_tag in response.css("a.filter-radio"):
            url = response.urljoin(a_tag.css("::attr(href)").get())

            # Pak alles behalve de teller (span) → alleen de naam
            naam_rouwe = a_tag.xpath("text()[normalize-space()]").get()
            naam = naam_rouwe.strip() if naam_rouwe else "onbekend"

            aantal_str = a_tag.css("span.filter-radio__counter::text").get()
            try:
                aantal = int(aantal_str.strip("()")) if aantal_str else None
            except ValueError:
                aantal = None

            yield {
                "organisatietype": naam,
                "url": url,
                "aantal": aantal
            }
