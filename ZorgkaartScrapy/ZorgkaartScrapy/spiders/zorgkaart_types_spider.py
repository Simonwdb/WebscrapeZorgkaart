import scrapy
import datetime
from typing import Generator, Dict, Any


class ZorgkaartOrganisatietypesSpider(scrapy.Spider):
    name = "zorgkaart_types"
    allowed_domains = ["zorgkaartnederland.nl"]
    start_urls = ["https://www.zorgkaartnederland.nl/overzicht/organisatietypes"]

    custom_settings = {
        "FEEDS": {
            "data/zorgkaart_types.json": {
                "format": "json",
                "encoding": "utf8",
                "overwrite": True,
            }
        }
    }

    def parse(self, response: scrapy.http.Response) -> Generator[Dict[str, Any], None, None]:
        self.logger.info("▶ Start met scrapen van organisatietypes...")

        totaal = 0

        for a_tag in response.css("a.filter-radio"):
            url = response.urljoin(a_tag.css("::attr(href)").get())

            naam_rouwe = a_tag.xpath("text()[normalize-space()]").get()
            naam = naam_rouwe.strip() if naam_rouwe else "onbekend"

            aantal_str = a_tag.css("span.filter-radio__counter::text").get()
            try:
                aantal = int(aantal_str.strip("()")) if aantal_str else None
            except ValueError:
                aantal = None

            self.logger.info(f"Gevonden organisatietype: {naam} ({aantal}) - {url}")
            totaal += 1

            yield {
                "organisatietype": naam,
                "url": url,
                "aantal": aantal,
                "scraped_at": datetime.date.today().isoformat()
            }

        self.logger.info(f"✅ Scrapen van organisatietypes voltooid ({totaal} types gevonden).")
